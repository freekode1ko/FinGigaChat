from tests.conftest import client


def test_get_menu():
    response = client.get("/api/v1/analytics/menu")
    assert response.status_code == 200


def test_get_section():
    response = client.get("/api/v1/analytics/section/1")
    assert response.status_code == 200


def test_send_reprots():
    response = client.post(
        "/api/v1/analytics/send/?user_id=123&report_id=321"  # FIXME
    )
    assert response.status_code == 202
