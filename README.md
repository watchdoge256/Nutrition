# Nutrition

A modular tool for meal planning, nutrition tracking, and shopping list generation.

## Features

- **Modular Architecture**: Clean separation of concerns with dedicated modules for storage, planning, shopping, and macro calculation
- **Nutrition Tracking**: Track calories, protein, fat, and carbs per ingredient with automatic aggregation
- **Interactive Planning**: Interactively accept, reject, or replace meal suggestions
- **Deterministic Planning**: Use seeds for reproducible meal plans
- **Smart Shopping Lists**: Efficient ingredient aggregation with O(1) lookup performance
- **Legacy Compatibility**: Seamlessly upgrade from old course storage format
- **Comprehensive Testing**: Full test suite ensuring reliability

## Installation

The package uses only standard library modules except for development dependencies.

For development (to run tests):
```bash
pip install pytest>=8.0
```

## New CLI Usage

The new modular CLI provides subcommands for different operations:

### Adding Courses

```bash
python -m nutrition.cli add --type breakfast --name "scrambled eggs" \
  --description "Beat eggs and cook in pan" \
  --ingredient "eggs,2,pieces,140,12,10,1" \
  --ingredient "butter,10,g,75,0,8,0"
```

Ingredient format: `name,amount,unit[,calories,protein,fat,carbs]`

### Listing Courses

```bash
# List all courses
python -m nutrition.cli list

# Filter by type
python -m nutrition.cli list --type breakfast
```

### Generating Meal Plans

```bash
# Basic meal plan
python -m nutrition.cli plan --days 7 --output weekly_menu.json

# Advanced options
python -m nutrition.cli plan \
  --days 5 \
  --servings 2 \
  --seed 42 \
  --no-reuse \
  --max-repeats 2 \
  --include "scrambled eggs" "pasta" \
  --exclude "salad" \
  --interactive \
  --shopping shopping_list.csv \
  --output custom_menu.json
```

#### Planning Options:
- `--days N`: Number of days (default: 7)
- `--servings N`: Number of servings per dish (default: 1)
- `--seed N`: Random seed for reproducible plans
- `--no-reuse`: Don't reuse dishes across days
- `--max-repeats N`: Maximum times a dish can appear
- `--interactive`: Interactive meal selection
- `--include DISH`: Include specific dishes (repeatable)
- `--exclude DISH`: Exclude specific dishes (repeatable)
- `--shopping FILE.csv`: Also generate shopping list
- `--output FILE.json`: Output file (default: menu.json)

### Interactive Planning

When using `--interactive`, you'll be prompted for each meal:

```
Day 1 breakfast: scrambled eggs. Accept? [Y/n/r=replace/x=skip]:
```

- `Y` or Enter: Accept the suggestion
- `n` or `r`: Try a different dish
- `x`: Skip this meal

### Generating Shopping Lists

```bash
# From existing menu
python -m nutrition.cli ingredients --menu weekly_menu.json --output shopping.csv
```

### Viewing Nutrition Summary

```bash
python -m nutrition.cli macros --menu weekly_menu.json
```

This displays a formatted table with per-day and overall nutrition totals.

## Menu File Format

Generated menu files include embedded nutrition totals:

```json
{
  "breakfast": {
    "scrambled eggs": {
      "description": "Beat eggs and cook in pan",
      "ingridients": {
        "eggs": {
          "amount": 2.0,
          "unit": "pieces",
          "calories": 140.0,
          "protein": 12.0,
          "fat": 10.0,
          "carbs": 1.0
        }
      }
    }
  },
  "nutrition_totals": {
    "per_day": [
      {
        "day_index": 0,
        "calories": 140.0,
        "protein": 12.0,
        "fat": 10.0,
        "carbs": 1.0
      }
    ],
    "overall": {
      "calories": 140.0,
      "protein": 12.0,
      "fat": 10.0,
      "carbs": 1.0
    }
  }
}
```

## Data Storage

Courses are stored in `courses.json` with automatic format versioning:

```json
{
  "version": 1,
  "courses": {
    "breakfast": {
      "scrambled eggs": {
        "description": "Beat eggs and cook in pan",
        "ingridients": {
          "eggs": {"amount": 2.0, "unit": "pieces", "calories": 140.0, ...}
        }
      }
    }
  }
}
```

Legacy format files are automatically upgraded on first use.

## Testing

Run the test suite:

```bash
pytest tests/
```

Or install development dependencies and run tests:

```bash
pip install -e .[dev]
pytest
```

## Legacy CLI (Deprecated)

**⚠️ The old `diet.py` script is deprecated. Please migrate to the new CLI.**

### Old Usage (still functional but deprecated):

```bash
./diet.py -rORa add -ct breakfast -n "scrambled eggs" -d "Beat eggs..." -ing "eggs,2,pieces"
./diet.py -rORa randomize -ds 7 -cr 1
```

### Migration Guide:

| Old Command | New Command |
|-------------|-------------|
| `diet.py -rORa add -ct TYPE -n NAME -d DESC -ing ING1 ING2` | `nutrition.cli add --type TYPE --name NAME --description DESC --ingredient ING1 --ingredient ING2` |
| `diet.py -rORa randomize -ds DAYS -cr REPEAT` | `nutrition.cli plan --days DAYS` (Note: repeats now handled differently) |

## Contributing

1. Run tests: `pytest tests/`
2. Follow existing code style
3. Add tests for new features
4. Update documentation

## Architecture

The codebase is organized into focused modules:

- `nutrition/models.py`: Data classes for Ingredient and Course
- `nutrition/storage.py`: Course persistence with legacy compatibility  
- `nutrition/planner.py`: Meal plan generation with constraints
- `nutrition/shopping.py`: Efficient ingredient aggregation
- `nutrition/macros.py`: Nutrition calculation and reporting
- `nutrition/cli.py`: Command-line interface

This modular design makes the code easier to test, maintain, and extend.
