async def test_create_task(client, auth_headers):
    proj = await client.post("/projects/", json={
        "name": "Proj", "description": "desc", "members": [],
    }, headers=auth_headers)
    pid = proj.json()["id"]

    res = await client.post("/tasks/", json={
        "title": "My Task",
        "description": "Task desc",
        "status": "todo",
        "project_id": pid,
    }, headers=auth_headers)
    assert res.status_code == 201
    data = res.json()
    assert data["title"] == "My Task"
    assert data["status"] == "todo"
    assert "id" in data


async def test_get_task_by_id(client, auth_headers):
    proj = await client.post("/projects/", json={
        "name": "P", "description": "d", "members": [],
    }, headers=auth_headers)
    pid = proj.json()["id"]
    created = await client.post("/tasks/", json={
        "title": "Task 1", "description": "d", "status": "todo", "project_id": pid,
    }, headers=auth_headers)
    tid = created.json()["id"]

    res = await client.get(f"/tasks/{tid}")
    assert res.status_code == 200
    assert res.json()["title"] == "Task 1"


async def test_update_task(client, auth_headers):
    proj = await client.post("/projects/", json={
        "name": "P", "description": "d", "members": [],
    }, headers=auth_headers)
    pid = proj.json()["id"]
    created = await client.post("/tasks/", json={
        "title": "Old", "description": "d", "status": "todo", "project_id": pid,
    }, headers=auth_headers)
    tid = created.json()["id"]

    res = await client.put(f"/tasks/{tid}", json={
        "title": "Updated", "status": "in_progress",
    }, headers=auth_headers)
    assert res.status_code == 200
    assert res.json()["title"] == "Updated"
    assert res.json()["status"] == "in_progress"


async def test_delete_task(client, auth_headers):
    proj = await client.post("/projects/", json={
        "name": "P", "description": "d", "members": [],
    }, headers=auth_headers)
    pid = proj.json()["id"]
    created = await client.post("/tasks/", json={
        "title": "To Delete", "description": "d", "status": "todo", "project_id": pid,
    }, headers=auth_headers)
    tid = created.json()["id"]

    res = await client.delete(f"/tasks/{tid}", headers=auth_headers)
    assert res.status_code == 204


async def test_filter_tasks_by_status(client, auth_headers):
    proj = await client.post("/projects/", json={
        "name": "P", "description": "d", "members": [],
    }, headers=auth_headers)
    pid = proj.json()["id"]

    await client.post("/tasks/", json={
        "title": "T1", "description": "d", "status": "todo", "project_id": pid,
    }, headers=auth_headers)
    await client.post("/tasks/", json={
        "title": "T2", "description": "d", "status": "done", "project_id": pid,
    }, headers=auth_headers)

    res = await client.get("/tasks/?status=todo")
    assert res.status_code == 200
    data = res.json()
    assert all(t["status"] == "todo" for t in data["items"])
