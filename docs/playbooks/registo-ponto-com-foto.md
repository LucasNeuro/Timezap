# Playbook: registo de ponto com foto

Processo alvo para o colaborador registar **entrada** ou **saída** (e variantes que a empresa ativar) **com envio de fotografia** como comprovação.

> **Nota de implementação:** até existir API de RH / base de dados / canal (ex. WhatsApp) ligada, o agente deve seguir o **fluxo conversacional** e deixar claro quando o registo está “apenas confirmado na conversa” vs “gravado no sistema” — ajusta esta frase quando integrares backend.

## Pré-requisitos

1. Colaborador **identificado** pelo método escolhido pela empresa (número de telefone no canal, matrícula, código curto, etc.).
2. Janela de tempo e tipo de marcação definidos pela política (**entrada**, **saída**, **pausa início/fim**, se aplicável).

## Fluxo principal (feliz caminho)

1. **Boas-vindas e contexto**
   - Confirma que estás a processar um **registo de ponto**.
   - Indica sucintamente que será necessária uma **foto** para concluir (sem alarmismo).

2. **Tipo de marcação**
   - Pergunta: entrada, saída ou outro tipo autorizado.
   - Se o canal já trouxer a intenção (ex.: botão “Entrada”), **confirma** verbalmente antes de seguir.

3. **Momento da marcação**
   - Usa a **hora do servidor/canal** como referência principal; comunica ao colaborador o **dia e hora** que estão a ser usados.
   - Se o colaborador indicar inconsistência forte (ex.: “são 9h mas registo mostra meia-noite”), **não discutas**: regista o pedido de correção como **exceção** e remete para o fluxo manual (RH/supervisor) conforme política da empresa.

4. **Pedido da foto**
   - Pede uma **foto clara**, de frente ou conforme política da empresa, com boa iluminação.
   - Indica formato aceite se o canal exigir (ex.: JPG/PNG por anexo).

5. **Receção e validação mínima (conversa)**
   - Se não houver ficheiro ou imagem: repete o pedido **uma vez**, com instruções mais concretas; se falhar outra vez, para o fluxo e explica que sem foto não há conclusão.
   - Se a imagem existir mas for **manifestamente inadequada**, pede nova foto (mensagem neutra).

6. **Confirmação final**
   - Resume em bullets: tipo de marcação + data/hora utilizada + confirmação de receção de foto (sim/não).
   - Pede confirmação explícita do colaborador: “Posso confirmar o registo?” — só depois consideras o passo concluído do ponto de vista do diálogo.
   - Agradece de forma breve.

## Fluxos alternativos

### Colaborador quer cancelar no meio
- Acknowledge sem julgar. Pergunta se deseja **recomeçar** mais tarde ou **sair**. Não registes marcações só pela conversa se o utilizador cancelou explicitamente.

### Colaborador em local remoto / teletrabalho
- Se a política da empresa permitir, segue o **mesmo** fluxo de foto onde fizer sentido.
- Se não for permitido, explica segundo política interna e remete ao canal oficial.

### Múltiplas marcações seguidas
- Processa **uma** marcação de cada vez. Após confirmar uma, pergunta se precisa de outra (com intervalo breve entre pedidos para evitar erro).

### Erro técnico (API indisponível, timeout)
- Informa que o registo **não pôde ser concluído no sistema**.
- Indica próximo passo: tentar novamente, outro canal, ou RH — conforme configurado pela empresa.

## Linguagem com o utilizador

- Frases curtas; listas quando houver vários passos.
- Evita termos como “checkpoint biométrico” a menos que a empresa os use oficialmente.

## Métricas de qualidade (para equipa de produto)

- Taxa de conversão feliz caminho vs pedidos de nova foto.
- Motivos de paragem (“sem foto”, “identidade não confirmada”).
- Mantém-se em instrumentação futura — o agente **não** precisa mencionar estas métricas ao colaborador.
