from pathlib import Path
from PIL import Image

def strip_image_metadata(input_path: str, output_path: str) -> str:
    """
    Strips all EXIF, GPS, and header metadata from an image,
    saving a sanitized copy without altering the original.
    """
    in_file = Path(input_path)
    out_file = Path(output_path)
    out_file.parent.mkdir(parents=True, exist_ok=True)

    with Image.open(in_file) as img:
        # Create a new blank image with same mode & dimensions
        data = list(img.getdata())
        clean_img = Image.new(img.mode, img.size)
        clean_img.putdata(data)
        
        # Save without any info or exif dictionary
        fmt = img.format if img.format in ["JPEG", "PNG", "WEBP"] else "JPEG"
        clean_img.save(str(out_file), format=fmt, quality=95)

    return str(out_file)
