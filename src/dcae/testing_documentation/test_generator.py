"""Module for generating test cases automatically based on code."""
from enum import Enum
from typing import Dict, List, Any, Optional
import ast
import inspect


class TestType(Enum):
    """Types of tests that can be generated."""
    UNIT = "unit"
    INTEGRATION = "integration"
    E2E = "end-to-end"
    PERFORMANCE = "performance"


class FrameworkPreference(Enum):
    """Supported test frameworks."""
    PYTEST = "pytest"
    UNITTEST = "unittest"
    NOSER = "nose"


class TestGenerator:
    """Automatically generates test cases based on code structure and requirements."""

    def __init__(self, framework: FrameworkPreference = FrameworkPreference.PYTEST):
        """
        Initialize the test generator.

        Args:
            framework: Preferred test framework to use
        """
        self.framework = framework
        self.test_templates = self._load_test_templates()

    def _load_test_templates(self) -> Dict[TestType, str]:
        """Load test templates for different test types."""
        templates = {}

        if self.framework == FrameworkPreference.PYTEST:
            templates[TestType.UNIT] = '''
def test_{function_name}_basic():
    """Test basic functionality of {function_name}."""
    # TODO: Implement test for {function_name}
    assert True

def test_{function_name}_edge_cases():
    """Test edge cases for {function_name}."""
    # TODO: Implement edge case tests
    assert True

def test_{function_name}_error_handling():
    """Test error handling for {function_name}."""
    # TODO: Implement error handling tests
    assert True
'''
        elif self.framework == FrameworkPreference.UNITTEST:
            templates[TestType.UNIT] = '''
class Test{ClassName}(unittest.TestCase):

    def test_{function_name}_basic(self):
        """Test basic functionality of {function_name}."""
        # TODO: Implement test for {function_name}
        self.assertTrue(True)

    def test_{function_name}_edge_cases(self):
        """Test edge cases for {function_name}."""
        # TODO: Implement edge case tests
        self.assertTrue(True)

    def test_{function_name}_error_handling(self):
        """Test error handling for {function_name}."""
        # TODO: Implement error handling tests
        self.assertTrue(True)
'''
        else:
            templates[TestType.UNIT] = '''
# Generic test template
def test_{function_name}():
    """Test for {function_name}."""
    # TODO: Implement test for {function_name}
    assert True
'''

        return templates

    def generate_from_code(self, source_code: str, test_type: TestType = TestType.UNIT) -> str:
        """
        Generate test cases based on provided source code.

        Args:
            source_code: Source code to analyze and generate tests for
            test_type: Type of tests to generate

        Returns:
            Generated test code as a string
        """
        # Parse the source code to extract functions/classes
        try:
            tree = ast.parse(source_code)
        except SyntaxError:
            raise ValueError("Invalid Python code provided")

        # Extract functions and classes
        functions = []
        classes = []

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                functions.append({
                    'name': node.name,
                    'params': [arg.arg for arg in node.args.args if arg.arg != 'self'],
                    'docstring': ast.get_docstring(node),
                    'decorators': [d.id if hasattr(d, 'id') else str(d) for d in node.decorator_list]
                })
            elif isinstance(node, ast.ClassDef):
                methods = []
                for item in node.body:
                    if isinstance(item, ast.FunctionDef):
                        methods.append({
                            'name': item.name,
                            'params': [arg.arg for arg in item.args.args if arg.arg != 'self'],
                            'docstring': ast.get_docstring(item),
                            'decorators': [d.id if hasattr(d, 'id') else str(d) for d in item.decorator_list]
                        })

                classes.append({
                    'name': node.name,
                    'methods': methods,
                    'docstring': ast.get_docstring(node)
                })

        # Generate test code
        test_code_parts = []

        # Import statements based on framework preference
        if self.framework == FrameworkPreference.PYTEST:
            test_code_parts.append("import pytest\n")
        elif self.framework == FrameworkPreference.UNITTEST:
            test_code_parts.append("import unittest\n")

        # Generate tests for functions
        for func in functions:
            template = self.test_templates.get(test_type, self.test_templates[TestType.UNIT])
            # Skip class_name replacement for function tests as it's not needed
            formatted_template = template
            if '{class_name}' in formatted_template:
                formatted_template = formatted_template.replace('{class_name}', 'PlaceholderClass')
            formatted_template = formatted_template.replace('{function_name}', func['name'])
            test_code_parts.append(formatted_template)

        # Generate tests for class methods
        for cls in classes:
            for method in cls['methods']:
                template = self.test_templates.get(test_type, self.test_templates[TestType.UNIT])
                # For class methods, use both function name and class name
                formatted_template = template
                if '{class_name}' in formatted_template:
                    formatted_template = formatted_template.replace('{class_name}', cls['name'])
                if '{function_name}' in formatted_template:
                    formatted_template = formatted_template.replace('{function_name}', method['name'])
                test_code_parts.append(formatted_template)

        return "\n".join(test_code_parts)

    def generate_from_requirements(self, requirements: List[Dict[str, Any]], test_type: TestType = TestType.UNIT) -> str:
        """
        Generate test cases based on requirements.

        Args:
            requirements: List of requirement dictionaries
            test_type: Type of tests to generate

        Returns:
            Generated test code as a string
        """
        test_code_parts = []

        if self.framework == FrameworkPreference.PYTEST:
            test_code_parts.append("import pytest\n")
        elif self.framework == FrameworkPreference.UNITTEST:
            test_code_parts.append("import unittest\n")

        for i, req in enumerate(requirements):
            req_name = req.get('name', f'requirement_{i}')
            req_desc = req.get('description', '')

            # Create test based on requirement
            if self.framework == FrameworkPreference.PYTEST:
                test_func = f'''
def test_requirement_{req_name.replace(" ", "_").lower()}():
    """Test requirement: {req_desc[:50]}..."""
    # TODO: Implement test for requirement: {req_desc}
    assert True
'''
            elif self.framework == FrameworkPreference.UNITTEST:
                test_func = f'''
    def test_requirement_{req_name.replace(" ", "_").lower()}(self):
        """Test requirement: {req_desc[:50]}..."""
        # TODO: Implement test for requirement: {req_desc}
        self.assertTrue(True)
'''

            test_code_parts.append(test_func)

        if self.framework == FrameworkPreference.UNITTEST:
            # Wrap in a test class
            class_name = "TestRequirements"
            unittest_wrapper = f'''
class {class_name}(unittest.TestCase):
{chr(10).join(["    " + line if line.strip() else line for line in ''.join(test_code_parts).strip().split(chr(10))])}

if __name__ == '__main__':
    unittest.main()
'''
            return unittest_wrapper
        else:
            return "\n".join(test_code_parts)

    def update_framework(self, framework: FrameworkPreference):
        """
        Update the preferred test framework.

        Args:
            framework: New framework preference
        """
        self.framework = framework
        self.test_templates = self._load_test_templates()