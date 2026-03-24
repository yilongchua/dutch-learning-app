from pydantic import BaseModel, Field
from typing import Optional, List

class NewThemeExtracted(BaseModel):
    theme : str = Field(default_factory=list, description="list of theme")

class AnswerExtracted(BaseModel):
    structured_dutch : str = Field(default="", description="structured dutch")

class TranslatedEnglishExtracted(BaseModel):
    translated_english : str = Field(default="", description="translated english")

class KeywordsExtracted(BaseModel):
    dutch: str = Field(default="", description="dutch word")
    english: str = Field(default="", description="translated english")
    

class NewExerciseExtracted(BaseModel):
    question: str = Field(default="", description="question")
    keywords: list[KeywordsExtracted] = Field(default_factory=list, description="list of keywords")

class NewListeningExtracted(BaseModel):
    text: str = Field( default="", description="A Dutch transcript (approximately 4-7 sentences).", min_length=50)
    question: str = Field( default="", description="A multiple-choice question about a specific detail in the transcript.")
    options: List[str] = Field( default_factory=list, description="A list of 4 plausible answer choices.", min_items=2, max_items=4)
    correct_answer: str = Field( default="", description="The correct answer (must exactly match one of the options).")
    english_translation: str = Field( default="", description="A faithful English translation of the Dutch transcript.")
    
    @classmethod
    def validate_correct_answer(cls, values):
        options = values.get("options", [])
        correct = values.get("correct_answer")
        if correct not in options:
            raise ValueError("correct_answer must be one of the options")
        return values

class EvaluatedExtracted(BaseModel):
    score: int = Field( default=0, description="Overall score (0‑100) reflecting fluency, correctness and keyword coverage.")
    score_breakdown: str = Field(default="", description=("A human‑readable dictionary string, e.g. ""\"{'fluency': 80, 'correctness': 70, 'keywordsoverage': 90}\"."))
    improved_text: str = Field(default="", description="Corrected B1‑level version of the student's answer.")
    feedback: str = Field(default="", description=("English feedback indicating weak areas (vocabulary, grammar, description, etc.)."))
    