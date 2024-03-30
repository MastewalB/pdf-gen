from django.http import HttpResponse
from django.shortcuts import render
from django.core.mail import send_mail, EmailMessage
from django.template.loader import render_to_string
from django.conf import settings
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from pdfapp.serializers import UserResponseSerializer
from pdfapp.models import UserResponse
from .utils import PDFGenerator, changeResponseToPdfFormat
import stripe
import json
from pdfadmin.models import Question, QuestionSection

stripe.api_key = settings.STRIPE_SECRET_KEY
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

            return Response(status=status.HTTP_200_OK, data={ 'message': 'success' })

        return Response(status=status.HTTP_400_BAD_REQUEST, data={ 'message': serializer.errors })

class PaymentView(APIView):

    def post(self, request):
        
        data = request.data
        paymentMethodId = data['payment_method_id']
        email = data['email']
        try:
            userResponse = UserResponse.objects.get(email=email)
            
            stripe.PaymentIntent.create(
                payment_method=paymentMethodId,
                currency=settings.PAYMENT_CURRENCY,
                amount=settings.PAYMENT_AMOUNT,
                automatic_payment_methods={
                    'enabled': True,
                    'allow_redirects': 'never'
                },
                confirm=True
            )
            userResponse.paid = True
            userResponse.save()

            serializer = UserResponseSerializer(userResponse)
            formattedResponse = changeResponseToPdfFormat(serializer.data)
            userEmail = formattedResponse['userInfo']['email']
            path = f"static/{userEmail}.pdf"
            PDFGenerator(path, formattedResponse)
            try:
                with open(path, 'rb') as pdf:
                    send_pdf_email(request, userEmail, pdf)
            except FileNotFoundError:
                return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR, data={ 'message': "Couldn't send email" })
            return Response(status=status.HTTP_200_OK, data={"message": "Success"})

        except UserResponse.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND, data={"message": "No form response associated with that email. Please use the same email as you used to submit response."})
        except stripe.error.CardError as e:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={"message": "Error while processing payment. {}".format(e.user_message)})
        except stripe.error.InvalidRequestError as e:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={"message": "Error while processing payment. Invalid request.", "error": str(e)})
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={"message": "Error while processing payment. Please try again.", "error": str(e)})

class PDFView(APIView):


    def post(self, request, email):
        
        file = open('pdfapp/question_info.json')
        questions = json.load(file)
        createdQuestions = []
        
        for sectionTitle in questions:

            sectionObject, created = QuestionSection.objects.get_or_create(title=sectionTitle)
            section = questions[sectionTitle]

            for q in section:
                question = section[q]
                correctAnswer = question['correctAnswer']
                content = question['question']
                suggestionTitle = question['suggestion']['title'] or "Suggestion"
                suggestionDetail = question['suggestion']['details']

                suggestionText = f'<b>{suggestionTitle}</b>'
                for detail in suggestionDetail:
                    suggestionText += f'<br />{detail}'
                suggestionText += '<br />'
                
                qObj = Question.objects.create(
                    section = sectionObject,
                    content = content,
                    correctAnswer = correctAnswer,
                    suggestion = suggestionText
                )
                qObj.save()
                createdQuestions.append(q)

        return Response(
            status=status.HTTP_200_OK,
            data=createdQuestions
        )

    def get(self, request, email):
        userResponse = UserResponse.objects.get(email=email)
        serializer = UserResponseSerializer(userResponse)
        serializer.is_valid()
        formattedResponse = changeResponseToPdfFormat(serializer.data)
        userEmail = formattedResponse['userInfo']['email']
        path = f"static/{userEmail}.pdf"
        PDFGenerator(path, formattedResponse)
        try:
            with open(path, 'rb') as pdf:
                send_pdf_email(request, userEmail, pdf)
        except FileNotFoundError:
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR, data={ 'message': "Couldn't send email" })
        return Response(status=status.HTTP_200_OK, data={"message": "Success", "response": serializer.data})
        # path = f"static/{email}.pdf"
        # try:
        #     with open(path, 'rb') as pdf:
                    
        #         response = HttpResponse(pdf.read(), content_type='application/pdf')
        #         response['Content-Disposition'] = f'inline;filename={path}.pdf'
        #         return response
        # except FileNotFoundError:
        #     return Response(status=status.HTTP_404_NOT_FOUND, data={ 'message': "File not Found" })


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