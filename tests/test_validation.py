INVALID_ID = "not-an-objectid"


async def test_register_short_password_rejected(client):
    res = await client.post("/auth/register", json={
        "name": "Test",
        "email": "short@example.com",
        "password": "abc",
    })
    assert res.status_code == 422


async def test_register_empty_name_rejected(client):
    res = await client.post("/auth/register", json={
        "name": "   ",
        "email": "noname@example.com",
        "password": "password123",
    })
    assert res.status_code == 422


async def test_register_whitespace_name_rejected(client):
    res = await client.post("/auth/register", json={
        "name": "   ",
        "email": "ws@example.com",
        "password": "password123",
    })
    assert res.status_code == 422


async def test_create_project_empty_name_rejected(client, auth_headers):
    res = await client.post("/projects/", json={
        "name": "",
        "description": "desc",
        "members": [],
    }, headers=auth_headers)
    assert res.status_code == 422


async def test_create_project_invalid_member_rejected(client, auth_headers):
    res = await client.post("/projects/", json={
        "name": "P",
        "description": "desc",
        "members": [INVALID_ID],
    }, headers=auth_headers)
    assert res.status_code == 400


async def test_get_project_invalid_id_bad_request(client):
    res = await client.get(f"/projects/{INVALID_ID}")
    assert res.status_code == 400


async def test_delete_project_invalid_id_bad_request(client, auth_headers):
    res = await client.delete(f"/projects/{INVALID_ID}", headers=auth_headers)
    assert res.status_code == 400


async def test_create_task_empty_title_rejected(client, auth_headers):
    res = await client.post("/tasks/", json={
        "title": "",
        "description": "d",
        "status": "todo",
        "project_id": "000000000000000000000000",
    }, headers=auth_headers)
    assert res.status_code == 422


async def test_create_task_invalid_project_id_bad_request(client, auth_headers):
    res = await client.post("/tasks/", json={
        "title": "T",
        "description": "d",
        "status": "todo",
        "project_id": INVALID_ID,
    }, headers=auth_headers)
    assert res.status_code == 400


async def test_create_task_invalid_assignee_bad_request(client, auth_headers):
    proj = await client.post("/projects/", json={
        "name": "P", "description": "desc", "members": [],
    }, headers=auth_headers)
    pid = proj.json()["id"]

    res = await client.post("/tasks/", json={
        "title": "T",
        "description": "d",
        "status": "todo",
        "project_id": pid,
        "assignee": INVALID_ID,
    }, headers=auth_headers)
    assert res.status_code == 400


async def test_update_task_invalid_assignee_bad_request(client, auth_headers):
    proj = await client.post("/projects/", json={
        "name": "P", "description": "desc", "members": [],
    }, headers=auth_headers)
    pid = proj.json()["id"]
    created = await client.post("/tasks/", json={
        "title": "T", "description": "d", "status": "todo", "project_id": pid,
    }, headers=auth_headers)
    tid = created.json()["id"]

    res = await client.put(f"/tasks/{tid}", json={
        "assignee": INVALID_ID,
    }, headers=auth_headers)
    assert res.status_code == 400


async def test_filter_tasks_invalid_project_id_bad_request(client):
    res = await client.get(f"/tasks/?project_id={INVALID_ID}")
    assert res.status_code == 400


async def test_filter_tasks_invalid_assignee_bad_request(client):
    res = await client.get(f"/tasks/?assignee={INVALID_ID}")
    assert res.status_code == 400


async def test_get_activity_invalid_task_id_bad_request(client, auth_headers):
    res = await client.get(f"/tasks/{INVALID_ID}/activity", headers=auth_headers)
    assert res.status_code == 400
