from flask import Flask, jsonify, request, session
from flask_cors import CORS
from .models import db, User, Message
from datetime import datetime

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///app.db"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = "supersecret"
    
    db.init_app(app)
    CORS(app)

    # ------------------ User Routes ------------------ #
    @app.route("/signup", methods=["POST"])
    def signup():
        data = request.get_json()
        username = data.get("username")
        password = data.get("password")
        if not username or not password:
            return jsonify({"error": "Missing username or password"}), 400
        if User.query.filter_by(username=username).first():
            return jsonify({"error": "Username taken"}), 400
        user = User(username=username, password=password)
        db.session.add(user)
        db.session.commit()
        return jsonify({"id": user.id, "username": user.username}), 201

    @app.route("/login", methods=["POST"])
    def login():
        data = request.get_json()
        username = data.get("username")
        password = data.get("password")
        user = User.query.filter_by(username=username, password=password).first()
        if not user:
            return jsonify({"error": "Invalid credentials"}), 401
        session["user_id"] = user.id
        return jsonify({"id": user.id, "username": user.username})

    @app.route("/check_session")
    def check_session():
        user_id = session.get("user_id")
        if not user_id:
            return jsonify({"user": None})
        user = User.query.get(user_id)
        return jsonify({"id": user.id, "username": user.username})

    # ------------------ Message Routes ------------------ #
    @app.route("/messages", methods=["GET"])
    def get_messages():
        messages = Message.query.all()
        return jsonify([
            {"id": m.id, "body": m.body, "username": m.username, "created_at": m.created_at.isoformat()}
            for m in messages
        ])

    @app.route("/messages", methods=["POST"])
    def create_message():
        data = request.get_json()
        body = data.get("body")
        username = data.get("username")
        if not body or not username:
            return jsonify({"error": "Missing body or username"}), 400
        message = Message(body=body, username=username, created_at=datetime.utcnow())
        db.session.add(message)
        db.session.commit()
        return jsonify({
            "id": message.id,
            "body": message.body,
            "username": message.username,
            "created_at": message.created_at.isoformat()
        }), 201

    @app.route("/messages/<int:id>", methods=["PATCH"])
    def update_message(id):
        message = Message.query.get_or_404(id)
        data = request.get_json()
        if "body" in data:
            message.body = data["body"]
        db.session.commit()
        return jsonify({
            "id": message.id,
            "body": message.body,
            "username": message.username,
            "created_at": message.created_at.isoformat()
        })

    @app.route("/messages/<int:id>", methods=["DELETE"])
    def delete_message(id):
        message = Message.query.get_or_404(id)
        db.session.delete(message)
        db.session.commit()
        return jsonify({"message": f"Message {id} deleted"}), 200

    return app
