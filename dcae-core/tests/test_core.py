"""Tests for DCAE core framework."""

import pytest
from pathlib import Path
import tempfile
import shutil

from dcae import DCAEFramework, DCAEResult


class TestDCAEResult:
    """Test DCAEResult dataclass."""

    def test_result_creation(self):
        """Test creating a DCAEResult."""
        result = DCAEResult(
            status="success",
            phase="design",
            timestamp="2026-03-22T00:00:00"
        )
        assert result.status == "success"
        assert result.phase == "design"
        assert result.artifacts == []
        assert result.recommendations == []

    def test_result_to_dict(self):
        """Test converting result to dictionary."""
        result = DCAEResult(
            status="success",
            phase="code",
            timestamp="2026-03-22T00:00:00",
            tests_total=5,
            tests_passed=5
        )
        result_dict = result.to_dict()
        assert result_dict["status"] == "success"
        assert result_dict["tests_total"] == 5

    def test_success_rate(self):
        """Test success rate calculation."""
        result = DCAEResult(
            status="success",
            phase="test",
            timestamp="2026-03-22T00:00:00",
            tests_total=10,
            tests_passed=8
        )
        assert result.success_rate == 80.0

    def test_success_rate_zero_tests(self):
        """Test success rate with no tests."""
        result = DCAEResult(
            status="success",
            phase="test",
            timestamp="2026-03-22T00:00:00"
        )
        assert result.success_rate == 0.0


class TestDCAEFramework:
    """Test DCAEFramework class."""

    @pytest.fixture
    def temp_project(self):
        """Create a temporary project directory."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)

    def test_framework_initialization(self, temp_project):
        """Test framework initializes correctly."""
        dcae = DCAEFramework(temp_project)
        assert dcae.project_root == Path(temp_project).resolve()
        assert dcae.state["phase"] == "init"

    def test_init_project(self, temp_project):
        """Test project initialization."""
        dcae = DCAEFramework(temp_project)
        result = dcae.init("test_project")
        
        assert result.status == "success"
        assert result.phase == "init"
        assert len(result.artifacts) > 0
        
        # Check directory structure was created
        project_dir = Path(temp_project) / "test_project"
        assert (project_dir / "tests").exists()
        assert (project_dir / "src").exists()
        assert (project_dir / "pytest.ini").exists()

    def test_design_phase(self, temp_project):
        """Test design phase creates test file."""
        dcae = DCAEFramework(temp_project)
        result = dcae.design("tests/test_feature.py")
        
        assert result.phase == "design"
        
        # Check test file was created
        test_file = Path(temp_project) / "tests" / "test_feature.py"
        assert test_file.exists()

    def test_code_phase(self, temp_project):
        """Test code phase creates source file."""
        dcae = DCAEFramework(temp_project)
        result = dcae.code("src/feature.py")
        
        assert result.phase == "code"
        
        # Check source file was created
        source_file = Path(temp_project) / "src" / "feature.py"
        assert source_file.exists()

    def test_status(self, temp_project):
        """Test status reporting."""
        dcae = DCAEFramework(temp_project)
        result = dcae.status()
        
        assert result.status == "success"
        assert result.phase == "init"


class TestCrossPlatform:
    """Test cross-platform functionality."""

    def test_platform_detection(self):
        """Test platform detection."""
        from dcae.core import get_platform
        platform = get_platform()
        assert platform in ["windows", "macos", "linux"]

    def test_python_command(self):
        """Test Python command detection."""
        from dcae.core import get_python_command
        cmd = get_python_command()
        assert isinstance(cmd, list)
        assert len(cmd) > 0
