import os
import time
import random
import string
import hashlib
import hmac
import base64
import json

# Secret Key for JWT & Security primitives
SECRET_KEY = "INTELLIGENT_AI_SUPER_SECRET_SECURITY_KEY_2026"
CURRENT_OTP_CODE = None
OTP_EXPIRATION_TIME = 0

def generate_otp_code(expiration_seconds: int = 300) -> str:
    global CURRENT_OTP_CODE, OTP_EXPIRATION_TIME
    CURRENT_OTP_CODE = "".join(random.choices(string.digits, k=6))
    OTP_EXPIRATION_TIME = time.time() + expiration_seconds
    print(f"[REMOTE SECURITY] New 6-Digit Pairing OTP Generated: {CURRENT_OTP_CODE} (Valid for 5 mins)")
    return CURRENT_OTP_CODE

def verify_otp_code(candidate_code: str) -> bool:
    global CURRENT_OTP_CODE, OTP_EXPIRATION_TIME
    if not CURRENT_OTP_CODE:
        return False
    if time.time() > OTP_EXPIRATION_TIME:
        CURRENT_OTP_CODE = None
        return False
    if candidate_code.strip() == CURRENT_OTP_CODE:
        CURRENT_OTP_CODE = None # One time use
        return True
    return False

def generate_jwt_token(device_id: str, device_name: str, expiry_hours: int = 720) -> str:
    """Generates a secure signed JWT access token for mobile devices."""
    header = {"alg": "HS256", "typ": "JWT"}
    payload = {
        "sub": device_id,
        "name": device_name,
        "iat": int(time.time()),
        "exp": int(time.time() + (expiry_hours * 3600))
    }
    
    encoded_header = base64.urlsafe_b64encode(json.dumps(header).encode()).decode().rstrip("=")
    encoded_payload = base64.urlsafe_b64encode(json.dumps(payload).encode()).decode().rstrip("=")
    
    signature_base = f"{encoded_header}.{encoded_payload}".encode()
    signature = hmac.new(SECRET_KEY.encode(), signature_base, hashlib.sha256).digest()
    encoded_signature = base64.urlsafe_b64encode(signature).decode().rstrip("=")
    
    return f"{encoded_header}.{encoded_payload}.{encoded_signature}"

def verify_jwt_token(token: str) -> dict:
    """Verifies and decodes a JWT token. Returns payload dict or None."""
    try:
        parts = token.split(".")
        if len(parts) != 3:
            return None
        
        encoded_header, encoded_payload, signature = parts
        
        # Verify Signature
        signature_base = f"{encoded_header}.{encoded_payload}".encode()
        expected_sig = base64.urlsafe_b64encode(hmac.new(SECRET_KEY.encode(), signature_base, hashlib.sha256).digest()).decode().rstrip("=")
        
        if not hmac.compare_digest(signature, expected_sig):
            return None
            
        # Decode Payload
        padded_payload = encoded_payload + "=" * (-len(encoded_payload) % 4)
        payload = json.loads(base64.urlsafe_b64decode(padded_payload).decode())
        
        if payload.get("exp", 0) < time.time():
            return None # Expired
            
        return payload
    except Exception as e:
        print("[REMOTE SECURITY] JWT Validation Error:", e)
        return None

def generate_qr_pairing_payload(server_url: str) -> dict:
    """Generates a secure QR Code pairing payload containing server URL and current OTP."""
    otp = generate_otp_code()
    payload = {
        "app": "INTELLIGENT_AI_REMOTE",
        "url": server_url,
        "otp": otp,
        "ts": int(time.time())
    }
    return payload

def generate_qr_image_base64(server_url: str) -> str:
    """Generates base64 data URI of QR code image for UI display."""
    try:
        import qrcode
        import io
        
        payload = generate_qr_pairing_payload(server_url)
        payload_str = json.dumps(payload)
        
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=6,
            border=2,
        )
        qr.add_data(payload_str)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        
        buffered = io.BytesIO()
        img.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        return f"data:image/png;base64,{img_str}"
    except ImportError:
        # Fallback to simple Google Charts QR API or base64 stub if qrcode library isn't installed
        payload = generate_qr_pairing_payload(server_url)
        payload_str = json.dumps(payload)
        from urllib.parse import quote
        return f"https://api.qrserver.com/v1/create-qr-code/?size=250x250&data={quote(payload_str)}"

def ensure_ssl_certificates():
    cert_dir = "jarvis_data"
    if not os.path.exists(cert_dir):
        os.makedirs(cert_dir)
        
    cert_file = os.path.abspath(os.path.join(cert_dir, "cert.pem"))
    key_file = os.path.abspath(os.path.join(cert_dir, "key.pem"))
    
    if os.path.exists(cert_file) and os.path.exists(key_file):
        return cert_file, key_file

    try:
        from cryptography import x509
        from cryptography.x509.oid import NameOID
        from cryptography.hazmat.primitives import hashes, serialization
        from cryptography.hazmat.primitives.asymmetric import rsa
        import datetime

        key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        subject = issuer = x509.Name([
            x509.NameAttribute(NameOID.COMMON_NAME, "INTELLIGENT_AI_REMOTE"),
        ])
        cert = x509.CertificateBuilder().subject_name(
            subject
        ).issuer_name(
            issuer
        ).public_key(
            key.public_key()
        ).serial_number(
            x509.random_serial_number()
        ).not_valid_before(
            datetime.datetime.utcnow()
        ).not_valid_after(
            datetime.datetime.utcnow() + datetime.timedelta(days=365)
        ).sign(key, hashes.SHA256())

        with open(key_file, "wb") as f:
            f.write(key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.TraditionalOpenSSL,
                encryption_algorithm=serialization.NoEncryption()
            ))

        with open(cert_file, "wb") as f:
            f.write(cert.public_bytes(serialization.Encoding.PEM))

        print("[REMOTE SECURITY] SSL Certificate & Key generated successfully.")
        return cert_file, key_file
    except Exception as e:
        print("[REMOTE SECURITY] Could not generate SSL Certificate:", e)
        return None, None
