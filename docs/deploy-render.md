# Deploy no Render — Web Service Timezap

## Erro típico: `Application exited early`

Se nos logs do deploy aparece:

`Running 'pip install ...'` **na fase Deploy** e depois **`Application exited early`**, quase sempre o **Start Command** está igual ao **Build Command** (só instala pacotes e o processo acaba).

- **Build Command:** `pip install --upgrade pip && pip install -r requirements.txt` (ou só `pip install -r requirements.txt`)
- **Start Command (tem de arrancar o servidor):** um destes:
  - `uvicorn app:app --host 0.0.0.0 --port $PORT` **(recomendado)**, ou
  - `python run.py`

Este repositório inclui **`Procfile`**. Se no painel Render deixares o **Start Command vazio**, o Render pode usar o `Procfile` com `uvicorn`.

## Variáveis

No painel **Environment**, define pelo menos `MISTRAL_API_KEY`. O Render injeta `PORT` e `RENDER=true`.

## Python

Para evitar 3.14.x por defeito, define **`PYTHON_VERSION=3.11.9`** nos Environment Variables e faz redeploy.
