"""
Command-line interface for the nutrition package.
"""

import argparse
import sys
from typing import List, Optional

from .models import Course, Ingredient
from .storage import CourseStorage
from .planner import MealPlanner
from .shopping import ShoppingListGenerator
from .macros import MacroCalculator


def parse_ingredient_string(ing_str: str) -> Ingredient:
    """Parse ingredient string in format: name,amount,unit[,calories,protein,fat,carbs]"""
    parts = ing_str.split(',')
    
    if len(parts) < 3:
        raise ValueError(f"Invalid ingredient format: {ing_str}. Expected: name,amount,unit[,calories,protein,fat,carbs]")
    
    name = parts[0].strip()
    try:
        amount = float(parts[1].strip())
    except ValueError:
        raise ValueError(f"Invalid amount in ingredient: {ing_str}")
    
    unit = parts[2].strip()
    
    # Optional nutrition values
    calories = protein = fat = carbs = None
    if len(parts) > 3:
        try:
            calories = float(parts[3].strip()) if parts[3].strip() else None
        except ValueError:
            raise ValueError(f"Invalid calories in ingredient: {ing_str}")
    
    if len(parts) > 4:
        try:
            protein = float(parts[4].strip()) if parts[4].strip() else None
        except ValueError:
            raise ValueError(f"Invalid protein in ingredient: {ing_str}")
    
    if len(parts) > 5:
        try:
            fat = float(parts[5].strip()) if parts[5].strip() else None
        except ValueError:
            raise ValueError(f"Invalid fat in ingredient: {ing_str}")
    
    if len(parts) > 6:
        try:
            carbs = float(parts[6].strip()) if parts[6].strip() else None
        except ValueError:
            raise ValueError(f"Invalid carbs in ingredient: {ing_str}")
    
    return Ingredient(name, amount, unit, calories, protein, fat, carbs)


def cmd_add(args):
    """Add a new course."""
    if not args.name or not args.type:
        print("Error: --name and --type are required for add command", file=sys.stderr)
        return 1
    
    if not args.ingredient:
        print("Error: At least one --ingredient is required", file=sys.stderr)
        return 1
    
    storage = CourseStorage()
    course = Course(args.name, args.type, args.description or "")
    
    try:
        for ing_str in args.ingredient:
            ingredient = parse_ingredient_string(ing_str)
            course.add_ingredient(ingredient)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    
    storage.add_course(course)
    print(f"Added {args.type} course: {args.name}")
    return 0


def cmd_list(args):
    """List courses."""
    storage = CourseStorage()
    courses = storage.list_courses(args.type)
    
    if not courses:
        print("No courses found.")
        return 0
    
    # Group by type for display
    by_type = {}
    for course in courses:
        if course.course_type not in by_type:
            by_type[course.course_type] = []
        by_type[course.course_type].append(course)
    
    for course_type, type_courses in sorted(by_type.items()):
        print(f"\n{course_type.upper()}:")
        for course in sorted(type_courses, key=lambda c: c.name):
            print(f"  - {course.name}")
            if course.description:
                print(f"    {course.description}")
    
    return 0


def cmd_plan(args):
    """Generate a meal plan."""
    storage = CourseStorage()
    planner = MealPlanner(storage)
    macro_calc = MacroCalculator()
    
    try:
        menu = planner.generate_plan(
            days=args.days,
            servings=args.servings,
            no_reuse=args.no_reuse,
            max_repeats=args.max_repeats,
            seed=args.seed,
            interactive=args.interactive,
            include=args.include,
            exclude=args.exclude
        )
        
        # Calculate nutrition totals
        nutrition_totals = macro_calc.calculate_plan_macros(menu)
        
        # Save plan with nutrition totals
        planner.save_plan(menu, args.output, nutrition_totals)
        print(f"Generated meal plan saved to {args.output}")
        
        # Generate shopping list if requested
        if args.shopping:
            shopping_gen = ShoppingListGenerator()
            shopping_gen.generate_from_menu(args.output, args.shopping)
            print(f"Shopping list saved to {args.shopping}")
        
        return 0
        
    except Exception as e:
        print(f"Error generating plan: {e}", file=sys.stderr)
        return 1


def cmd_ingredients(args):
    """Generate shopping list from existing menu."""
    try:
        shopping_gen = ShoppingListGenerator()
        ingredients = shopping_gen.generate_from_menu(args.menu, args.output)
        print(f"Shopping list with {len(ingredients)} ingredients saved to {args.output}")
        return 0
    except Exception as e:
        print(f"Error generating shopping list: {e}", file=sys.stderr)
        return 1


def cmd_macros(args):
    """Display nutrition macros from menu."""
    try:
        macro_calc = MacroCalculator()
        macro_calc.load_and_print_macros(args.menu)
        return 0
    except Exception as e:
        print(f"Error loading macros: {e}", file=sys.stderr)
        return 1


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Nutrition planning and macro tracking tool",
        prog="python -m nutrition.cli"
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Add command
    add_parser = subparsers.add_parser('add', help='Add a new course')
    add_parser.add_argument('--type', required=True, help='Course type (breakfast, lunch, dinner, etc.)')
    add_parser.add_argument('--name', required=True, help='Course name')
    add_parser.add_argument('--description', help='Course description')
    add_parser.add_argument('--ingredient', action='append', required=True,
                           help='Ingredient in format: name,amount,unit[,calories,protein,fat,carbs]')
    
    # List command
    list_parser = subparsers.add_parser('list', help='List courses')
    list_parser.add_argument('--type', help='Filter by course type')
    
    # Plan command
    plan_parser = subparsers.add_parser('plan', help='Generate meal plan')
    plan_parser.add_argument('--days', type=int, default=7, help='Number of days (default: 7)')
    plan_parser.add_argument('--servings', type=int, default=1, help='Number of servings (default: 1)')
    plan_parser.add_argument('--no-reuse', action='store_true', help='Disallow reusing courses')
    plan_parser.add_argument('--max-repeats', type=int, help='Maximum times a course can repeat')
    plan_parser.add_argument('--seed', type=int, help='Random seed for reproducibility')
    plan_parser.add_argument('--interactive', action='store_true', help='Interactive meal selection')
    plan_parser.add_argument('--include', action='append', help='Include specific courses')
    plan_parser.add_argument('--exclude', action='append', help='Exclude specific courses')
    plan_parser.add_argument('--output', default='menu.json', help='Output file (default: menu.json)')
    plan_parser.add_argument('--shopping', help='Also generate shopping list to this file')
    
    # Ingredients command
    ingredients_parser = subparsers.add_parser('ingredients', help='Generate shopping list from menu')
    ingredients_parser.add_argument('--menu', default='menu.json', help='Menu file (default: menu.json)')
    ingredients_parser.add_argument('--output', default='shopping_list.csv', help='Output file (default: shopping_list.csv)')
    
    # Macros command
    macros_parser = subparsers.add_parser('macros', help='Display nutrition summary')
    macros_parser.add_argument('--menu', default='menu.json', help='Menu file (default: menu.json)')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    # Dispatch to command handlers
    commands = {
        'add': cmd_add,
        'list': cmd_list,
        'plan': cmd_plan,
        'ingredients': cmd_ingredients,
        'macros': cmd_macros,
    }
    
    return commands[args.command](args)


if __name__ == '__main__':
    sys.exit(main())