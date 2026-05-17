import base64

def encrypt_message(chat_id, sender_id, receiver_id, text):
    """Простое кодирование base64 (для демонстрации)"""
    encoded = base64.b64encode(text.encode()).decode()
    return encoded.encode()

def decrypt_message(chat_id, user1_id, user2_id, encrypted_text):
    """Декодирование base64"""
    try:
        decoded = base64.b64decode(encrypted_text).decode()
        return decoded
    except:
        return "🔒 [сообщение зашифровано]"
