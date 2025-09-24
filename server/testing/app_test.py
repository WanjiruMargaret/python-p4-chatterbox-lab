import pytest
from datetime import datetime
from server.app import create_app
from server.models import db, Message

@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    app = create_app()
    app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "SQLALCHEMY_TRACK_MODIFICATIONS": False,
    })

    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()

@pytest.fixture
def message(app):
    """Create a sample message for testing."""
    m = Message(body="Hello 👋", username="Liza")
    with app.app_context():
        db.session.add(m)
        db.session.commit()
        yield m
        db.session.delete(m)
        db.session.commit()

def test_message_has_correct_columns(app):
    with app.app_context():
        m = Message(body="Hello 👋", username="Liza")
        db.session.add(m)
        db.session.commit()

        assert m.body == "Hello 👋"
        assert m.username == "Liza"
        assert isinstance(m.created_at, datetime)

        db.session.delete(m)
        db.session.commit()

def test_returns_list_of_json_objects(client, message):
    response = client.get("/messages")
    records = Message.query.all()

    assert response.status_code == 200
    for msg in response.json:
        assert msg['id'] in [record.id for record in records]
        assert msg['body'] in [record.body for record in records]

def test_creates_new_message_in_database(client, app):
    client.post("/messages", json={"body":"Hello 👋", "username":"Liza"})
    with app.app_context():
        m = Message.query.filter_by(body="Hello 👋").first()
        assert m
        db.session.delete(m)
        db.session.commit()

def test_returns_data_for_newly_created_message_as_json(client, app):
    response = client.post("/messages", json={"body":"Hello 👋", "username":"Liza"})
    assert response.content_type == "application/json"
    assert response.json["body"] == "Hello 👋"
    assert response.json["username"] == "Liza"

    with app.app_context():
        m = Message.query.filter_by(body="Hello 👋").first()
        db.session.delete(m)
        db.session.commit()

def test_updates_body_of_message_in_database(client, app, message):
    original_body = message.body
    client.patch(f"/messages/{message.id}", json={"body": "Goodbye 👋"})

    with app.app_context():
        updated = Message.query.filter_by(body="Goodbye 👋").first()
        assert updated
        updated.body = original_body
        db.session.add(updated)
        db.session.commit()

def test_returns_data_for_updated_message_as_json(client, app, message):
    response = client.patch(f"/messages/{message.id}", json={"body": "Goodbye 👋"})
    assert response.content_type == "application/json"
    assert response.json["body"] == "Goodbye 👋"

    with app.app_context():
        updated = Message.query.filter_by(body="Goodbye 👋").first()
        updated.body = message.body
        db.session.add(updated)
        db.session.commit()

def test_deletes_message_from_database(client, app):
    with app.app_context():
        m = Message(body="Hello 👋", username="Liza")
        db.session.add(m)
        db.session.commit()
        message_id = m.id

    client.delete(f"/messages/{m.id}")

    with app.app_context():
        deleted = Message.query.filter_by(body="Hello 👋").first()
        assert deleted is None
