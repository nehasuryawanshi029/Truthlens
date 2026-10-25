import os
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

def create_demo_images():
    output_dir = Path(__file__).resolve().parent / "samples"
    output_dir.mkdir(parents=True, exist_ok=True)

    # 1. Mumbai Flooding 2019 (Waterlogging, brown floodwater, urban road)
    img_flood = Image.new("RGB", (800, 500), color="#4A5240")
    draw = ImageDraw.Draw(img_flood)
    draw.rectangle([0, 0, 800, 220], fill="#6B7882")
    draw.rectangle([60, 80, 220, 220], fill="#3D454C")
    draw.rectangle([250, 40, 420, 220], fill="#2E353B")
    draw.rectangle([450, 100, 600, 220], fill="#4A5258")
    draw.rectangle([640, 60, 750, 220], fill="#384046")
    draw.rectangle([0, 220, 800, 500], fill="#5C5138")
    draw.rectangle([300, 180, 520, 320], fill="#9E2A2B")
    draw.rectangle([320, 200, 500, 240], fill="#1C2526")
    for y in range(250, 480, 25):
        draw.line([(50, y), (750, y)], fill="#6E6247", width=3)
    draw.text((30, 450), "PRESS PHOTO ARCHIVE • CENTRAL MUMBAI MONSOON • JULY 2019", fill="#D4CDBC")
    flood_path = output_dir / "mumbai_flooding_2019.jpg"
    img_flood.save(str(flood_path), format="JPEG", quality=90)

    # 2. Synthetic Cyclone (Ultra-dramatic unnatural purple/cyan swirl)
    img_cyclone = Image.new("RGB", (800, 500), color="#1B102E")
    draw = ImageDraw.Draw(img_cyclone)
    draw.rectangle([0, 350, 800, 500], fill="#0A1C2A")
    for r in range(40, 320, 30):
        draw.arc([400 - r, 200 - r, 400 + r, 200 + r], start=0, end=270, fill="#7928CA", width=12)
        draw.arc([400 - r, 200 - r, 400 + r, 200 + r], start=90, end=360, fill="#0070F3", width=8)
    draw.ellipse([370, 170, 430, 230], fill="#E2E8F0")
    cyclone_path = output_dir / "synthetic_cyclone.jpg"
    img_cyclone.save(str(cyclone_path), format="JPEG", quality=90)

    # 3. Earthquake Relief Effort
    img_relief = Image.new("RGB", (800, 500), color="#8C9A9E")
    draw = ImageDraw.Draw(img_relief)
    draw.polygon([(0, 300), (250, 140), (500, 280), (800, 180), (800, 500), (0, 500)], fill="#5C5449")
    draw.polygon([(150, 360), (320, 220), (490, 360)], fill="#EAE6DF")
    draw.polygon([(320, 220), (490, 360), (620, 320), (450, 200)], fill="#D2CCC0")
    draw.rectangle([305, 270, 335, 310], fill="#B91C1C")
    draw.rectangle([290, 280, 350, 300], fill="#B91C1C")
    draw.rectangle([100, 400, 250, 460], fill="#785938")
    draw.rectangle([550, 390, 720, 450], fill="#785938")
    draw.text((30, 460), "UN OCHA / FIELD LOGISTICS • DISASTER RESPONSE AREA", fill="#FFFFFF")
    relief_path = output_dir / "turkey_earthquake_relief.jpg"
    img_relief.save(str(relief_path), format="JPEG", quality=90)

    # 4. Paris 2018 Protest
    img_protest = Image.new("RGB", (800, 500), color="#38434F")
    draw = ImageDraw.Draw(img_protest)
    draw.rectangle([0, 80, 200, 360], fill="#827B70")
    draw.rectangle([600, 80, 800, 360], fill="#827B70")
    draw.polygon([(200, 360), (600, 360), (750, 500), (50, 500)], fill="#292D32")
    draw.rectangle([350, 300, 410, 380], fill="#FBBF24")
    draw.ellipse([365, 260, 395, 295], fill="#1C1E21")
    draw.rectangle([450, 320, 490, 390], fill="#FBBF24")
    draw.ellipse([200, 150, 550, 300], fill="#64748B")
    draw.text((30, 460), "EDITORIAL ARCHIVE • CHAMPS-ÉLYSÉES • NOV 2018", fill="#E2E8F0")
    protest_path = output_dir / "paris_protest_2018.jpg"
    img_protest.save(str(protest_path), format="JPEG", quality=90)

    # 5. Local Fallen Tree
    img_tree = Image.new("RGB", (800, 500), color="#7A8874")
    draw = ImageDraw.Draw(img_tree)
    draw.rectangle([0, 260, 800, 500], fill="#3F4448")
    draw.rectangle([0, 380, 800, 420], fill="#9CA3AF")
    draw.line([(100, 300), (650, 410)], fill="#4A3525", width=28)
    draw.ellipse([500, 320, 720, 450], fill="#2D4A22")
    draw.text((30, 460), "MOBILE PHONE CAPTURE • RESIDENTIAL ROADWAY", fill="#D1D5DB")
    tree_path = output_dir / "local_fallen_tree.jpg"
    img_tree.save(str(tree_path), format="JPEG", quality=90)

    # 6. Sangli Ganapati Mandir (Historic black basalt stone temple with Krishna river ghāts)
    img_sangli = Image.new("RGB", (800, 500), color="#1C2024")
    draw = ImageDraw.Draw(img_sangli)
    # Sky
    draw.rectangle([0, 0, 800, 180], fill="#687884")
    # Krishna River Water in foreground
    draw.rectangle([0, 360, 800, 500], fill="#2A3D45")
    for y in range(370, 490, 18):
        draw.line([(30, y), (770, y)], fill="#3B525C", width=2)
    # Stone Ghat Steps descending into water
    for step, y in enumerate(range(280, 360, 16)):
        draw.rectangle([60 - step * 10, y, 740 + step * 10, y + 16], fill="#33383E", outline="#252A30")
    # Black Basalt Temple Sanctum & Spire (Hemadpanthi Maratha Architecture)
    draw.polygon([(340, 60), (400, 20), (460, 60), (480, 180), (320, 180)], fill="#23272B", outline="#171A1D") # Main Shikhara
    draw.rectangle([260, 180, 540, 280], fill="#2A2F35", outline="#1F2327") # Sabhamandapa
    # Carved Black Stone Pillars
    for p_x in [280, 330, 380, 430, 480, 520]:
        draw.rectangle([p_x, 200, p_x + 12, 280], fill="#1C1F22")
    # Ornate Stone Arches
    draw.arc([330, 195, 390, 230], start=180, end=360, fill="#3D444C", width=4)
    draw.arc([430, 195, 490, 230], start=180, end=360, fill="#3D444C", width=4)
    # Watermark / Tag
    draw.text((30, 460), "GANAPATI MANDIR • KRISHNA RIVER GHAT • SANGLI ARCHIVE", fill="#CBD5E1")
    sangli_path = output_dir / "sangli_ganapati_mandir.jpg"
    img_sangli.save(str(sangli_path), format="JPEG", quality=92)

    print("All demo images (including Sangli Ganapati Mandir) created successfully in", output_dir)

if __name__ == "__main__":
    create_demo_images()
