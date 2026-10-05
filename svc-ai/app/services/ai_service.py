from app.clients.llm_client import LLMClient
from app.clients.vision_client import VisionClient


class AIService:

    def __init__(self):
        self.llm_client = LLMClient()
        self.vision_client = VisionClient()

    def process_llm(self, prompt: str):

        try:

            response = self.llm_client.generate_response(prompt)

            return {
                "success": True,
                "type": "llm",
                "response": response
            }

        except Exception as e:

            return {
                "success": False,
                "type": "llm",
                "error": str(e)
            }

    def process_vision(self, image):

        try:

            return self.vision_client.analyze(image)

        except Exception as e:

            return {
                "success": False,
                "detections": [],
                "error": str(e)
            }