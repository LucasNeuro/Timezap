"""Arranca o servidor AgentOS (local ou Render)."""

from __future__ import annotations

import os

import uvicorn


def _is_render() -> bool:
    return os.getenv("RENDER", "").strip().lower() == "true"


if __name__ == "__main__":
    # No Render: PORT vem do ambiente; o processo tem de escutar em 0.0.0.0
    default_host = "0.0.0.0" if _is_render() else "127.0.0.1"
    host = os.getenv("HOST", default_host)
    port = int(os.getenv("PORT", "8000"))
    default_reload = "0" if _is_render() else "1"
    reload = os.getenv("RELOAD", default_reload) not in ("0", "false", "False")
    uvicorn.run("app:app", host=host, port=port, reload=reload)
