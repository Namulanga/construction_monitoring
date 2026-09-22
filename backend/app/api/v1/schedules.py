from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.schedule_parser import parse_schedule_file

router = APIRouter()


@router.post("/upload")
async def upload_schedule(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.filename.lower().endswith((".xlsx", ".xls", ".csv")):
        raise HTTPException(400, "Ожидается .xlsx / .xls / .csv")
    content = await file.read()
    stats = parse_schedule_file(content, file.filename, db)
    return {"status": "ok", "parsed": stats}