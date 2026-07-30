async def test_register(client):
    res = await client.post("/auth/register", json={
        "name": "Alice",
        "email": "alice@example.com",
        "password": "secret123",
    })
    assert res.status_code == 201
    data = res.json()
    assert data["name"] == "Alice"
    assert data["email"] == "alice@example.com"
    assert "id" in data


async def test_register_duplicate_email(client):
    await client.post("/auth/register", json={
        "name": "Alice",
        "email": "alice@example.com",
        "password": "secret123",
    })
    res = await client.post("/auth/register", json={
        "name": "Alice Again",
        "email": "alice@example.com",
        "password": "secret456",
    })
    assert res.status_code == 400
    assert "already registered" in res.json()["detail"].lower()


async def test_login_success(client):
    await client.post("/auth/register", json={
        "name": "Bob",
        "email": "bob@example.com",
        "password": "mypassword",
    })
    res = await client.post("/auth/login", json={
        "email": "bob@example.com",
        "password": "mypassword",
    })
    assert res.status_code == 200
    data = res.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


async def test_login_wrong_password(client):
    await client.post("/auth/register", json={
        "name": "Bob",
        "email": "bob@example.com",
        "password": "mypassword",
    })
    res = await client.post("/auth/login", json={
        "email": "bob@example.com",
        "password": "wrongpassword",
    })
    assert res.status_code == 401
