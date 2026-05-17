from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from .models import Chat, Message
from .encryption import encrypt_message, decrypt_message
from users.models import User, ContactNickname
import json
from django.utils import timezone


@login_required
def messenger_view(request):
    """Главная страница мессенджера"""
    chats = Chat.objects.filter(participants=request.user).prefetch_related(
        'participants', 'messages'
    )

    users = User.objects.exclude(id=request.user.id)

    nicknames = ContactNickname.objects.filter(owner=request.user)
    nicknames_dict = {n.contact_id: n.nickname for n in nicknames}

    # Подготавливаем данные для каждого чата
    chats_data = []
    for chat in chats:
        other_user = chat.participants.exclude(id=request.user.id).first()
        last_msg = chat.messages.last()

        # Получаем отображаемое имя
        display_name = other_user.username
        if other_user and other_user.id in nicknames_dict:
            display_name = nicknames_dict[other_user.id]

        chats_data.append({
            'chat': chat,
            'other_user': other_user,
            'last_msg': last_msg,
            'display_name': display_name,
        })

    context = {
        'chats_data': chats_data,
        'users': users,
    }
    return render(request, 'messenger.html', context)


@login_required
def chat_detail(request, chat_id):
    """Получить сообщения чата (расшифрованные)"""
    chat = get_object_or_404(Chat, id=chat_id)

    if request.user not in chat.participants.all():
        return HttpResponseForbidden()

    other_user = chat.participants.exclude(id=request.user.id).first()
    messages = chat.messages.all().order_by('timestamp')

    messages_data = []
    for msg in messages:
        try:
            if msg.message_type == 'text' and msg.encrypted_text:
                text = decrypt_message(
                    chat.id,
                    msg.sender.id,
                    other_user.id,
                    msg.encrypted_text
                )
            else:
                text = ''
        except:
            text = '🔒 [не удалось расшифровать]'

        messages_data.append({
            'id': msg.id,
            'sender': msg.sender.username,
            'sender_id': msg.sender.id,
            'text': text,
            'type': msg.message_type,
            'file_url': msg.file.url if msg.file else None,
            'timestamp': msg.timestamp.strftime('%H:%M'),
        })

    return JsonResponse({'messages': messages_data})


@login_required
@csrf_exempt
def send_message(request, chat_id):
    """Отправить сообщение (с шифрованием)"""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=400)

    chat = get_object_or_404(Chat, id=chat_id)

    if request.user not in chat.participants.all():
        return HttpResponseForbidden()

    other_user = chat.participants.exclude(id=request.user.id).first()

    if request.FILES.get('file'):
        file = request.FILES['file']
        content_type = file.content_type

        if content_type.startswith('image/'):
            msg_type = 'image'
        elif content_type.startswith('video/'):
            msg_type = 'video'
        else:
            msg_type = 'file'

        message = Message.objects.create(
            chat=chat,
            sender=request.user,
            message_type=msg_type,
            file=file
        )
    else:
        data = json.loads(request.body)
        text = data.get('text', '')

        encrypted = encrypt_message(
            chat.id,
            request.user.id,
            other_user.id,
            text
        )

        message = Message.objects.create(
            chat=chat,
            sender=request.user,
            message_type='text',
            encrypted_text=encrypted
        )

    return JsonResponse({
        'status': 'ok',
        'message_id': message.id,
        'timestamp': message.timestamp.strftime('%H:%M')
    })


@login_required
def start_chat(request, user_id):
    """Создать или найти существующий чат с пользователем"""
    other_user = get_object_or_404(User, id=user_id)

    chat = Chat.objects.filter(
        participants=request.user
    ).filter(
        participants=other_user
    ).first()

    if not chat:
        chat = Chat.objects.create()
        chat.participants.add(request.user, other_user)

    return redirect('messenger')
