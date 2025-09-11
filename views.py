from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Message, User # Import your Message model
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from cryptography.fernet import Fernet

# User Registration View
def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}!')
            login(request, user)
            return redirect('inbox')  # Redirect to inbox after registration
        else:
            for error in form.errors.values():
                messages.error(request, error)
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

# User Login View
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'You are now logged in as {username}.')
                return redirect('inbox')  # Redirect to inbox after login
            else:
                messages.error(request, 'Invalid username or password.')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = AuthenticationForm()
    return render(request, 'registration/login.html', {'form': form})

# User Logout View
@login_required #Only allow logged in users
def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('login')  # Redirect to login page after logout

# Secure Messaging Views
@login_required
def inbox_view(request):
    user = request.user
    messages_list = Message.objects.filter(receiver=user).order_by('-timestamp')
    page = request.GET.get('page', 1)
    paginator = Paginator(messages_list, 10)  # Show 10 messages per page
    try:
        messages_page = paginator.page(page)
    except PageNotAnInteger:
        messages_page = paginator.page(1)
    except EmptyPage:
        messages_page = paginator.page(paginator.num_pages)
    return render(request, 'messaging/inbox.html', {'messages': messages_page,
     'paginator': paginator, 
     'page_obj': messages_page, })

@login_required
def outbox_view(request):
    user = request.user
    messages_list = Message.objects.filter(sender=user).order_by('-timestamp')
    page = request.GET.get('page', 1)
    paginator = Paginator(messages_list, 10)  # Show 10 messages per page
    try:
        messages_page = paginator.page(page)
    except PageNotAnInteger:
        messages_page = paginator.page(1)
    except EmptyPage:
        messages_page = paginator.page(paginator.num_pages)
    return render(request, 'messaging/outbox.html', {'messages': messages_page})

@login_required
def compose_message_view(request):
    if request.method == 'POST':
        receiver_username = request.POST.get('receiver')
        content = request.POST.get('content')
        try:
            receiver = User.objects.get(username__iexact=receiver_username)
            message = Message(sender=request.user, receiver=receiver, content=content)
            # ENCRYPT MESSAGE CONTENT HERE
            message.save()
            messages.success(request, 'Message sent successfully!')
            return redirect('outbox')
        except User.DoesNotExist:
            messages.error(request, 'Invalid receiver username.')
    return render(request, 'messaging/compose.html')

@login_required
def view_message_view(request, message_id):
    try:
        message = Message.objects.get(pk=message_id)
        if message.receiver == request.user or message.sender == request.user:
            # DECRYPT MESSAGE CONTENT HERE
            return render(request, 'messaging/view_message.html', {'message': message})
        else:
            messages.error(request, 'You do not have permission to view this message.')
            return redirect('inbox')
    except Message.DoesNotExist:
        messages.error(request, 'Message not found.')
        return redirect('inbox')