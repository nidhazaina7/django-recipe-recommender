from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.conf import settings
from .models import Recipe, UserFavorites, UserPreferences, RecipeRating, UserProfile
from .forms import UserRegistrationForm, UserForm, UserProfileForm, UserPreferencesForm, ProfilePictureForm
from .utils import get_similar_recipes
import pandas as pd
import os

# Home page
def home(request):
    return render(request, 'recipes/home.html')


import random
def recipe_finder(request):
    query = request.GET.get('q', '')  # Search query
    recipes = []
    suggestions = []

    # Fetch recipes based on the search query
    if query:
        recipes = Recipe.objects.filter(title__icontains=query)

    # Check if the user is authenticated before fetching favorites
    if request.user.is_authenticated:
        # Fetch the user's favorite recipes
        user_favorites = UserFavorites.objects.filter(user=request.user)
        if user_favorites.exists():
            favorite_recipe_ids = [fav.recipe.id for fav in user_favorites]

            # Get all recipes excluding user's favorite recipes
            other_recipes = Recipe.objects.exclude(id__in=favorite_recipe_ids)

            # Convert to list and shuffle for randomness
            other_recipes_list = list(other_recipes)
            random.shuffle(other_recipes_list)

            # Pick up to 5 random recipes
            suggestions = other_recipes_list[:5]
    else:
        # Handle case for anonymous users (optional)
        suggestions = []  # You can provide some default suggestions or leave it empty

    # Pass the context to the template
    context = {
        'query': query,
        'recipes': recipes,
        'suggestions': suggestions,
    }
    return render(request, 'recipes/search_results.html', context)

# Recipe Detail
from django.db.models import Avg

@login_required
def recipe_detail(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)

    ingredients_list = []
    if recipe.ingredients:
        for line in recipe.ingredients.split('\n'):
            line = line.strip()
            if line:  # Skip empty lines
                ingredients_list.append(line)
    
    # Pre-process instructions into a list
    instructions_list = []
    if recipe.instructions:
        for line in recipe.instructions.split('\n'):
            line = line.strip()
            if line:  # Skip empty lines
                instructions_list.append(line)

    if request.method == 'POST':
        rating_value = int(request.POST.get('rating'))
        
        # Create or update the user's rating for the recipe
        RecipeRating.objects.update_or_create(
            user=request.user,
            recipe=recipe,
            defaults={'rating': rating_value}
        )

        # Redirect to the same page to display the updated rating
        return redirect('recipe_detail', recipe_id=recipe.id)

    # Calculate average rating for the recipe
    avg_rating = recipe.ratings.aggregate(avg=Avg('rating'))['avg'] or 0

    # Get the user's rating if available
    user_rating = None
    if request.user.is_authenticated:
        user_rating_obj = RecipeRating.objects.filter(user=request.user, recipe=recipe).first()
        if user_rating_obj:
            user_rating = user_rating_obj.rating

    return render(request, 'recipes/recipes_details.html', {
        'recipe': recipe,
        'avg_rating': round(avg_rating, 1),
        'user_rating': user_rating,
        'ingredients_list': ingredients_list,
        'instructions_list': instructions_list,
    })


# User Register
def user_register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            login(request, user)
            return redirect('home')
    else:
        form = UserRegistrationForm()
    return render(request, 'users/register.html', {'form': form})

# User Login
def user_login(request):
    form = AuthenticationForm(data=request.POST or None)
    if request.method == 'POST' and form.is_valid():
        login(request, form.get_user())
        return redirect('home')
    return render(request, 'users/login.html', {'form': form})

# User Logout
def user_logout(request):
    logout(request)
    return redirect('home')

# Favorites Management
@login_required
def add_to_favorites(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)
    UserFavorites.objects.get_or_create(user=request.user, recipe=recipe)
    return redirect('favorites')

@login_required
def remove_from_favorites(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)
    UserFavorites.objects.filter(user=request.user, recipe=recipe).delete()
    return redirect('home')

@login_required
def favorites(request):
    favorite_recipes = request.user.favorite_recipes.all()
    return render(request, 'recipes/favorites.html', {'favorite_recipes': favorite_recipes})


# User Profile and Preferences
@login_required
def user_profile(request):
    # Get or create user preferences and profile
    preferences, _ = UserPreferences.objects.get_or_create(user=request.user)
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    
    favorite_recipes = Recipe.objects.filter(
        id__in=UserFavorites.objects.filter(user=request.user).values_list('recipe', flat=True)
    )

    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=request.user)
        preferences_form = UserPreferencesForm(request.POST, instance=preferences)
        picture_form = ProfilePictureForm(request.POST, request.FILES, instance=profile)

        if 'update_info' in request.POST:
            if user_form.is_valid() and preferences_form.is_valid():
                user_form.save()
                preferences_form.save()
                return redirect('profile')

        elif 'update_picture' in request.POST:
            if picture_form.is_valid():
                picture_form.save()
                return redirect('profile')
    else:
        user_form = UserForm(instance=request.user)
        preferences_form = UserPreferencesForm(instance=preferences)
        picture_form = ProfilePictureForm(instance=profile)

    return render(request, 'users/profile.html', {
        'user_form': user_form,
        'preferences_form': preferences_form,
        'preferences': preferences,
        'favorite_recipes': favorite_recipes,
        'picture_form': picture_form,
    })



# Meal Planner Utility
DIET_FILES = {
    'paleo': 'paleo.csv',
    'keto': 'keto.csv',
    'vegan': 'vegan.csv',
    'mediterranean': 'mediterranean.csv',
    'dash': 'dash.csv',
}

def load_diet_data(diet):
    file_path = os.path.join(settings.BASE_DIR, 'recipes', 'templates', 'data', DIET_FILES.get(diet, ''))
    if os.path.exists(file_path):
        return pd.read_csv(file_path)
    else:
        return pd.DataFrame()


def build_meal_plan(df, days, include_nutrition=True):
    meals_per_day = 3
    selected = df.sample(n=days * meals_per_day, replace=True).reset_index(drop=True)
    plan = []

    for day in range(days):
        meals = selected.iloc[day*3:(day+1)*3]
        for _, meal in meals.iterrows():
            ing_list = meal.get('Ingredients', '')
            meal['Ingredients'] = [i.strip() for i in ing_list.split(',')] if ing_list else []

        summary = {
            'protein': round(meals.get('Protein(g)', pd.Series()).sum(), 2) if include_nutrition else 'N/A',
            'carbs': round(meals.get('Carbs(g)', pd.Series()).sum(), 2) if include_nutrition else 'N/A',
            'fat': round(meals.get('Fat(g)', pd.Series()).sum(), 2) if include_nutrition else 'N/A',
        }

        plan.append({'day': day + 1, 'meals': meals.to_dict(orient='records'), 'summary': summary})

    return plan

# Meal Planner View
@login_required
def meal_planner_view(request):
    if request.method == 'POST':
        diet = request.POST.get('diet_type', '').lower()
        days = int(request.POST.get('days', 1))
        include_nutrition = request.POST.get('include_nutrition') == 'on'

        df = load_diet_data(diet)

        if df.empty:
            return render(request, 'recipes/meal_planner.html', {
                'error': 'No data found for the selected diet type.',
            })

        meal_plan = build_meal_plan(df, days, include_nutrition)

        if not meal_plan:
            return render(request, 'recipes/meal_planner.html', {
                'error': 'No meal plan could be generated with the provided data.',
            })

        return render(request, 'recipes/meal_plan_result.html', {
            'meal_plan': meal_plan,
            'diet': diet,
            'days': days,
            'include_nutrition': include_nutrition,
        })

    return render(request, 'recipes/meal_planner.html')


from django.db.models import Q
from .forms import MoodForm
from .utils import MOOD_TO_RECIPE_TAGS
from .models import Recipe
from .utils import get_similar_recipes

def recommendations_view(request):
    mood_form = MoodForm()
    mood_recipes = None
    ai_recipes = None
    ingredient_query = None

    # Handle mood-based recipe recommendations
    if request.method == "POST" and 'mood' in request.POST:
        mood_form = MoodForm(request.POST)
        if mood_form.is_valid():
            mood = mood_form.cleaned_data["mood"]
            keywords = MOOD_TO_RECIPE_TAGS.get(mood, [])
            if keywords:
                query = Q()
                for keyword in keywords:
                    query |= Q(title__icontains=keyword)
                mood_recipes = Recipe.objects.filter(query)

    # Handle ingredient-based recipe recommendations
    if request.method == "GET":
        ingredient_query = request.GET.get('ingredients', '')
        if ingredient_query:
            ingredients = [ing.strip().lower() for ing in ingredient_query.split(',') if ing.strip()]
            recipes = Recipe.objects.all()
            for ingredient in ingredients:
                recipes = recipes.filter(ingredients__icontains=ingredient)
            ai_recipes = recipes

    # Debugging output to check if recipes are being fetched
    print("Mood Recipes:", mood_recipes)
    print("AI Recipes:", ai_recipes)

    return render(request, 'recipes/recommendations.html', {
        'mood_form': mood_form,
        'mood_recipes': mood_recipes,
        'ai_recipes': ai_recipes,
        'ingredient_query': ingredient_query
    })



from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import UploadedContent, Comment
from .forms import UploadContentForm, CommentForm
from django.urls import reverse

# Read: View all uploaded content (Explore)
def explore(request):
    contents = UploadedContent.objects.all().order_by('-uploaded_at')
    return render(request, 'recipes/explore.html', {'contents': contents, 'user': request.user})

@login_required
def content_detail(request, content_id):
    content = get_object_or_404(UploadedContent, id=content_id)
    comments = content.comments.all().order_by('-created_at')

    # Edit: Update existing comment
    if 'edit_comment' in request.GET:
        comment_id = request.GET['edit_comment']
        comment = get_object_or_404(Comment, id=comment_id)
        if comment.user == request.user:
            if request.method == 'POST':
                form = CommentForm(request.POST, instance=comment)
                if form.is_valid():
                    form.save()
                    return redirect('content_details', content_id=content_id)
            else:
                form = CommentForm(instance=comment)

            return render(request, 'recipes/content_details.html', {
                'content': content,
                'comments': comments,
                'form': form,
                'editing_comment': comment.id,  # Pass the comment ID being edited
            })

    # Delete: Delete a comment
    if 'delete_comment' in request.GET:
        comment_id = request.GET['delete_comment']
        comment = get_object_or_404(Comment, id=comment_id)
        if comment.user == request.user:
            comment.delete()
        return redirect('content_details', content_id=content_id)

    # Create: Add new comment
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.user = request.user
            comment.content = content
            comment.save()
            return redirect('content_details', content_id=content_id)
    else:
        form = CommentForm()

    return render(request, 'recipes/content_details.html', {
        'content': content,
        'comments': comments,
        'form': form,
        'editing_comment': None,
    })


# Create: Upload new content
@login_required
def upload_content(request):
    if request.method == 'POST':
        form = UploadContentForm(request.POST, request.FILES)
        if form.is_valid():
            content = form.save(commit=False)
            content.user = request.user
            content.save()
            return redirect('user_uploaded_content')
    else:
        form = UploadContentForm()

    return render(request, 'recipes/upload_content.html', {'form': form})


# Update: Edit existing content
@login_required
def edit_content(request, content_id):
    content = get_object_or_404(UploadedContent, id=content_id)
    if content.user != request.user:
        return redirect('user_uploaded_content')

    if request.method == 'POST':
        form = UploadContentForm(request.POST, request.FILES, instance=content)
        if form.is_valid():
            form.save()
            return redirect('user_uploaded_content')
    else:
        form = UploadContentForm(instance=content)

    return render(request, 'recipes/upload_content.html', {'form': form, 'content': content})

# Delete: Delete content
@login_required
def delete_content(request, content_id):
    content = get_object_or_404(UploadedContent, id=content_id)
    if content.user == request.user:
        content.delete()
    return redirect('user_uploaded_content')

# View: Show only the logged-in user's uploaded content
@login_required
def user_uploaded_content(request):
    contents = UploadedContent.objects.filter(user=request.user).order_by('-uploaded_at')
    return render(request, 'recipes/user_uploaded_content.html', {'contents': contents})

@login_required
def like_content(request, content_id):
    content = get_object_or_404(UploadedContent, id=content_id)

    if request.user in content.likes.all():
        content.likes.remove(request.user)
    else:
        content.likes.add(request.user)

    return redirect('content_details', content_id=content_id)