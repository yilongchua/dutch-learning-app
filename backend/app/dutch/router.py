from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
import os, sys
# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))
from sqlmodel import Session, select
from typing import List, Optional
import os
import uuid
from datetime import datetime
from datetime import timezone
from fastapi.responses import FileResponse
import asyncio

from backend.app.dutch.core.database import get_session
from backend.app.dutch.schema.schemas import ExerciseContent, ExerciseContentReceive
from backend.app.dutch.service.llm_service import LocalLLMService
from backend.app.dutch.service.evaluator import EvaluatorService
from backend.app.dutch.service.exercise_queue import exercise_queue_service
from backend.base.asr import ASRService
from backend.base.tts import TTSService
from backend.config.config import settings

router = APIRouter(tags=["dutch"])

# Services instances
llm_service = LocalLLMService()
evaluator_service = EvaluatorService()
asr_service = ASRService()
tts_service = TTSService()
@router.get("/")
async def dutch_root():
    return {"status": "online", "app": "dutch"}

@router.get("/health")
async def health_check():
    return {"status": "healthy", "app": "dutch"}

@router.get("/history")
async def get_history(limit: int = 20, session: Session = Depends(get_session)):
    query = (
        select(ExerciseContent)
        .where(ExerciseContent.status.in_(["served", "completed"]))
        .order_by(ExerciseContent.created_at.desc())
        .limit(limit)
    )
    results = session.exec(query).all()
    return results

import json
import random

@router.get("/generate-theme")
async def generate_theme():
    theme_path = os.path.join(os.path.dirname(__file__), "../../../data/app/dutch/theme.json")
    try:
        with open(theme_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            themes = data.get('theme', [])
            if themes:
                return {"theme": random.choice(themes)}
    except Exception as e:
        print(f"[!] Error loading themes in router: {e}")
    
    return {"theme": "Dagelijkse routine"}

@router.get("/exercise/{category}")
async def get_exercise(category: str, theme: str = "Dagelijkse routine"):
    if category not in ["writing", "listening", "speaking"]:
        raise HTTPException(status_code=400, detail="Unsupported exercise category")

    exercise = await exercise_queue_service.get_next_exercise(category=category, theme=theme)
    asyncio.create_task(exercise_queue_service.refill_if_needed())
    return exercise

@router.post("/evaluate/writing/improve")
@router.post("/evaluate/writing")
async def evaluate_writing(payload: ExerciseContentReceive, session: Session = Depends(get_session)):
    # 1. Fetch existing exercise if ID is provided, or create new one
    if payload.id:
        exercise = session.get(ExerciseContent, payload.id)
        if not exercise:
            # Fallback to new if id provided but not found
            exercise = ExerciseContent()
    else:
        exercise = ExerciseContent()

    # 2. Map frontend data to model fields
    # Use direct values or fallback to aliases (text/prompt/date)
    exercise.user_answer = payload.user_answer or payload.text or ""
    exercise.question = payload.question or payload.prompt or ""
    exercise.theme = payload.theme or exercise.theme
    exercise.exercise_type = payload.exercise_type or exercise.exercise_type or "writing"
    
    # 3. Handle status and dates
    exercise.status = "completed"
    exercise.updated_at = datetime.now(timezone.utc)
    if payload.date:
        exercise.date_completed = payload.date
    else:
        exercise.date_completed = datetime.now().strftime("%Y-%m-%d")

    # 4. Evaluation logic
    # Rule-based
    rule_results = evaluator_service.evaluate_writing(exercise.user_answer)
    
    # LLM-based (updates score, breakdown, feedback, etc. in place)
    exercise = await llm_service.evaluate(exercise)
    
    # Optional enhancement: merge rule feedback
    if rule_results['rule_score'] < 100:
        exercise.feedback = f"{rule_results['rule_feedback']}\n\n{exercise.feedback}"
    
    # 5. Save/Update in DB
    session.add(exercise)
    session.commit()
    session.refresh(exercise)
    
    return exercise

@router.post("/evaluate/speaking")
async def evaluate_speaking(
    exercise_id: Optional[int] = Form(None),
    theme: str = Form(...),
    date: str = Form(...),
    prompt: str = Form(...),
    keywords: str = Form(...),
    audio: UploadFile = File(...),
    session: Session = Depends(get_session)
):
    # Save audio temporarily
    audio_filename = f"speaking_{uuid.uuid4().hex}.wav"
    audio_path = os.path.join(settings.AUDIO_DIR, audio_filename)
    
    with open(audio_path, "wb") as buffer:
        buffer.write(await audio.read())
    
    # Transcribe
    transcription = asr_service.transcribe(audio_path)
    
    if exercise_id:
        exercise = session.get(ExerciseContent, exercise_id)
        if not exercise:
            exercise = ExerciseContent()
    else:
        exercise = ExerciseContent()

    exercise.exercise_type = "speaking"
    exercise.theme = theme
    exercise.question = prompt
    exercise.user_answer = transcription
    exercise.status = "completed"
    exercise.date_completed = date
    exercise.updated_at = datetime.now(timezone.utc)
    
    result = await llm_service.evaluate(exercise)
    
    session.add(result)
    session.commit()
    session.refresh(result)
    
    return {
        "transcription": transcription,
        "score": result.score,
        "feedback": result.feedback,
        "improved_text": result.improved_text,
        "score_breakdown": result.score_breakdown,
        "exercise_id": result.id
    }

@router.get("/tts")
async def get_tts(text: str):
    filename = f"tts_{uuid.uuid4().hex}.wav"
    output_path = os.path.join(settings.AUDIO_DIR, filename)
    
    result_path = tts_service.generate_audio(text, output_path)
    
    if not result_path or not os.path.exists(result_path):
        raise HTTPException(status_code=500, detail="Failed to generate audio")
        
    return FileResponse(result_path, media_type="audio/wav")
