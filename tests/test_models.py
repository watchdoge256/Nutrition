"""
Tests for the models module.
"""

import pytest
import json
from nutrition.models import Ingredient, Course


class TestIngredient:
    """Test Ingredient class functionality."""

    def test_ingredient_creation(self):
        """Test basic ingredient creation."""
        ing = Ingredient("Eggs", 2.0, "pieces", 140, 12, 10, 1)
        assert ing.name == "eggs"  # Should be lowercased
        assert ing.amount == 2.0
        assert ing.unit == "pieces"
        assert ing.calories == 140
        assert ing.protein == 12
        assert ing.fat == 10
        assert ing.carbs == 1

    def test_ingredient_without_nutrition(self):
        """Test ingredient creation without nutrition info."""
        ing = Ingredient("Salt", 5, "g")
        assert ing.name == "salt"
        assert ing.amount == 5
        assert ing.unit == "g"
        assert ing.calories is None
        assert ing.protein is None
        assert ing.fat is None
        assert ing.carbs is None

    def test_ingredient_to_dict(self):
        """Test ingredient serialization to dict."""
        ing = Ingredient("Milk", 200, "ml", 120, 8, 5, 12)
        data = ing.to_dict()
        
        expected = {
            'amount': 200,
            'unit': 'ml',
            'calories': 120,
            'protein': 8,
            'fat': 5,
            'carbs': 12
        }
        assert data == expected

    def test_ingredient_to_dict_no_nutrition(self):
        """Test ingredient serialization without nutrition."""
        ing = Ingredient("Water", 250, "ml")
        data = ing.to_dict()
        
        expected = {
            'amount': 250,
            'unit': 'ml'
        }
        assert data == expected

    def test_ingredient_from_dict(self):
        """Test ingredient deserialization from dict."""
        data = {
            'amount': 100,
            'unit': 'g',
            'calories': 300,
            'protein': 20,
            'fat': 15,
            'carbs': 25
        }
        ing = Ingredient.from_dict("Chicken", data)
        
        assert ing.name == "chicken"
        assert ing.amount == 100
        assert ing.unit == "g"
        assert ing.calories == 300
        assert ing.protein == 20
        assert ing.fat == 15
        assert ing.carbs == 25

    def test_ingredient_scale(self):
        """Test ingredient scaling."""
        ing = Ingredient("Rice", 50, "g", 175, 4, 1, 35)
        scaled = ing.scale(2.0)
        
        assert scaled.name == "rice"
        assert scaled.amount == 100
        assert scaled.unit == "g"
        assert scaled.calories == 350
        assert scaled.protein == 8
        assert scaled.fat == 2
        assert scaled.carbs == 70

    def test_ingredient_scale_no_nutrition(self):
        """Test scaling ingredient without nutrition data."""
        ing = Ingredient("Oil", 10, "ml")
        scaled = ing.scale(1.5)
        
        assert scaled.amount == 15
        assert scaled.calories is None


class TestCourse:
    """Test Course class functionality."""

    def test_course_creation(self):
        """Test basic course creation."""
        course = Course("Scrambled Eggs", "breakfast", "Beat and cook eggs")
        assert course.name == "scrambled eggs"
        assert course.course_type == "breakfast"
        assert course.description == "Beat and cook eggs"
        assert len(course.ingredients) == 0

    def test_course_add_ingredient(self):
        """Test adding ingredients to course."""
        course = Course("Pasta", "lunch")
        ing1 = Ingredient("pasta", 100, "g", 350, 12, 2, 70)
        ing2 = Ingredient("sauce", 50, "ml", 30, 1, 1, 5)
        
        course.add_ingredient(ing1)
        course.add_ingredient(ing2)
        
        assert len(course.ingredients) == 2
        assert "pasta" in course.ingredients
        assert "sauce" in course.ingredients

    def test_course_to_dict(self):
        """Test course serialization."""
        course = Course("Test Dish", "dinner", "Test description")
        ing = Ingredient("test_ing", 50, "g", 100, 5, 2, 10)
        course.add_ingredient(ing)
        
        data = course.to_dict()
        expected = {
            'description': 'Test description',
            'ingridients': {  # Legacy spelling
                'test_ing': {
                    'amount': 50,
                    'unit': 'g',
                    'calories': 100,
                    'protein': 5,
                    'fat': 2,
                    'carbs': 10
                }
            }
        }
        
        assert data == expected

    def test_course_from_dict(self):
        """Test course deserialization."""
        data = {
            'description': 'Test recipe',
            'ingridients': {
                'ingredient1': {
                    'amount': 25,
                    'unit': 'g',
                    'calories': 50
                },
                'ingredient2': {
                    'amount': 100,
                    'unit': 'ml'
                }
            }
        }
        
        course = Course.from_dict("Test Course", "lunch", data)
        
        assert course.name == "test course"
        assert course.course_type == "lunch"
        assert course.description == "Test recipe"
        assert len(course.ingredients) == 2
        assert "ingredient1" in course.ingredients
        assert course.ingredients["ingredient1"].calories == 50
        assert course.ingredients["ingredient2"].calories is None

    def test_course_scale_servings(self):
        """Test scaling course for multiple servings."""
        course = Course("Salad", "lunch")
        ing = Ingredient("lettuce", 50, "g", 10, 1, 0, 2)
        course.add_ingredient(ing)
        
        scaled = course.scale_servings(3)
        
        assert scaled.name == "salad"
        assert scaled.course_type == "lunch"
        assert len(scaled.ingredients) == 1
        assert scaled.ingredients["lettuce"].amount == 150
        assert scaled.ingredients["lettuce"].calories == 30

    def test_round_trip_serialization(self):
        """Test that course can be serialized and deserialized maintaining nutrition data."""
        # Create original course
        course = Course("Complex Dish", "dinner", "Complex recipe")
        ing1 = Ingredient("protein", 100, "g", 200, 25, 5, 0)
        ing2 = Ingredient("carbs", 80, "g", 300, 8, 1, 60)
        course.add_ingredient(ing1)
        course.add_ingredient(ing2)
        
        # Serialize
        data = course.to_dict()
        
        # Deserialize
        restored = Course.from_dict("Complex Dish", "dinner", data)
        
        # Verify everything matches
        assert restored.name == course.name
        assert restored.course_type == course.course_type
        assert restored.description == course.description
        assert len(restored.ingredients) == len(course.ingredients)
        
        for name, orig_ing in course.ingredients.items():
            rest_ing = restored.ingredients[name]
            assert rest_ing.amount == orig_ing.amount
            assert rest_ing.unit == orig_ing.unit
            assert rest_ing.calories == orig_ing.calories
            assert rest_ing.protein == orig_ing.protein
            assert rest_ing.fat == orig_ing.fat
            assert rest_ing.carbs == orig_ing.carbs