from django.http import HttpResponse
from django.shortcuts import render
from django.core.mail import send_mail, EmailMessage
from django.template.loader import render_to_string
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from pdfapp.serializers import UserResponseSerializer
from .utils import PDFGenerator, changeResponseToPdfFormat

# Create your views here.
 
def index(request):
    return render(request, 'index.html')

class UserResponseView(APIView):

    def post(self, request):
        data = request.data

        serializer = UserResponseSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            
            formattedResponse = changeResponseToPdfFormat(serializer.data)
            userEmail = formattedResponse['userInfo']['email']
            path = f"static/{userEmail}.pdf"
            PDFGenerator(path, formattedResponse)
            with open(path, 'rb') as pdf:
                send_pdf_email(request, userEmail, pdf)

            # with open(path, 'rb') as pdf:
            #     response = HttpResponse(pdf.read(), content_type='application/pdf')
            # response['Content-Disposition'] = f'inline;filename={path}.pdf'
            return Response(status=status.HTTP_200_OK, data={ 'message': 'success' })

        return Response(status=status.HTTP_400_BAD_REQUEST, data={ 'message': serializer.errors })
    

class PDFView(APIView):

    def get(self, request):
        data = request.data
        if 'email' not in data:
              return Response(status=status.HTTP_400_BAD_REQUEST, data={ 'message': 'No email provided' })

        path = f"static/{data['email']}.pdf"
        with open('pdfapp/sample.pdf', 'rb') as pdf:
            response = HttpResponse(pdf.read(), content_type='application/pdf')
            response['Content-Disposition'] = f'inline;filename={path}.pdf'
            return response

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