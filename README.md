## Dataset

O dataset utilizado é o **Customer Support Ticket Dataset**, publicado por **Suraj** no Kaggle. Ele possui 8.469 tickets e 17 colunas, cobrindo informações do cliente, produto, tipo/assunto do ticket, status, prioridade, canal, tempos de atendimento e satisfação. A página oficial descreve também usos em análise de suporte, NLP, previsão de satisfação, previsão de tempo de resolução, segmentação e recomendação.

Fonte: Kaggle — https://www.kaggle.com/datasets/suraj520/customer-support-ticket-dataset

O notebook documenta a origem, características, qualidade, limpeza, análise univariada e hipóteses.

### Justificativa

Ele foi escolhido porque relaciona diretamente atendimento ao cliente, classificação de intenção e automação de suporte. O campo **Ticket Type** fornece uma variável categórica que pode servir como referência para a futura classificação de intenções, enquanto **Ticket Subject** e **Ticket Description** representam a entrada textual que será enviada à rota `/predict`.

### Credenciais

- usuário: `admin`
- senha: `admin123`

### Rotas

| Método | Rota | Acesso | Descrição |
|---|---|---|---|
| GET | `/health` | Público | Verifica disponibilidade |
| POST | `/auth/token` | Público | Autentica o admin e gera JWT |
| POST | `/predict` | Bearer JWT | Recebe texto e simula intenção |