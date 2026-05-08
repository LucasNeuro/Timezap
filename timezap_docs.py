"""Carrega texto de orientação do agente a partir de ``docs/persona``, ``docs/guardrails``, ``docs/playbooks``."""

from __future__ import annotations

from pathlib import Path

_ROOT = Path(__file__).resolve().parent
_DOCS = _ROOT / "docs"


def _read_file(path: Path) -> str:
    if not path.is_file():
        return ""
    return path.read_text(encoding="utf-8").strip()


def compose_agent_instructions_from_docs() -> str:
    """
    Concatena persona, guardrails e todos os ``*.md`` em ``docs/playbooks`` (por nome).

    Se nada existir, devolve instrução mínima.
    """
    blocks: list[str] = []

    persona = _read_file(_DOCS / "persona" / "persona.md")
    if persona:
        blocks.append("## Persona\n\n" + persona)

    guardrails = _read_file(_DOCS / "guardrails" / "guardrails.md")
    if guardrails:
        blocks.append("## Guardrails\n\n" + guardrails)

    play_dir = _DOCS / "playbooks"
    if play_dir.is_dir():
        for md in sorted(play_dir.glob("*.md")):
            body = _read_file(md)
            if body:
                blocks.append(f"## Playbook ({md.name})\n\n{body}")

    if not blocks:
        return (
            "És o assistente do sistema de registo de ponto. "
            "Preenche os ficheiros em docs/persona, docs/guardrails e docs/playbooks."
        )

    return "\n\n---\n\n".join(blocks)
