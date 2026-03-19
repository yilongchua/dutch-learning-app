from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List

from backend.app.scheduler.service.scheduler_service import (
    scheduler_service,
    get_all_jobs,
    add_job,
    delete_job,
)

router = APIRouter()


class CronJobIn(BaseModel):
    task_type: str
    schedule_time: str   # e.g. "08:00 AM"
    input_number: int = 1


class CronJobOut(CronJobIn):
    id: str


@router.get("/", response_model=List[CronJobOut])
def list_jobs():
    return get_all_jobs()


@router.post("/", response_model=CronJobOut)
def create_job(job_in: CronJobIn):
    new_job = add_job(job_in.model_dump())
    scheduler_service.add_job_to_scheduler(new_job)
    return new_job


@router.delete("/{job_id}")
def remove_job(job_id: str):
    deleted = delete_job(job_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Job not found")
    scheduler_service.remove_job_from_scheduler(job_id)
    return {"status": "deleted"}
