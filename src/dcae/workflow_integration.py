"""
Workflow Integration Module

This module implements the integration of the review mechanism with development workflows,
CI/CD pipelines, and team collaboration features in the DCAE framework.
"""
from typing import Dict, Any, List, Optional, Callable
from pathlib import Path
import subprocess
import os
import json
from datetime import datetime
import tempfile


class DevelopmentWorkflowIntegrator:
    """Integrates review mechanism with development workflows."""

    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
        self.git_root = self._find_git_root()

    def _find_git_root(self) -> Optional[Path]:
        """Find the git root directory for the project."""
        current_path = self.project_path.resolve()

        while current_path.parent != current_path:  # Stop at filesystem root
            git_dir = current_path / ".git"
            if git_dir.exists() and git_dir.is_dir():
                return current_path
            current_path = current_path.parent

        return None

    def is_git_repository(self) -> bool:
        """Check if the project is in a git repository."""
        return self.git_root is not None

    def install_git_hooks(self, hook_types: List[str] = None) -> bool:
        """
        Install git hooks for automatic reviews.

        Args:
            hook_types: List of hook types to install (pre-commit, pre-push, etc.)

        Returns:
            True if installation was successful, False otherwise
        """
        if not self.is_git_repository():
            print("Project is not in a git repository. Cannot install git hooks.")
            return False

        hooks_dir = self.git_root / ".git" / "hooks"
        hooks_dir.mkdir(exist_ok=True)

        if hook_types is None:
            hook_types = ["pre-commit"]

        # Define hook scripts for different types
        hook_scripts = {
            "pre-commit": f'''#!/usr/bin/env python3
import subprocess
import sys
import os

# Change to the git root directory
script_dir = os.path.dirname(os.path.abspath(__file__))
git_root = os.path.dirname(script_dir)
os.chdir(git_root)

print("Running DCAE review before commit...")

# Run DCAE review on staged files
result = subprocess.run([
    sys.executable, "-c",
    f"""
import sys
sys.path.insert(0, '{os.path.join(git_root, 'src')}')
from dcae.unified_review import UnifiedReviewInterface
import subprocess

# Get list of staged Python files
result = subprocess.run(['git', 'diff', '--cached', '--name-only', '--diff-filter=d'],
                       capture_output=True, text=True, cwd='{git_root}')
staged_files = [f for f in result.stdout.strip().split('\\n') if f.endswith('.py')]

if staged_files:
    reviewer = UnifiedReviewInterface('{git_root}')
    results = reviewer.run_comprehensive_review(target_path='{git_root}')

    # Check for high/critical issues
    summary = results.get('summary', {{}})
    high_severity = summary.get('findings_by_severity', {{}}).get('high', 0) + \\
                   summary.get('findings_by_severity', {{}}).get('critical', 0)

    if high_severity > 0:
        print(f"{{high_severity}} high or critical issues found. Commit blocked.")
        sys.exit(1)
    else:
        print(f"Review passed with {{summary.get('total_findings', 0)}} findings.")
else:
    print("No Python files staged for commit.")
"""
], capture_output=True, text=True)

if result.returncode != 0:
    print("DCAE review failed:")
    print(result.stderr)
    sys.exit(1)
else:
    print("DCAE review passed.")
    print(result.stdout)
''',
            "pre-push": f'''#!/usr/bin/env python3
import subprocess
import sys
import os

# Change to the git root directory
script_dir = os.path.dirname(os.path.abspath(__file__))
git_root = os.path.dirname(script_dir)
os.chdir(git_root)

print("Running comprehensive DCAE review before push...")

# Run comprehensive review
result = subprocess.run([
    sys.executable, "-c",
    f"""
import sys
sys.path.insert(0, '{os.path.join(git_root, 'src')}')
from dcae.unified_review import UnifiedReviewInterface

reviewer = UnifiedReviewInterface('{git_root}')
results = reviewer.run_comprehensive_review()

# Check for high/critical issues
summary = results.get('summary', {{}})
high_severity = summary.get('findings_by_severity', {{}}).get('high', 0) + \\
               summary.get('findings_by_severity', {{}}).get('critical', 0)

if high_severity > 0:
    print(f"{{high_severity}} high or critical issues found. Push blocked.")
    sys.exit(1)
else:
    print(f"Comprehensive review passed with {{summary.get('total_findings', 0)}} findings.")
"""
], capture_output=True, text=True)

if result.returncode != 0:
    print("DCAE review failed:")
    print(result.stderr)
    sys.exit(1)
else:
    print("DCAE review passed.")
    print(result.stdout)
'''
        }

        success = True
        for hook_type in hook_types:
            if hook_type in hook_scripts:
                hook_file = hooks_dir / hook_type
                try:
                    with open(hook_file, 'w') as f:
                        f.write(hook_scripts[hook_type])

                    # Make executable
                    hook_file.chmod(0o755)
                    print(f"Installed {hook_type} hook at {hook_file}")
                except Exception as e:
                    print(f"Failed to install {hook_type} hook: {e}")
                    success = False

        return success

    def integrate_with_editor(self, editor_type: str = "vscode") -> bool:
        """
        Integrate review mechanism with code editors/IDEs.

        Args:
            editor_type: Type of editor to integrate with (vscode, vim, etc.)

        Returns:
            True if integration was successful, False otherwise
        """
        if editor_type.lower() == "vscode":
            return self._setup_vscode_integration()
        elif editor_type.lower() == "vim":
            return self._setup_vim_integration()
        else:
            print(f"Editor {editor_type} integration not supported yet.")
            return False

    def _setup_vscode_integration(self) -> bool:
        """Set up VSCode integration."""
        vscode_dir = self.project_path / ".vscode"
        vscode_dir.mkdir(exist_ok=True)

        # Create settings.json for Python configuration
        settings_path = vscode_dir / "settings.json"
        settings = {
            "python.linting.enabled": True,
            "python.linting.pylintEnabled": False,
            "python.linting.flake8Enabled": False,
            "python.formatting.provider": "black",
            "python.analysis.typeCheckingMode": "basic"
        }

        # Add DCAE-specific settings if they don't exist
        if settings_path.exists():
            try:
                with open(settings_path, 'r') as f:
                    existing_settings = json.load(f)
                existing_settings.update(settings)
                settings = existing_settings
            except:
                pass

        with open(settings_path, 'w') as f:
            json.dump(settings, f, indent=2)

        # Create tasks.json for DCAE review tasks
        tasks_path = vscode_dir / "tasks.json"
        tasks = {
            "version": "2.0.0",
            "tasks": [
                {
                    "label": "DCAE Review Current File",
                    "type": "shell",
                    "command": "python",
                    "args": [
                        "-c",
                        f"from dcae.unified_review import UnifiedReviewInterface; reviewer = UnifiedReviewInterface('.'); results = reviewer.run_comprehensive_review(target_path='${{file}}'); print('Findings:', results.get('summary', {{}}).get('total_findings', 0))"
                    ],
                    "group": "build",
                    "presentation": {
                        "echo": True,
                        "reveal": "always",
                        "focus": False,
                        "panel": "shared"
                    },
                    "problemMatcher": []
                },
                {
                    "label": "DCAE Full Project Review",
                    "type": "shell",
                    "command": "python",
                    "args": [
                        "-c",
                        f"from dcae.unified_review import UnifiedReviewInterface; reviewer = UnifiedReviewInterface('.'); results = reviewer.run_comprehensive_review(); print('Findings:', results.get('summary', {{}}).get('total_findings', 0))"
                    ],
                    "group": "build",
                    "presentation": {
                        "echo": True,
                        "reveal": "always",
                        "focus": False,
                        "panel": "shared"
                    },
                    "problemMatcher": []
                }
            ]
        }

        with open(tasks_path, 'w') as f:
            json.dump(tasks, f, indent=2)

        # Create launch.json for debugging
        launch_path = vscode_dir / "launch.json"
        launch = {
            "version": "0.2.0",
            "configurations": [
                {
                    "name": "Python: DCAE Review",
                    "type": "python",
                    "request": "launch",
                    "program": "${workspaceFolder}/src/dcae/review_main.py",
                    "console": "integratedTerminal",
                    "args": ["review", "${file}"],
                    "cwd": "${workspaceFolder}"
                }
            ]
        }

        with open(launch_path, 'w') as f:
            json.dump(launch, f, indent=2)

        print(f"VSCode integration set up in {vscode_dir}")
        return True

    def _setup_vim_integration(self) -> bool:
        """Set up Vim integration."""
        # This is a placeholder - actual Vim integration would be more complex
        vim_config = f'''
" DCAE Review Integration
function! DCAEReviewCurrentFile()
    execute "!python -c \"from dcae.unified_review import UnifiedReviewInterface; reviewer = UnifiedReviewInterface('.'); results = reviewer.run_comprehensive_review(target_path='".expand('%:p')."'); print('Findings:', results.get('summary', {{}}).get('total_findings', 0))\""
endfunction

function! DCAEReviewProject()
    execute "!python -c \"from dcae.unified_review import UnifiedReviewInterface; reviewer = UnifiedReviewInterface('.'); results = reviewer.run_comprehensive_review(); print('Findings:', results.get('summary', {{}}).get('total_findings', 0))\""
endfunction

" Map keys for DCAE commands
nnoremap <leader>dr :call DCAEReviewCurrentFile()<CR>
nnoremap <leader>dR :call DCAEReviewProject()<CR>

" Show DCAE in status line
set statusline+=%{DCAEStatus()}
function! DCAEStatus()
    return ' DCAE'
endfunction
'''

        vimrc_path = self.project_path / ".vimrc"

        # Append to existing .vimrc or create new one
        mode = 'a' if vimrc_path.exists() else 'w'
        with open(vimrc_path, mode) as f:
            if mode == 'w':
                f.write('" DCAE Review Integration\n')
            f.write(vim_config)

        print(f"Vim integration added to {vimrc_path}")
        return True


class CIPipelineIntegrator:
    """Integrates review mechanism with CI/CD pipelines."""

    def __init__(self, project_path: str):
        self.project_path = Path(project_path)

    def setup_github_actions(self, workflow_name: str = "dcae-review") -> bool:
        """Set up GitHub Actions workflow."""
        github_dir = self.project_path / ".github" / "workflows"
        github_dir.mkdir(parents=True, exist_ok=True)

        workflow_file = github_dir / f"{workflow_name}.yml"

        workflow_content = f"""name: DCAE Code Review

on:
  push:
    branches: [ main, develop, feature/** ]
  pull_request:
    branches: [ main, develop ]

permissions:
  contents: read
  pull-requests: write

jobs:
  review:
    runs-on: ubuntu-latest

    steps:
    - name: Checkout code
      uses: actions/checkout@v4

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
        cache: 'pip'

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        if [ -f requirements.txt ]; then pip install -r requirements.txt; fi
        pip install dcae-framework  # Install DCAE if published, or add src to path

    - name: Run DCAE Review
      run: |
        python -c "
import sys
sys.path.insert(0, './src')
from dcae.unified_review import UnifiedReviewInterface

reviewer = UnifiedReviewInterface('.')
results = reviewer.run_comprehensive_review()

# Generate report
report_path = reviewer.generate_unified_report(results, output_format='text')
print(f'Review completed. Report saved to: {{report_path}}')

# Check for critical/high issues
summary = results.get('summary', {{}})
high_critical_count = (
    summary.get('findings_by_severity', {{}}).get('high', 0) +
    summary.get('findings_by_severity', {{}}).get('critical', 0)
)

if high_critical_count > 0:
    print(f'ERROR: {{high_critical_count}} high/critical issues found')
    sys.exit(1)
else:
    print(f'SUCCESS: {{summary.get(\"total_findings\", 0)}} issues found (all low/medium)')
"

    - name: Upload Review Report
      uses: actions/upload-artifact@v3
      if: always()
      with:
        name: dcae-review-report
        path: review_report_*.txt
        retention-days: 30
"""

        with open(workflow_file, 'w') as f:
            f.write(workflow_content)

        print(f"GitHub Actions workflow created at {workflow_file}")
        return True

    def setup_gitlab_ci(self) -> bool:
        """Set up GitLab CI configuration."""
        gitlab_ci_file = self.project_path / ".gitlab-ci.yml"

        gitlab_content = f"""stages:
  - review
  - test
  - deploy

variables:
  PYTHON_VERSION: "3.11"

.before_script_template:
  before_script:
    - apt-get update -qq && apt-get install -y -qq git python3 python3-pip
    - pip3 install --upgrade pip
    - if [ -f requirements.txt ]; then pip3 install -r requirements.txt; fi

dcae-review:
  stage: review
  extends: .before_script_template
  script:
    - |
      python3 -c "
      import sys
      sys.path.insert(0, './src')
      from dcae.unified_review import UnifiedReviewInterface

      reviewer = UnifiedReviewInterface('.')
      results = reviewer.run_comprehensive_review()

      # Generate report
      report_path = reviewer.generate_unified_report(results, output_format='text')
      print(f'Review completed. Report saved to: {{report_path}}')

      # Check for critical/high issues
      summary = results.get('summary', {{}})
      high_critical_count = (
          summary.get('findings_by_severity', {{}}).get('high', 0) +
          summary.get('findings_by_severity', {{}}).get('critical', 0)
      )

      if high_critical_count > 0:
          print(f'ERROR: {{high_critical_count}} high/critical issues found')
          exit(1)
      else:
          print(f'SUCCESS: {{summary.get(\"total_findings\", 0)}} issues found (all low/medium)')
      "
  artifacts:
    reports:
      dotenv: REVIEW_STATUS
    paths:
      - review_report_*.txt
    expire_in: 1 week
  only:
    - main
    - merge_requests
"""

        with open(gitlab_ci_file, 'w') as f:
            f.write(gitlab_content)

        print(f"GitLab CI configuration created at {gitlab_ci_file}")
        return True

    def setup_jenkins_pipeline(self) -> bool:
        """Set up Jenkins pipeline configuration."""
        jenkinsfile = self.project_path / "Jenkinsfile"

        jenkins_content = f"""pipeline {{
    agent any

    tools {{
        python 'Python311'  // Configure this tool in Jenkins
    }}

    stages {{
        stage('Checkout') {{
            steps {{
                checkout scm
            }}
        }}

        stage('Setup') {{
            steps {{
                sh 'python3 -m pip install --upgrade pip'
                sh 'if [ -f requirements.txt ]; then python3 -m pip install -r requirements.txt; fi'
            }}
        }}

        stage('DCAE Review') {{
            steps {{
                script {{
                    sh '''
                    python3 -c "
                    import sys
                    sys.path.insert(0, './src')
                    from dcae.unified_review import UnifiedReviewInterface

                    reviewer = UnifiedReviewInterface('.')
                    results = reviewer.run_comprehensive_review()

                    # Generate report
                    report_path = reviewer.generate_unified_report(results, output_format='text')
                    print(f'Review completed. Report saved to: {{report_path}}')

                    # Check for critical/high issues
                    summary = results.get('summary', {{}})
                    high_critical_count = (
                        summary.get('findings_by_severity', {{}}).get('high', 0) +
                        summary.get('findings_by_severity', {{}}).get('critical', 0)
                    )

                    if high_critical_count > 0:
                        print(f'ERROR: {{high_critical_count}} high/critical issues found')
                        exit(1)
                    else:
                        print(f'SUCCESS: {{summary.get(\"total_findings\", 0)}} issues found (all low/medium)')
                    "
                    '''
                }}
            }}
            post {{
                always {{
                    archiveArtifacts artifacts: 'review_report_*.txt', fingerprint: true
                }}
            }}
        }}

        stage('Tests') {{
            when {{
                not {{
                    anyOf {{
                        expression {{ env.CHANGE_TARGET != null }}  // Not a merge request
                        expression {{ currentBuild.result == 'SUCCESS' }}  // Previous stage passed
                    }}
                }}
            }}
            steps {{
                sh 'echo Running tests after successful review...'
                // Add your test steps here
            }}
        }}
    }}

    post {{
        always {{
            publishHTML([
                allowMissing: true,
                alwaysLinkToLastBuild: true,
                keepAll: true,
                reportDir: '.',
                reportFiles: 'review_report_*.html',
                reportName: 'DCAE Review Report'
            ])
        }}
        success {{
            echo 'Build and review successful!'
        }}
        failure {{
            echo 'Build or review failed!'
        }}
    }}
}}
"""

        with open(jenkinsfile, 'w') as f:
            f.write(jenkins_content)

        print(f"Jenkins pipeline configuration created at {jenkinsfile}")
        return True


class TeamCollaborationIntegrator:
    """Provides team collaboration features for the review mechanism."""

    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
        self.notifications_enabled = True

    def setup_notification_system(
        self,
        channels: List[str] = None,
        recipients: List[str] = None
    ) -> Dict[str, Any]:
        """
        Set up notification system for review results.

        Args:
            channels: List of notification channels (email, slack, discord, etc.)
            recipients: List of recipient addresses

        Returns:
            Configuration details
        """
        if channels is None:
            channels = ["console"]

        config = {
            "channels": channels,
            "recipients": recipients or [],
            "notification_triggers": [
                "review_complete",
                "high_severity_found",
                "critical_severity_found",
                "review_failed"
            ],
            "enabled": True
        }

        # Create notification configuration file
        config_dir = self.project_path / ".dcae" / "notifications"
        config_dir.mkdir(parents=True, exist_ok=True)

        config_file = config_dir / "config.json"
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)

        print(f"Notification system configured: {', '.join(channels)}")
        return config

    def create_issue_tracker_integration(
        self,
        tracker_type: str,
        config: Dict[str, Any]
    ) -> bool:
        """
        Integrate with issue trackers like Jira, GitHub Issues, etc.

        Args:
            tracker_type: Type of issue tracker (jira, github_issues, etc.)
            config: Configuration for the issue tracker connection

        Returns:
            True if integration was successful, False otherwise
        """
        integration_file = self.project_path / ".dcae" / "integrations" / f"{tracker_type}_config.json"
        integration_file.parent.mkdir(parents=True, exist_ok=True)

        with open(integration_file, 'w') as f:
            json.dump(config, f, indent=2)

        print(f"Issue tracker integration set up for {tracker_type}")
        return True

    def generate_collaboration_report(
        self,
        results: Dict[str, Any],
        output_format: str = "markdown"
    ) -> str:
        """
        Generate a collaboration-friendly report from review results.

        Args:
            results: Review results to include in the report
            output_format: Format for the report (markdown, html, json)

        Returns:
            Path to the generated report
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_filename = f"dcae_collaboration_report_{timestamp}.{output_format}"
        report_path = self.project_path / report_filename

        if output_format == "markdown":
            report_content = self._generate_markdown_report(results)
        elif output_format == "html":
            report_content = self._generate_html_report(results)
        elif output_format == "json":
            report_content = json.dumps(results, indent=2, default=str)
        else:
            raise ValueError(f"Unsupported output format: {output_format}")

        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report_content)

        return str(report_path)

    def _generate_markdown_report(self, results: Dict[str, Any]) -> str:
        """Generate a markdown report for collaboration."""
        summary = results.get("summary", {})

        markdown = f"""# DCAE Review Report

**Review Session:** {results.get('review_timestamp', 'N/A')}
**Project:** {results.get('project_path', 'N/A')}
**Target:** {results.get('target_path', 'Entire project')}

## Executive Summary

- **Total Findings:** {summary.get('total_findings', 0)}
- **Overall Score:** {summary.get('overall_score', 0)}/100
- **Review Duration:** {results.get('duration', 'N/A')} seconds

## Findings Summary

### By Severity
"""

        for severity, count in summary.get("findings_by_severity", {}).items():
            markdown += f"- {severity.title()}: {count}\n"

        markdown += "\n### By Category\n"
        for category, count in summary.get("findings_by_category", {}).items():
            markdown += f"- {category.replace('_', ' ').title()}: {count}\n"

        markdown += f"""

## Detailed Findings

Found {len(results.get('findings', []))} specific issues that need attention:

> **Note:** For detailed information about each finding, including specific file locations and recommendations, please see the full technical report.

## Recommendations

Based on this review, the following actions are recommended:

1. Address all HIGH and CRITICAL severity issues before merging/deployment
2. Consider improvements for MEDIUM severity issues
3. Review LOW severity issues for potential future enhancements

## Next Steps

- Review the full report for detailed findings
- Assign issues to appropriate team members
- Plan remediation timeline
- Re-run review after fixes are implemented
"""

        return markdown

    def _generate_html_report(self, results: Dict[str, Any]) -> str:
        """Generate an HTML report for collaboration."""
        summary = results.get("summary", {})

        html = f"""<!DOCTYPE html>
<html>
<head>
    <title>DCAE Review Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; background-color: #f5f5f5; }}
        .container {{ max-width: 800px; margin: 0 auto; background-color: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        h1 {{ color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px; }}
        h2 {{ color: #34495e; margin-top: 30px; }}
        .summary-card {{ background-color: #ecf0f1; padding: 15px; border-radius: 5px; margin: 10px 0; }}
        .metric {{ display: inline-block; margin-right: 20px; }}
        .metric-value {{ font-size: 1.5em; font-weight: bold; color: #2980b9; }}
        .metric-label {{ font-size: 0.9em; color: #7f8c8d; }}
        .severity-high {{ color: #e74c3c; }}
        .severity-medium {{ color: #f39c12; }}
        .severity-low {{ color: #27ae60; }}
        ul {{ margin: 10px 0; padding-left: 20px; }}
        li {{ margin: 5px 0; }}
        .recommendations {{ background-color: #fff3cd; border-left: 4px solid #ffc107; padding: 15px; margin: 20px 0; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>DCAE Review Report</h1>

        <div class="summary-card">
            <h3>Review Information</h3>
            <p><strong>Review Session:</strong> {results.get('review_timestamp', 'N/A')}</p>
            <p><strong>Project:</strong> {results.get('project_path', 'N/A')}</p>
            <p><strong>Target:</strong> {results.get('target_path', 'Entire project')}</p>
        </div>

        <h2>Executive Summary</h2>
        <div class="summary-card">
            <div class="metric">
                <div class="metric-value">{summary.get('total_findings', 0)}</div>
                <div class="metric-label">Total Findings</div>
            </div>
            <div class="metric">
                <div class="metric-value">{summary.get('overall_score', 0)}/100</div>
                <div class="metric-label">Overall Score</div>
            </div>
            <div class="metric">
                <div class="metric-value">{results.get('duration', 'N/A')}s</div>
                <div class="metric-label">Duration</div>
            </div>
        </div>

        <h2>Findings Breakdown</h2>
        <h3>By Severity</h3>
        <ul>
"""

        for severity, count in summary.get("findings_by_severity", {}).items():
            css_class = f"severity-{severity.lower()}" if severity.lower() in ['high', 'medium', 'low'] else ""
            html += f'            <li class="{css_class}">{severity.title()}: {count}</li>\n'

        html += "        </ul>"
        html += "        <h3>By Category</h3>\n        <ul>\n"

        for category, count in summary.get("findings_by_category", {}).items():
            html += f'            <li>{category.replace("_", " ").title()}: {count}</li>\n'

        html += f"""        </ul>

        <h2>Findings Details</h2>
        <p>Found {len(results.get('findings', []))} specific issues that need attention.</p>

        <div class="recommendations">
            <h3>Recommendations</h3>
            <ol>
                <li>Address all HIGH and CRITICAL severity issues before merging/deployment</li>
                <li>Consider improvements for MEDIUM severity issues</li>
                <li>Review LOW severity issues for potential future enhancements</li>
            </ol>
        </div>

        <h2>Next Steps</h2>
        <ol>
            <li>Review the full technical report for detailed findings</li>
            <li>Assign issues to appropriate team members</li>
            <li>Plan remediation timeline</li>
            <li>Re-run review after fixes are implemented</li>
        </ol>

        <footer style="margin-top: 40px; padding-top: 20px; border-top: 1px solid #eee; color: #7f8c8d; font-size: 0.9em;">
            <p>Generated by DCAE Review Mechanism</p>
        </footer>
    </div>
</body>
</html>
"""
        return html


def main():
    """Example usage of the workflow integration components."""
    import tempfile

    # Create a temporary project for demonstration
    with tempfile.TemporaryDirectory() as temp_dir:
        project_path = Path(temp_dir) / "test_project"
        project_path.mkdir()

        print("DCAE Review & Quality Assurance - Workflow Integration")
        print("="*70)

        # Initialize the integrators
        dev_workflow_integrator = DevelopmentWorkflowIntegrator(str(project_path))
        ci_integrator = CIPipelineIntegrator(str(project_path))
        collab_integrator = TeamCollaborationIntegrator(str(project_path))

        # Simulate some review results for demonstration
        sample_results = {
            "summary": {
                "total_findings": 15,
                "overall_score": 78,
                "findings_by_severity": {
                    "critical": 1,
                    "high": 2,
                    "medium": 5,
                    "low": 7
                },
                "findings_by_category": {
                    "security": 3,
                    "performance": 4,
                    "code_quality": 5,
                    "best_practices": 3
                }
            },
            "review_timestamp": datetime.now().isoformat(),
            "project_path": str(project_path),
            "target_path": "src/",
            "duration": 45.3
        }

        # Development workflow integration
        print("Setting up development workflow integration...")

        # Since this is a temp directory without git, we'll just show what would happen
        print("  - Git hooks integration: Would install pre-commit and pre-push hooks")
        print("  - Editor integration: Setting up VSCode tasks and settings...")
        dev_workflow_integrator._setup_vscode_integration()

        # CI/CD pipeline integration
        print("\nSetting up CI/CD pipeline integration...")
        print("  - GitHub Actions: Creating workflow file...")
        ci_integrator.setup_github_actions()

        print("  - GitLab CI: Creating configuration...")
        ci_integrator.setup_gitlab_ci()

        print("  - Jenkins: Creating pipeline configuration...")
        ci_integrator.setup_jenkins_pipeline()

        # Team collaboration features
        print("\nSetting up team collaboration features...")

        # Notification system setup
        print("  - Notification system: Configuring...")
        collab_integrator.setup_notification_system(
            channels=["console", "email"],
            recipients=["team@example.com"]
        )

        # Generate collaboration reports
        print("  - Generating collaboration reports...")
        md_report = collab_integrator.generate_collaboration_report(sample_results, "markdown")
        html_report = collab_integrator.generate_collaboration_report(sample_results, "html")

        print(f"    Markdown report: {md_report}")
        print(f"    HTML report: {html_report}")

        print("\nWorkflow integration setup completed!")


if __name__ == "__main__":
    main()