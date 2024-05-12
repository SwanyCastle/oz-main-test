from django.db import models

from common.models import Common
from foods.models import FoodIngredient, FoodType
from users.models import CustomUser


class Recipe(Common):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    food_type = models.ForeignKey(FoodType, on_delete=models.CASCADE)
    food_ingredients = models.ManyToManyField(FoodIngredient)
    title = models.CharField(max_length=255)
    content = models.TextField()
    thumbnail = models.URLField(null=True, blank=True)
    difficulty = models.CharField(max_length=100)
