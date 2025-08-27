"""
Shopping list generation with efficient ingredient aggregation.
"""

import csv
from typing import Dict, List
from .models import Ingredient


class ShoppingListGenerator:
    """Generates shopping lists from meal plans."""

    def aggregate_ingredients(self, menu: Dict) -> List[Ingredient]:
        """Efficiently aggregate ingredients from a meal plan using dict accumulator."""
        # Use dict for O(1) lookup instead of O(N) scan
        aggregated = {}

        for course_type, dishes in menu.items():
            if course_type == 'nutrition_totals':  # Skip nutrition metadata
                continue
                
            for dish_name, dish_data in dishes.items():
                # Handle both 'ingredients' and legacy 'ingridients' spelling
                ingredients_data = dish_data.get('ingridients', dish_data.get('ingredients', {}))
                
                for ing_name, ing_data in ingredients_data.items():
                    ingredient = Ingredient.from_dict(ing_name, ing_data)
                    
                    if ing_name in aggregated:
                        # Add to existing ingredient (same unit assumed)
                        existing = aggregated[ing_name]
                        if existing.unit == ingredient.unit:
                            aggregated[ing_name] = Ingredient(
                                name=ing_name,
                                amount=existing.amount + ingredient.amount,
                                unit=existing.unit,
                                calories=(existing.calories or 0) + (ingredient.calories or 0) if existing.calories is not None or ingredient.calories is not None else None,
                                protein=(existing.protein or 0) + (ingredient.protein or 0) if existing.protein is not None or ingredient.protein is not None else None,
                                fat=(existing.fat or 0) + (ingredient.fat or 0) if existing.fat is not None or ingredient.fat is not None else None,
                                carbs=(existing.carbs or 0) + (ingredient.carbs or 0) if existing.carbs is not None or ingredient.carbs is not None else None,
                            )
                        else:
                            # Different units - keep separate (could enhance with unit conversion)
                            key = f"{ing_name}_{ingredient.unit}"
                            aggregated[key] = ingredient
                    else:
                        aggregated[ing_name] = ingredient

        return list(aggregated.values())

    def write_shopping_list(self, ingredients: List[Ingredient], filename: str = "shopping_list.csv"):
        """Write ingredients to CSV file."""
        with open(filename, 'w', newline='') as f:
            writer = csv.writer(f)
            
            # Header with legacy spelling for compatibility
            writer.writerow(['Ingridient', 'Amount', 'Unit'])
            
            for ingredient in ingredients:
                writer.writerow([ingredient.name, ingredient.amount, ingredient.unit])

    def generate_from_menu(self, menu_filename: str = "menu.json", output_filename: str = "shopping_list.csv"):
        """Generate shopping list directly from menu file."""
        import json
        
        with open(menu_filename, 'r') as fp:
            menu = json.load(fp)
        
        ingredients = self.aggregate_ingredients(menu)
        self.write_shopping_list(ingredients, output_filename)
        return ingredients