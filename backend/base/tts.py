import subprocess, os, time, random
from typing import Optional

# Auto-accept Coqui TTS non-commercial license agreement
os.environ["COQUI_TOS_AGREED"] = "1"

# Non-heavy imports
import torch

class NativeSayService:
    def __init__(self, voice="Xander"):
        self.voice = voice
        print(f"NativeSayService: Initialized (Voice: {self.voice})")

    def generate(self, text: str, output_path: str) -> bool:
        cmd = [ "say", "-v", self.voice, "-o", output_path, "--data-format=LEI16@44100", text]
        print(f"NativeSayService: Running command: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True)
        return result.returncode == 0

class XTTSv2Service:
    def __init__(self):
        self.device = "mps"
        self.tts = None
        self._init_model()

    def _init_model(self):
        try:
            torch.serialization.add_safe_globals([XttsConfig, XttsAudioConfig,
                                                  BaseDatasetConfig, BaseAudioConfig, BaseTrainingConfig])
        except Exception as e:
            print(f"XTTSv2Service: Warning - could not register safe globals: {e}")

        self.tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(self.device)
        print("XTTSv2Service: Model loaded.")

    def generate(self, text: str, output_path: str) -> bool:
        try:
            print(f"XTTSv2Service: Generating audio for: {text[:30]}...")
            self.tts.tts_to_file(text=text, speaker_wav=None, language="nl", file_path=output_path)
            return os.path.exists(output_path)
        except Exception as e:
            print(f"XTTSv2Service: Error: {e}")
            return False

class TTSService:
    def __init__(self):
        self.say_service = NativeSayService()
        self.xtts_service = None # Lazy load XTTS because it's heavy
        print("TTSService: Initialized with lazy-loading for XTTS v2")

    def _get_xtts(self):
        if self.xtts_service is None:
            try:
                self.xtts_service = XTTSv2Service()
            except Exception as e:
                print(f"TTSService: Failed to initialize XTTSv2: {e}")
                return None
        return self.xtts_service

    def generate_audio(self, text: str, output_path: str) -> Optional[str]:
        try:
            # Ensure the output directory exists
            output_dir = os.path.dirname(output_path)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir, exist_ok=True)

            # Randomly choose between backends (50/50 chance)
            # Note: XTTS will be initialized on first selection
            use_xtts = random.random() < 0.5
            
            success = False
            service_name = "None"

            if use_xtts:
                xtts = self._get_xtts()
                if xtts:
                    service_name = "XTTSv2"
                    success = xtts.generate(text, output_path)
                else:
                    print("TTSService: Falling back to 'say' because XTTS failed to init")
                    service_name = "NativeSay (Fallback)"
                    success = self.say_service.generate(text, output_path)
            else:
                service_name = "NativeSay"
                success = self.say_service.generate(text, output_path)

            if success and os.path.exists(output_path):
                size = os.path.getsize(output_path)
                print(f"TTSService: [{service_name}] Successfully generated {output_path} ({size} bytes)")
                return output_path
            else:
                print(f"TTSService: [{service_name}] Generation failed.")
                return None
                
        except Exception as e:
            print(f"TTSService: Unexpected failure: {e}")
            import traceback
            traceback.print_exc()
            return None
