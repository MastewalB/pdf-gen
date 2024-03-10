from django.urls import path
from pdfapp.views import index, UserResponseView, PDFView, PaymentView

urlpatterns = [
    path('insert/', UserResponseView.as_view()),
    path('payment/', PaymentView.as_view()),
    path('view/<str:email>', PDFView.as_view())
]