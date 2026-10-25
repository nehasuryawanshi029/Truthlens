import os
import hashlib
from pathlib import Path
from PIL import Image, ExifTags
import numpy as np

def extract_image_metadata(file_path: str) -> dict:
    """
    Stage A Deep Image & Metadata Forensics:
    Extracts format, dimensions, SHA-256 hash, EXIF metadata, GPS coordinates,
    and authenticity indicators.
    Clearly distinguishes routine missing metadata from evidence of manipulation.
    """
    path = Path(file_path)
    file_size = path.stat().st_size
    
    # Calculate SHA-256
    hasher = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(8192):
            hasher.update(chunk)
    sha256_hash = hasher.hexdigest()

    with Image.open(file_path) as img:
        width, height = img.size
        format_name = img.format or path.suffix.replace(".", "").upper()
        mode = img.mode

        # Perceptual hash calculation (difference hash dHash)
        p_hash = compute_dhash(img)

        # Color distribution summary
        color_summary = get_color_summary(img)

        # EXIF extraction
        exif_raw = img.getexif()
        exif_data = {}
        gps_data = {"has_gps": False}
        software_markers = []

        if exif_raw:
            for tag_id, value in exif_raw.items():
                tag_name = ExifTags.TAGS.get(tag_id, str(tag_id))
                
                # Filter out raw byte arrays or non-serializable objects
                if isinstance(value, (bytes, bytearray)):
                    continue
                
                if tag_name in ["Make", "Model", "Software", "DateTime", "DateTimeOriginal", "Artist", "Copyright", "LensModel", "UserComment", "ImageDescription"]:
                    exif_data[tag_name] = str(value).strip()
                    if tag_name == "Software":
                        software_markers.append(str(value).strip())

            # Check for GPS Info IFD
            try:
                gps_ifd = exif_raw.get_ifd(ExifTags.IFD.GPSInfo)
                if gps_ifd:
                    gps_parsed = parse_gps_info(gps_ifd)
                    if gps_parsed:
                        gps_data = gps_parsed
            except Exception:
                pass

        # Check for AI generation markers or editing markers in metadata/info
        authenticity_signals = analyze_authenticity_signals(img, exif_data, software_markers)

    return {
        "file_type": format_name,
        "file_size_bytes": file_size,
        "dimensions": f"{width}x{height}",
        "color_mode": mode,
        "sha256_hash": sha256_hash,
        "exif_data": exif_data,
        "gps_data": gps_data,
        "perceptual_hash": p_hash,
        "color_histogram_summary": color_summary,
        "authenticity_signals": authenticity_signals,
        "limitations": "Absence of EXIF metadata is standard across messaging and social platforms (WhatsApp, X, Instagram) and does not indicate image tampering."
    }

def compute_dhash(image: Image.Image, hash_size: int = 8) -> str:
    """Computes difference hash (dHash) for fast visual similarity comparison."""
    try:
        resized = image.convert("L").resize((hash_size + 1, hash_size), Image.Resampling.LANCZOS)
        pixels = list(resized.getdata())
        
        diff = []
        for row in range(hash_size):
            for col in range(hash_size):
                left = pixels[row * (hash_size + 1) + col]
                right = pixels[row * (hash_size + 1) + col + 1]
                diff.append(1 if left > right else 0)
        
        decimal_val = 0
        hex_str = []
        for index, value in enumerate(diff):
            if value:
                decimal_val += 2 ** (index % 4)
            if (index % 4) == 3:
                hex_str.append(hex(decimal_val)[2:])
                decimal_val = 0
        return "".join(hex_str)
    except Exception:
        return "0000000000000000"

def get_color_summary(image: Image.Image) -> str:
    """Generates dominant hue and tone distribution summary."""
    try:
        thumb = image.convert("RGB").resize((50, 50))
        arr = np.array(thumb)
        r_mean, g_mean, b_mean = np.mean(arr[:, :, 0]), np.mean(arr[:, :, 1]), np.mean(arr[:, :, 2])
        return f"Dominant RGB Balance: R:{int(r_mean)} G:{int(g_mean)} B:{int(b_mean)}"
    except Exception:
        return "Color profile unavailable"

def parse_gps_info(gps_ifd: dict) -> dict:
    """Parses GPS IFD into approximate coordinates with privacy notice."""
    try:
        def to_deg(values):
            d = float(values[0])
            m = float(values[1])
            s = float(values[2])
            return d + (m / 60.0) + (s / 3600.0)

        lat_ref = gps_ifd.get(1, 'N')
        lat_val = gps_ifd.get(2)
        lon_ref = gps_ifd.get(3, 'E')
        lon_val = gps_ifd.get(4)

        if lat_val and lon_val:
            lat = to_deg(lat_val)
            if lat_ref == 'S':
                lat = -lat
            lon = to_deg(lon_val)
            if lon_ref == 'W':
                lon = -lon

            return {
                "has_gps": True,
                "latitude": round(lat, 4),
                "longitude": round(lon, 4),
                "redacted_display": f"{round(lat, 2)}° {lat_ref}, {round(lon, 2)}° {lon_ref} (Approximate for privacy)",
                "note": "Extracted from embedded EXIF. May reflect file creation device rather than actual event location."
            }
    except Exception:
        pass
    return {"has_gps": False}

def analyze_authenticity_signals(image: Image.Image, exif_data: dict, software_markers: list) -> dict:
    """
    Evaluates image authenticity signals:
    - Distinguishes missing metadata from manipulation
    - Detects image editing software signatures (Photoshop, GIMP)
    - Detects generative AI synthesis indicators
    """
    signals = {
        "synthetic_indicator": "Low / Inconclusive",
        "has_editing_signatures": False,
        "editing_software_detected": None,
        "metadata_integrity": "Normal",
        "notes": []
    }

    # Check software tags
    for software in software_markers:
        lower_sw = software.lower()
        if any(tool in lower_sw for tool in ["photoshop", "gimp", "canva", "lightroom", "affinity"]):
            signals["has_editing_signatures"] = True
            signals["editing_software_detected"] = software
            signals["notes"].append(f"Image was saved or modified using {software}.")
        if any(ai_tool in lower_sw for ai_tool in ["midjourney", "stable diffusion", "dall-e", "comfyui", "flux", "novelai"]):
            signals["synthetic_indicator"] = "High (AI software metadata signature detected)"
            signals["notes"].append(f"Metadata directly references generative AI pipeline: {software}")

    # Check PNG chunks / JPEG info text
    for k, v in image.info.items():
        if isinstance(v, str):
            lower_v = v.lower()
            if any(term in lower_v for term in ["parameters", "steps:", "sampler:", "cfg scale:", "model:"]):
                signals["synthetic_indicator"] = "High (AI diffusion generation prompt parameters found in metadata)"
                signals["notes"].append("Embedded PNG chunk contains diffusion model generation parameters.")

    # Error Level Analysis (ELA) and Compression Integrity Heuristic
    try:
        ela_diff = compute_ela_variance(image)
        if ela_diff > 28.0:
            signals["has_editing_signatures"] = True
            signals["notes"].append(f"High compression error-level variance ({round(ela_diff, 1)}): indicates potential multi-stage editing or composited elements.")
        signals["ela_score"] = round(ela_diff, 2)
    except Exception:
        signals["ela_score"] = 0.0

    # Contextual note about missing EXIF
    if not exif_data:
        signals["metadata_integrity"] = "Stripped / Absent"
        signals["notes"].append("No camera EXIF metadata found. This is standard behavior across social messaging networks (WhatsApp, X, Instagram) and does not imply visual manipulation.")

    signals["limitations_notice"] = (
        "Forensic limitations: Absence of metadata does not establish falsity. "
        "Metadata timestamps reflect device clocks, which can be modified. "
        "AI detection heuristics are probabilistic indicators and must never be treated as definitive legal proof."
    )

    return signals

def compute_ela_variance(img: Image.Image) -> float:
    """Computes Error Level Analysis (ELA) compression discrepancy metric."""
    import io
    buffer = io.BytesIO()
    rgb = img.convert("RGB")
    rgb.save(buffer, "JPEG", quality=90)
    buffer.seek(0)
    resaved = Image.open(buffer)
    
    arr_orig = np.array(rgb, dtype=float)
    arr_resaved = np.array(resaved, dtype=float)
    diff = np.abs(arr_orig - arr_resaved)
    
    # Calculate variance across 16x16 grid blocks
    h, w, _ = diff.shape
    bh, bw = max(16, h // 8), max(16, w // 8)
    block_means = []
    for y in range(0, h - bh + 1, bh):
        for x in range(0, w - bw + 1, bw):
            block = diff[y:y+bh, x:x+bw]
            block_means.append(np.mean(block))
    
    if block_means:
        return float(np.std(block_means))
    return 0.0
