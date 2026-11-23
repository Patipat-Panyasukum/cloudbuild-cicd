from unittest.mock import ANY, MagicMock, patch

import pytest

# main.py creates a BigQuery client during import. Mock its constructor first
# so collecting this unit test does not require Google Cloud credentials.
with patch("google.cloud.bigquery.Client", autospec=True):
    from main import app, client as app_client

@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

@patch.object(app_client,'load_table_from_uri')
@patch.object(app_client,'get_table')
def test_main_endpoint(mock_get_table, mock_load_table_from_uri, client):
    mock_load_job = MagicMock()
    mock_load_table_from_uri.return_value = mock_load_job

    mock_table = MagicMock()
    mock_table.num_rows = 50
    mock_get_table.return_value = mock_table

    response = client.get('/')
    assert response.status_code == 200
    data = response.get_json()
    assert 'data' in data
    assert data['data'] == 50
    
    mock_load_table_from_uri.assert_called_once_with(
        "gs://mlops-test-bucket137/us-states.csv",
        "project-f1433245-a1c4-4477-abb.test_schema.us_states",
        job_config=ANY,
    )
    mock_load_job.result.assert_called_once()
    mock_get_table.assert_called_once_with(
        "project-f1433245-a1c4-4477-abb.test_schema.us_states"
    )
