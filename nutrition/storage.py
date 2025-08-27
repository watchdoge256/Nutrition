"""
Storage management for courses with legacy compatibility.
"""

import json
import os
from typing import Dict, List, Optional
from .models import Course, Ingredient


class CourseStorage:
    """Manages loading and saving courses with backward compatibility."""

    def __init__(self, filename: str = "courses.json"):
        self.filename = filename

    def load_courses(self) -> Dict[str, Dict[str, Course]]:
        """Load courses from storage, handling legacy format."""
        if not os.path.exists(self.filename):
            return {}

        try:
            with open(self.filename, 'r') as fp:
                data = json.load(fp)
        except (json.JSONDecodeError, FileNotFoundError):
            return {}

        # Check if this is the new versioned format
        if isinstance(data, dict) and 'version' in data:
            return self._load_versioned_format(data)
        else:
            # Legacy format - upgrade it
            return self._load_legacy_format(data)

    def _load_legacy_format(self, data: Dict) -> Dict[str, Dict[str, Course]]:
        """Load courses from legacy format and auto-upgrade."""
        courses = {}
        
        for course_type, dishes in data.items():
            courses[course_type] = {}
            for dish_name, dish_data in dishes.items():
                course = Course.from_dict(dish_name, course_type, dish_data)
                courses[course_type][dish_name] = course

        # Auto-save in new format
        self.save_courses(courses)
        return courses

    def _load_versioned_format(self, data: Dict) -> Dict[str, Dict[str, Course]]:
        """Load courses from versioned format."""
        courses = {}
        course_data = data.get('courses', {})
        
        for course_type, dishes in course_data.items():
            courses[course_type] = {}
            for dish_name, dish_data in dishes.items():
                course = Course.from_dict(dish_name, course_type, dish_data)
                courses[course_type][dish_name] = course

        return courses

    def save_courses(self, courses: Dict[str, Dict[str, Course]]):
        """Save courses in versioned format."""
        data = {
            'version': 1,
            'courses': {}
        }

        for course_type, dishes in courses.items():
            data['courses'][course_type] = {}
            for dish_name, course in dishes.items():
                data['courses'][course_type][dish_name] = course.to_dict()

        with open(self.filename, 'w') as fp:
            json.dump(data, fp, indent=2)

    def add_course(self, course: Course):
        """Add a single course to storage."""
        courses = self.load_courses()
        
        if course.course_type not in courses:
            courses[course.course_type] = {}
            
        courses[course.course_type][course.name] = course
        self.save_courses(courses)

    def list_courses(self, course_type: Optional[str] = None) -> List[Course]:
        """List all courses, optionally filtered by type."""
        courses = self.load_courses()
        result = []

        if course_type:
            course_type = course_type.lower()
            if course_type in courses:
                result.extend(courses[course_type].values())
        else:
            for type_courses in courses.values():
                result.extend(type_courses.values())

        return result

    def get_courses_by_type(self) -> Dict[str, List[Course]]:
        """Get courses organized by type."""
        courses = self.load_courses()
        result = {}
        
        for course_type, dishes in courses.items():
            result[course_type] = list(dishes.values())
            
        return result