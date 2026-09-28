"""
Tests for backend hardware detection module.
"""

from lecturelens.backends.detect import detect_hardware


def test_detect_hardware_structure():
    report = detect_hardware()
    assert isinstance(report, dict)
    assert "python_version" in report
    assert "machine" in report
    assert "cpu_count" in report
    assert "onnxruntime_installed" in report
    assert "qnn_available" in report
    assert "verdict" in report
    assert report["verdict"] in ["NPU READY", "PARTIAL (CPU fallback available)", "NOT READY"]
    assert isinstance(report["hints"], list)
