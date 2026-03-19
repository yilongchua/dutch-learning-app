from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
import os, sys
# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))
from sqlmodel import Session, select, func
from typing import List, Optional
import os
import uuid
from datetime import datetime
from fastapi.responses import FileResponse

from backend.app.dutch.core.database import get_session
from backend.app.dutch.schema.schemas import ExerciseContent, ExerciseContentReceive
from backend.app.dutch.service.llm_service import LocalLLMService
from backend.app.dutch.service.evaluator import EvaluatorService
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
    exercise = ExerciseContent(exercise_type=category, theme=theme)
    if category == "listening":
        exercise = await llm_service.generate_listening(exercise)
    else:
        exercise = await llm_service.generate_exercise(exercise)
    
    return exercise

@router.post("/evaluate/writing/improve")
@router.post("/evaluate/writing")
async def evaluate_writing(payload: ExerciseContentReceive, session: Session = Depends(get_session)):
    # Map frontend aliases
    data_dict = payload.dict()
    if payload.text and not payload.user_answer:
        data_dict["user_answer"] = payload.text
    if payload.prompt and not payload.question:
        data_dict["question"] = payload.prompt
    if payload.date and not payload.date_completed:
        data_dict["date_completed"] = payload.date
    
    # Remove aliases before creating SQLModel
    for k in ["text", "prompt", "date"]:
        data_dict.pop(k, None)
    
    exercise = ExerciseContent(**data_dict)

    # 1. Rule-based evaluation
    rule_results = evaluator_service.evaluate_writing(exercise.user_answer)
    
    # 2. LLM Evaluation
    result = await llm_service.evaluate(exercise)
    
    # 3. Combine/Augment
    if rule_results['rule_score'] < 100:
        result.feedback = f"{rule_results['rule_feedback']}\n\n{result.feedback}"
    
    # Save/Update exercise
    result.status = "completed"
    result.date_completed = datetime.now().strftime("%Y-%m-%d")
    session.add(result)
    session.commit()
    session.refresh(result)
    
    return result

@router.post("/evaluate/speaking")
async def evaluate_speaking(
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
    
    # Build exercise object for evaluation
    exercise = ExerciseContent(
        exercise_type="speaking",
        theme=theme,
        question=prompt,
        user_answer=transcription,
        status="completed",
        date_completed=date
    )
    
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
