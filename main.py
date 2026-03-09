from fastapi import FastAPI, Query, Depends
from typing import Optional
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.orm import DeclarativeBase, sessionmaker, Session

SQLALCHEMY_DATABASE_URL = "postgresql://vladislavbagaev@localhost/family_budget"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autoflush=False, bind=engine)

class Base(DeclarativeBase): pass

class BudgetRecord(Base):
    __tablename__ = "budget_records"
    id = Column(Integer, primary_key=True, index=True)
    category = Column(String)
    amount = Column(Float)
    type = Column(String)

class FamilyMemberDB(Base):
    __tablename__ = "family_members"
    id = Column(Integer, primary_key=True, index=True)
    member_id = Column(String, unique=True, index=True)
    name = Column(String)
    income = Column(Float)
    job = Column(String)

Base.metadata.create_all(bind=engine)

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class BudgetItemSchema(BaseModel):
    category: str
    amount: float
    type: str

class UpdateBudgetItemSchema(BaseModel):
    category: Optional[str] = None
    amount: Optional[float] = None
    type: Optional[str] = None

class FamilyMemberSchema(BaseModel):
    name: str
    income: float
    job: str

class UpdateFamilyMemberSchema(BaseModel):
    name: Optional[str] = None
    income: Optional[float] = None
    job: Optional[str] = None

@app.get("/")
async def home(db: Session = Depends(get_db)):
    records = db.query(BudgetRecord).all()
    return {"message": "API учёта семейного хозяйства", "records": records}

@app.get("/get-record/{record_id}")
async def get_record(record_id: int, db: Session = Depends(get_db)):
    record = db.get(BudgetRecord, record_id)
    if not record:
        return {"Error": "Запись не найдена"}
    return record

@app.post("/create-record")
async def create_record(item: BudgetItemSchema, db: Session = Depends(get_db)):
    record = BudgetRecord(category=item.category, amount=item.amount, type=item.type)
    db.add(record)
    db.commit()
    db.refresh(record)
    return record

@app.put("/update-record/{record_id}")
async def update_record(record_id: int, item: UpdateBudgetItemSchema, db: Session = Depends(get_db)):
    record = db.get(BudgetRecord, record_id)
    if not record:
        return {"Error": "Запись не найдена"}
    if item.category is not None:
        record.category = item.category
    if item.amount is not None:
        record.amount = item.amount
    if item.type is not None:
        record.type = item.type
    db.commit()
    db.refresh(record)
    return record

@app.delete("/delete-record")
async def delete_record(record_id: int = Query(..., description="ID записи"), db: Session = Depends(get_db)):
    record = db.get(BudgetRecord, record_id)
    if not record:
        return {"Error": "Запись не найдена"}
    db.delete(record)
    db.commit()
    return {"Done": "Запись успешно удалена"}

@app.get("/get-member/{member_id}")
async def get_member(member_id: str, db: Session = Depends(get_db)):
    member = db.query(FamilyMemberDB).filter(FamilyMemberDB.member_id == member_id).first()
    if not member:
        return {"Error": "Член семьи не найден"}
    return member

@app.post("/create-member/{member_id}")
async def create_member(member_id: str, member: FamilyMemberSchema, db: Session = Depends(get_db)):
    existing = db.query(FamilyMemberDB).filter(FamilyMemberDB.member_id == member_id).first()
    if existing:
        return {"Error": "Такой член семьи уже существует"}
    new_member = FamilyMemberDB(member_id=member_id, name=member.name, income=member.income, job=member.job)
    db.add(new_member)
    db.commit()
    db.refresh(new_member)
    return new_member

@app.put("/update-member/{member_id}")
async def update_member(member_id: str, member: UpdateFamilyMemberSchema, db: Session = Depends(get_db)):
    existing = db.query(FamilyMemberDB).filter(FamilyMemberDB.member_id == member_id).first()
    if not existing:
        return {"Error": "Член семьи не найден"}
    if member.name is not None:
        existing.name = member.name
    if member.income is not None:
        existing.income = member.income
    if member.job is not None:
        existing.job = member.job
    db.commit()
    db.refresh(existing)
    return existing

@app.delete("/delete-member")
async def delete_member(member_id: str = Query(..., description="Роль члена семьи"), db: Session = Depends(get_db)):
    existing = db.query(FamilyMemberDB).filter(FamilyMemberDB.member_id == member_id).first()
    if not existing:
        return {"Error": "Член семьи не найден"}
    db.delete(existing)
    db.commit()
    return {"Done": "Член семьи успешно удалён"}

