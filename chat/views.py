from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from .models import Chat, Message
from users.models import User, ContactNickname
import json


@login_required
def messenger_view(request):
    chats = Chat.objects.filter(participants=request.user).prefetch_related(
        'participants', 'messages'
    )
    users = User.objects.exclude(id=request.user.id)
    nicknames = ContactNickname.objects.filter(owner=request.user)
    nicknames_dict = {n.contact_id: n.nickname for n in nicknames}

    chats_data = []
    for chat in chats:
        other_user = chat.participants.exclude(id=request.user.id).first()
        last_msg = chat.messages.last()
        display_name = other_user.username
        if other_user and other_user.id in nicknames_dict:
            display_name = nicknames_dict[other_user.id]
        chats_data.append({
            'chat': chat,
            'other_user': other_user,
            'last_msg': last_msg,
            'display_name': display_name,
        })

    return render(request, 'messenger.html', {
        'chats_data': chats_data,
        'users': users,
    })


@login_required
def chat_detail(request, chat_id):
    chat = get_object_or_404(Chat, id=chat_id)
    if request.user not in chat.participants.all():
        return HttpResponseForbidden()

    messages = chat.messages.all().order_by('timestamp')
    messages_data = []
    for msg in messages:
        messages_data.append({
            'id': msg.id,
            'sender': msg.sender.username,
            'sender_id': msg.sender.id,
            'text': msg.text_content or '',
            'type': msg.message_type,
            'file_url': msg.file.url if msg.file else None,
            'timestamp': msg.timestamp.strftime('%H:%M'),
        })
    return JsonResponse({'messages': messages_data})


@login_required
@csrf_exempt
def send_message(request, chat_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=400)

    chat = get_object_or_404(Chat, id=chat_id)
    if request.user not in chat.participants.all():
        return HttpResponseForbidden()

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
            chat=chat, sender=request.user,
            message_type=msg_type, file=file
        )
    else:
        data = json.loads(request.body)
        text = data.get('text', '')
        message = Message.objects.create(
            chat=chat, sender=request.user,
            message_type='text', text_content=text
        )

    return JsonResponse({
        'status': 'ok',
        'message_id': message.id,
        'timestamp': message.timestamp.strftime('%H:%M')
    })


@login_required
def start_chat(request, user_id):
    other_user = get_object_or_404(User, id=user_id)
    chat = Chat.objects.filter(participants=request.user).filter(participants=other_user).first()
    if not chat:
        chat = Chat.objects.create()
        chat.participants.add(request.user, other_user)
    return redirect('messenger')
