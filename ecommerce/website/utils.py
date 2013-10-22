from django.contrib import messages

def remove_message(request, message_text):
    storage = messages.get_messages(request)
    for message in storage._queued_messages:
        if message.message == message_text:
            storage._queued_messages.remove(message)