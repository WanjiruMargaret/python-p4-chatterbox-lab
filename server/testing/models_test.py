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
    """Message model has body, username, and created_at columns."""
    with app.app_context():
        m = Message(body="Hello 👋", username="Liza")
        db.session.add(m)
        db.session.commit()

        assert m.body == "Hello 👋"
        assert m.username == "Liza"
        assert isinstance(m.created_at, datetime)

        db.session.delete(m)
        db.session.commit()

def test_message_can_be_created_and_deleted(app):
    """Test that a message can be added and removed from the database."""
    with app.app_context():
        m = Message(body="Test Message", username="Tester")
        db.session.add(m)
        db.session.commit()

        # Verify creation
        saved = Message.query.filter_by(body="Test Message").first()
        assert saved is not None
        assert saved.username == "Tester"

        # Clean up
        db.session.delete(saved)
        db.session.commit()

def test_fixture_message_exists(message):
    """The message fixture creates a message that exists in the database."""
    assert message.body == "Hello 👋"
    assert message.username == "Liza"
    assert isinstance(message.created_at, datetime)
