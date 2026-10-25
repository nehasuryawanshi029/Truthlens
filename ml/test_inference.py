import sys
import json
import torch
from PIL import Image
from transformers import AutoImageProcessor, AutoModelForImageClassification

MODEL_ID = "umm-maybe/AI-image-detector"

def test_inference():
    print(f"Loading processor & model for {MODEL_ID}...")
    processor = AutoImageProcessor.from_pretrained(MODEL_ID)
    model = AutoModelForImageClassification.from_pretrained(MODEL_ID)
    model.eval()

    print(f"Model ID2LABEL: {model.config.id2label}")
    print(f"Model LABEL2ID: {model.config.label2id}")

    test_images = [
        ("Real photo", "data/samples/mumbai_flooding_2019.jpg"),
        ("Synthetic art/cyclone", "data/samples/synthetic_cyclone.jpg"),
    ]

    for label_desc, img_path in test_images:
        image = Image.open(img_path).convert("RGB")
        inputs = processor(images=image, return_tensors="pt")
        with torch.no_grad():
            outputs = model(**inputs)
            logits = outputs.logits
            probs = torch.nn.functional.softmax(logits, dim=-1)[0]
        
        pred_idx = torch.argmax(probs).item()
        pred_label = model.config.id2label[pred_idx]
        conf = probs[pred_idx].item()
        
        print(f"\n--- {label_desc} ({img_path}) ---")
        print(f"Raw Probabilities: {[f'{model.config.id2label[i]}: {probs[i].item():.4f}' for i in range(len(probs))]}")
        print(f"Top prediction: {pred_label} (Confidence: {conf:.4f})")

if __name__ == "__main__":
    test_inference()
