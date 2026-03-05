# Best Practices Template

## Purpose
Template for adding new best practices to the DCAE framework.

## Template

```python
def add_new_best_practice_example(self, path: Path):
    """Example function showing how to add a new best practice check."""

    for file_path in path.rglob("*.py"):  # Or whatever extension you're checking
        if file_path.is_file():
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                lines = content.split('\n')
                for i, line in enumerate(lines, 1):
                    # Add your specific check here

                    # Example: Check for a specific pattern
                    if "your_pattern_here" in line.lower():
                        finding = ReviewFinding(
                            id=f"bp_category_specific_{file_path}:{i}",
                            category=ReviewCategory.BEST_PRACTICES,  # Or a new category
                            severity=ReviewSeverity.MEDIUM,  # Adjust as needed
                            file_path=str(file_path),
                            line_number=i,
                            issue_description="Description of the issue found",
                            recommendation="Recommendation to fix the issue",
                            code_snippet=line.strip()
                        )
                        self.findings.append(finding)

            except Exception as e:
                print(f"    Warning: Could not review {file_path}: {str(e)}")
```

## Steps to Add a New Best Practice

1. **Define the Check Logic**: Determine what pattern, structure, or anti-pattern you want to detect.

2. **Choose Appropriate Category**: Use an existing category or create a new one in the `ReviewCategory` enum.

3. **Set Severity Level**: Assign appropriate severity based on the importance of the issue:
   - `INFO`: Minor observations
   - `LOW`: Minor issues that don't affect functionality
   - `MEDIUM`: Issues that could lead to problems
   - `HIGH`: Significant issues that should be fixed
   - `CRITICAL`: Critical issues that must be addressed immediately

4. **Add Configuration Option**: If your check should be configurable, add an option to the `_get_default_config` method.

5. **Call Your Method**: Add a call to your new method in the `review_generated_output` method.

6. **Test Your Check**: Create test code that both passes and fails your check to verify it works correctly.

## Configuration Template

Add to the configuration dictionary in `_get_default_config()`:

```python
"new_practice_category": {
    "enable_your_check": True,  # Enable/disable the check
    "your_threshold_setting": 10,  # Any thresholds you need
    # ... other settings
}
```

## Example: Adding a Memory Leak Detection Check

```python
def _review_memory_management(self, path: Path):
    """Review code for potential memory management issues."""
    print(f"  Performing memory management review in: {path}")

    # Only check if enabled in config
    if not self.config.get("memory_management", {}).get("enable_leak_detection", False):
        return

    for file_path in path.rglob("*.py"):
        if file_path.is_file():
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                lines = content.split('\n')
                for i, line in enumerate(lines, 1):
                    # Example: Check for circular references creation
                    if "import gc" not in content and ("__del__" in line or "atexit.register" in line):
                        finding = ReviewFinding(
                            id=f"mem_mgmt_gc_{file_path}:{i}",
                            category=ReviewCategory.BEST_PRACTICES,
                            severity=ReviewSeverity.MEDIUM,
                            file_path=str(file_path),
                            line_number=i,
                            issue_description="Potential memory management issue without garbage collection awareness",
                            recommendation="Consider explicit memory management or proper use of context managers",
                            code_snippet=line.strip()
                        )
                        self.findings.append(finding)

            except Exception as e:
                print(f"    Warning: Could not review {file_path}: {str(e)}")
```

Then register it by adding the call in the main review method:

```python
def review_generated_output(self, target_path: Optional[str] = None) -> ReviewReport:
    # ... existing calls ...
    self._review_memory_management(review_path)  # Add this line
    # ... rest of method ...
```

## Best Practices for Writing Checks

1. **Be Specific**: Targeted checks are more useful than general ones.

2. **Minimize False Positives**: Ensure your patterns are specific enough to avoid flagging valid code.

3. **Provide Clear Recommendations**: Users should understand exactly what to do to address the finding.

4. **Consider Performance**: Avoid expensive operations that could slow down the review process.

5. **Handle Exceptions Gracefully**: Always wrap file operations in try/catch blocks.

6. **Document Your Checks**: Add docstrings explaining what each check looks for.
```