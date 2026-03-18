import language_tool_python
import spacy
from typing import List, Dict
import os
from backend.config.config import settings

class EvaluatorService:
    def __init__(self):
        try:
            # nl_core_news_sm might need to be downloaded
            self.nlp = spacy.load('nl_core_news_sm')
        except Exception as e:
            print(f"Warning: Spacy model 'nl_core_news_sm' not found. Rule-based flow check will be limited. {e}")
            self.nlp = None
            
        try:
            self.tool = language_tool_python.LanguageTool('nl')
        except Exception as e:
            print(f"Warning: LanguageTool (nl) could not be initialized. Grammar checks will be limited. {e}")
            self.tool = None

    def evaluate_writing(self, text: str) -> Dict:
        feedback = []
        score = 100
        
        if self.tool:
            matches = self.tool.check(text)
            score = max(0, 100 - (len(matches) * 5))
            for match in matches:
                feedback.append(f"- {match.message}")
        
        # Word count check
        word_count = len(text.split())
        if word_count < 80:
            feedback.append("- The text is a bit short for B1. Try to aim for 80-120 words.")
            score -= 10
        elif word_count > 150:
            feedback.append("- The text is a bit long. Try to keep it concise (80-120 words).")
            
        return {
            "rule_score": float(max(0, score)),
            "rule_feedback": "\n".join(feedback) if feedback else "No basic grammatical errors found."
        }

    def evaluate_speaking(self, transcript: str, expected_keywords: List[str]) -> Dict:
        count = 0
        transcript_lower = transcript.lower()
        for word in expected_keywords:
            if word.lower() in transcript_lower:
                count += 1
        
        base_score = (count / len(expected_keywords)) * 100 if expected_keywords else 100
        
        feedback = []
        if self.nlp:
            doc = self.nlp(transcript)
            sentence_count = len(list(doc.sents))
            if sentence_count < 3:
                base_score *= 0.7
                feedback.append("- Try to speak in complete sentences to show your B1 flow.")
            else:
                feedback.append(f"- Good job! You mentioned {count} out of {len(expected_keywords)} key points.")
        else:
            feedback.append(f"- Mentioned {count}/{len(expected_keywords)} keywords.")

        return {
            "rule_score": float(base_score),
            "rule_feedback": "\n".join(feedback)
        }
