from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import RegisterForm, AvatarForm
from .models import User, ContactNickname
from chat.models import Chat


def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('messenger')
    else:
        form = RegisterForm()
    return render(request, 'register.html', {'form': form})


def logout_view(request):
    """Выход из аккаунта"""
    logout(request)
    return redirect('login')


@login_required
def profile_view(request):
    if request.method == 'POST':
        form = AvatarForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = AvatarForm()

    # Получаем всех с кем есть чаты
    chats = Chat.objects.filter(participants=request.user)
    contacts = []
    for chat in chats:
        other = chat.participants.exclude(id=request.user.id).first()
        if other and other not in contacts:
            contacts.append(other)

    # Получаем никнеймы
    nicknames = ContactNickname.objects.filter(owner=request.user)

    context = {
        'form': form,
        'contacts': contacts,
        'nicknames': nicknames,
    }
    return render(request, 'profile.html', context)


@login_required
def set_nickname(request, user_id):
    """Установить никнейм для контакта"""
    contact = get_object_or_404(User, id=user_id)

    if request.method == 'POST':
        nickname = request.POST.get('nickname', '')

        if nickname:
            ContactNickname.objects.update_or_create(
                owner=request.user,
                contact=contact,
                defaults={'nickname': nickname}
            )
        else:
            # Если никнейм пустой — удаляем
            ContactNickname.objects.filter(
                owner=request.user,
                contact=contact
            ).delete()

    # Если запрос из AJAX — возвращаем JSON
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        from django.http import JsonResponse
        return JsonResponse({'status': 'ok'})

    return redirect('profile')