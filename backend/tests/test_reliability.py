import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.config import settings
from app.services.session_metrics_service import session_metrics_service


def test_config_secret_masking():
    """Verify that settings does not leak full API keys."""
    masked = settings.masked_gemini_key
    assert masked != settings.gemini_api_key
    assert "..." in masked or masked == "NOT_SET"
    print("[PASS] test_config_secret_masking")


def test_session_metrics_duration_formatting():
    """Verify clean human-readable duration formatting."""
    assert session_metrics_service._format_duration(0) == "0s"
    assert session_metrics_service._format_duration(14200) == "14.2s"
    assert session_metrics_service._format_duration(124000) == "2m 4s"
    assert session_metrics_service._format_duration(360000) == "6m 0s"
    print("[PASS] test_session_metrics_duration_formatting")


def test_file_upload_validation_rules():
    """Verify file extension and upload size limits."""
    allowed = settings.allowed_file_extensions
    assert ".pdf" in allowed
    assert ".docx" in allowed
    assert ".txt" in allowed
    assert ".md" in allowed
    assert ".exe" not in allowed
    assert ".sh" not in allowed
    assert settings.max_upload_size_bytes == 10 * 1024 * 1024
    print("[PASS] test_file_upload_validation_rules")


def test_health_check_payload():
    """Verify health check response schema."""
    from app.schemas.health import HealthResponse
    hr = HealthResponse(status="healthy", service="ventureos-api", version="0.9.0", timestamp="2026-09-04T00:00:00Z")
    assert hr.status == "healthy"
    assert hr.version == "0.9.0"
    assert hr.timestamp is not None
    print("[PASS] test_health_check_payload")


if __name__ == "__main__":
    test_config_secret_masking()
    test_session_metrics_duration_formatting()
    test_file_upload_validation_rules()
    test_health_check_payload()
    print("\nAll Reliability Tests Passed Successfully!")
