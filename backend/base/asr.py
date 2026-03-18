import os
import mlx_whisper

class ASRService:
    def __init__(self, model_id: str = "mlx-community/whisper-large-v3-turbo"):
        self.model_id = model_id
        # We don't need to preload the model here as mlx_whisper.transcribe handles it,
        # but we can store the ID. MLX models are usually cached by huggingface_hub.
    def transcribe(self, audio_path: str, language: str = "nl") -> str:
        if not os.path.exists(audio_path):
             return {"error": "Audio file not found"}

        print(f"Processing audio file with MLX Whisper: {audio_path}")
        try:
            result = mlx_whisper.transcribe(audio_path, path_or_hf_repo=self.model_id, 
                                            language=language, fp16=True)
            return result.get("text", "").strip()
        except Exception as e:
            print(f"Error during transcription: {e}")
            return ""

