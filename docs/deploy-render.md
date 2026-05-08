# Deploy no Render — Timezap

O teu log **ainda** mostra na fase **Deploy** something como:

`Running 'pip install --upgrade pip && pip install -r requirements.txt'`

e depois **Application exited early**. Isso só acontece quando o **Start Command** no painel do Render está **igual ao Build Command** (instala pacotes e termina — **não há servidor**).

---

## Correção imediata (Web Service em “Python”)

1. Abre [Render Dashboard](https://dashboard.render.com) → serviço **Timezap** → **Settings**.
2. Localiza **Start Command**.
3. **Apaga tudo** que seja `pip install` (ou comando de build).
4. Cola **uma** destas linhas (recomendado a primeira):

```bash
uvicorn app:app --host 0.0.0.0 --port $PORT
```

ou:

```bash
python run.py
```

5. Confirma que **Build Command** continua só com `pip install …` (esse é o lugar certo para o pip).
6. **Save Changes** → **Manual Deploy**.

O **`Procfile`** do repositório **só vale** se o **Start Command estiver vazio**; se o campo tiver `pip install`, o Render **ignora** o Procfile.

---

## Opção Dockerfile (menos erro de configuração)

O repositório tem **`Dockerfile`** que faz build e arranca só com **`uvicorn`**.

1. No mesmo serviço (ou novo): **Settings** → muda **Environment** / tipo de runtime para **Docker** (mantendo o mesmo repositório).
2. **Dockerfile path:** `Dockerfile` (raiz do repo).
3. **Start Command** no painel: **deixa vazio** (usa o `CMD` do Dockerfile).
4. **Save** → redeploy.

O `render.yaml` do repo está alinhado com **Docker** para quem usar **Blueprint**.

---

## Variáveis necessárias

- **`MISTRAL_API_KEY`** (secret), no Environment do serviço.
- **`PORT`** — o Render injeta; não definas à mão.

---

## Resumo

| Fase Render    | Deve corresponder a…                                      |
|----------------|------------------------------------------------------------|
| Build          | `pip install -r requirements.txt` (etc.)                   |
| Start / Deploy | `uvicorn app:app --host 0.0.0.0 --port $PORT` **ou** Dockerfile |

Enquanto o Start for `pip install`, o deploy **sempre** falha da mesma forma.
