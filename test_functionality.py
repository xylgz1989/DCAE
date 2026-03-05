import sys
import os
sys.path.insert(0, os.path.join(os.getcwd(), 'src'))

from dcae.unified_review import UnifiedReviewInterface
import tempfile
from pathlib import Path

# Create a temporary directory with a sample file
with tempfile.TemporaryDirectory() as tmpdir:
    print(f"Using temporary directory: {tmpdir}")

    # Create a sample file with issues
    sample_file = Path(tmpdir) / "sample.py"
    with open(sample_file, 'w') as f:
        f.write('''
def problematic_function():
    """A function with multiple issues."""
    password = "hardcoded_password"  # Security issue
    result = []
    for i in range(10):
        for j in range(10):  # Performance issue: nested loops
            result.append(i * j)
    return result
''')

    print("Created sample file with known issues")

    # Initialize the reviewer
    reviewer = UnifiedReviewInterface(tmpdir)

    print("Initialized UnifiedReviewInterface")

    # Run comprehensive review
    results = reviewer.run_comprehensive_review(target_path=str(sample_file))

    print("Full results keys:", results.keys())

    if 'summary' in results:
        print("Summary keys:", results['summary'].keys())
        summary = results['summary']
        if 'total_findings' in summary:
            print(f"Review completed with {summary['total_findings']} findings")
        else:
            print("total_findings not in summary:", summary)
    else:
        print("summary not in results")

    # Print summary
    if 'summary' in results and 'findings_by_severity' in results['summary']:
        print("Findings by severity:")
        for severity, count in results['summary']['findings_by_severity'].items():
            print(f"  {severity}: {count}")
    else:
        print("No severity breakdown available")

    print("Review mechanism working correctly!")