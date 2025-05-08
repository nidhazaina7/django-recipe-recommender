import os
import django
import sys
import re
from datasets import load_dataset

# Setup Django
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'recipe_recommender.settings')
django.setup()

# Import after Django setup
from recipes.models import Recipe

def load_huggingface_recipes():
    dataset = load_dataset("corbt/all-recipes", split="train")

    for item in dataset.select(range(100)):  # Limit to first 100 recipes
        raw = item['input']
        
        # Extract title (first line)
        title = raw.split('\n')[0].strip()

        # Extract ingredients using regex between "Ingredients:" and "Directions:"
        ingredients_match = re.search(r'Ingredients:\n(.*?)\nDirections:', raw, re.DOTALL)
        ingredients = ingredients_match.group(1).strip() if ingredients_match else 'No ingredients found'

        # Extract directions (everything after "Directions:")
        directions_match = re.search(r'Directions:\n(.*)', raw, re.DOTALL)
        instructions = directions_match.group(1).strip() if directions_match else 'No instructions found'

        # Create recipe entry in the database
        Recipe.objects.create(
            title=title,
            ingredients=ingredients,
            instructions=instructions,
            description='',
            tags='',
            minutes=None,
        )
    print("Recipes loaded successfully.")

if __name__ == "__main__":
    load_huggingface_recipes()
