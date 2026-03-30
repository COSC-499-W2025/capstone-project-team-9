import os
import sys

from fastapi.testclient import TestClient
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from api.main import app

client = TestClient(app)


def test_request_context_preserves_existing_request_id():
    """
    Ensure that if a request already has X-Request-ID,
    the middleware preserves it.
    """

    custom_id = "test-request-id-123"

    response = client.get(
        "/api/health",
        headers={"X-Request-ID": custom_id}
    )

    assert response.status_code == 200

    # middleware should preserve the existing X-Request-ID
    assert response.headers.get("X-Request-ID") == custom_id

def test_request_context_includes_request_id_on_error():
    """
    Ensure request ID is included even when request fails.
    """

    response = client.get("/api/non-existent-endpoint")

    # This endpoint doesn't exist, so it should return 404, but still include X-Request-ID
    assert response.status_code == 404

    # Check that X-Request-ID is present in the response headers
    request_id = response.headers.get("X-Request-ID")

    assert request_id is not None
    assert len(request_id) > 0


def test_api_health_response_format():
    response = client.get("/api/health")

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, dict)    