from django.http import StreamingHttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Chat
from users.models import Account
import json
import time

# Dictionary to hold SSE clients (stores response objects)
clients = {}

@csrf_exempt
def send_message(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            sender_id = data.get('sender')
            recipient_id = data.get('recipient')
            message_content = data.get('message')

            if not sender_id or not recipient_id or not message_content:
                return JsonResponse({'error': 'Missing sender, recipient, or message'}, status=400)

            sender = Account.objects.get(id=sender_id)
            recipient = Account.objects.get(id=recipient_id)

            # Save message to database
            new_chat = Chat(sender=sender, recipient=recipient, message=message_content)
            new_chat.save()

            # Notify recipient in real-time if they are connected
            if recipient.id in clients:
                response = clients[recipient.id]
                try:
                    response.write(f"data: {json.dumps({'sender': sender.username, 'message': message_content})}\n\n")
                    response.flush()  # Ensures message is sent immediately
                except Exception as e:
                    print(f"Error sending SSE message: {str(e)}")
                    del clients[recipient.id]  # Remove inactive client

            return JsonResponse({'status': 'Message sent'})

        except Account.DoesNotExist:
            return JsonResponse({'error': 'Sender or recipient does not exist'}, status=400)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON format'}, status=400)
        except Exception as e:
            return JsonResponse({'error': f'Unexpected error: {str(e)}'}, status=500)

    return JsonResponse({'error': 'Only POST requests are allowed'}, status=405)


# Stream messages using SSE
def stream_messages(request, user_id):
    def event_stream(user):
        try:
            existing_chats = Chat.objects.filter(recipient=user).order_by('timestamp')
            for chat in existing_chats:
                yield f"data: {json.dumps({'sender': chat.sender.username, 'message': chat.message})}\n\n"

            clients[user.id] = True  # Store active user connection

            while True:
                time.sleep(15)  # ✅ Send heartbeat every 15 seconds
                yield "data: {}\n\n"  # Keeps connection alive

        except Exception as e:
            yield f"data: {json.dumps({'error': f'Error: {str(e)}'})}\n\n"

    # Ensure user exists
    try:
        user = Account.objects.get(id=user_id)
    except Account.DoesNotExist:
        return JsonResponse({'error': 'User does not exist'}, status=404)

    return StreamingHttpResponse(event_stream(user), content_type='text/event-stream')


@login_required
def chat_view(request):
    current_user = request.user
    officer = Account.objects.filter(role="officer").first()
    recipient = officer if officer else None

    return render(request, 'chats/chat.html', {
        'current_user': current_user,
        'recipient': recipient
    })
