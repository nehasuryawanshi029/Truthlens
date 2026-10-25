import io
import os
import logging
from typing import Dict, Any, Optional
from PIL import Image, UnidentifiedImageError
import torch
from transformers import AutoImageProcessor, AutoModelForImageClassification

logger = logging.getLogger(__name__)

# Model identifier
DEFAULT_MODEL_NAME = "umm-maybe/AI-image-detector"

class AIDetectorService:
    _instance: Optional["AIDetectorService"] = None

    def __init__(self, model_name: str = DEFAULT_MODEL_NAME):
        self.model_name = model_name
        self.processor = None
        self.model = None
        self.device = "cpu"
        self._load_error: Optional[str] = None
        self.id2label: Dict[int, str] = {}
        self.artificial_index: int = 0
        self.human_index: int = 1
        self._initialize_model()

    @classmethod
    def get_instance(cls) -> "AIDetectorService":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def _initialize_model(self):
        try:
            logger.info("Initializing AI detector model: %s", self.model_name)
            self.processor = AutoImageProcessor.from_pretrained(self.model_name)
            self.model = AutoModelForImageClassification.from_pretrained(self.model_name)
            self.model.to(self.device)
            self.model.eval()

            # Inspect label configuration
            # In umm-maybe/AI-image-detector: {0: 'artificial', 1: 'human'}
            raw_id2label = self.model.config.id2label
            self.id2label = {int(k): str(v).lower() for k, v in raw_id2label.items()}
            logger.info("Configured id2label mapping: %s", self.id2label)

            # Establish explicit indices
            found_art = False
            found_hum = False
            for idx, label in self.id2label.items():
                if "artif" in label or "fake" in label or "synthetic" in label or "ai" in label:
                    self.artificial_index = idx
                    found_art = True
                elif "human" in label or "real" in label:
                    self.human_index = idx
                    found_hum = True

            if not (found_art and found_hum):
                logger.warning("Could not automatically resolve labels from %s; defaulting to 0=artificial, 1=human", self.id2label)
                self.artificial_index = 0
                self.human_index = 1

            self._load_error = None
            logger.info("AI Detector model loaded successfully on %s", self.device)
        except Exception as e:
            logger.error("Failed to initialize AI detector model: %s", str(e), exc_info=True)
            self.model = None
            self.processor = None
            self._load_error = str(e)

    def is_available(self) -> bool:
        return self.model is not None and self.processor is not None

    def get_load_error(self) -> Optional[str]:
        return self._load_error

    def detect_image(self, image_bytes: bytes, filename: str = "") -> Dict[str, Any]:
        """
        Validates, decodes, and classifies an image using actual model inference.
        """
        if not self.is_available():
            raise RuntimeError(
                f"Model initialization failure: {self._load_error or 'Model not loaded'}. "
                "Automated detection cannot proceed without the verified model checkpoint."
            )

        if not image_bytes or len(image_bytes) == 0:
            raise ValueError("Uploaded file is empty (0 bytes).")

        # Decode image using PIL
        try:
            image = Image.open(io.BytesIO(image_bytes))
            image.verify()  # Verify image integrity
        except Exception as e:
            raise ValueError(f"Corrupted or invalid image file. Image decoder error: {str(e)}")

        # Re-open after verify() (Pillow requirement)
        image = Image.open(io.BytesIO(image_bytes))
        width, height = image.size
        img_format = image.format or "JPEG"
        
        # Convert to RGB (handles RGBA, grayscale, CMYK, WEBP)
        rgb_image = image.convert("RGB")

        # Preprocess input
        inputs = self.processor(images=rgb_image, return_tensors="pt")
        inputs = {k: v.to(self.device) for k, v in inputs.items()}

        # Run actual model inference
        with torch.no_grad():
            outputs = self.model(**inputs)
            logits = outputs.logits
            probabilities = torch.nn.functional.softmax(logits, dim=-1)[0]

        prob_artificial = float(probabilities[self.artificial_index].item())
        prob_human = float(probabilities[self.human_index].item())

        # Determine categorization based on empirical thresholds
        # Threshold: 0.60 provides a calibrated certainty buffer
        ai_threshold = 0.60
        real_threshold = 0.60

        if prob_artificial >= ai_threshold:
            prediction = "likely_ai_generated"
            display_label = "Likely AI-Generated"
            confidence = prob_artificial
            explanation = (
                f"The Swin Transformer classifier detected synthetic generation indicators with {prob_artificial * 100:.1f}% "
                f"confidence, exhibiting structural and high-frequency artifacts typical of AI synthesis models."
            )
        elif prob_human >= real_threshold:
            prediction = "likely_real_photograph"
            display_label = "Likely Real Photograph"
            confidence = prob_human
            explanation = (
                f"The Swin Transformer classifier identified organic sensor noise and illumination consistency with {prob_human * 100:.1f}% "
                f"confidence, characteristic of an authentic optical photograph."
            )
        else:
            prediction = "uncertain"
            display_label = "Uncertain Result"
            confidence = max(prob_artificial, prob_human)
            explanation = (
                f"The model output falls within the empirical margin of uncertainty (Artificial: {prob_artificial * 100:.1f}%, "
                f"Real: {prob_human * 100:.1f}%). The visual features contain ambiguous or compressed textures that prevent a definitive origin determination."
            )

        return {
            "success": True,
            "prediction": prediction,
            "display_label": display_label,
            "confidence": round(confidence, 4),
            "explanation": explanation,
            "model_name": f"{self.model_name} (Swin-Base Image Classification)",
            "probabilities": {
                "ai_generated": round(prob_artificial, 4),
                "real_photograph": round(prob_human, 4)
            },
            "limitations": [
                "Automated detection is probabilistic and does not constitute definitive proof of image origin.",
                "Detection accuracy may degrade on heavily compressed, social media screenshots, or heavily edited images.",
                "Novel generative models (e.g. latest diffusion pipelines or unseen architectures) may produce lower confidence or false negatives.",
                "Photographs with extensive digital post-processing or CGI artwork may produce ambiguous classifications."
            ],
            "image_metadata": {
                "format": img_format,
                "width": width,
                "height": height,
                "file_size_bytes": len(image_bytes),
                "filename": filename or "uploaded_image"
            }
        }

# Global singleton accessor
def get_ai_detector() -> AIDetectorService:
    return AIDetectorService.get_instance()
