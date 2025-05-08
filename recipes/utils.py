from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from .models import Recipe
import numpy as np

def get_similar_recipes(user_input):
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    from .models import Recipe

    if not user_input.strip():
        return []

    # Fetch recipes with non-empty ingredients
    raw_recipes = Recipe.objects.exclude(ingredients__isnull=True).exclude(ingredients__exact='')
    filtered_recipes = [recipe for recipe in raw_recipes if recipe.ingredients.strip()]

    if not filtered_recipes:
        return []

    documents = [recipe.ingredients for recipe in filtered_recipes]
    documents.append(user_input)

    tfidf = TfidfVectorizer(stop_words='english')
    tfidf_matrix = tfidf.fit_transform(documents)

    if tfidf_matrix.shape[0] < 2:
        return []

    cosine_sim = cosine_similarity(tfidf_matrix[-1], tfidf_matrix[:-1])
    sim_scores = list(enumerate(cosine_sim[0]))

    # Sort all recipes by similarity (highest first)
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)

    # Return all filtered recipes sorted by similarity
    all_similar_recipes = [filtered_recipes[i[0]] for i in sim_scores]

    return all_similar_recipes


import pandas as pd
import random

def build_meal_plan(diet_data, days):
    """
    Builds a meal plan for a specified number of days and generates a shopping list.
    Args:
        diet_data (DataFrame): Dataframe containing diet data with recipes.
        days (int): Number of days for the meal plan.

    Returns:
        meal_plan (list): List of meal plan details for each day.
        shopping_list (list): List of ingredients for the shopping list.
    """
    meal_plan = []
    shopping_list = []

    for day in range(1, days + 1):
        daily_meals = []

        # Randomly select meals for the day
        for _ in range(3):  # Assuming 3 meals per day
            meal = diet_data.sample(n=1).iloc[0]  # Randomly pick one recipe
            daily_meals.append({
                'Recipe_name': meal['Recipe_name'],
                'Cuisine_type': meal['Cuisine_type'],
                'Protein(g)': meal['Protein(g)'],
                'Carbs(g)': meal['Carbs(g)'],
                'Fat(g)': meal['Fat(g)'],
                'Ingredients': meal['Ingredients'].split(',')  # Assuming ingredients are stored as a comma-separated string
            })

            # Add ingredients to the shopping list
            for ingredient in meal['Ingredients'].split(','):
                shopping_list.append(ingredient.strip())

        meal_plan.append({
            'day': day,
            'meals': daily_meals,
        })

    # Remove duplicate ingredients from the shopping list
    shopping_list = list(set(shopping_list))

    return meal_plan, shopping_list


import os
from django.conf import settings

DIET_FILES = {
    'paleo': 'paleo.csv',
    'keto': 'keto.csv',
    'vegan': 'vegan.csv',
    'mediterranean': 'mediterranean.csv',
    'dash': 'dash.csv',
}

def load_diet_data(diet):
    # Modify the file path to point to the correct location inside your templates folder
    file_path = os.path.join(settings.BASE_DIR, 'recipes', 'templates', 'data', DIET_FILES.get(diet, ''))

    # Print the file path for debugging
    print(f"Looking for diet file at: {file_path}")
    
    # Check if the file exists
    if os.path.exists(file_path):
        return pd.read_csv(file_path)
    else:
        # Print a warning message if file is not found
        print(f"File not found: {file_path}")
        return pd.DataFrame()

# recipes/utils.py

MOOD_TO_RECIPE_TAGS = {
    "happy": ["dessert", "cake", "ice cream", "smoothie"],
    "lazy": ["one-pot", "quick", "5-minute", "no-cook"],
    "stressed": ["comfort food", "noodles", "cheesy", "soup"],
    "healthy": ["salad", "vegan", "gluten-free", "smoothie"],
    "sad": ["chocolate", "mac and cheese", "cookies", "pasta"],
    "angry": ["spicy", "fried", "crunchy", "burger"],
    "romantic": ["italian", "chocolate", "wine", "steak"],
}

