import io
import os
import qrcode
from qrcode.image.pil import PilImage
from supabase_manager import upload_bytes

def generate_qr(unique_id: str, save_dir: str) -> str:
    """
    Generate a QR code PNG for the given unique_id.
    Uploads to Supabase Storage and returns the public URL.
    """
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    qr.add_data(unique_id)
    qr.make(fit=True)

    img = qr.make_image(fill_color="#00f5ff", back_color="#0d0d1a")
    
    # Save to bytes instead of file
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='PNG')
    img_byte_arr.seek(0)

    # Upload to Supabase Storage
    remote_path = f"{unique_id}.png"
    public_url = upload_bytes("qrcodes", img_byte_arr, remote_path, content_type="image/png")

    return public_url
