from rest_framework import fields, serializers

class UserResponseSerializer(serializers.Serializer):

    name = serializers.CharField(max_length=200, required=True)
    email = serializers.EmailField(required=True)
    response = serializers.JSONField(required=True)

    