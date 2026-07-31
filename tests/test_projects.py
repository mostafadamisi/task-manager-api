async def test_create_project(client, auth_headers):
    res = await client.post("/projects/", json={
        "name": "My Project",
        "description": "Test project",
        "members": [],
    }, headers=auth_headers)
    assert res.status_code == 201
    data = res.json()
    assert data["name"] == "My Project"
    assert "id" in data
    assert data["owner"] is not None


async def test_list_projects(client, auth_headers):
    await client.post("/projects/", json={
        "name": "P1", "description": "desc", "members": [],
    }, headers=auth_headers)
    res = await client.get("/projects/")
    assert res.status_code == 200
    assert len(res.json()["items"]) >= 1


async def test_get_project_by_id(client, auth_headers):
    created = await client.post("/projects/", json={
        "name": "P2", "description": "desc", "members": [],
    }, headers=auth_headers)
    pid = created.json()["id"]
    res = await client.get(f"/projects/{pid}")
    assert res.status_code == 200
    assert res.json()["name"] == "P2"


async def test_get_project_not_found(client):
    res = await client.get("/projects/000000000000000000000000")
    assert res.status_code == 404


async def test_delete_project(client, auth_headers):
    created = await client.post("/projects/", json={
        "name": "P3", "description": "desc", "members": [],
    }, headers=auth_headers)
    pid = created.json()["id"]
    res = await client.delete(f"/projects/{pid}", headers=auth_headers)
    assert res.status_code == 204


async def test_delete_project_forbidden(client, auth_headers):
    res = await client.post("/auth/register", json={
        "name": "Other", "email": "other@example.com", "password": "password456",
    })
    other_token = res.json()["id"]
    created = await client.post("/projects/", json={
        "name": "P4", "description": "desc", "members": [],
    }, headers=auth_headers)
    pid = created.json()["id"]
    other_headers = {"Authorization": "Bearer invalidtoken"}
    res = await client.delete(f"/projects/{pid}", headers=other_headers)
    assert res.status_code == 401
