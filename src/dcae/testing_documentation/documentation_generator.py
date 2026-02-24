"""Module for generating documentation automatically based on code."""
from enum import Enum
from typing import Dict, List, Any, Optional
import ast
import inspect


class DocFormat(Enum):
    """Supported documentation formats."""
    MARKDOWN = "markdown"
    RST = "rst"
    DOCSTRING = "docstring"
    HTML = "html"


class DocumentationGenerator:
    """Automatically generates documentation based on code structure and requirements."""

    def __init__(self, format: DocFormat = DocFormat.MARKDOWN):
        """
        Initialize the documentation generator.

        Args:
            format: Preferred documentation format
        """
        self.format = format
        self.templates = self._load_templates()

    def _load_templates(self) -> Dict[str, str]:
        """Load documentation templates for different formats."""
        templates = {}

        # Markdown templates
        templates['markdown_function'] = '''## {function_name}

{docstring}

### Parameters
{parameters}

### Returns
{returns}

### Example
```python
{example}
```
'''

        templates['markdown_class'] = '''# {class_name}

{docstring}

## Methods

{methods}
'''

        # RestructuredText templates
        templates['rst_function'] = '''{function_name}
{underline}

{docstring}

:Parameters: {parameters}
:Returns: {returns}
:Example:

.. code-block:: python

   {example}
'''

        templates['rst_class'] = '''{class_name}
{underline}

{docstring}

Methods
-------

{methods}
'''

        return templates

    def generate_from_code(self, source_code: str) -> str:
        """
        Generate documentation based on provided source code.

        Args:
            source_code: Source code to analyze and generate docs for

        Returns:
            Generated documentation as a string
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
                    'docstring': ast.get_docstring(node) or "No description provided.",
                    'return_annotation': ast.unparse(node.returns) if node.returns else "None",
                    'decorators': [d.id if hasattr(d, 'id') else str(d) for d in node.decorator_list]
                })
            elif isinstance(node, ast.ClassDef):
                methods = []
                for item in node.body:
                    if isinstance(item, ast.FunctionDef):
                        methods.append({
                            'name': item.name,
                            'params': [arg.arg for arg in item.args.args if arg.arg != 'self'],
                            'docstring': ast.get_docstring(item) or "No description provided.",
                            'return_annotation': ast.unparse(item.returns) if item.returns else "None",
                            'decorators': [d.id if hasattr(d, 'id') else str(d) for d in item.decorator_list]
                        })

                classes.append({
                    'name': node.name,
                    'methods': methods,
                    'docstring': ast.get_docstring(node) or "No description provided."
                })

        # Generate documentation based on format
        doc_parts = []

        # Add functions documentation
        for func in functions:
            params_str = ", ".join(func['params'])
            returns_str = func['return_annotation']

            if self.format == DocFormat.MARKDOWN:
                underline = '#' * len(func['name'])
                doc_parts.append(self.templates['markdown_function'].format(
                    function_name=func['name'],
                    docstring=func['docstring'],
                    parameters=params_str,
                    returns=returns_str,
                    example=f"# Example usage of {func['name']}\nresult = {func['name']}()"
                ))
            elif self.format == DocFormat.RST:
                underline = '=' * len(func['name'])
                doc_parts.append(self.templates['rst_function'].format(
                    function_name=func['name'],
                    underline=underline,
                    docstring=func['docstring'],
                    parameters=params_str,
                    returns=returns_str,
                    example=f"# Example usage of {func['name']}\nresult = {func['name']}()"
                ))

        # Add classes documentation
        for cls in classes:
            method_docs = []
            for method in cls['methods']:
                params_str = ", ".join(method['params'])
                returns_str = method['return_annotation']

                if self.format == DocFormat.MARKDOWN:
                    method_doc = f"### {method['name']}\n\n{method['docstring']}\n\n"
                    method_doc += f"**Parameters**: {params_str}\n\n"
                    method_doc += f"**Returns**: {returns_str}\n\n"
                    method_docs.append(method_doc)
                elif self.format == DocFormat.RST:
                    method_doc = f"{method['name']}\n{'-' * len(method['name'])}\n\n"
                    method_doc += f"{method['docstring']}\n\n"
                    method_doc += f":Parameters: {params_str}\n"
                    method_doc += f":Returns: {returns_str}\n\n"
                    method_docs.append(method_doc)

            if self.format == DocFormat.MARKDOWN:
                underline = '#' * len(cls['name'])
                doc_parts.append(self.templates['markdown_class'].format(
                    class_name=cls['name'],
                    docstring=cls['docstring'],
                    underline=underline,
                    methods="\n".join(method_docs)
                ))
            elif self.format == DocFormat.RST:
                underline = '=' * len(cls['name'])
                doc_parts.append(self.templates['rst_class'].format(
                    class_name=cls['name'],
                    docstring=cls['docstring'],
                    underline=underline,
                    methods="\n".join(method_docs)
                ))

        return "\n\n".join(doc_parts)

    def generate_from_requirements(self, requirements: List[Dict[str, Any]]) -> str:
        """
        Generate documentation based on requirements.

        Args:
            requirements: List of requirement dictionaries

        Returns:
            Generated documentation as a string
        """
        doc_parts = []

        for req in requirements:
            req_id = req.get('id', 'unknown')
            req_name = req.get('name', 'Unnamed Requirement')
            req_desc = req.get('description', 'No description provided.')
            req_acceptance = req.get('acceptance_criteria', 'No acceptance criteria defined.')

            if self.format == DocFormat.MARKDOWN:
                doc_parts.append(f"## {req_name} (REQ-{req_id})\n\n{req_desc}\n\n### Acceptance Criteria\n{req_acceptance}\n")
            elif self.format == DocFormat.RST:
                underline = '=' * len(req_name)
                doc_parts.append(f"{req_name} (REQ-{req_id})\n{underline}\n\n{req_desc}\n\nAcceptance Criteria\n{req_acceptance}\n")

        return "\n\n".join(doc_parts)

    def update_format(self, format: DocFormat):
        """
        Update the preferred documentation format.

        Args:
            format: New format preference
        """
        self.format = format
        self.templates = self._load_templates()