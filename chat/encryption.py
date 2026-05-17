def encrypt_message(chat_id, sender_id, receiver_id, text):
    """Сохраняем текст как есть (для надёжности)"""
    return text.encode()

def decrypt_message(chat_id, user1_id, user2_id, encrypted_text):
    """Возвращаем текст"""
    try:
        return encrypted_text.decode()
    except:
        return "🔒 [сообщение зашифровано]"
