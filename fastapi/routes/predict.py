from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from database import get_session
from models.database import Prediction
from models.predict import PredictRequest, PredictResponse, PredictionResponse
from security.jwt import get_current_user

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
def predict(
    payload: PredictRequest,
    current_user=Depends(get_current_user),
    session: Session = Depends(get_session)
):
    intent = deterministic_intent(payload.text)

    prediction = Prediction(
        text=payload.text,
        intent=intent,
        owner_id=current_user.id
    )

    session.add(prediction)
    session.commit()
    session.refresh(prediction)

    return {
        "text": prediction.text,
        "intent": prediction.intent
    }


@router.get("/predict/{prediction_id}", response_model=PredictionResponse)
def get_prediction(
    prediction_id: int,
    current_user=Depends(get_current_user),
    session: Session = Depends(get_session)
):
    prediction = session.exec(
        select(Prediction).where(
            Prediction.id == prediction_id
        )
    ).first()

    if not prediction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prediction não encontrada"
        )

    if prediction.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado"
        )

    return prediction