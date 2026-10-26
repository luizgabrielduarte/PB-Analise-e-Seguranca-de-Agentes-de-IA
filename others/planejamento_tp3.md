# Planejamento TP3

## 1. Modelo candidato

O modelo candidato inicial será a **Regressão Logística**, utilizando
uma abordagem de classificação multiclasse para prever a intenção de uma
mensagem. Ela é adequada como ponto de partida porque funciona bem com
atributos textuais esparsos, costuma ser rápida para treinar e permite
estabelecer uma referência simples para avaliar o desempenho do
classificador.

O conjunto de dados do projeto contém tickets de atendimento ao cliente.
O campo `Ticket Type` poderá ser usado como rótulo inicial da
classificação, enquanto `Ticket Subject` e `Ticket Description` são
candidatos a compor o texto de entrada. Antes do treinamento, será
necessário confirmar a qualidade dos rótulos, tratar valores ausentes e
separar os dados em conjuntos de treino e teste. O desempenho será
avaliado com métricas adequadas à classificação multiclasse, como
precisão, recall e F1-score.

## 2. Estratégia de representação do texto

Será utilizado o **CountVectorizer**, do scikit-learn, para converter o
texto das mensagens em uma matriz numérica de contagens de palavras.
Cada coluna representa um termo presente no vocabulário aprendido
durante o ajuste, e cada valor indica quantas vezes esse termo aparece
no texto.

A técnica foi escolhida por ser simples, interpretável e compatível com
modelos tradicionais de classificação, como a Regressão Logística. Ela
oferece uma linha de base adequada para a etapa inicial do projeto, sem
exigir modelos pré-treinados ou grande capacidade computacional. O
vocabulário deve ser ajustado apenas com os dados de treino, para evitar
vazamento de informação para a avaliação.

## 3. Alvo autorizado para teste adversarial no TP4/TP5

**Alvo de desenvolvimento local:** `http://127.0.0.1:8000`

Esse endereço corresponde à API FastAPI executada localmente para
desenvolvimento e testes autorizados. As rotas previstas no projeto são:

-   `GET /health` --- verificação de disponibilidade;
-   `POST /auth/token` --- autenticação e emissão de token;
-   `POST /predict` --- envio de texto para previsão, protegida por
    token Bearer.

O endereço `127.0.0.1` aponta para a própria máquina e não é acessível
diretamente pelos demais integrantes da equipe. Portanto, antes das
atividades de pentest do TP4/TP5, a equipe deverá confirmar e registrar
o endereço IP ou URL do ambiente compartilhado/de teste que estiver
autorizado para a atividade. Até que esse ambiente seja disponibilizado,
o alvo válido deste planejamento é apenas a instância local da API, e os
testes devem ficar restritos a ela. Não se deve testar sistemas de
terceiros nem qualquer endereço sem autorização explícita.
