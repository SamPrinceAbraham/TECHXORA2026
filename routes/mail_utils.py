import os
import time
import smtplib
import ssl
import threading
import requests
import io
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

def _get_smtp_creds():
    """Read SMTP credentials from environment, stripping spaces from App Password."""
    return {
        'server':   os.getenv('SMTP_SERVER', 'smtp.gmail.com'),
        'user':     os.getenv('SMTP_USER', ''),
        'password': os.getenv('SMTP_PASS', '').replace(' ', ''),   # strip App Password spaces
        'sender':   os.getenv('SENDER_EMAIL', os.getenv('SMTP_USER', '')),
    }

def _build_message(sender, to_email, subject, body, pdf_paths=None):
    msg = MIMEMultipart()
    msg['From']    = f"TECHXORA '26 <{sender}>"
    msg['To']      = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))
    
    if pdf_paths:
        for path in pdf_paths:
            content = None
            filename = os.path.basename(path)
            
            if path.startswith('http'):
                try:
                    resp = requests.get(path)
                    if resp.status_code == 200:
                        content = resp.content
                        if '?' in filename:
                            filename = filename.split('?')[0]
                except Exception as e:
                    print(f"[MAIL] ✗ Failed to download attachment from {path}: {e}")
            elif os.path.exists(path):
                with open(path, 'rb') as f:
                    content = f.read()
            
            if content:
                part = MIMEApplication(content)
                part.add_header('Content-Disposition', 'attachment',
                                filename=filename)
                msg.attach(part)
    return msg

def _try_port_465(creds, msg, to_email, timeout=15):
    """Send via SSL on port 465. Returns True on success."""
    ctx = ssl.create_default_context()
    try:
        with smtplib.SMTP_SSL(creds['server'], 465, context=ctx, timeout=timeout) as s:
            s.login(creds['user'], creds['password'])
            s.send_message(msg)
        print(f"[MAIL] ✓ Sent to {to_email} via port 465 (SSL)")
        return True
    except smtplib.SMTPAuthenticationError as e:
        print(f"[MAIL] ✗ AUTH FAILED port 465: {e}")
        return False
    except Exception as e:
        print(f"[MAIL] ✗ Port 465 failed: {e}")
        return False

def _try_port_587(creds, msg, to_email, timeout=10):
    """Send via STARTTLS on port 587. Returns True on success."""
    try:
        with smtplib.SMTP(creds['server'], 587, timeout=timeout) as s:
            s.ehlo()
            s.starttls()
            s.ehlo()
            s.login(creds['user'], creds['password'])
            s.send_message(msg)
        print(f"[MAIL] ✓ Sent to {to_email} via port 587 (STARTTLS)")
        return True
    except Exception as e:
        print(f"[MAIL] ✗ Port 587 failed: {e}")
        return False

def _send_email(to_email, subject, body, pdf_paths=None, max_retries=2):
    creds = _get_smtp_creds()
    if not creds['user'] or not creds['password']:
        print("[MAIL] ✗ SMTP_USER or SMTP_PASS missing in .env")
        return False

    msg = _build_message(creds['sender'], to_email, subject, body, pdf_paths)

    for attempt in range(1, max_retries + 1):
        if _try_port_465(creds, msg, to_email): return True
        if _try_port_587(creds, msg, to_email): return True
        if attempt < max_retries: time.sleep(4 * attempt)
    return False

def _send_email_async(to_email, subject, body, pdf_paths=None, max_retries=2):
    t = threading.Thread(target=_send_email, args=(to_email, subject, body, pdf_paths), kwargs={'max_retries': max_retries}, daemon=False)
    t.start()
    return t

def test_smtp_connection():
    results = {}
    creds = _get_smtp_creds()
    try:
        ctx = ssl.create_default_context()
        with smtplib.SMTP_SSL(creds['server'], 465, context=ctx, timeout=8) as s:
            results['port_465'] = 'OK'
    except Exception as e: results['port_465'] = str(e)
    return results

def send_registration_received_email(team, participants, async_send=True):
    leader_email = participants[0].email if participants else None
    if not leader_email: return False
    subject = f"Registration Received – TECHXORA '26: {team.team_name}"
    body = f"Thank you for registering {team.team_name}.\n\nDomain: {team.domain}\nParticipants:\n"
    for p in participants: body += f" - {p.name}\n"
    body += "\nID cards will be sent once verified.\n\nBest regards,\nOrganizing Committee"
    if async_send: _send_email_async(leader_email, subject, body)
    else: _send_email(leader_email, subject, body)
    return True

send_registration_email = send_registration_received_email

def send_id_card_email(participant_email, participant_name, unique_id, pdf_url, password=None, team_name=None, domain=None, async_send=True):
    subject = f"Your ID Card & Registration Confirmed – TECHXORA '26"
    body = f"Dear {participant_name},\n\nYour registration for TECHXORA '26 is confirmed!\n\nID: {unique_id}\nPass: {password}\n\nPDF attached.\n\nBest regards,\nOrganizing Committee"
    pdfs = [pdf_url] if pdf_url else []
    if async_send: _send_email_async(participant_email, subject, body, pdf_paths=pdfs)
    else: _send_email(participant_email, subject, body, pdf_paths=pdfs)
    return True

def send_announcement_email(to_email, title, message, async_send=True):
    subject = f"Announcement: {title} – TECHXORA '26"
    if async_send: _send_email_async(to_email, subject, message)
    else: _send_email(to_email, subject, message)
    return True

def send_team_confirmation_email(team, participants, pdf_paths, async_send=True):
    for i, p in enumerate(participants):
        pdf = pdf_paths[i] if i < len(pdf_paths) else None
        send_id_card_email(p.email, p.name, p.unique_id, pdf, password=p.password, team_name=team.team_name, domain=team.domain, async_send=async_send)
    return True
