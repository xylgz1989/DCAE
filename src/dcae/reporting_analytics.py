"""
Reporting and Analytics Module

This module implements unified reporting, dashboard interface, trend analysis,
and historical tracking for the DCAE review mechanism.
"""
from typing import Dict, Any, List, Optional, Union
from pathlib import Path
import json
import csv
from datetime import datetime, timedelta
from dataclasses import dataclass
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from io import StringIO


@dataclass
class ReviewSnapshot:
    """Captures the state of a review at a specific point in time."""
    timestamp: datetime
    project_path: str
    target_path: str
    total_findings: int
    findings_by_severity: Dict[str, int]
    findings_by_category: Dict[str, int]
    overall_score: float
    review_duration: float
    metadata: Dict[str, Any]


class HistoricalReviewTracker:
    """Tracks historical review data for trend analysis."""

    def __init__(self, db_path: str = None):
        if db_path:
            self.db_path = Path(db_path)
        else:
            self.db_path = Path.home() / ".dcae" / "review_history.db"

        # Ensure directory exists
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        self._initialize_database()

    def _initialize_database(self) -> None:
        """Initialize the database with required tables."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Create reviews table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS reviews (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                project_path TEXT,
                target_path TEXT,
                total_findings INTEGER,
                findings_by_severity TEXT,
                findings_by_category TEXT,
                overall_score REAL,
                review_duration REAL,
                metadata TEXT
            )
        """)

        conn.commit()
        conn.close()

    def save_review_snapshot(self, snapshot: ReviewSnapshot) -> bool:
        """Save a review snapshot to the database."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO reviews (
                    timestamp, project_path, target_path, total_findings,
                    findings_by_severity, findings_by_category, overall_score,
                    review_duration, metadata
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                snapshot.timestamp.isoformat(),
                snapshot.project_path,
                snapshot.target_path,
                snapshot.total_findings,
                json.dumps(snapshot.findings_by_severity),
                json.dumps(snapshot.findings_by_category),
                snapshot.overall_score,
                snapshot.review_duration,
                json.dumps(snapshot.metadata)
            ))

            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error saving review snapshot: {e}")
            return False

    def get_historical_data(
        self,
        project_path: Optional[str] = None,
        days_back: int = 30
    ) -> List[ReviewSnapshot]:
        """Retrieve historical review data."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Calculate date threshold
        threshold_date = (datetime.now() - timedelta(days=days_back)).isoformat()

        # Build query
        query = """
            SELECT timestamp, project_path, target_path, total_findings,
                   findings_by_severity, findings_by_category, overall_score,
                   review_duration, metadata
            FROM reviews
            WHERE timestamp >= ?
        """
        params = [threshold_date]

        if project_path:
            query += " AND project_path = ?"
            params.append(project_path)

        query += " ORDER BY timestamp DESC"

        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()

        snapshots = []
        for row in rows:
            try:
                timestamp = datetime.fromisoformat(row[0])
                snapshot = ReviewSnapshot(
                    timestamp=timestamp,
                    project_path=row[1],
                    target_path=row[2],
                    total_findings=row[3],
                    findings_by_severity=json.loads(row[4]),
                    findings_by_category=json.loads(row[5]),
                    overall_score=row[6],
                    review_duration=row[7],
                    metadata=json.loads(row[8])
                )
                snapshots.append(snapshot)
            except Exception as e:
                print(f"Error parsing historical data row: {e}")

        return snapshots

    def get_trend_data(
        self,
        project_path: Optional[str] = None,
        days_back: int = 30
    ) -> Dict[str, Any]:
        """Get trend data for analysis."""
        historical_data = self.get_historical_data(project_path, days_back)

        # Organize data by date for trends
        dates = []
        total_findings = []
        overall_scores = []
        severity_breakdown = {}

        for snapshot in historical_data:
            dates.append(snapshot.timestamp.date().isoformat())
            total_findings.append(snapshot.total_findings)
            overall_scores.append(snapshot.overall_score)

            # Track severity trends
            for severity, count in snapshot.findings_by_severity.items():
                if severity not in severity_breakdown:
                    severity_breakdown[severity] = []
                severity_breakdown[severity].append(count)

        trend_data = {
            "dates": dates,
            "total_findings": total_findings,
            "overall_scores": overall_scores,
            "severity_trends": severity_breakdown,
            "average_total_findings": sum(total_findings) / len(total_findings) if total_findings else 0,
            "average_overall_score": sum(overall_scores) / len(overall_scores) if overall_scores else 0,
            "total_snapshots": len(historical_data)
        }

        return trend_data


class DashboardGenerator:
    """Generates visual dashboards for review analytics."""

    def __init__(self, historical_tracker: HistoricalReviewTracker):
        self.historical_tracker = historical_tracker

    def generate_overall_dashboard(
        self,
        project_path: Optional[str] = None,
        days_back: int = 30,
        output_path: str = "review_dashboard.html"
    ) -> str:
        """Generate an overall dashboard with multiple visualizations."""
        trend_data = self.historical_tracker.get_trend_data(project_path, days_back)

        # Generate the HTML content for the dashboard
        html_content = self._create_dashboard_html(trend_data, days_back)

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)

        return output_path

    def _create_dashboard_html(self, trend_data: Dict[str, Any], days_back: int) -> str:
        """Create HTML content for the dashboard."""
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>DCAE Review Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5; }}
        .dashboard-container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .header {{ text-align: center; margin-bottom: 30px; }}
        .metrics-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 30px; }}
        .metric-card {{ background: #f8f9fa; border-radius: 8px; padding: 15px; text-align: center; border-left: 4px solid #007bff; }}
        .metric-value {{ font-size: 2em; font-weight: bold; color: #007bff; }}
        .metric-label {{ color: #6c757d; }}
        .chart-container {{ background: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }}
        .chart-title {{ margin-bottom: 15px; font-weight: bold; }}
        .trend-summary {{ background: #e7f3ff; padding: 15px; border-radius: 8px; margin-top: 20px; }}
    </style>
</head>
<body>
    <div class="dashboard-container">
        <div class="header">
            <h1>DCAE Review Dashboard</h1>
            <p>Last {days_back} days overview</p>
        </div>

        <div class="metrics-grid">
            <div class="metric-card">
                <div class="metric-value">{trend_data.get('total_snapshots', 0)}</div>
                <div class="metric-label">Reviews Conducted</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{trend_data.get('average_total_findings', 0):.1f}</div>
                <div class="metric-label">Avg. Findings per Review</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{trend_data.get('average_overall_score', 0):.1f}/100</div>
                <div class="metric-label">Avg. Quality Score</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{len(trend_data.get('dates', []))}</div>
                <div class="metric-label">Days Tracked</div>
            </div>
        </div>

        <div class="chart-container">
            <div class="chart-title">Total Findings Over Time</div>
            <canvas id="findingsChart" width="400" height="200"></canvas>
        </div>

        <div class="chart-container">
            <div class="chart-title">Quality Score Over Time</div>
            <canvas id="scoreChart" width="400" height="200"></canvas>
        </div>

        <div class="chart-container">
            <div class="chart-title">Severity Trends</div>
            <canvas id="severityChart" width="400" height="200"></canvas>
        </div>

        <div class="trend-summary">
            <h3>Trend Analysis</h3>
            <p>
"""

        # Add trend analysis text
        if trend_data.get('overall_scores'):
            recent_scores = trend_data['overall_scores'][-5:] if len(trend_data['overall_scores']) >= 5 else trend_data['overall_scores']
            avg_recent = sum(recent_scores) / len(recent_scores)

            initial_scores = trend_data['overall_scores'][:5] if len(trend_data['overall_scores']) >= 5 else trend_data['overall_scores']
            avg_initial = sum(initial_scores) / len(initial_scores)

            if avg_recent > avg_initial:
                html += f"Quality scores have <span style='color: green; font-weight: bold;'>improved</span> by {avg_recent - avg_initial:.1f} points on average in recent reviews."
            elif avg_recent < avg_initial:
                html += f"Quality scores have <span style='color: red; font-weight: bold;'>declined</span> by {avg_initial - avg_recent:.1f} points on average in recent reviews."
            else:
                html += "Quality scores have remained relatively stable."

        html += """
            </p>
        </div>
    </div>

    <script>
        // Chart for total findings
        const findingsCtx = document.getElementById('findingsChart').getContext('2d');
        new Chart(findingsCtx, {
            type: 'line',
            data: {
                labels: """ + json.dumps(trend_data.get('dates', [])) + """,
                datasets: [{
                    label: 'Total Findings',
                    data: """ + json.dumps(trend_data.get('total_findings', [])) + """,
                    borderColor: 'rgb(255, 99, 132)',
                    backgroundColor: 'rgba(255, 99, 132, 0.2)',
                    tension: 0.1
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    title: {
                        display: true,
                        text: 'Total Findings Over Time'
                    }
                }
            }
        });

        // Chart for quality scores
        const scoreCtx = document.getElementById('scoreChart').getContext('2d');
        new Chart(scoreCtx, {
            type: 'line',
            data: {
                labels: """ + json.dumps(trend_data.get('dates', [])) + """,
                datasets: [{
                    label: 'Quality Score',
                    data: """ + json.dumps(trend_data.get('overall_scores', [])) + """,
                    borderColor: 'rgb(54, 162, 235)',
                    backgroundColor: 'rgba(54, 162, 235, 0.2)',
                    tension: 0.1
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    title: {
                        display: true,
                        text: 'Quality Score Over Time'
                    }
                }
            }
        });

        // Chart for severity trends
        const severityCtx = document.getElementById('severityChart').getContext('2d');
        const severityData = """ + json.dumps(trend_data.get('severity_trends', {})) + """;

        const severityDatasets = [];
        const colors = [
            'rgba(255, 99, 132, 0.2)',   // Red
            'rgba(255, 159, 64, 0.2)',   // Orange
            'rgba(255, 205, 86, 0.2)',   // Yellow
            'rgba(75, 192, 192, 0.2)',   // Green
            'rgba(54, 162, 235, 0.2)'    // Blue
        ];

        const borderColor = [
            'rgb(255, 99, 132)',
            'rgb(255, 159, 64)',
            'rgb(255, 205, 86)',
            'rgb(75, 192, 192)',
            'rgb(54, 162, 235)'
        ];

        let colorIndex = 0;
        for (const [severity, values] of Object.entries(severityData)) {
            severityDatasets.push({
                label: severity.charAt(0).toUpperCase() + severity.slice(1),
                data: values,
                borderColor: borderColor[colorIndex % borderColor.length],
                backgroundColor: colors[colorIndex % colors.length],
                tension: 0.1
            });
            colorIndex++;
        }

        new Chart(severityCtx, {
            type: 'line',
            data: {
                labels: """ + json.dumps(trend_data.get('dates', [])) + """,
                datasets: severityDatasets
            },
            options: {
                responsive: true,
                plugins: {
                    title: {
                        display: true,
                        text: 'Severity Trends Over Time'
                    }
                }
            }
        });
    </script>
</body>
</html>
"""

        return html

    def generate_detailed_report(
        self,
        project_path: Optional[str] = None,
        days_back: int = 30,
        output_path: str = "detailed_report.html"
    ) -> str:
        """Generate a detailed analytical report."""
        historical_data = self.historical_tracker.get_historical_data(project_path, days_back)

        if not historical_data:
            return ""

        # Generate report content
        report_html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Detailed Review Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .header {{ background-color: #f0f0f0; padding: 15px; border-radius: 5px; }}
        .section {{ margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }}
        table {{ border-collapse: collapse; width: 100%; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #f2f2f2; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Detailed Review Report</h1>
        <p>Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        <p>Period: Last {days_back} days</p>
    </div>

    <div class="section">
        <h2>Review Statistics</h2>
        <p>Total Reviews: {len(historical_data)}</p>
        <p>Average Findings per Review: {sum(s.total_findings for s in historical_data) / len(historical_data):.2f}</p>
        <p>Average Quality Score: {sum(s.overall_score for s in historical_data) / len(historical_data):.2f}/100</p>
    </div>

    <div class="section">
        <h2>Detailed Review History</h2>
        <table>
            <tr><th>Date</th><th>Target</th><th>Findings</th><th>Score</th><th>Duration</th></tr>
        """

        for snapshot in historical_data:
            report_html += f"""
            <tr>
                <td>{snapshot.timestamp.strftime('%Y-%m-%d %H:%M')}</td>
                <td>{snapshot.target_path}</td>
                <td>{snapshot.total_findings}</td>
                <td>{snapshot.overall_score:.1f}</td>
                <td>{snapshot.review_duration:.2f}s</td>
            </tr>
            """

        report_html += """
        </table>
    </div>

    <div class="section">
        <h2>Findings Breakdown by Category</h2>
        """

        # Aggregate category data across all snapshots
        category_totals = {}
        for snapshot in historical_data:
            for category, count in snapshot.findings_by_category.items():
                if category not in category_totals:
                    category_totals[category] = 0
                category_totals[category] += count

        report_html += "<ul>"
        for category, total in category_totals.items():
            report_html += f"<li>{category.replace('_', ' ').title()}: {total}</li>"
        report_html += "</ul>"

        report_html += """
    </div>
</body>
</html>
        """

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(report_html)

        return output_path


class UnifiedReportingSystem:
    """Unified system for all reporting needs."""

    def __init__(self, historical_tracker: HistoricalReviewTracker):
        self.historical_tracker = historical_tracker
        self.dashboard_generator = DashboardGenerator(historical_tracker)

    def generate_current_report(
        self,
        review_results: Dict[str, Any],
        report_formats: List[str] = None,
        output_dir: str = None
    ) -> Dict[str, str]:
        """
        Generate reports for the current review results.

        Args:
            review_results: Results from the current review
            report_formats: List of formats to generate (html, json, csv, txt)
            output_dir: Directory to save reports

        Returns:
            Dictionary mapping format to file path
        """
        if report_formats is None:
            report_formats = ["html", "json"]

        if output_dir is None:
            output_dir = Path.cwd()
        else:
            output_dir = Path(output_dir)

        output_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        outputs = {}

        for fmt in report_formats:
            if fmt == "html":
                file_path = output_dir / f"review_report_{timestamp}.html"
                self._generate_html_report(review_results, str(file_path))
                outputs[fmt] = str(file_path)
            elif fmt == "json":
                file_path = output_dir / f"review_report_{timestamp}.json"
                self._generate_json_report(review_results, str(file_path))
                outputs[fmt] = str(file_path)
            elif fmt == "csv":
                file_path = output_dir / f"review_report_{timestamp}.csv"
                self._generate_csv_report(review_results, str(file_path))
                outputs[fmt] = str(file_path)
            elif fmt == "txt":
                file_path = output_dir / f"review_report_{timestamp}.txt"
                self._generate_txt_report(review_results, str(file_path))
                outputs[fmt] = str(file_path)

        return outputs

    def _generate_html_report(self, results: Dict[str, Any], output_path: str) -> None:
        """Generate HTML report."""
        summary = results.get("summary", {})
        findings = results.get("findings", [])

        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>DCAE Review Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .header {{ background-color: #f0f0f0; padding: 15px; border-radius: 5px; }}
        .summary {{ background-color: #e6f3ff; padding: 15px; margin: 10px 0; border-left: 4px solid #007acc; }}
        .finding {{ border: 1px solid #ccc; margin: 10px 0; padding: 10px; border-radius: 5px; }}
        .severity-high {{ border-left: 5px solid #dc3545; }}
        .severity-medium {{ border-left: 5px solid #fd7e14; }}
        .severity-low {{ border-left: 5px solid #28a745; }}
        .severity-info {{ border-left: 5px solid #17a2b8; }}
        .severity-critical {{ border-left: 5px solid #6f42c1; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>DCAE Review Report</h1>
        <p><strong>Generated at:</strong> {results.get('review_timestamp', datetime.now().isoformat())}</p>
        <p><strong>Project:</strong> {results.get('project_path', 'Unknown')}</p>
        <p><strong>Target:</strong> {results.get('target_path', 'Entire project')}</p>
    </div>

    <div class="summary">
        <h2>Review Summary</h2>
        <p><strong>Total Findings:</strong> {summary.get('total_findings', 0)}</p>
        <p><strong>Overall Score:</strong> {summary.get('overall_score', 0)}/100</p>
        <p><strong>Duration:</strong> {results.get('duration', 'Unknown')} seconds</p>
    </div>

    <h2>Findings by Severity</h2>
    <ul>
        {"".join([f'<li><strong>{sev.title()}:</strong> {count}</li>' for sev, count in summary.get('findings_by_severity', {}).items()])}
    </ul>

    <h2>Findings by Category</h2>
    <ul>
        {"".join([f'<li><strong>{cat.replace("_", " ").title()}:</strong> {count}</li>' for cat, count in summary.get('findings_by_category', {}).items()])}
    </ul>

    <h2>Detailed Findings</h2>
    {"".join([
        f'''
        <div class="finding severity-{getattr(f, "severity", "info").lower()}">
            <p><strong>Module:</strong> {getattr(f, "module", "Unknown")}</p>
            <p><strong>Category:</strong> {getattr(f, "category", "Unknown")}</p>
            <p><strong>Severity:</strong> {getattr(f, "severity", "info").title()}</p>
            <p><strong>File:</strong> {getattr(f, "file_path", "Unknown")}:{getattr(f, "line_number", 0)}</p>
            <p><strong>Issue:</strong> {getattr(f, "issue_description", "No description")}</p>
            <p><strong>Recommendation:</strong> {getattr(f, "recommendation", "No recommendation")}</p>
            <pre>{getattr(f, "code_snippet", "")}</pre>
        </div>
        ''' for f in findings
    ])}
</body>
</html>
        """

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)

    def _generate_json_report(self, results: Dict[str, Any], output_path: str) -> None:
        """Generate JSON report."""
        # Create a simplified version of results for JSON serialization
        serializable_results = self._make_serializable(results)

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(serializable_results, f, indent=2, default=str)

    def _make_serializable(self, obj):
        """Recursively convert objects to be JSON serializable."""
        if hasattr(obj, '__dict__'):
            # Convert objects to dictionaries
            result = {key: self._make_serializable(value) for key, value in obj.__dict__.items()}
            result['_type'] = obj.__class__.__name__
            return result
        elif isinstance(obj, list):
            return [self._make_serializable(item) for item in obj]
        elif isinstance(obj, dict):
            return {key: self._make_serializable(value) for key, value in obj.items()}
        elif isinstance(obj, (datetime,)):
            return obj.isoformat()
        else:
            return obj

    def _generate_csv_report(self, results: Dict[str, Any], output_path: str) -> None:
        """Generate CSV report of findings."""
        findings = results.get("findings", [])

        if not findings:
            # Create empty CSV with headers
            with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(["Module", "Category", "Severity", "File", "Line", "Issue", "Recommendation"])
        else:
            with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(["Module", "Category", "Severity", "File", "Line", "Issue", "Recommendation"])

                for finding in findings:
                    writer.writerow([
                        getattr(finding, "module", ""),
                        getattr(finding, "category", ""),
                        getattr(finding, "severity", ""),
                        getattr(finding, "file_path", ""),
                        getattr(finding, "line_number", ""),
                        getattr(finding, "issue_description", ""),
                        getattr(finding, "recommendation", "")
                    ])

    def _generate_txt_report(self, results: Dict[str, Any], output_path: str) -> None:
        """Generate plain text report."""
        summary = results.get("summary", {})
        findings = results.get("findings", [])

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("DCAE Review Report\n")
            f.write("=" * 50 + "\n")
            f.write(f"Generated at: {results.get('review_timestamp', datetime.now().isoformat())}\n")
            f.write(f"Project: {results.get('project_path', 'Unknown')}\n")
            f.write(f"Target: {results.get('target_path', 'Entire project')}\n\n")

            f.write("SUMMARY\n")
            f.write("-" * 15 + "\n")
            f.write(f"Total Findings: {summary.get('total_findings', 0)}\n")
            f.write(f"Overall Score: {summary.get('overall_score', 0)}/100\n")
            f.write(f"Duration: {results.get('duration', 'Unknown')} seconds\n\n")

            f.write("Findings by Severity:\n")
            for sev, count in summary.get('findings_by_severity', {}).items():
                f.write(f"  {sev.title()}: {count}\n")

            f.write("\nFindings by Category:\n")
            for cat, count in summary.get('findings_by_category', {}).items():
                f.write(f"  {cat.replace('_', ' ').title()}: {count}\n")

            f.write(f"\nDETAILED FINDINGS ({len(findings)} total)\n")
            f.write("-" * 30 + "\n")

            for i, finding in enumerate(findings, 1):
                f.write(f"{i}. Module: {getattr(finding, 'module', 'Unknown')}\n")
                f.write(f"   Category: {getattr(finding, 'category', 'Unknown')}\n")
                f.write(f"   Severity: {getattr(finding, 'severity', 'info').title()}\n")
                f.write(f"   Location: {getattr(finding, 'file_path', 'Unknown')}:{getattr(finding, 'line_number', 0)}\n")
                f.write(f"   Issue: {getattr(finding, 'issue_description', 'No description')}\n")
                f.write(f"   Recommendation: {getattr(finding, 'recommendation', 'No recommendation')}\n")
                if hasattr(finding, 'code_snippet') and getattr(finding, 'code_snippet'):
                    f.write(f"   Code: {getattr(finding, 'code_snippet', '')[:100]}...\n")
                f.write("\n")


def main():
    """Example usage of the reporting and analytics system."""
    import tempfile

    # Create a temporary directory for demonstration
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        print("DCAE Review & Quality Assurance - Reporting and Analytics")
        print("="*70)

        # Initialize the historical tracker
        tracker = HistoricalReviewTracker(str(temp_path / "review_history.db"))

        # Create some sample historical data
        sample_snapshots = [
            ReviewSnapshot(
                timestamp=datetime.now() - timedelta(days=7),
                project_path="/home/user/project",
                target_path="src/",
                total_findings=25,
                findings_by_severity={"critical": 1, "high": 3, "medium": 8, "low": 13},
                findings_by_category={"security": 5, "performance": 7, "code_quality": 8, "best_practices": 5},
                overall_score=75.0,
                review_duration=45.2,
                metadata={"review_type": "full_project"}
            ),
            ReviewSnapshot(
                timestamp=datetime.now() - timedelta(days=5),
                project_path="/home/user/project",
                target_path="src/",
                total_findings=22,
                findings_by_severity={"critical": 0, "high": 2, "medium": 7, "low": 13},
                findings_by_category={"security": 4, "performance": 6, "code_quality": 7, "best_practices": 5},
                overall_score=78.0,
                review_duration=42.1,
                metadata={"review_type": "full_project"}
            ),
            ReviewSnapshot(
                timestamp=datetime.now() - timedelta(days=3),
                project_path="/home/user/project",
                target_path="src/",
                total_findings=18,
                findings_by_severity={"critical": 0, "high": 1, "medium": 5, "low": 12},
                findings_by_category={"security": 3, "performance": 4, "code_quality": 6, "best_practices": 5},
                overall_score=82.0,
                review_duration=38.5,
                metadata={"review_type": "full_project"}
            ),
            ReviewSnapshot(
                timestamp=datetime.now(),
                project_path="/home/user/project",
                target_path="src/",
                total_findings=15,
                findings_by_severity={"critical": 0, "high": 1, "medium": 4, "low": 10},
                findings_by_category={"security": 2, "performance": 3, "code_quality": 5, "best_practices": 5},
                overall_score=85.0,
                review_duration=35.0,
                metadata={"review_type": "full_project"}
            )
        ]

        # Save snapshots to history
        for snapshot in sample_snapshots:
            tracker.save_review_snapshot(snapshot)

        print(f"Saved {len(sample_snapshots)} historical review snapshots")

        # Initialize the reporting system
        reporting_system = UnifiedReportingSystem(tracker)
        dashboard_gen = DashboardGenerator(tracker)

        # Simulate current review results for report generation
        current_results = {
            "summary": {
                "total_findings": 15,
                "overall_score": 85.0,
                "findings_by_severity": {
                    "critical": 0,
                    "high": 1,
                    "medium": 4,
                    "low": 10
                },
                "findings_by_category": {
                    "security": 2,
                    "performance": 3,
                    "code_quality": 5,
                    "best_practices": 5
                }
            },
            "review_timestamp": datetime.now().isoformat(),
            "project_path": "/home/user/project",
            "target_path": "src/",
            "duration": 35.0
        }

        # Generate various reports
        print("\nGenerating reports...")
        report_outputs = reporting_system.generate_current_report(
            current_results,
            report_formats=["html", "json", "txt"],
            output_dir=temp_path
        )

        for fmt, path in report_outputs.items():
            print(f"  {fmt.upper()} report: {path}")

        # Generate dashboard
        print("\nGenerating dashboard...")
        dashboard_path = dashboard_gen.generate_overall_dashboard(
            project_path="/home/user/project",
            days_back=30,
            output_path=str(temp_path / "dashboard.html")
        )
        print(f"  Dashboard: {dashboard_path}")

        # Generate detailed report
        print("\nGenerating detailed report...")
        detailed_report_path = dashboard_gen.generate_detailed_report(
            project_path="/home/user/project",
            days_back=30,
            output_path=str(temp_path / "detailed_report.html")
        )
        print(f"  Detailed report: {detailed_report_path}")

        # Show trend analysis
        print("\nTrend Analysis:")
        trend_data = tracker.get_trend_data("/home/user/project", 30)
        print(f"  - Number of reviews tracked: {trend_data.get('total_snapshots', 0)}")
        print(f"  - Average findings per review: {trend_data.get('average_total_findings', 0):.1f}")
        print(f"  - Average quality score: {trend_data.get('average_overall_score', 0):.1f}/100")

        if trend_data.get('overall_scores'):
            recent_improvement = trend_data['overall_scores'][-1] - trend_data['overall_scores'][0]
            print(f"  - Quality trend: {'Improvement' if recent_improvement > 0 else 'Decline'} of {abs(recent_improvement):.1f} points")

        print("\nReporting and analytics system demonstrated successfully!")


if __name__ == "__main__":
    main()