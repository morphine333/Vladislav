from fastapi import FastAPI, Query
from typing import Optional
from pydantic import BaseModel

app = FastAPI()

# Словарь с записями о доходах и расходах семьи
budget = {
    1: {
        "category": "Продукты",
        "amount": 5000.0,
        "type": "расход"
    },
    2: {
        "category": "Зарплата",
        "amount": 50000.0,
        "type": "доход"
    }
}

# Модель для добавления новой записи
class BudgetItem(BaseModel):
    category: str
    amount: float
    type: str

# Модель для обновления записи
class UpdateBudgetItem(BaseModel):
    category: Optional[str] = None
    amount: Optional[float] = None
    type: Optional[str] = None

# GET - получить все записи
@app.get("/")
async def home():
    return {"message": "API учёта семейного хозяйства", "records": budget}

# GET - получить запись по номеру
@app.get("/get-record/{record_id}")
async def get_record(record_id: int):
    if record_id not in budget:
        return {"Error": "Запись не найдена"}
    return budget[record_id]

# POST - добавить новую запись
@app.post("/create-record/{record_id}")
async def create_record(record_id: int, item: BudgetItem):
    if record_id in budget:
        return {"Error": "Запись с таким номером уже существует"}
    budget[record_id] = item
    return budget[record_id]

# PUT - обновить запись
@app.put("/update-record/{record_id}")
async def update_record(record_id: int, item: UpdateBudgetItem):
    if record_id not in budget:
        return {"Error": "Запись не найдена"}
    if item.category is not None:
        budget[record_id].category = item.category
    if item.amount is not None:
        budget[record_id].amount = item.amount
    if item.type is not None:
        budget[record_id].type = item.type
    return budget[record_id]

# DELETE - удалить запись
@app.delete("/delete-record")
async def delete_record(record_id: int = Query(..., description="Номер записи для удаления")):
    if record_id not in budget:
        return {"Error": "Запись не найдена"}
    del budget[record_id]
    return {"Done": "Запись успешно удалена"}

# Второй словарь - члены семьи (ключ - строка)
family_members = {
    "папа": {"name": "Иван", "income": 60000.0, "job": "инженер"},
    "мама": {"name": "Елена", "income": 45000.0, "job": "учитель"}
}

# Модель для добавления члена семьи
class FamilyMember(BaseModel):
    name: str
    income: float
    job: str

# Модель для обновления члена семьи
class UpdateFamilyMember(BaseModel):
    name: Optional[str] = None
    income: Optional[float] = None
    job: Optional[str] = None

# GET - получить члена семьи по имени роли
@app.get("/get-member/{member_id}")
async def get_member(member_id: str):
    if member_id not in family_members:
        return {"Error": "Член семьи не найден"}
    return family_members[member_id]

# POST - добавить члена семьи
@app.post("/create-member/{member_id}")
async def create_member(member_id: str, member: FamilyMember):
    if member_id in family_members:
        return {"Error": "Такой член семьи уже существует"}
    family_members[member_id] = member
    return family_members[member_id]

# PUT - обновить данные члена семьи
@app.put("/update-member/{member_id}")
async def update_member(member_id: str, member: UpdateFamilyMember):
    if member_id not in family_members:
        return {"Error": "Член семьи не найден"}
    if member.name is not None:
        family_members[member_id].name = member.name
    if member.income is not None:
        family_members[member_id].income = member.income
    if member.job is not None:
        family_members[member_id].job = member.job
    return family_members[member_id]

# DELETE - удалить члена семьи
@app.delete("/delete-member")
async def delete_member(member_id: str = Query(..., description="Роль члена семьи (папа, мама и т.д.)")):
    if member_id not in family_members:
        return {"Error": "Член семьи не найден"}
    del family_members[member_id]
    return {"Done": "Член семьи успешно удалён"}