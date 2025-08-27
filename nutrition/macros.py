"""
Nutrition macro calculation and aggregation.
"""

import json
from typing import Dict, List, Tuple
from .models import Ingredient


class MacroCalculator:
    """Calculates and aggregates nutritional macros from meal plans."""

    def calculate_plan_macros(self, menu: Dict) -> Dict:
        """Calculate per-day and overall nutrition totals for a meal plan."""
        daily_macros = []
        overall_macros = {'calories': 0, 'protein': 0, 'fat': 0, 'carbs': 0}

        # Group dishes by day (assuming sequential ordering)
        days_data = self._organize_by_days(menu)

        for day_index, day_dishes in enumerate(days_data):
            day_totals = {'day_index': day_index, 'calories': 0, 'protein': 0, 'fat': 0, 'carbs': 0}

            for dish_data in day_dishes:
                dish_macros = self._calculate_dish_macros(dish_data)
                for macro in ['calories', 'protein', 'fat', 'carbs']:
                    day_totals[macro] += dish_macros[macro]

            daily_macros.append(day_totals)

            # Add to overall totals
            for macro in ['calories', 'protein', 'fat', 'carbs']:
                overall_macros[macro] += day_totals[macro]

        return {
            'per_day': daily_macros,
            'overall': overall_macros
        }

    def _organize_by_days(self, menu: Dict) -> List[List[Dict]]:
        """Organize menu dishes by days (simplified - assumes all course types have same number of days)."""
        if not menu or 'nutrition_totals' in menu:
            # Remove nutrition_totals if present to avoid processing it
            menu = {k: v for k, v in menu.items() if k != 'nutrition_totals'}

        if not menu:
            return []

        # Get the maximum number of dishes in any course type to determine days
        max_dishes = max(len(dishes) for dishes in menu.values()) if menu else 0
        
        days_data = []
        for day in range(max_dishes):
            day_dishes = []
            for course_type, dishes in menu.items():
                dish_names = list(dishes.keys())
                if day < len(dish_names):
                    dish_name = dish_names[day]
                    day_dishes.append(dishes[dish_name])
            days_data.append(day_dishes)

        return days_data

    def _calculate_dish_macros(self, dish_data: Dict) -> Dict:
        """Calculate macros for a single dish."""
        macros = {'calories': 0, 'protein': 0, 'fat': 0, 'carbs': 0}

        # Handle both 'ingredients' and legacy 'ingridients' spelling
        ingredients_data = dish_data.get('ingridients', dish_data.get('ingredients', {}))

        for ing_name, ing_data in ingredients_data.items():
            # Add missing nutrition fields with default values if they don't exist
            for field in ['calories', 'protein', 'fat', 'carbs']:
                if field in ing_data and ing_data[field] is not None:
                    macros[field] += ing_data[field]

        return macros

    def print_macro_summary(self, nutrition_totals: Dict):
        """Print a formatted table of nutrition totals."""
        print("\n=== Nutrition Summary ===")
        
        if 'per_day' in nutrition_totals:
            print("\nPer Day:")
            print(f"{'Day':<5} {'Calories':<10} {'Protein':<10} {'Fat':<8} {'Carbs':<8}")
            print("-" * 45)
            
            for day_data in nutrition_totals['per_day']:
                day_num = day_data['day_index'] + 1
                print(f"{day_num:<5} {day_data['calories']:<10.1f} {day_data['protein']:<10.1f} {day_data['fat']:<8.1f} {day_data['carbs']:<8.1f}")

        if 'overall' in nutrition_totals:
            overall = nutrition_totals['overall']
            print(f"\nOverall Totals:")
            print(f"{'Total':<5} {overall['calories']:<10.1f} {overall['protein']:<10.1f} {overall['fat']:<8.1f} {overall['carbs']:<8.1f}")
        
        print()

    def load_and_print_macros(self, menu_filename: str = "menu.json"):
        """Load menu file and print macro summary."""
        with open(menu_filename, 'r') as fp:
            menu = json.load(fp)

        if 'nutrition_totals' in menu:
            # Use existing nutrition totals
            self.print_macro_summary(menu['nutrition_totals'])
        else:
            # Calculate nutrition totals
            nutrition_totals = self.calculate_plan_macros(menu)
            self.print_macro_summary(nutrition_totals)