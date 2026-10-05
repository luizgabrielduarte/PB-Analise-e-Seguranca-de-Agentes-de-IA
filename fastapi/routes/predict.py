from fastapi import APIRouter, Depends

from models.predict import PredictRequest, PredictResponse
from security.jwt import get_current_admin

router = APIRouter(tags=["Prediction"])


def deterministic_intent(text: str) -> str:
    normalized = text.lower()
    if any(term in normalized for term in ["reembolso", "refund", "devolver", "dinheiro de volta"]):
        return "refund_request"
    if any(term in normalized for term in ["cancelar", "cancelamento", "cancellation"]):
        return "cancellation_request"
    if any(term in normalized for term in ["pagamento", "cobrança", "cobranca", "fatura", "billing"]):
        return "billing_inquiry"
    if any(term in normalized for term in ["comprar", "compatibilidade", "recomendação", "recomendacao", "produto"]):
        return "product_inquiry"
    return "technical_issue"


@router.post("/predict", response_model=PredictResponse)
def predict(payload: PredictRequest, current_admin: str = Depends(get_current_admin)):
    return {"text": payload.text, "intent": deterministic_intent(payload.text)}
