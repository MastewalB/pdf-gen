from django.urls import path
from pdfadmin.views import LoginView, QuestionsView, AllQuestionsView, QuestionSectionView, AllQuestionSectionView

urlpatterns = [
    path('login/', LoginView.as_view()),
    path('questions/', QuestionsView.as_view()),
    path('questions/update/<str:id>', QuestionsView.as_view()),
    path('questions/list/', AllQuestionsView.as_view()),
    path('sections/', QuestionSectionView.as_view()),
    path('sections/list', AllQuestionSectionView.as_view())
]