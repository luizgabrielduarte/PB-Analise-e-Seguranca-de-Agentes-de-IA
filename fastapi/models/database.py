from sqlmodel import Field, SQLModel


class User(SQLModel, table=True):
    __tablename__ = "users"

    id: int | None = Field(default=None, primary_key=True)
    username: str = Field(unique=True, index=True)
    password: str
    role: str = "user"


class Prediction(SQLModel, table=True):
    __tablename__ = "predictions"

    id: int | None = Field(default=None, primary_key=True)
    text: str
    intent: str
    owner_id: int = Field(foreign_key="users.id")