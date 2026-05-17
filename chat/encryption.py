def encrypt_message(chat_id, sender_id, receiver_id, text):
    """Сохраняем текст без шифрования (для стабильной работы)"""
    return text.encode()

def decrypt_message(chat_id, user1_id, user2_id, encrypted_text):
    """Возвращаем текст как есть"""
    try:
        return encrypted_text.decode()
    except:
        return "🔒 [сообщение зашифровано]"
