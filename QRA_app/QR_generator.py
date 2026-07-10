import os
import qrcode
import random
from django.conf import settings



def generate_qr_code(data, filename):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    
    qr.add_data(data)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    qr_folder = os.path.join(settings.BASE_DIR, "static", "qr_codes")
    
    os.makedirs(qr_folder, exist_ok=True)
    
    random_number = random.randint(1000, 9999)
    filename = f"{filename}_{random_number}.jpg"
    file_path = os.path.join(qr_folder, filename)
    
    img.save(file_path)