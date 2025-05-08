from django.urls import path
from . import views
from django.contrib.auth import views as auth_views  # Import Django's auth views

urlpatterns = [
    path('', views.home, name='home'),
    path('recipe/<int:recipe_id>/', views.recipe_detail, name='recipe_detail'),
    path('search/', views.recipe_finder, name='search'),
    path('recommendations/', views.recommendations_view, name='recommendations'),
    path('register/', views.user_register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('profile/', views.user_profile, name='profile'),
    path('favorites/', views.favorites, name='favorites'),
    path('add_to_favorites/<int:recipe_id>/', views.add_to_favorites, name='add_to_favorites'),
    path('remove_from_favorites/<int:recipe_id>/', views.remove_from_favorites, name='remove_from_favorites'),
    path('profile/', views.user_profile, name='user_profile'),
    path('meal-planner/', views.meal_planner_view, name='meal_planner'),
    path('recipe/<int:recipe_id>/', views.recipe_detail, name='recipe_detail'),
    path('explore/', views.explore, name='explore'),
    path('upload/', views.upload_content, name='upload_content'),
    path('content/<int:content_id>/', views.content_detail, name='content_details'),
    path('content/<int:content_id>/edit/', views.edit_content, name='edit_content'),
    path('content/<int:content_id>/delete/', views.delete_content, name='delete_content'),
    path('my-uploads/', views.user_uploaded_content, name='user_uploaded_content'), 
    path('content/<int:content_id>/like/', views.like_content, name='like_content'),

]

