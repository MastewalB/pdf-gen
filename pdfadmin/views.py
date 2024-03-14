from django.http import HttpResponse
from django.shortcuts import render
from django.template.loader import render_to_string
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework import serializers, status
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from pdfadmin.models import Question, QuestionSection
from pdfadmin.serializers import LoginSerializer, QuestionSerializer,QuestionIdListSerializer, QuestionSectionSerializer
from pdfadmin.backends import AdminAuthBackend
from pdfapp.models import UserResponse
from pdfapp.serializers import UserInformationSerializer

# Create your views here.

class LoginView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = LoginSerializer(data = request.data)
        serializer.is_valid(raise_exception=True)

        try:
            username = serializer.validated_data['username']
            password = serializer.validated_data['password']
            user = AdminAuthBackend.authenticate(username=username, password=password)
            token = AdminAuthBackend.encode_token(user)

            return Response(
                {
                    "token": token
                }
            )
        except serializers.ValidationError:
            return Response(
                {
                    "message": "Invalid Login Credentials"
                }
            )



class QuestionsView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request):
        serializer = QuestionSerializer(data = request.data)
        
        if serializer.is_valid():
            questionSection = get_object_or_404(QuestionSection, id = request.data['section'])
            serializer.context['section'] = questionSection
            serializer.save()

            return Response(
                status=status.HTTP_201_CREATED,
                data={
                    "question": serializer.data
                }
            )

        return Response(
            status=status.HTTP_400_BAD_REQUEST,
            data={
                'message': serializer.errors
            }
        )


    def put(self, request, id):
        serializer = QuestionSerializer(data = request.data)
        if serializer.is_valid():
            try:
                question = Question.objects.get(id = id)
                serializer.update(question, serializer.validated_data)

                return Response(
                    status=status.HTTP_200_OK,
                    data={
                        "question": QuestionSerializer(question).data
                    }
                )
        
            except Question.DoesNotExist:
                return Response(
                    {
                        "message": "No Such Question"
                    },
                    status=status.HTTP_404_NOT_FOUND
                )

        return Response(
            status=status.HTTP_400_BAD_REQUEST,
            data={
                'message': serializer.errors
            }
        )
    
    def delete(self, request):
        serializer = QuestionIdListSerializer(data = request.data)
        serializer.is_valid(raise_exception=True)
        for id in serializer.validated_data['ids']:
            question = Question.objects.filter(id = id)
            if question:
                question[0].delete()
        return Response(status=status.HTTP_200_OK)
        
    
class AllQuestionsView(ListAPIView):
    permission_classes = [IsAdminUser]

    serializer_class = QuestionSerializer
    pagination_class = PageNumberPagination

    def get_queryset(self):
        filters = self.request.data['filters'] if 'filters' in self.request.data else None
        if filters:
            field = filters['field']
            values = filters['values']
            result = Question.objects.raw(f'SELECT * FROM pdfadmin_question WHERE {field} IN ({toPgArray(values)})')
            return result
        queryset = Question.objects.all()
        return queryset

class QuestionSectionView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request):
        serializer = QuestionSectionSerializer(data = request.data)
        if serializer.is_valid():
            serializer.save()

            return Response(
                status=status.HTTP_201_CREATED,
                data={
                    "section": serializer.data
                }
            )

        return Response(
            status=status.HTTP_400_BAD_REQUEST,
            data={
                'message': serializer.errors
            }
        )
    
    def put(self, request, id):
        serializer = QuestionSectionSerializer(data=request.data)
        if serializer.is_valid():
            try:
                section = QuestionSection(id = id)
                serializer.update(section, serializer.validated_data)

                return Response(
                    status=status.HTTP_200_OK,
                    data={
                        "section": serializer.data
                    }
                )
        
            except QuestionSection.DoesNotExist:
                return Response(
                    {
                        "message": "No Such Section"
                    },
                    status=status.HTTP_404_NOT_FOUND
                )

        return Response(
            status=status.HTTP_400_BAD_REQUEST,
            data={
                'message': serializer.errors
            }
        )

class AllQuestionSectionView(ListAPIView):
    serializer_class = QuestionSectionSerializer
    pagination_class = PageNumberPagination

    def get_queryset(self):
        filters = self.request.data['filters'] if 'filters' in self.request.data else None
        if filters:
            field = filters['field']
            values = filters['values']
            result = QuestionSection.objects.raw(f'SELECT * FROM pdfadmin_questionsection WHERE {field} IN ({toPgArray(values)})')
            return result
        queryset = QuestionSection.objects.all()
        return queryset

class UserListView(ListAPIView):
    permission_classes = [IsAdminUser]
    
    serializer_class = UserInformationSerializer
    pagination_class = PageNumberPagination

    def get_queryset(self):
        return UserResponse.objects.all()

class AnalyticsView(APIView):
    permission_classes = [IsAdminUser]
    
    def get(self, request):

        users = UserResponse.objects.count()
        paidUsers = UserResponse.objects.filter(paid=True).count()
        questions = Question.objects.count()

        return Response(
            status=status.HTTP_200_OK,
            data = {
                "questions": questions,
                "payments": paidUsers,
                "users": users
            }
        )


def toPgArray(array):
    for i in range(len(array)):
        array[i] = f"\'{array[i]}\'"
    return f"{','.join(array)}"