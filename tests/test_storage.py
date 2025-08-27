"""
Tests for the storage module.
"""

import pytest
import json
import tempfile
import os
from nutrition.models import Course, Ingredient
from nutrition.storage import CourseStorage


class TestCourseStorage:
    """Test CourseStorage class functionality."""

    def test_storage_empty_file(self):
        """Test loading from non-existent file."""
        with tempfile.NamedTemporaryFile(delete=True) as tf:
            os.unlink(tf.name)  # Delete the file so it doesn't exist
            storage = CourseStorage(tf.name)
            courses = storage.load_courses()
            assert courses == {}

    def test_storage_save_and_load(self):
        """Test saving and loading courses."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as tf:
            storage = CourseStorage(tf.name)
            
            # Create test course
            course = Course("test dish", "breakfast", "Test description")
            ing = Ingredient("test_ing", 50, "g", 100, 5, 2, 10)
            course.add_ingredient(ing)
            
            # Save course
            storage.add_course(course)
            
            # Load courses
            courses = storage.load_courses()
            
            assert "breakfast" in courses
            assert "test dish" in courses["breakfast"]
            loaded_course = courses["breakfast"]["test dish"]
            assert loaded_course.description == "Test description"
            assert len(loaded_course.ingredients) == 1
            assert loaded_course.ingredients["test_ing"].calories == 100
            
        os.unlink(tf.name)

    def test_legacy_format_compatibility(self):
        """Test loading and auto-upgrading legacy format."""
        legacy_data = {
            "breakfast": {
                "scrambled eggs": {
                    "description": "Beat eggs and cook",
                    "ingridients": {
                        "eggs": {"amount": 2.0, "unit": "pieces"},
                        "butter": {"amount": 10.0, "unit": "g"}
                    }
                }
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as tf:
            json.dump(legacy_data, tf)
            tf.flush()
            
            storage = CourseStorage(tf.name)
            courses = storage.load_courses()
            
            # Verify legacy data was loaded correctly
            assert "breakfast" in courses
            assert "scrambled eggs" in courses["breakfast"]
            course = courses["breakfast"]["scrambled eggs"]
            assert course.description == "Beat eggs and cook"
            assert "eggs" in course.ingredients
            assert course.ingredients["eggs"].amount == 2.0
            
            # Verify file was auto-upgraded to new format
            with open(tf.name, 'r') as f:
                saved_data = json.load(f)
            assert "version" in saved_data
            assert saved_data["version"] == 1
            assert "courses" in saved_data
            
        os.unlink(tf.name)

    def test_versioned_format_load(self):
        """Test loading versioned format."""
        versioned_data = {
            "version": 1,
            "courses": {
                "lunch": {
                    "pasta": {
                        "description": "Cook pasta",
                        "ingridients": {
                            "pasta": {
                                "amount": 100.0,
                                "unit": "g",
                                "calories": 350,
                                "protein": 12,
                                "fat": 2,
                                "carbs": 70
                            }
                        }
                    }
                }
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as tf:
            json.dump(versioned_data, tf)
            tf.flush()
            
            storage = CourseStorage(tf.name)
            courses = storage.load_courses()
            
            assert "lunch" in courses
            assert "pasta" in courses["lunch"]
            course = courses["lunch"]["pasta"]
            assert course.description == "Cook pasta"
            pasta_ing = course.ingredients["pasta"]
            assert pasta_ing.calories == 350
            assert pasta_ing.protein == 12
            
        os.unlink(tf.name)

    def test_add_multiple_courses(self):
        """Test adding multiple courses."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as tf:
            storage = CourseStorage(tf.name)
            
            # Add first course
            course1 = Course("dish1", "breakfast")
            storage.add_course(course1)
            
            # Add second course to same type
            course2 = Course("dish2", "breakfast")
            storage.add_course(course2)
            
            # Add course to different type
            course3 = Course("dish3", "lunch")
            storage.add_course(course3)
            
            courses = storage.load_courses()
            
            assert len(courses) == 2  # Two course types
            assert len(courses["breakfast"]) == 2
            assert len(courses["lunch"]) == 1
            assert "dish1" in courses["breakfast"]
            assert "dish2" in courses["breakfast"]
            assert "dish3" in courses["lunch"]
            
        os.unlink(tf.name)

    def test_list_courses(self):
        """Test listing courses with and without filters."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as tf:
            storage = CourseStorage(tf.name)
            
            # Add test courses
            course1 = Course("breakfast dish", "breakfast")
            course2 = Course("lunch dish", "lunch")
            course3 = Course("dinner dish", "dinner")
            
            storage.add_course(course1)
            storage.add_course(course2)
            storage.add_course(course3)
            
            # Test listing all courses
            all_courses = storage.list_courses()
            assert len(all_courses) == 3
            
            # Test filtering by type
            breakfast_courses = storage.list_courses("breakfast")
            assert len(breakfast_courses) == 1
            assert breakfast_courses[0].name == "breakfast dish"
            
            # Test non-existent type
            none_courses = storage.list_courses("snack")
            assert len(none_courses) == 0
            
        os.unlink(tf.name)

    def test_get_courses_by_type(self):
        """Test getting courses organized by type."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as tf:
            storage = CourseStorage(tf.name)
            
            # Add test courses
            course1 = Course("eggs", "breakfast")
            course2 = Course("toast", "breakfast")
            course3 = Course("salad", "lunch")
            
            storage.add_course(course1)
            storage.add_course(course2)
            storage.add_course(course3)
            
            by_type = storage.get_courses_by_type()
            
            assert "breakfast" in by_type
            assert "lunch" in by_type
            assert len(by_type["breakfast"]) == 2
            assert len(by_type["lunch"]) == 1
            
            breakfast_names = [c.name for c in by_type["breakfast"]]
            assert "eggs" in breakfast_names
            assert "toast" in breakfast_names
            
        os.unlink(tf.name)

    def test_corrupt_json_handling(self):
        """Test handling of corrupted JSON file."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as tf:
            tf.write("invalid json content {")
            tf.flush()
            
            storage = CourseStorage(tf.name)
            courses = storage.load_courses()
            
            # Should return empty dict for corrupted file
            assert courses == {}
            
        os.unlink(tf.name)