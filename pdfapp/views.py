from django.http import HttpResponse
from django.shortcuts import render
from django.core.mail import send_mail, EmailMessage
from django.template.loader import render_to_string
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from pdfapp.serializers import UserResponseSerializer
from pdfapp.models import UserResponse
from .utils import PDFGenerator, changeResponseToPdfFormat

# Create your views here.
 
def index(request):
    return render(request, 'index.html')

class UserResponseView(APIView):

    def post(self, request):
        data = request.data

        serializer = UserResponseSerializer(data=data)
        if serializer.is_valid():
            
            obj, created = UserResponse.objects.update_or_create(
                email=serializer.data['email'],
                defaults=serializer.data
            )
            formattedResponse = changeResponseToPdfFormat(serializer.data)
            userEmail = formattedResponse['userInfo']['email']
            path = f"static/{userEmail}.pdf"
            PDFGenerator(path, formattedResponse)
            try:
                with open(path, 'rb') as pdf:
                    send_pdf_email(request, userEmail, pdf)
            except FileNotFoundError:
                return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR, data={ 'message': "Couldn't send email" })

            return Response(status=status.HTTP_200_OK, data={ 'message': 'success' })

        return Response(status=status.HTTP_400_BAD_REQUEST, data={ 'message': serializer.errors })
    

class PDFView(APIView):

    def get(self, request, email):

        path = f"static/{email}.pdf"
        try:
            with open(path, 'rb') as pdf:
                    
                response = HttpResponse(pdf.read(), content_type='application/pdf')
                response['Content-Disposition'] = f'inline;filename={path}.pdf'
                return response
        except FileNotFoundError:
            return Response(status=status.HTTP_404_NOT_FOUND, data={ 'message': "File not Found" })


def send_pdf_email(request, to_email, pdf):
    mail_subject = "Your Quiz Result"
    message = render_to_string('send_pdf.html', {
        'title': mail_subject,
    })
    email = EmailMessage(
        mail_subject, message, to=[to_email]
    )
    email.attach(pdf.name, pdf.read(), 'application/pdf')
    if email.send():
        return True
    return False