from rest_framework import serializers
from chat.models import Message, Thread, Message


class ThreadShortSerializer(serializers.ModelSerializer):
    """
    Serializer for the Thread model, providing a short version of the thread details.

    WARNING:
    - The 'id' field in the serialized output is NOT the actual primary key from the database,
      but rather the 'uuid' field of the Thread model. If your application relies on the 'id'
      field as a unique identifier, be aware that this is actually the 'uuid'.
    """
    id = serializers.UUIDField(source='uuid', read_only=True)

    class Meta:
        model = Thread
        fields = ('id', 'created_at')
        read_only_fields = ('id', 'created_at')


class ChatInputSerializer(serializers.Serializer):
    input = serializers.CharField(help_text='The input message content provided by the user.')
    context = serializers.JSONField(help_text='Context of the input message.')

class MessageSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    answer = serializers.CharField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Message
        fields = ('id', 'answer', 'created_at')