"""
WhatsApp via UAZAPI (uazapiGO): webhook entrante + POST /send/text.

O ``Whatsapp`` incluído no Agno usa a WhatsApp Cloud API da Meta — não serve para UAZAPI.
Variáveis: ``UAZAPI_BASE_URL``, ``UAZAPI_INSTANCE_TOKEN`` (ver ``.env.example``).
"""

from __future__ import annotations

import logging
import os
from typing import Any

import httpx
from fastapi import APIRouter, BackgroundTasks, HTTPException, Request

from agno.agent import Agent
from agno.os.interfaces.base import BaseInterface

log = logging.getLogger("timezap.uazapi")


def _env_flag_true(name: str) -> bool:
    return os.getenv(name, "").strip().lower() in ("1", "true", "yes", "on")


def uazapi_config() -> tuple[str, str] | None:
    base = os.getenv("UAZAPI_BASE_URL", "").strip().rstrip("/")
    token = os.getenv("UAZAPI_INSTANCE_TOKEN", "").strip()
    if not base or not token:
        return None
    return base, token


def _chunks(text: str, size: int) -> list[str]:
    return [text[i : i + size] for i in range(0, len(text), size)]


async def send_uazapi_text(*, base_url: str, token: str, number: str, text: str) -> None:
    url = f"{base_url}/send/text"
    payload = {"number": number, "text": text}
    headers = {"token": token, "Content-Type": "application/json"}
    async with httpx.AsyncClient(timeout=120.0) as client:
        r = await client.post(url, json=payload, headers=headers)
        if r.status_code >= 400:
            log.warning("UAZAPI send/text failed status=%s body=%s", r.status_code, r.text[:500])
        r.raise_for_status()


async def broadcast_uazapi_text(*, base_url: str, token: str, number: str, content: Any) -> None:
    plain = "" if content is None else str(content).strip()
    if not plain:
        plain = "…"
    for part in _chunks(plain, 4000):
        await send_uazapi_text(base_url=base_url, token=token, number=number, text=part)


def _incoming_message_dicts(payload: dict[str, Any]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []

    for key in ("messages", "Messages", "msgs"):
        v = payload.get(key)
        if isinstance(v, list):
            out.extend(m for m in v if isinstance(m, dict))

    data = payload.get("data") or payload.get("Data")
    if isinstance(data, list):
        out.extend(m for m in data if isinstance(m, dict))
    elif isinstance(data, dict):
        inner = (
            data.get("messages") or data.get("Messages") or data.get("message") or data.get("Message")
        )
        if isinstance(inner, list):
            out.extend(m for m in inner if isinstance(m, dict))
        elif isinstance(inner, dict):
            out.append(inner)
        elif data.get("chatid") or data.get("messageid"):
            out.append(data)

    singular = payload.get("message") or payload.get("Message")
    if isinstance(singular, dict):
        out.append(singular)

    if not out and isinstance(payload.get("chatid"), str):
        out.append(payload)

    seen: set[int] = set()
    dedup: list[dict[str, Any]] = []
    for m in out:
        i = id(m)
        if i in seen:
            continue
        seen.add(i)
        dedup.append(m)
    return dedup


def _reply_target(msg: dict[str, Any]) -> str | None:
    cid = msg.get("chatid") or msg.get("chatId") or msg.get("wa_chatid")
    if isinstance(cid, str) and cid.strip():
        return cid.strip()
    sender = msg.get("sender")
    if isinstance(sender, str) and sender.strip():
        return sender.strip()
    return None


def _incoming_text_body(msg: dict[str, Any]) -> str | None:
    txt = msg.get("text")
    if isinstance(txt, str) and txt.strip():
        return txt.strip()
    ct = msg.get("content")
    if isinstance(ct, str) and ct.strip():
        return ct.strip()
    return None


def _should_ignore_message(msg: dict[str, Any]) -> bool:
    if msg.get("fromMe") is True:
        return True
    if msg.get("wasSentByApi") is True:
        return True
    if _env_flag_true("UAZAPI_IGNORE_GROUPS") and msg.get("isGroup") is True:
        return True

    mt = str(msg.get("messageType") or msg.get("type") or "").strip()
    if mt and mt.lower() not in ("text", "conversation", "extendedtextmessage"):
        return True

    return not (_incoming_text_body(msg) or "")


def attach_uazapi_routes(router: APIRouter, agent: Agent) -> APIRouter:
    webhook_secret_expected = os.getenv("UAZAPI_WEBHOOK_SECRET", "").strip() or None

    def _verify(request: Request) -> None:
        if not webhook_secret_expected:
            return
        if request.query_params.get("secret", "") != webhook_secret_expected:
            raise HTTPException(status_code=403, detail="Invalid webhook secret")

    async def handle_payload(payload: dict[str, Any], background_tasks: BackgroundTasks) -> dict[str, str]:
        cfg = uazapi_config()
        if not cfg:
            log.error("Webhook UAZAPI recebido sem UAZAPI_BASE_URL / UAZAPI_INSTANCE_TOKEN")
            raise HTTPException(status_code=503, detail="UAZAPI not configured")

        base_url, _ = cfg

        msgs = _incoming_message_dicts(payload)
        queued = False
        for msg in msgs:
            if _should_ignore_message(msg):
                continue
            target = _reply_target(msg)
            text_in = _incoming_text_body(msg)
            if not target or not text_in:
                continue
            background_tasks.add_task(_run_agent_and_reply, agent, base_url, target, text_in)
            queued = True

        return {"status": "ok" if queued else "ignored"}

    @router.post("/webhook")
    async def webhook_post(request: Request, background_tasks: BackgroundTasks):
        _verify(request)
        try:
            body = await request.json()
        except Exception as exc:
            raise HTTPException(status_code=400, detail="Invalid JSON") from exc
        if not isinstance(body, dict):
            raise HTTPException(status_code=400, detail="Expected JSON object")
        return await handle_payload(body, background_tasks)

    @router.head("/webhook")
    async def webhook_head(request: Request):
        _verify(request)
        return ""

    @router.get("/status")
    async def iface_status(request: Request):
        _verify(request)
        return {
            "uazapi_configured": uazapi_config() is not None,
            "webhook_requires_secret": webhook_secret_expected is not None,
            "ignore_groups": _env_flag_true("UAZAPI_IGNORE_GROUPS"),
        }

    return router


async def _run_agent_and_reply(agent: Agent, base_url: str, recipient: str, user_text: str) -> None:
    cfg = uazapi_config()
    if not cfg:
        return
    _, token = cfg
    short_user = recipient.split("@", 1)[0] if "@" in recipient else recipient

    try:
        out = await agent.arun(user_text, user_id=short_user, session_id=f"wa:{recipient}")
        await broadcast_uazapi_text(
            base_url=base_url,
            token=token,
            number=recipient,
            content=out.content,
        )
    except Exception:
        log.exception("UAZAPI agent/send failed recipient=%s", recipient)
        try:
            await send_uazapi_text(
                base_url=base_url,
                token=token,
                number=recipient,
                text="Não consegui processar agora. Tenta de novo em instantes.",
            )
        except Exception:
            log.exception("UAZAPI fallback send failed")


class UazapiWhatsappInterface(BaseInterface):
    """Registar em ``AgentOS(..., interfaces=[UazapiWhatsappInterface(agent=...)])``."""

    type = "uazapi_whatsapp"
    router: APIRouter

    def __init__(
        self,
        agent: Agent,
        *,
        prefix: str = "/uazapi",
        tags: list[str] | None = None,
    ):
        self.agent = agent
        self.team = None
        self.workflow = None
        self.prefix = prefix
        self.tags = tags or ["UAZAPI", "WhatsApp"]
        nested = APIRouter(prefix=self.prefix, tags=self.tags)
        self.router = attach_uazapi_routes(nested, agent)

    def get_router(self, use_async: bool = True, **kwargs: Any) -> APIRouter:
        _ = use_async
        _ = kwargs
        return self.router
