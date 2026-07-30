async def create_project_and_task(client, auth_headers):
    proj = await client.post("/projects/", json={
        "name": "Activity Proj", "description": "desc", "members": [],
    }, headers=auth_headers)
    pid = proj.json()["id"]

    task = await client.post("/tasks/", json={
        "title": "Activity Task", "description": "d", "status": "todo", "project_id": pid,
    }, headers=auth_headers)
    tid = task.json()["id"]

    return pid, tid


async def test_activity_created_on_task_create(client, auth_headers):
    _, tid = await create_project_and_task(client, auth_headers)

    res = await client.get(f"/tasks/{tid}/activity", headers=auth_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["total"] >= 1
    assert data["items"][0]["action"] == "task.created"
    assert data["items"][0]["task_id"] == tid


async def test_activity_logged_on_task_update(client, auth_headers):
    _, tid = await create_project_and_task(client, auth_headers)

    await client.put(f"/tasks/{tid}", json={
        "status": "done", "title": "Updated",
    }, headers=auth_headers)

    res = await client.get(f"/tasks/{tid}/activity", headers=auth_headers)
    assert res.status_code == 200
    data = res.json()
    actions = [item["action"] for item in data["items"]]
    assert "task.created" in actions
    assert "task.updated" in actions


async def test_activity_status_changed_action(client, auth_headers):
    _, tid = await create_project_and_task(client, auth_headers)

    await client.put(f"/tasks/{tid}", json={"status": "done"}, headers=auth_headers)

    res = await client.get(f"/tasks/{tid}/activity", headers=auth_headers)
    data = res.json()
    update_entry = next(i for i in data["items"] if i["action"] == "task.status_changed")
    assert update_entry is not None
    assert update_entry["changes"]["status"]["old"] == "todo"
    assert update_entry["changes"]["status"]["new"] == "done"


async def test_activity_logged_on_task_delete(client, auth_headers):
    _, tid = await create_project_and_task(client, auth_headers)

    await client.delete(f"/tasks/{tid}", headers=auth_headers)

    res = await client.get(f"/tasks/{tid}/activity", headers=auth_headers)
    assert res.status_code == 200
    data = res.json()
    actions = [item["action"] for item in data["items"]]
    assert "task.deleted" in actions


async def test_activity_pagination(client, auth_headers):
    pid, tid = await create_project_and_task(client, auth_headers)

    for i in range(5):
        await client.put(f"/tasks/{tid}", json={"title": f"Update {i}"}, headers=auth_headers)

    res = await client.get(f"/tasks/{tid}/activity?page=1&limit=3", headers=auth_headers)
    assert res.status_code == 200
    data = res.json()
    assert len(data["items"]) == 3
    assert data["total"] > 3
    assert data["page"] == 1
    assert data["pages"] > 1


async def test_activity_requires_auth(client):
    res = await client.get("/tasks/000000000000000000000000/activity")
    assert res.status_code == 401
