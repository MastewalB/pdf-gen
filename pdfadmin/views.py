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
from pdfadmin.serializers import LoginSerializer, QuestionSerializer,QuestionIdListSerializer, QuestionSectionSerializer, ListQuestionSectionSerializer
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
                status=status.HTTP_200_OK,
                data = {
                    "token": token
                }
            )
        
        except ValueError:
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data = {
                    "message": "Invalid Login Credentials Provided"
                }
            )
        
        except Exception as e:
            return Response(
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                data = {
                    "message": str(e)
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
    
class QuestionDeleteView(APIView):
    permission_classes = [IsAdminUser]

    def delete(self, request):

        if 'id' not in request.data:
            return Response(
                {
                    "message": "id must be provided"
                },
                status=status.HTTP_400_BAD_REQUEST
                )
        id = request.data['id']
        section = Question.objects.filter(id = id)
        if section:
            section[0].delete()
            return Response(
                {
                    "message": "item deleted successfully"
                },
                status=status.HTTP_200_OK
                )
        else:
            return Response(
                {
                    "message": "No question found"
                },
                status=status.HTTP_404_NOT_FOUND
                )  
        
    
class AllQuestionsView(ListAPIView):

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
                section = QuestionSection.objects.get(id = id)
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

    def delete(self, request):
        serializer = QuestionIdListSerializer(data = request.data)
        serializer.is_valid(raise_exception=True)
        for id in serializer.validated_data['ids']:
            section = QuestionSection.objects.filter(id = id)
            if section:
                questionCount = Question.objects.filter(section = section[0])
                if len(questionCount) <= 0:
                    section[0].delete()
                else:
                    return Response(
                        {
                        "message": "The section has questions."
                        },
                        status=status.HTTP_400_BAD_REQUEST
                    )
        return Response(
                {
                    "message": "Section deleted successfully."
                        },
                status=status.HTTP_200_OK)        

class AllQuestionSectionView(ListAPIView):
    serializer_class = ListQuestionSectionSerializer
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
        sections = QuestionSection.objects.count()

        return Response(
            status=status.HTTP_200_OK,
            data = {
                "questions": questions,
                "payments": paidUsers,
                "users": users,
                "sections": sections
            }
        )


def toPgArray(array):
    for i in range(len(array)):
        array[i] = f"\'{array[i]}\'"
    return f"{','.join(array)}"