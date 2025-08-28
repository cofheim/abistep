from fastapi import FastAPI, HTTPException, status
from typing import Dict, List

from app.schemas import SUser, SUserCreate, STransfer

app = FastAPI(
    title="API управления балансом пользователей",
    description="Простой API для управления балансом пользователей",
    version="1.0.0",
)


users_db: Dict[int, SUser] = {}
user_id_counter = 1


@app.get("/")
def read_root():
    return {"message": "Добро пожаловать в API управления балансом пользователей"}


@app.post(
    "/users",
    response_model=SUser,
    status_code=status.HTTP_201_CREATED,
    tags=["Users"],
    summary="Создать нового пользователя",
    responses={
        status.HTTP_400_BAD_REQUEST: {"description": "Email уже зарегистрирован"}
    },
)
def create_user(user: SUserCreate):
    global user_id_counter
    for existing_user in users_db.values():
        if existing_user.email == user.email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Такой email уже зарегистрирован",
            )

    new_user = SUser(
        id=user_id_counter, name=user.name, email=user.email, balance=user.balance
    )
    users_db[new_user.id] = new_user
    user_id_counter += 1
    return new_user


@app.get(
    "/users",
    response_model=List[SUser],
    tags=["Users"],
    summary="Получить список всех пользователей",
)
def get_users():
    return list(users_db.values())


@app.post(
    "/transfer",
    tags=["Transfers"],
    summary="Перевести деньги между пользователями",
    responses={
        status.HTTP_404_NOT_FOUND: {"description": "Пользователь не найден"},
        status.HTTP_400_BAD_REQUEST: {
            "description": "Некорректный запрос на перевод (например, недостаточно средств или перевод самому себе)"
        },
    },
)
def transfer_money(transfer: STransfer):
    from_user = users_db.get(transfer.from_user_id)
    to_user = users_db.get(transfer.to_user_id)

    if not from_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Отправитель не найден"
        )
    if not to_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Получатель не найден"
        )

    if from_user.id == to_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Нельзя переводить деньги самому себе",
        )

    if from_user.balance < transfer.amount:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Недостаточно средств"
        )

    from_user.balance -= transfer.amount
    to_user.balance += transfer.amount

    return {"message": "Перевод выполнен успешно"}
