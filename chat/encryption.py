from cryptography.fernet import Fernet
from django.conf import settings
import hashlib
import base64

def get_chat_key(chat_id, user1_id, user2_id):
    """Генерирует ключ шифрования на основе ID чата и участников"""
    # Сортируем ID чтобы ключ был одинаковым у обоих
    ids = sorted([user1_id, user2_id])
    raw = f"{chat_id}:{ids[0]}:{ids[1]}:{settings.SECRET_KEY}".encode()
    key = hashlib.sha256(raw).digest()
    return base64.urlsafe_b64encode(key)

def encrypt_message(chat_id, sender_id, receiver_id, text):
    """Шифрует сообщение"""
    key = get_chat_key(chat_id, sender_id, receiver_id)
    f = Fernet(key)
    return f.encrypt(text.encode())

def decrypt_message(chat_id, user1_id, user2_id, encrypted_text):
    """Расшифровывает сообщение"""
    key = get_chat_key(chat_id, user1_id, user2_id)
    f = Fernet(key)
    return f.decrypt(encrypted_text).decode()