import pytest

@pytest.mark.asyncio
async def test_register_student(client):
    response = await client.post("/register/", json={
        "telegram_id": 12345,
        "first_name": "Igor",
        "last_name": "Testov"
    })
    
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_add_and_get_score(client):

    tg_id = 999
    await client.post("/register/", json={
        "telegram_id": tg_id,
        "first_name": "Score",
        "last_name": "Master"
    })

    score_payload = {
        "telegram_id": tg_id,
        "subject": "Math",
        "score": 85
    }
    response = await client.post("/scores/", json=score_payload)
    assert response.status_code == 200
    

    if response.headers.get("content-type") == "application/json":
         assert response.json()["score"] == 85

    response = await client.get(f"/scores/{tg_id}")
    assert response.status_code == 200
    data = response.json()

    found = False
    for item in data:
        if item["subject"] == "Math" and item["score"] == 85:
            found = True
            break
    assert found is True

@pytest.mark.asyncio
async def test_invalid_score(client):
    tg_id = 555
    await client.post("/register/", json={
        "telegram_id": tg_id,
        "first_name": "Bad",
        "last_name": "Score"
    })


    response = await client.post("/scores/", json={
        "telegram_id": tg_id,
        "subject": "Math",
        "score": 150  # Ошибка!
    })
    

    assert response.status_code == 422