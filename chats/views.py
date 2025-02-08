from django.http import StreamingHttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from .models import Chat
from users.models import Account
import json
import time

# Store active clients for SSE
clients = {}

@csrf_exempt
def send_message(request):
    """Handles sending messages between users"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            sender_id = data.get('sender')
            recipient_id = data.get('recipient')
            message_content = data.get('message')

            # Validate required fields
            if not sender_id or not recipient_id or not message_content:
                return JsonResponse({'error': 'Missing sender, recipient, or message'}, status=400)

            # Fetch sender and recipient from the database
            sender = get_object_or_404(Account, id=sender_id)
            recipient = get_object_or_404(Account, id=recipient_id)

            # Save the message to the database
            Chat.objects.create(sender=sender, recipient=recipient, message=message_content)

            # Notify recipient via SSE if connected
            if recipient.id in clients:
                for response in clients[recipient.id]:
                    try:
                        response.write(f"data: {json.dumps({'sender': sender.username, 'sender_id': sender.id, 'message': message_content})}\n\n")
                        response.flush()
                    except Exception as e:
                        print(f"SSE error: {e}")

            return JsonResponse({'status': 'Message sent'})

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON format'}, status=400)
        except Exception as e:
            return JsonResponse({'error': f'Unexpected error: {str(e)}'}, status=500)

    return JsonResponse({'error': 'Only POST requests are allowed'}, status=405)


def stream_messages(request, user_id):
    """Streams messages in real-time using SSE"""
    user = get_object_or_404(Account, id=user_id)

    def event_stream():
        try:
            # Fetch all chats involving the current user
            chats = Chat.objects.filter(Q(sender=user) | Q(recipient=user)).order_by('timestamp')

            # Stream existing messages
            for chat in chats:
                yield f"data: {json.dumps({'sender': chat.sender.username, 'sender_id': chat.sender.id, 'message': chat.message})}\n\n"

            # Add the current user to the clients dictionary
            if user.id not in clients:
                clients[user.id] = []
            clients[user.id].append(request)

            # Keep the connection open for new messages
            while True:
                time.sleep(1)
                if user.id not in clients:
                    break
                yield ''

        except Exception as e:
            yield f"data: {json.dumps({'error': f'Error: {str(e)}'})}\n\n"

    response = StreamingHttpResponse(event_stream(), content_type='text/event-stream')
    response['Cache-Control'] = 'no-cache'
    response['X-Accel-Buffering'] = 'no'
    return response


@login_required
def chat_view(request):
    """Loads the chat page with a search bar and chat history"""
    current_user = request.user

    # Get users with whom the current user has previous messages
    previous_chats = Chat.objects.filter(Q(sender=current_user) | Q(recipient=current_user))
    user_ids = set()
    for chat in previous_chats:
        user_ids.add(chat.sender.id)
        user_ids.add(chat.recipient.id)

    user_ids.discard(current_user.id)  # Remove the current user
    chat_users = Account.objects.filter(id__in=user_ids)

    return render(request, 'chats/chat.html', {
        'current_user': current_user,
        'chat_users': chat_users
    })


def search_users(request):
    """Search for users dynamically via AJAX"""
    if request.method == "GET":
        query = request.GET.get('q', '')
        users = Account.objects.filter(username__icontains=query)[:10]  # Limit to 10 results
        user_list = [{'id': user.id, 'username': user.username} for user in users]
        return JsonResponse({'users': user_list})
    return JsonResponse({'error': 'Invalid request'}, status=400)