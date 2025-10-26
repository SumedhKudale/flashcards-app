from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    path('decks/', views.deck_list_view, name='deck_list'),
    path('decks/create/', views.deck_create_view, name='deck_create'),
    path('decks/<int:deck_id>/', views.deck_detail_view, name='deck_detail'),
    path('decks/<int:deck_id>/edit/', views.deck_edit_view, name='deck_edit'),
    path('decks/<int:deck_id>/delete/', views.deck_delete_view, name='deck_delete'),
    
    path('decks/<int:deck_id>/cards/create/', views.card_create_view, name='card_create'),
    path('cards/<int:card_id>/edit/', views.card_edit_view, name='card_edit'),
    path('cards/<int:card_id>/delete/', views.card_delete_view, name='card_delete'),
    
    path('decks/<int:deck_id>/review/', views.review_view, name='review'),
    path('settings/', views.settings_view, name='settings'),
]
