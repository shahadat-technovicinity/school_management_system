from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile
import os

def generate_card_image_service(student, template_id):
    """
    Takes a Student object and returns a file object ready to save.
    """
    # 1. Setup Canvas (Standard ID Card Size: 3.375 x 2.125 inches @ 300 DPI = 1012x638 px)
    width, height = 1012, 638
    img = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(img)

    # 2. Load Template Background (You need a base image in your static folder)
    # Assuming you have a 'base_template.png' in your app
    base_path = os.path.join(os.path.dirname(__file__), 'assets', 'card_base.png')
    if os.path.exists(base_path):
        base = Image.open(base_path)
        img.paste(base, (0,0))

    # 3. Draw Text (Coordinates depend on your design)
    font = ImageFont.truetype("arial.ttf", 24)
    
    # Name
    name = f"{student.first_name} {student.last_name or ''}"
    draw.text((100, 300), name, font=font, fill=(0, 0, 0))
    
    # ID / Admission No
    draw.text((100, 350), f"ID: {student.admission_number}", font=font, fill=(0, 0, 0))
    
    # Class/Section
    draw.text((100, 400), f"Class: {student.class_name} - {student.section}", font=font, fill=(0, 0, 0))

    # 4. Paste Student Photo
    if student.photo:
        # Open student photo from Django storage
        student_photo = Image.open(student.photo)
        # Resize to fit circle or square (e.g., 150x150)
        student_photo = student_photo.resize((150, 150))
        # Paste at specific coordinates
        img.paste(student_photo, (50, 100))

    # 5. Save to Memory
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    
    # Return as Django File object
    return InMemoryUploadedFile(
        buffer, 'ImageField', f"{student.admission_number}_id_card.png", 'image/png', buffer.getbuffer().nbytes, None
    )