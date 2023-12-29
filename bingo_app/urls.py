from django.urls import path
from . import views

urlpatterns = [
    path('suggest/', views.suggest_view, name='suggest'),
    path('thanks/', views.thanks_view, name='thanks'),
    path('upvote/<int:suggestion_id>/', views.upvote, name='upvote'),
    path('downvote/<int:suggestion_id>/', views.downvote, name='downvote'),
    path('', views.landing_page, name='start'),
    path('create_project/', views.create_project, name='create_project'),
    path('join_project/', views.join_project, name='join_project'),
    path('generate_bingo_card/', views.generate_bingo_card, name='generate_bingo_card'),
]