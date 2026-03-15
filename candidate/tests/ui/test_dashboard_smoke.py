def test_dashboard_loads(page, dashboard_base_url):
    response = page.goto(dashboard_base_url, wait_until="domcontentloaded")
    assert response is not None
    assert response.ok