"""
Tests for the macros module.
"""

import pytest
import tempfile
import os
import json
from io import StringIO
import sys
from nutrition.macros import MacroCalculator


class TestMacroCalculator:
    """Test MacroCalculator class functionality."""

    def test_calculate_plan_macros_simple(self):
        """Test basic macro calculation for a simple plan."""
        menu = {
            "breakfast": {
                "eggs": {
                    "ingridients": {
                        "eggs": {
                            "amount": 2,
                            "unit": "pieces",
                            "calories": 140,
                            "protein": 12,
                            "fat": 10,
                            "carbs": 1
                        },
                        "butter": {
                            "amount": 10,
                            "unit": "g",
                            "calories": 75,
                            "protein": 0,
                            "fat": 8,
                            "carbs": 0
                        }
                    }
                }
            },
            "lunch": {
                "salad": {
                    "ingridients": {
                        "lettuce": {
                            "amount": 100,
                            "unit": "g",
                            "calories": 15,
                            "protein": 1,
                            "fat": 0,
                            "carbs": 3
                        }
                    }
                }
            }
        }
        
        calculator = MacroCalculator()
        nutrition_totals = calculator.calculate_plan_macros(menu)
        
        # Check structure
        assert 'per_day' in nutrition_totals
        assert 'overall' in nutrition_totals
        
        # Should have one day since each course type has one dish
        assert len(nutrition_totals['per_day']) == 1
        
        day0 = nutrition_totals['per_day'][0]
        assert day0['day_index'] == 0
        assert day0['calories'] == 230  # 140 + 75 + 15
        assert day0['protein'] == 13   # 12 + 0 + 1
        assert day0['fat'] == 18       # 10 + 8 + 0
        assert day0['carbs'] == 4      # 1 + 0 + 3
        
        # Overall should match day totals for single day
        overall = nutrition_totals['overall']
        assert overall['calories'] == 230
        assert overall['protein'] == 13
        assert overall['fat'] == 18
        assert overall['carbs'] == 4

    def test_calculate_plan_macros_multiple_days(self):
        """Test macro calculation for multi-day plan."""
        menu = {
            "breakfast": {
                "eggs": {
                    "ingridients": {
                        "eggs": {"amount": 2, "unit": "pieces", "calories": 140, "protein": 12}
                    }
                },
                "oats": {
                    "ingridients": {
                        "oats": {"amount": 50, "unit": "g", "calories": 190, "protein": 6}
                    }
                }
            },
            "lunch": {
                "salad": {
                    "ingridients": {
                        "lettuce": {"amount": 100, "unit": "g", "calories": 15, "protein": 1}
                    }
                },
                "pasta": {
                    "ingridients": {
                        "pasta": {"amount": 100, "unit": "g", "calories": 350, "protein": 12}
                    }
                }
            }
        }
        
        calculator = MacroCalculator()
        nutrition_totals = calculator.calculate_plan_macros(menu)
        
        # Should have 2 days
        assert len(nutrition_totals['per_day']) == 2
        
        # Day 0: eggs + salad
        day0 = nutrition_totals['per_day'][0]
        assert day0['calories'] == 155  # 140 + 15
        assert day0['protein'] == 13   # 12 + 1
        
        # Day 1: oats + pasta
        day1 = nutrition_totals['per_day'][1]
        assert day1['calories'] == 540  # 190 + 350
        assert day1['protein'] == 18   # 6 + 12
        
        # Overall should be sum of both days
        overall = nutrition_totals['overall']
        assert overall['calories'] == 695  # 155 + 540
        assert overall['protein'] == 31   # 13 + 18

    def test_calculate_plan_macros_missing_nutrition(self):
        """Test macro calculation when some ingredients lack nutrition data."""
        menu = {
            "breakfast": {
                "mixed": {
                    "ingridients": {
                        "eggs": {
                            "amount": 2,
                            "unit": "pieces",
                            "calories": 140,
                            "protein": 12
                        },
                        "salt": {
                            "amount": 1,
                            "unit": "g"
                            # No nutrition data
                        }
                    }
                }
            }
        }
        
        calculator = MacroCalculator()
        nutrition_totals = calculator.calculate_plan_macros(menu)
        
        # Should only count nutrition from eggs
        day0 = nutrition_totals['per_day'][0]
        assert day0['calories'] == 140
        assert day0['protein'] == 12
        assert day0['fat'] == 0  # Salt has no fat data
        assert day0['carbs'] == 0  # Salt has no carbs data

    def test_calculate_plan_macros_empty_menu(self):
        """Test macro calculation with empty menu."""
        menu = {}
        
        calculator = MacroCalculator()
        nutrition_totals = calculator.calculate_plan_macros(menu)
        
        assert nutrition_totals['per_day'] == []
        assert nutrition_totals['overall'] == {'calories': 0, 'protein': 0, 'fat': 0, 'carbs': 0}

    def test_calculate_plan_macros_with_existing_nutrition_totals(self):
        """Test that existing nutrition_totals are ignored during calculation."""
        menu = {
            "breakfast": {
                "eggs": {
                    "ingridients": {
                        "eggs": {"amount": 2, "unit": "pieces", "calories": 140}
                    }
                }
            },
            "nutrition_totals": {
                "overall": {"calories": 999}  # Should be ignored
            }
        }
        
        calculator = MacroCalculator()
        nutrition_totals = calculator.calculate_plan_macros(menu)
        
        # Should calculate from actual ingredients, not use existing totals
        assert nutrition_totals['overall']['calories'] == 140

    def test_print_macro_summary(self, capsys):
        """Test formatted printing of macro summary."""
        nutrition_totals = {
            'per_day': [
                {'day_index': 0, 'calories': 500.5, 'protein': 25.2, 'fat': 20.1, 'carbs': 50.3},
                {'day_index': 1, 'calories': 600.7, 'protein': 30.8, 'fat': 25.9, 'carbs': 60.4}
            ],
            'overall': {'calories': 1101.2, 'protein': 56.0, 'fat': 46.0, 'carbs': 110.7}
        }
        
        calculator = MacroCalculator()
        calculator.print_macro_summary(nutrition_totals)
        
        captured = capsys.readouterr()
        output = captured.out
        
        # Check that summary was printed
        assert "Nutrition Summary" in output
        assert "Per Day:" in output
        assert "Overall Totals:" in output
        
        # Check day data
        assert "1     500.5" in output  # Day 1
        assert "2     600.7" in output  # Day 2
        
        # Check overall data
        assert "1101.2" in output
        assert "56.0" in output

    def test_load_and_print_macros_existing_totals(self, capsys):
        """Test loading and printing macros when nutrition_totals exist."""
        menu = {
            "breakfast": {"eggs": {"ingridients": {"eggs": {"amount": 2, "unit": "pieces"}}}},
            "nutrition_totals": {
                "overall": {"calories": 1000, "protein": 50, "fat": 30, "carbs": 100}
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as tf:
            json.dump(menu, tf)
            tf.flush()
            
            calculator = MacroCalculator()
            calculator.load_and_print_macros(tf.name)
            
            captured = capsys.readouterr()
            output = captured.out
            
            # Should use existing nutrition_totals
            assert "1000.0" in output
            assert "50.0" in output
            
        os.unlink(tf.name)

    def test_load_and_print_macros_calculate_totals(self, capsys):
        """Test loading and printing when nutrition_totals need to be calculated."""
        menu = {
            "breakfast": {
                "eggs": {
                    "ingridients": {
                        "eggs": {
                            "amount": 2,
                            "unit": "pieces",
                            "calories": 140,
                            "protein": 12
                        }
                    }
                }
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as tf:
            json.dump(menu, tf)
            tf.flush()
            
            calculator = MacroCalculator()
            calculator.load_and_print_macros(tf.name)
            
            captured = capsys.readouterr()
            output = captured.out
            
            # Should calculate and display macros
            assert "140.0" in output  # Calories
            assert "12.0" in output   # Protein
            
        os.unlink(tf.name)

    def test_calculate_dish_macros(self):
        """Test calculation of macros for a single dish."""
        dish_data = {
            "description": "Test dish",
            "ingridients": {
                "ingredient1": {
                    "amount": 100,
                    "unit": "g",
                    "calories": 200,
                    "protein": 20,
                    "fat": 10,
                    "carbs": 5
                },
                "ingredient2": {
                    "amount": 50,
                    "unit": "g",
                    "calories": 100,
                    "protein": 5,
                    "fat": 2,
                    "carbs": 15
                }
            }
        }
        
        calculator = MacroCalculator()
        macros = calculator._calculate_dish_macros(dish_data)
        
        assert macros['calories'] == 300  # 200 + 100
        assert macros['protein'] == 25   # 20 + 5
        assert macros['fat'] == 12       # 10 + 2
        assert macros['carbs'] == 20     # 5 + 15

    def test_organize_by_days(self):
        """Test organization of menu dishes by days."""
        menu = {
            "breakfast": {
                "eggs": {"ingridients": {}},
                "oats": {"ingridients": {}}
            },
            "lunch": {
                "salad": {"ingridients": {}},
                "pasta": {"ingridients": {}}
            }
        }
        
        calculator = MacroCalculator()
        days_data = calculator._organize_by_days(menu)
        
        # Should have 2 days (max dishes in any course type)
        assert len(days_data) == 2
        
        # Each day should have 2 dishes (one from each course type)
        assert len(days_data[0]) == 2
        assert len(days_data[1]) == 2

    def test_organize_by_days_uneven(self):
        """Test organization when course types have different numbers of dishes."""
        menu = {
            "breakfast": {
                "eggs": {"ingridients": {}},
                "oats": {"ingridients": {}},
                "toast": {"ingridients": {}}
            },
            "lunch": {
                "salad": {"ingridients": {}}
            }
        }
        
        calculator = MacroCalculator()
        days_data = calculator._organize_by_days(menu)
        
        # Should have 3 days (max from breakfast)
        assert len(days_data) == 3
        
        # Day 0: eggs + salad
        assert len(days_data[0]) == 2
        # Day 1: oats (no lunch)
        assert len(days_data[1]) == 1
        # Day 2: toast (no lunch)
        assert len(days_data[2]) == 1

    def test_manual_recomputation_matches(self):
        """Test that calculated totals match manual recomputation."""
        menu = {
            "breakfast": {
                "dish1": {
                    "ingridients": {
                        "ing1": {"amount": 10, "unit": "g", "calories": 100, "protein": 10, "fat": 5, "carbs": 15},
                        "ing2": {"amount": 5, "unit": "g", "calories": 50, "protein": 3, "fat": 2, "carbs": 8}
                    }
                }
            },
            "lunch": {
                "dish2": {
                    "ingridients": {
                        "ing3": {"amount": 20, "unit": "g", "calories": 200, "protein": 20, "fat": 8, "carbs": 25}
                    }
                }
            }
        }
        
        calculator = MacroCalculator()
        nutrition_totals = calculator.calculate_plan_macros(menu)
        
        # Manual calculation
        # Day 0: dish1 + dish2 = (100+50) + 200 = 350 calories
        #                      = (10+3) + 20 = 33 protein
        #                      = (5+2) + 8 = 15 fat
        #                      = (15+8) + 25 = 48 carbs
        
        day0 = nutrition_totals['per_day'][0]
        assert day0['calories'] == 350
        assert day0['protein'] == 33
        assert day0['fat'] == 15
        assert day0['carbs'] == 48
        
        # Overall should match day0 for single day
        overall = nutrition_totals['overall']
        assert overall['calories'] == 350
        assert overall['protein'] == 33
        assert overall['fat'] == 15
        assert overall['carbs'] == 48