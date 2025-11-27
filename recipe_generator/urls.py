from django.urls import path
from . import views

urlpatterns = [
    path('chat/', views.chat_view, name='chat'),
    path('generate/', views.generate_recipe_api, name='generate_recipe_api'), # La API que ya creamos
]