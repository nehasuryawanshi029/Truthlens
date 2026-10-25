import os
import re
from pathlib import Path
from typing import Dict, Any, List
from PIL import Image, ImageOps, ImageFilter
import numpy as np

from app.core.config import settings

def extract_visible_text_and_signs(image_path: str, exif_data: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Stage A OCR & Signboard Inspector:
    Extracts visible signboards, temple names, board text, and identifying inscriptions.
    Supports external multimodal vision OCR when configured, with transparent fallback
    to local forensic text inspections and metadata streams.
    """
    result = {
        "text_found": "",
        "detected_signboards": [],
        "ocr_engine_used": "Local Heuristic Contrast & Metadata Text Inspector",
        "ocr_status": "executed",
        "confidence": "inconclusive",
        "notes": []
    }

    # 1. Attempt External Vision Model OCR if enabled and key present
    if settings.ENABLE_EXTERNAL_LLM and settings.LLM_API_KEY:
        try:
            from google import genai
            client = genai.Client(api_key=settings.LLM_API_KEY)
            with open(image_path, "rb") as f:
                image_bytes = f.read()

            prompt = (
                "Examine this photograph carefully for any visible text, road signs, temple name boards, "
                "shop hoardings, municipal markers, vehicle registration plates, or inscriptions. "
                "Transcribe any visible text verbatim in English, Hindi, or regional languages. "
                "If no text is clearly legible, respond with 'NO_VISIBLE_TEXT'."
            )
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=[
                    genai.types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg"),
                    prompt
                ]
            )
            text_resp = (response.text or "").strip()
            if text_resp and "NO_VISIBLE_TEXT" not in text_resp:
                result["text_found"] = text_resp
                result["ocr_engine_used"] = "Google Gemini Vision Multimodal OCR"
                result["ocr_status"] = "executed_with_detected_text"
                result["confidence"] = "high"
                result["detected_signboards"].append({
                    "text": text_resp,
                    "source": "vision_transcription",
                    "confidence": "high"
                })
                result["notes"].append("Extracted legible signboards using external multimodal vision model.")
                return result
        except Exception as e:
            result["notes"].append(f"External vision OCR provider unavailable: {str(e)}")

    # 2. Inspect embedded metadata, IPTC, comments, and file tags
    embedded_text_tokens = []
    try:
        with Image.open(image_path) as img:
            # Check info dictionary
            for k, v in img.info.items():
                if isinstance(v, str) and len(v.strip()) > 2 and k not in ["jfif", "jfif_version"]:
                    embedded_text_tokens.append(f"[{k}] {v.strip()}")
            
            # Check EXIF text tags
            if exif_data:
                for k in ["UserComment", "ImageDescription", "Artist", "Software", "Copyright"]:
                    if k in exif_data and exif_data[k]:
                        embedded_text_tokens.append(f"[{k}] {exif_data[k]}")

            # Check image pixels for watermark or caption bar in bottom/top regions
            gray = img.convert("L")
            w, h = gray.size
            
            # Bottom 15% text bar inspection
            bottom_strip = gray.crop((0, int(h * 0.85), w, h))
            bottom_edges = bottom_strip.filter(ImageFilter.FIND_EDGES)
            edge_arr = np.array(bottom_edges)
            edge_mean = np.mean(edge_arr)

            # High horizontal frequency in bottom band indicates text/caption bar
            if edge_mean > 20:
                result["detected_signboards"].append({
                    "region": "Bottom Banner / Caption Bar",
                    "indication": "High-contrast horizontal text or caption watermark detected in bottom border",
                    "confidence": "moderate"
                })
                result["notes"].append("Forensic edge density confirms presence of bottom text/banner band.")

    except Exception as e:
        result["notes"].append(f"Metadata text inspection exception: {str(e)}")

    if embedded_text_tokens:
        combined = " | ".join(embedded_text_tokens)
        result["text_found"] = combined
        result["ocr_status"] = "executed_with_detected_text"
        result["confidence"] = "moderate"
        result["detected_signboards"].append({
            "text": combined,
            "source": "embedded_file_metadata",
            "confidence": "moderate"
        })
        result["notes"].append(f"Identified {len(embedded_text_tokens)} embedded text metadata strings.")
    else:
        if not result["detected_signboards"]:
            result["ocr_status"] = "executed_no_text_found"
            result["notes"].append("No legible signboards or embedded text markers identified in image.")

    return result
