from http import HTTPStatus

import pytest
from fastapi.testclient import TestClient

from mader.app import app


@pytest.mark.asyncio
async def test_read_root():
    client = TestClient(app)
    response = client.get('/')
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'Hello World!'}
