import base64
import hashlib
from cryptography.fernet import Fernet

# ЕДИНЫЙ КЛЮЧ ШИФРОВАНИЯ (задаём жёстко)
MASTER_KEY = 'TeleWebSecretKey2026!'

def get_chat_key(chat_id, user1_id, user2_id):
    ids = sorted([str(user1_id), str(user2_id)])
    raw = f"{chat_id}:{ids[0]}:{ids[1]}:{MASTER_KEY}"
    key = hashlib.sha256(raw.encode()).digest()
    return base64.urlsafe_b64encode(key)

def encrypt_message(chat_id, sender_id, receiver_id, text):
    key = get_chat_key(chat_id, sender_id, receiver_id)
    f = Fernet(key)
    return f.encrypt(text.encode())

def decrypt_message(chat_id, user1_id, user2_id, encrypted_text):
    try:
        key = get_chat_key(chat_id, user1_id, user2_id)
        f = Fernet(key)
        return f.decrypt(encrypted_text).decode()
    except:
        return "🔒 [не удалось расшифровать]"
