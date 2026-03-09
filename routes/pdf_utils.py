import os
import io
from reportlab.lib.pagesizes import A6
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from supabase_manager import upload_bytes
import requests

# ... (colors and constants remain the same)
DARK_BG  = colors.HexColor('#050810')
DARK_BG2 = colors.HexColor('#0a0f1e')
CYAN     = colors.HexColor('#00f5ff')
VIOLET   = colors.HexColor('#a78bfa')
AMBER    = colors.HexColor('#f59e0b')
WHITE    = colors.white
MUTED    = colors.HexColor('#475569')
DEEP_PUR = colors.HexColor('#1e1b4b')

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def _get_asset(rel_path):
    """Return absolute path to a static asset, or None if missing."""
    p = os.path.join(BASE_DIR, 'static', *rel_path.split('/'))
    return p if os.path.exists(p) else None

def generate_id_card(participant, output_path=None) -> str:
    """
    Generate a stylish PDF ID card for a participant and upload to Supabase.
    Returns the public URL of the PDF.
    """
    buf = io.BytesIO()
    W, H = A6  # 105 × 148 mm  ≈  297 × 420 pts
    c = canvas.Canvas(buf, pagesize=A6)

    # ── Full dark gradient background ─────────────────────────────────────────
    c.setFillColor(DARK_BG)
    c.rect(0, 0, W, H, fill=1, stroke=0)

    # ── Side neon accent strips ────────────────────────────────────────────────
    c.setFillColor(CYAN)
    c.rect(0, 0, 2.5*mm, H, fill=1, stroke=0)          # left strip
    c.setFillColor(VIOLET)
    c.rect(W - 2.5*mm, 0, 2.5*mm, H, fill=1, stroke=0) # right strip

    # ── Top header band ───────────────────────────────────────────────────────
    c.setFillColor(DEEP_PUR)
    c.rect(0, H - 24*mm, W, 24*mm, fill=1, stroke=0)

    # Cyan bottom edge on header
    c.setFillColor(CYAN)
    c.rect(0, H - 25*mm, W, 1.2*mm, fill=1, stroke=0)

    # ── Logos: college left, hackathon right — same size ─────────────────────
    # Standard static assets can still be local if bundled with Vercel
    clg_logo  = _get_asset('logos/act.png')
    hack_logo = _get_asset('logos/techXora.png')

    logo_size = 19*mm
    logo_pad  = 2*mm
    logo_y    = H - 23*mm

    if clg_logo:
        try:
            c.drawImage(ImageReader(clg_logo), logo_pad, logo_y,
                        width=logo_size, height=logo_size,
                        preserveAspectRatio=True, mask='auto')
        except Exception:
            pass

    if hack_logo:
        try:
            c.drawImage(ImageReader(hack_logo),
                        W - logo_pad - logo_size, logo_y,
                        width=logo_size, height=logo_size,
                        preserveAspectRatio=True, mask='auto')
        except Exception:
            pass

    # ── College + event text ──
    c.setFillColor(WHITE)
    c.setFont('Helvetica-Bold', 8.5)
    c.drawCentredString(W / 2, H - 5.5*mm, 'AGNI COLLEGE OF TECHNOLOGY')

    c.setFillColor(colors.HexColor('#c4b5fd'))
    c.setFont('Helvetica', 6)
    c.drawCentredString(W / 2, H - 11*mm, 'DEPARTMENT OF COMPUTER SCIENCE AND ENGINEERING')

    c.setFillColor(CYAN)
    c.setFont('Helvetica-Bold', 12)
    c.drawCentredString(W / 2, H - 19*mm, "TECHXORA '26")

    # ── Watermark ──
    if hack_logo:
        try:
            c.saveState()
            c.setFillAlpha(0.06)
            wm_size = 55*mm
            c.drawImage(ImageReader(hack_logo),
                        (W - wm_size) / 2, (H - wm_size) / 2,
                        width=wm_size, height=wm_size,
                        preserveAspectRatio=True, mask='auto')
            c.restoreState()
        except Exception:
            pass

    # ── Tag ──
    c.setFillColor(VIOLET)
    c.setFont('Helvetica-Bold', 6)
    c.drawCentredString(W / 2, H - 23*mm, '— PARTICIPANT —')

    # ── Name ──
    c.setFillColor(WHITE)
    c.setFont('Helvetica-Bold', 15)
    name_y = H - 31*mm
    name = participant.name.upper()
    if len(name) > 18:
        c.setFont('Helvetica-Bold', 11)
    c.drawCentredString(W / 2, name_y, name)

    c.setStrokeColor(CYAN)
    c.setLineWidth(0.8)
    c.line(10*mm, name_y - 2*mm, W - 10*mm, name_y - 2*mm)

    # ── QR Code from URL ──
    qr_size = 42*mm
    qr_x = (W - qr_size) / 2
    qr_y = name_y - 9*mm - qr_size

    if participant.qr_path:
        try:
            # QR is now a URL
            resp = requests.get(participant.qr_path, stream=True)
            if resp.status_code == 200:
                qr_img = ImageReader(io.BytesIO(resp.content))
                c.drawImage(qr_img, qr_x, qr_y, width=qr_size, height=qr_size,
                            preserveAspectRatio=True, mask='auto')
        except Exception as e:
            print(f"Error drawing QR in PDF: {e}")

    # QR border
    c.setStrokeColor(VIOLET)
    c.setLineWidth(0.4)
    c.rect(qr_x - 2*mm, qr_y - 2*mm, qr_size + 4*mm, qr_size + 4*mm, fill=0, stroke=1)
    c.setStrokeColor(CYAN)
    c.setLineWidth(1)
    c.rect(qr_x - 0.8*mm, qr_y - 0.8*mm, qr_size + 1.6*mm, qr_size + 1.6*mm, fill=0, stroke=1)

    # ── ID Pill ──
    id_y = qr_y - 9*mm
    pill_w = 60*mm
    pill_h = 7*mm
    pill_x = (W - pill_w) / 2
    c.setFillColor(colors.HexColor('#0d1126'))
    c.roundRect(pill_x, id_y - 1.5*mm, pill_w, pill_h, 3*mm, fill=1, stroke=0)
    c.setStrokeColor(CYAN)
    c.setLineWidth(0.6)
    c.roundRect(pill_x, id_y - 1.5*mm, pill_w, pill_h, 3*mm, fill=0, stroke=1)

    c.setFillColor(CYAN)
    c.setFont('Helvetica-Bold', 13)
    c.drawCentredString(W / 2, id_y + 1*mm, participant.unique_id)

    # ── Team Info ──
    info_y = id_y - 9*mm
    team_name = (participant.team_obj.team_name or "TEAM").upper()
    domain = (participant.team_obj.domain or "").upper()

    c.setFillColor(WHITE)
    c.setFont('Helvetica-Bold', 8)
    c.drawCentredString(W / 2, info_y, f"TEAM: {team_name}")

    c.setFillColor(VIOLET)
    c.setFont('Helvetica', 7)
    c.drawCentredString(W / 2, info_y - 5*mm, f"DOMAIN: {domain}")

    # ── Password ──
    pwd_y = info_y - 11*mm
    c.setFillColor(AMBER)
    c.setFont('Helvetica-Bold', 11)
    c.drawCentredString(W / 2, pwd_y, f"PASS: {participant.password or '----'}")

    c.save()
    buf.seek(0)
    
    # Upload to Supabase Storage
    remote_path = f"{participant.unique_id}.pdf"
    public_url = upload_bytes("id_cards", buf, remote_path, content_type="application/pdf")
    
    return public_url
