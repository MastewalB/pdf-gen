from django.urls import path
from pdfapp.views import index, UserResponseView

urlpatterns = [
    path('', index, name='index'),
    path('insert/', UserResponseView.as_view())
]