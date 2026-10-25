from typing import Dict, Any, List
from app.services.image_analysis.vision_service import analyze_image_with_vision

def analyze_scene_clues(image_path: str, exif_data: Dict[str, Any] = None, user_claim: str = None) -> Dict[str, Any]:
    """
    Stage A Scene Forensics & Visual Inspection:
    Delegates to TruthLens General-Purpose Vision Understanding Pipeline.
    Supports hosted neural vision models (Gemini, OpenAI/Ollama) and local
    forensic spatial-frequency computer vision.
    Never assumes every image is a landmark or news event.
    Never presents predictions as verified facts.
    """
    return analyze_image_with_vision(image_path, exif_data=exif_data, user_claim=user_claim)
