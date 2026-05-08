# Documentação Timezap (agente de ponto)

Este diretório define **comportamento do agente** em ficheiros editáveis, sem código.

| Pasta | Ficheiro | Função |
|--------|-----------|--------|
| `persona/` | `persona.md` | Identidade, tom e papel do agente face aos colaboradores. |
| `guardrails/` | `guardrails.md` | Limites obrigatórios: dados pessoais, fotos, recusas, escalamento. |
| `playbooks/` | `*.md` | Fluxos operacionais (ex.: registo de ponto **com foto**). |

Ao arrancar, `app.py` junta estes Markdown na ordem: persona → guardrails → playbooks (ordenados por nome).

**Reinicia** o servidor (`python run.py`) depois de alterares os `.md` para o agente ler a versão nova.

**Deploy (Render):** ver [`deploy-render.md`](deploy-render.md).

**Ideia do produto:** o agente **Timezap** é o **cérebro** do sistema: orquestra o registo de ponto (entrada/saída com **foto**, fluxos guiados e regras). Canais e backends conectam-se depois ao que o Timezap já decide em conversação; os playbooks descrevem o processo alvo.
