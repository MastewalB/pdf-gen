from django.urls import path
from pdfapp.views import index, UserResponseView, PDFView

urlpatterns = [
    path('insert/', UserResponseView.as_view()),
    path('view/', PDFView.as_view())
]