"""
Meal planning with interactive selection and constraints.
"""

import json
import random
from typing import Dict, List, Optional, Set
from .models import Course
from .storage import CourseStorage


class MealPlanner:
    """Generates meal plans with various constraints and interactive selection."""

    def __init__(self, storage: Optional[CourseStorage] = None):
        self.storage = storage or CourseStorage()

    def generate_plan(
        self,
        days: int = 7,
        servings: int = 1,
        no_reuse: bool = False,
        max_repeats: Optional[int] = None,
        seed: Optional[int] = None,
        interactive: bool = False,
        include: Optional[List[str]] = None,
        exclude: Optional[List[str]] = None
    ) -> Dict:
        """Generate a meal plan with specified constraints."""
        
        if seed is not None:
            random.seed(seed)

        courses_by_type = self.storage.get_courses_by_type()
        
        # Apply include/exclude filters
        if include or exclude:
            courses_by_type = self._apply_filters(courses_by_type, include, exclude)

        menu = {}
        used_courses = set() if no_reuse else None
        repeat_counts = {} if max_repeats is not None else None

        for course_type, available_courses in courses_by_type.items():
            if not available_courses:
                continue
                
            menu[course_type] = {}
            type_available = available_courses.copy()

            for day in range(days):
                if not type_available:
                    # If we've run out of courses and no_reuse is True, skip
                    if no_reuse:
                        continue
                    # Otherwise, reset available courses
                    type_available = available_courses.copy()

                if interactive:
                    course = self._interactive_selection(day, course_type, type_available)
                    if course is None:  # Skip meal
                        continue
                else:
                    course = random.choice(type_available)

                # Check repeat constraints
                if max_repeats is not None:
                    course_key = f"{course.course_type}:{course.name}"
                    if repeat_counts.get(course_key, 0) >= max_repeats:
                        # Remove from available and try again
                        type_available.remove(course)
                        if not type_available:
                            if no_reuse:
                                continue
                            type_available = available_courses.copy()
                        course = random.choice(type_available)

                # Scale for servings and add to menu
                scaled_course = course.scale_servings(servings)
                menu[course_type][course.name] = scaled_course.to_dict()

                # Update tracking
                if no_reuse and used_courses is not None:
                    used_courses.add(course.name)
                    type_available.remove(course)

                if max_repeats is not None and repeat_counts is not None:
                    course_key = f"{course.course_type}:{course.name}"
                    repeat_counts[course_key] = repeat_counts.get(course_key, 0) + 1

        return menu

    def _apply_filters(
        self, 
        courses_by_type: Dict[str, List[Course]], 
        include: Optional[List[str]], 
        exclude: Optional[List[str]]
    ) -> Dict[str, List[Course]]:
        """Apply include/exclude filters to courses."""
        filtered = {}
        
        for course_type, courses in courses_by_type.items():
            filtered_courses = courses.copy()
            
            if include:
                include_lower = [name.lower() for name in include]
                filtered_courses = [c for c in filtered_courses if c.name in include_lower]
            
            if exclude:
                exclude_lower = [name.lower() for name in exclude]
                filtered_courses = [c for c in filtered_courses if c.name not in exclude_lower]
            
            filtered[course_type] = filtered_courses
            
        return filtered

    def _interactive_selection(self, day: int, course_type: str, available_courses: List[Course]) -> Optional[Course]:
        """Interactive course selection. Returns None if meal should be skipped."""
        course = random.choice(available_courses)
        
        while True:
            response = input(f"Day {day + 1} {course_type}: {course.name}. Accept? [Y/n/r=replace/x=skip]: ").strip().lower()
            
            if response in ['', 'y', 'yes']:
                return course
            elif response in ['n', 'no', 'r', 'replace']:
                # Try to pick a different course
                remaining = [c for c in available_courses if c.name != course.name]
                if remaining:
                    course = random.choice(remaining)
                    continue
                else:
                    print(f"No other {course_type} courses available.")
                    return course
            elif response in ['x', 'skip']:
                return None
            else:
                print("Please enter Y/n/r/x")

    def save_plan(self, menu: Dict, filename: str = "menu.json", nutrition_totals: Optional[Dict] = None):
        """Save meal plan to file with optional nutrition totals."""
        # Create a copy to avoid modifying the original menu
        menu_to_save = menu.copy()
        if nutrition_totals:
            menu_to_save['nutrition_totals'] = nutrition_totals
            
        with open(filename, 'w') as fp:
            json.dump(menu_to_save, fp, indent=2)

    def load_plan(self, filename: str = "menu.json") -> Dict:
        """Load meal plan from file."""
        with open(filename, 'r') as fp:
            return json.load(fp)