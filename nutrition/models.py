"""
Data models for nutrition tracking system.
"""

from dataclasses import dataclass, field
from typing import Dict, Optional
import json


@dataclass
class Ingredient:
    """Represents an ingredient with optional nutritional information."""
    name: str
    amount: float
    unit: str
    calories: Optional[float] = None
    protein: Optional[float] = None  # grams
    fat: Optional[float] = None      # grams
    carbs: Optional[float] = None    # grams

    def __post_init__(self):
        """Normalize name to lowercase."""
        self.name = self.name.lower()

    def to_dict(self) -> Dict:
        """Convert to dictionary format for JSON serialization."""
        result = {
            'amount': self.amount,
            'unit': self.unit
        }
        
        # Add nutrition fields if they exist
        if self.calories is not None:
            result['calories'] = self.calories
        if self.protein is not None:
            result['protein'] = self.protein
        if self.fat is not None:
            result['fat'] = self.fat
        if self.carbs is not None:
            result['carbs'] = self.carbs
            
        return result

    @classmethod
    def from_dict(cls, name: str, data: Dict) -> 'Ingredient':
        """Create ingredient from dictionary data."""
        return cls(
            name=name,
            amount=data['amount'],
            unit=data['unit'],
            calories=data.get('calories'),
            protein=data.get('protein'),
            fat=data.get('fat'),
            carbs=data.get('carbs')
        )

    def scale(self, multiplier: float) -> 'Ingredient':
        """Return a new ingredient with scaled amounts."""
        return Ingredient(
            name=self.name,
            amount=self.amount * multiplier,
            unit=self.unit,
            calories=self.calories * multiplier if self.calories is not None else None,
            protein=self.protein * multiplier if self.protein is not None else None,
            fat=self.fat * multiplier if self.fat is not None else None,
            carbs=self.carbs * multiplier if self.carbs is not None else None,
        )


@dataclass
class Course:
    """Represents a dish/course with ingredients and description."""
    name: str
    course_type: str  # breakfast, lunch, dinner, etc.
    description: str = ""
    ingredients: Dict[str, Ingredient] = field(default_factory=dict)

    def __post_init__(self):
        """Normalize names to lowercase."""
        self.name = self.name.lower()
        self.course_type = self.course_type.lower()

    def add_ingredient(self, ingredient: Ingredient):
        """Add an ingredient to this course."""
        self.ingredients[ingredient.name] = ingredient

    def to_dict(self) -> Dict:
        """Convert to dictionary format for JSON serialization."""
        return {
            'description': self.description,
            'ingridients': {  # Keep legacy spelling for compatibility
                name: ing.to_dict() 
                for name, ing in self.ingredients.items()
            }
        }

    @classmethod
    def from_dict(cls, name: str, course_type: str, data: Dict) -> 'Course':
        """Create course from dictionary data."""
        course = cls(name=name, course_type=course_type, description=data.get('description', ''))
        
        # Handle both 'ingredients' and legacy 'ingridients' spelling
        ingredients_data = data.get('ingridients', data.get('ingredients', {}))
        
        for ing_name, ing_data in ingredients_data.items():
            ingredient = Ingredient.from_dict(ing_name, ing_data)
            course.add_ingredient(ingredient)
            
        return course

    def scale_servings(self, servings: int) -> 'Course':
        """Return a new course with ingredients scaled for multiple servings."""
        scaled_course = Course(
            name=self.name,
            course_type=self.course_type,
            description=self.description
        )
        
        for name, ingredient in self.ingredients.items():
            scaled_course.add_ingredient(ingredient.scale(servings))
            
        return scaled_course