from django.db import models
from django.contrib.auth.models import User

# ─── Recipe Model ─────────────────────────────────────────────────────
class Recipe(models.Model):
    title = models.CharField(max_length=255)
    ingredients = models.TextField()  # Store ingredients as newline-separated string
    instructions = models.TextField()
    description = models.TextField(blank=True, null=True)
    tags = models.TextField(blank=True, null=True)
    minutes = models.IntegerField(blank=True, null=True)  # Preparation time
    nutrition = models.JSONField(blank=True, null=True)  # Nutrition info (fetched & stored as JSON)
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)  # New field for average rating
   
    def __str__(self):
        return self.title

    def update_average_rating(self):
        """Calculate and update the average rating for the recipe."""
        ratings = self.ratings.all()  # Fetch all ratings for this recipe
        total_rating = sum(rating.rating for rating in ratings)  # Sum of all ratings
        num_ratings = ratings.count()  # Count of ratings
        if num_ratings > 0:
            self.average_rating = total_rating / num_ratings  # Calculate the average
        else:
            self.average_rating = 0  # If no ratings, set to 0
        self.save()  # Save the updated average rating


# ─── Favorite Recipes ─────────────────────────────────────────────────
class UserFavorites(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorite_recipes')
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'recipe')

    def __str__(self):
        return f'{self.user.username} - {self.recipe.title}'


# ─── User Preferences ────────────────────────────────────────────────
class UserPreferences(models.Model):
    DIET_CHOICES = [
        ('no_restriction', 'No Restriction'),
        ('vegetarian', 'Vegetarian'),
        ('vegan', 'Vegan'),
        ('gluten_free', 'Gluten-Free'),
    ]

    CUISINE_CHOICES = [
        ('indian', 'Indian'),
        ('italian', 'Italian'),
        ('mexican', 'Mexican'),
        ('chinese', 'Chinese'),
    ]

    SKILL_CHOICES = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    diet = models.CharField(max_length=20, choices=DIET_CHOICES, default='no_restriction')
    favorite_cuisine = models.CharField(max_length=20, choices=CUISINE_CHOICES, default='indian')
    skill_level = models.CharField(max_length=20, choices=SKILL_CHOICES, default='beginner')
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)

    def __str__(self):
        return f"{self.user.username}'s Preferences"


# ─── Optional Separate Profile Model ─────────────────────────────────
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"


# ─── Recipe Rating ───────────────────────────────────────────────────
class RecipeRating(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='ratings')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    date_added = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('recipe', 'user')

    def __str__(self):
        return f"{self.user.username} rated {self.recipe.title} - {self.rating}"

    def save(self, *args, **kwargs):
        """Override the save method to update the average rating of the recipe."""
        super().save(*args, **kwargs)  # Save the rating
        self.recipe.update_average_rating()  # Update the recipe's average rating


# ─── Meal Plan Model ─────────────────────────────────────────────────
class MealPlan(models.Model):
    title = models.CharField(max_length=255, default='Untitled')  # Default value added
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    description = models.TextField(default='No description provided')
    diet_type = models.CharField(max_length=100)
    recipes = models.ManyToManyField(Recipe)
    target_users = models.ManyToManyField(User, related_name="assigned_plans", blank=True)

    def __str__(self):
        return self.title


class UploadedContent(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField()
    image = models.ImageField(upload_to='uploads/')
    ingredients = models.TextField()
    steps = models.TextField()
    uploaded_at = models.DateTimeField(auto_now_add=True)

    likes = models.ManyToManyField(User, related_name='liked_contents', blank=True)

    def total_likes(self):
        return self.likes.count()

    def __str__(self):
        return self.title


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.ForeignKey(UploadedContent, related_name='comments', on_delete=models.CASCADE, null=True)  # Allow null values
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.text



