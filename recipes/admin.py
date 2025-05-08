from django.contrib import admin
from .models import Recipe, MealPlan, UserFavorites, RecipeRating, UserPreferences, UserProfile, UploadedContent, Comment

admin.site.register(Recipe)
admin.site.register(MealPlan)
admin.site.register(UserFavorites)
admin.site.register(UserPreferences)
admin.site.register(RecipeRating)
admin.site.register(UserProfile)
# admin.site.register(UploadedContent)
admin.site.register(Comment)
# admin.site.register(Like)

@admin.register(UploadedContent)
class UploadedContentAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'uploaded_at')

