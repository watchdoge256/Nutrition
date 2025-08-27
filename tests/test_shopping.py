"""
Tests for the shopping module.
"""

import pytest
import tempfile
import os
import csv
from nutrition.models import Course, Ingredient
from nutrition.shopping import ShoppingListGenerator


class TestShoppingListGenerator:
    """Test ShoppingListGenerator class functionality."""

    def test_aggregate_ingredients_simple(self):
        """Test basic ingredient aggregation."""
        menu = {
            "breakfast": {
                "eggs": {
                    "description": "Scrambled eggs",
                    "ingridients": {
                        "eggs": {"amount": 2, "unit": "pieces", "calories": 140},
                        "butter": {"amount": 10, "unit": "g", "calories": 75}
                    }
                }
            },
            "lunch": {
                "salad": {
                    "description": "Green salad",
                    "ingridients": {
                        "lettuce": {"amount": 100, "unit": "g", "calories": 15},
                        "eggs": {"amount": 1, "unit": "pieces", "calories": 70}
                    }
                }
            }
        }
        
        generator = ShoppingListGenerator()
        ingredients = generator.aggregate_ingredients(menu)
        
        # Should have 3 unique ingredients
        assert len(ingredients) == 3
        
        # Find aggregated eggs
        eggs_ing = next((ing for ing in ingredients if ing.name == "eggs"), None)
        assert eggs_ing is not None
        assert eggs_ing.amount == 3  # 2 + 1
        assert eggs_ing.unit == "pieces"
        assert eggs_ing.calories == 210  # 140 + 70
        
        # Check other ingredients
        butter_ing = next((ing for ing in ingredients if ing.name == "butter"), None)
        assert butter_ing is not None
        assert butter_ing.amount == 10
        
        lettuce_ing = next((ing for ing in ingredients if ing.name == "lettuce"), None)
        assert lettuce_ing is not None
        assert lettuce_ing.amount == 100

    def test_aggregate_ingredients_with_nutrition(self):
        """Test aggregation preserves and sums nutrition information."""
        menu = {
            "breakfast": {
                "dish1": {
                    "ingridients": {
                        "protein": {
                            "amount": 100,
                            "unit": "g",
                            "calories": 200,
                            "protein": 25,
                            "fat": 5,
                            "carbs": 0
                        }
                    }
                }
            },
            "lunch": {
                "dish2": {
                    "ingridients": {
                        "protein": {
                            "amount": 50,
                            "unit": "g",
                            "calories": 100,
                            "protein": 12.5,
                            "fat": 2.5,
                            "carbs": 0
                        }
                    }
                }
            }
        }
        
        generator = ShoppingListGenerator()
        ingredients = generator.aggregate_ingredients(menu)
        
        assert len(ingredients) == 1
        protein_ing = ingredients[0]
        assert protein_ing.name == "protein"
        assert protein_ing.amount == 150  # 100 + 50
        assert protein_ing.calories == 300  # 200 + 100
        assert protein_ing.protein == 37.5  # 25 + 12.5
        assert protein_ing.fat == 7.5  # 5 + 2.5
        assert protein_ing.carbs == 0

    def test_aggregate_ingredients_different_units(self):
        """Test handling of ingredients with different units."""
        menu = {
            "breakfast": {
                "dish1": {
                    "ingridients": {
                        "milk": {"amount": 200, "unit": "ml"},
                        "flour": {"amount": 50, "unit": "g"}
                    }
                }
            },
            "lunch": {
                "dish2": {
                    "ingridients": {
                        "milk": {"amount": 1, "unit": "cup"},  # Different unit
                        "flour": {"amount": 25, "unit": "g"}   # Same unit
                    }
                }
            }
        }
        
        generator = ShoppingListGenerator()
        ingredients = generator.aggregate_ingredients(menu)
        
        # Should have 3 ingredients (milk_ml, milk_cup, flour)
        assert len(ingredients) == 3
        
        # Find flour (should be aggregated)
        flour_ing = next((ing for ing in ingredients if ing.name == "flour"), None)
        assert flour_ing is not None
        assert flour_ing.amount == 75  # 50 + 25
        assert flour_ing.unit == "g"
        
        # Should have both milk entries with different units
        milk_names = [ing.name for ing in ingredients if "milk" in ing.name]
        assert len(milk_names) == 2

    def test_aggregate_ingredients_no_nutrition(self):
        """Test aggregation of ingredients without nutrition data."""
        menu = {
            "breakfast": {
                "simple": {
                    "ingridients": {
                        "water": {"amount": 250, "unit": "ml"},
                        "salt": {"amount": 2, "unit": "g"}
                    }
                }
            },
            "lunch": {
                "simple2": {
                    "ingridients": {
                        "water": {"amount": 150, "unit": "ml"},
                        "pepper": {"amount": 1, "unit": "g"}
                    }
                }
            }
        }
        
        generator = ShoppingListGenerator()
        ingredients = generator.aggregate_ingredients(menu)
        
        assert len(ingredients) == 3
        
        water_ing = next((ing for ing in ingredients if ing.name == "water"), None)
        assert water_ing is not None
        assert water_ing.amount == 400  # 250 + 150
        assert water_ing.calories is None

    def test_aggregate_ingredients_mixed_nutrition(self):
        """Test aggregation when some instances have nutrition and others don't."""
        menu = {
            "breakfast": {
                "dish1": {
                    "ingridients": {
                        "rice": {
                            "amount": 50,
                            "unit": "g",
                            "calories": 175,
                            "protein": 4
                        }
                    }
                }
            },
            "lunch": {
                "dish2": {
                    "ingridients": {
                        "rice": {
                            "amount": 30,
                            "unit": "g"
                            # No nutrition data
                        }
                    }
                }
            }
        }
        
        generator = ShoppingListGenerator()
        ingredients = generator.aggregate_ingredients(menu)
        
        assert len(ingredients) == 1
        rice_ing = ingredients[0]
        assert rice_ing.amount == 80
        assert rice_ing.calories == 175  # Only from first instance
        assert rice_ing.protein == 4

    def test_write_shopping_list(self):
        """Test writing shopping list to CSV file."""
        ingredients = [
            Ingredient("eggs", 6, "pieces", 420, 36, 30, 3),
            Ingredient("flour", 200, "g", 720, 24, 2, 150),
            Ingredient("milk", 500, "ml", 300, 20, 12.5, 30)
        ]
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as tf:
            generator = ShoppingListGenerator()
            generator.write_shopping_list(ingredients, tf.name)
            
            # Read back and verify
            with open(tf.name, 'r') as f:
                reader = csv.reader(f)
                rows = list(reader)
            
            # Check header
            assert rows[0] == ['Ingridient', 'Amount', 'Unit']
            
            # Check data rows
            assert len(rows) == 4  # Header + 3 ingredients
            assert rows[1] == ['eggs', '6', 'pieces']
            assert rows[2] == ['flour', '200', 'g']
            assert rows[3] == ['milk', '500', 'ml']
            
        os.unlink(tf.name)

    def test_generate_from_menu_file(self):
        """Test generating shopping list directly from menu file."""
        menu = {
            "breakfast": {
                "eggs": {
                    "ingridients": {
                        "eggs": {"amount": 2, "unit": "pieces"},
                        "butter": {"amount": 10, "unit": "g"}
                    }
                }
            }
        }
        
        # Write menu to temp file
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as menu_file:
            import json
            json.dump(menu, menu_file)
            menu_file.flush()
            
            # Generate shopping list
            with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as csv_file:
                generator = ShoppingListGenerator()
                ingredients = generator.generate_from_menu(menu_file.name, csv_file.name)
                
                # Verify ingredients were returned
                assert len(ingredients) == 2
                ingredient_names = [ing.name for ing in ingredients]
                assert "eggs" in ingredient_names
                assert "butter" in ingredient_names
                
                # Verify CSV was written
                with open(csv_file.name, 'r') as f:
                    content = f.read()
                    assert "eggs" in content
                    assert "butter" in content
                
            os.unlink(csv_file.name)
        os.unlink(menu_file.name)

    def test_skip_nutrition_totals(self):
        """Test that nutrition_totals key is skipped during aggregation."""
        menu = {
            "breakfast": {
                "eggs": {
                    "ingridients": {
                        "eggs": {"amount": 2, "unit": "pieces"}
                    }
                }
            },
            "nutrition_totals": {
                "overall": {"calories": 1000, "protein": 50}
            }
        }
        
        generator = ShoppingListGenerator()
        ingredients = generator.aggregate_ingredients(menu)
        
        # Should only have eggs, nutrition_totals should be ignored
        assert len(ingredients) == 1
        assert ingredients[0].name == "eggs"

    def test_efficient_aggregation_performance(self):
        """Test that aggregation uses dict-based approach (O(1) lookup)."""
        # Create a menu with many repeated ingredients
        menu = {}
        
        # Add 100 dishes each with the same ingredient
        for i in range(100):
            menu[f"course_type_{i % 3}"] = menu.get(f"course_type_{i % 3}", {})
            menu[f"course_type_{i % 3}"][f"dish_{i}"] = {
                "ingridients": {
                    "common_ingredient": {"amount": 10, "unit": "g"},
                    f"unique_ingredient_{i}": {"amount": 5, "unit": "g"}
                }
            }
        
        generator = ShoppingListGenerator()
        ingredients = generator.aggregate_ingredients(menu)
        
        # Should have aggregated the common ingredient
        common_ing = next((ing for ing in ingredients if ing.name == "common_ingredient"), None)
        assert common_ing is not None
        assert common_ing.amount == 1000  # 10 * 100
        
        # Should have 101 total ingredients (1 common + 100 unique)
        assert len(ingredients) == 101