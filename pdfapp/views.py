from django.shortcuts import render
from rest_framework import status, serializers
from rest_framework.views import APIView
from rest_framework.response import Response
from pdfapp.serializers import UserResponseSerializer

# Create your views here.
 
def index(request):
    return render(request, 'index.html')

class UserResponseView(APIView):

    def post(self, request):
        data = request.data
        print(data)
        serializer = UserResponseSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            
            return Response(
                data={
                    'done'
                },
                status=status.HTTP_201_CREATED
            )
        print(serializer.errors)
        return Response(status=status.HTTP_400_BAD_REQUEST, data={'Invalid'})