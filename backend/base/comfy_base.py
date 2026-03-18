import json, os, httpx, random
from typing import Any, Optional, Dict
from config.config import settings
from pathlib import Path

class ComfyUIService:
    def __init__(self):
        self.base_url = settings.COMFYUI_API_URL
        self.comfy_dir = Path(settings.COMFYUI_DIR)
        self.comfy_output_dir = self.comfy_dir / "output"
        self.workflow_folder = Path(__file__).parent / "workflow"

    def _load_workflow(self, json_file: str) -> Optional[dict]:
        """Loads the ComfyUI API JSON workflow."""
        if os.path.exists(self.workflow_folder + "/" + json_file):
            with open(json_file, "r") as f:
                workflow = json.load(f)
            return workflow
        else:
            print(f"Warning: Workflow not found at {json_file}")
            return None
    
    async def call_comfyApi(self, payload:dict) -> Optional[str]:
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(f"{self.base_url}/prompt", json=payload, timeout=30.0)
                response.raise_for_status()
                data = response.json()    
                return data.get("prompt_id", None) 
            except Exception as e:
                print(f"ComfyUI API Error: {e}")
                return None
    
    async def check_prompt_status(self, prompt_id: str) -> dict:
        """
        Checks ComfyUI /history/{prompt_id} to see if the generation is complete.
        """
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(f"{self.base_url}/history/{prompt_id}", timeout=10.0)
                response.raise_for_status()
                data = response.json()
                if prompt_id in data:
                    prompt_data = data[prompt_id]
                    outputs = prompt_data.get("outputs", {})
                    return outputs
                else:
                    return {"status":"pending", "message": "pending"}
            except Exception as e:
                print(f"Error checking ComfyUI status for {prompt_id}: {e}")
                return {"status": "error", "message": str(e)}


    @property
    def set_video_filename(workflow:dict, file_prefix:str) -> dict:
        workflow["50"]["inputs"]["filename_prefix"] = file_prefix
        return workflow
    @property
    def set_img_filename(workflow:dict, file_prefix:str) -> dict:
        workflow["60"]["inputs"]["filename_prefix"] = file_prefix
        return workflow
    @property
    def input_image_prompt(workflow:dict, image_prompt:str) -> dict:
        workflow['83:27']["inputs"]["text"] = image_prompt
        return workflow
    @property
    def set_positive_image_prompt(workflow:dict, image_prompt:str) -> dict:
        workflow['6']["inputs"]["text"] = image_prompt
        return workflow
    @property
    def set_negative_image_prompt(workflow:dict, image_prompt:str) -> dict:
        workflow['7']["inputs"]["text"] = image_prompt
        return workflow


    async def generate_image(self,image_prompt:str,  file_prefix: str) -> Optional[str]:
        workflow_path = "text2image.json"
        workflow = self._load_workflow(workflow_path)
        workflow = self.set_img_filename(workflow, file_prefix)
        workflow = self.input_image_prompt(workflow, image_prompt)
        result = await self.call_comfyApi(payload={"prompt": workflow})        
        return result
    async def generate_video(self, pos_image_prompt:str, neg_image_prompt:str,  file_prefix: str) -> Optional[str]:
        workflow_path = "text2image.json"
        workflow = self._load_workflow(workflow_path)
        workflow = self.set_video_filename(workflow, file_prefix)
        workflow = self.set_positive_image_prompt(workflow, pos_image_prompt)
        workflow = self.set_negative_image_prompt(workflow, neg_image_prompt)
        
        result = await self.call_comfyApi(payload={"prompt": workflow})        
        return result
                    