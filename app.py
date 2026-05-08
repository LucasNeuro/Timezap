"""

AgentOS: **Timezap** — agente-inteligência (o cérebro) do sistema de registo de ponto.

Comportamento em Markdown:



  docs/persona/persona.md

  docs/guardrails/guardrails.md

  docs/playbooks/*.md



Modelo: Mistral. SQLite: tmp/agentos.db



  pip install -r requirements.txt

  python run.py



Windows / HTTPS Mistral: AGNO_USE_CERTIFI_CA, AGNO_SSL_TRUSTSTORE.

"""



from __future__ import annotations



import os

import ssl

from pathlib import Path

from typing import Any



from dotenv import load_dotenv



from timezap_docs import compose_agent_instructions_from_docs



load_dotenv()





def _certifi_bundle_path() -> str | None:

    """PEM certifi; desativar: AGNO_USE_CERTIFI_CA=0."""

    raw = os.getenv("AGNO_USE_CERTIFI_CA", "").strip().lower()

    if raw in ("0", "false", "no", "off"):

        return None

    import sys



    if sys.platform != "win32" and raw == "":

        return None

    if raw not in ("", "1", "true", "yes", "on"):

        return None

    try:

        import certifi



        return certifi.where()

    except ImportError:

        return None





def _apply_certifi_ssl_bundle_env() -> None:

    ca = _certifi_bundle_path()

    if not ca:

        return

    os.environ.setdefault("SSL_CERT_FILE", ca)

    os.environ.setdefault("REQUESTS_CA_BUNDLE", ca)

    os.environ.setdefault("CURL_CA_BUNDLE", ca)





_apply_certifi_ssl_bundle_env()



from agno.agent import Agent

from agno.db.sqlite import SqliteDb

from agno.models.mistral import MistralChat

from agno.os import AgentOS





def _httpx_verify_for_mistral_sdk() -> str | ssl.SSLContext | None:

    """Truststore no Windows; AGNO_SSL_TRUSTSTORE=0 → certifi se existir."""

    import sys



    ts = os.getenv("AGNO_SSL_TRUSTSTORE", "").strip().lower()

    if ts not in ("0", "false", "no", "off"):

        if sys.platform == "win32":

            try:

                import truststore



                return truststore.SSLContext(ssl.PROTOCOL_TLS_CLIENT)

            except ImportError:

                pass

    return _certifi_bundle_path()





def _mistral_sdk_http_clients() -> dict[str, Any] | None:

    verify = _httpx_verify_for_mistral_sdk()

    if verify is None:

        return None

    import httpx



    return {

        "client": httpx.Client(verify=verify),

        "async_client": httpx.AsyncClient(verify=verify),

    }





_db_dir = Path(__file__).resolve().parent / "tmp"

_db_dir.mkdir(parents=True, exist_ok=True)



_mistral_key = os.getenv("MISTRAL_API_KEY")

_model_id = os.getenv("MISTRAL_MODEL_ID", "mistral-large-latest")

_mistral_client_params = _mistral_sdk_http_clients()

_instructions = compose_agent_instructions_from_docs()



agent_simples = Agent(

    name="Timezap",

    model=MistralChat(

        id=_model_id,

        api_key=_mistral_key,

        client_params=_mistral_client_params,

    ),

    db=SqliteDb(db_file=str(_db_dir / "agentos.db")),

    instructions=_instructions,

    markdown=True,

)



agent_os = AgentOS(agents=[agent_simples])

app = agent_os.get_app()


