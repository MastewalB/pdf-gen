from rest_framework import fields, serializers
from pdfapp.models import UserResponse

class UserResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserResponse
        fields = ('name', 'email', 'response')
    
    def create(self, validated_data):
        user_response = UserResponse(
            name = validated_data['name'],
            email = validated_data['email'],
            response = validated_data['response']
        )
        user_response.save()
        return user_response
    