"""WebApp Module"""

import os
from datetime import datetime

# from flask import Flask, render_template, request, url_for, redirect
# from sqlalchemy import create_engine, and_
# from sqlalchemy import and_
# from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy.orm import sessionmaker
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
# import simplejson as json
import json


basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(basedir, "main.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# Connect to the database
# Base = declarative_base()
# engine = create_engine(app.config["SQLALCHEMY_DATABASE_URI"])
# Session = sessionmaker(bind=engine)
# Base.metadata.create_all(engine)
# session = Session()

# def is_json(my_json):
#    """Determine if a string is in JSON format."""
#    try:
#        json.loads(my_json)
#    except ValueError:
#        return False
#    return True

def is_json(expression):
    """Determine if a string is in JSON format."""
    if (str(type(expression)) == "<class 'dict'>"):
        return True
    else:
        return False


def dump_datetime(value):
    """Deserialize datetime object into string form for JSON processing."""
    if value is None:
        return None
    return [value.strftime("%Y-%m-%d"), value.strftime("%H:%M:%S")]


class User(db.Model):
    """Data model for user accounts."""

    __tablename__ = "User"
    user_id = db.Column("user_id", db.Integer, primary_key=True)
    first_name = db.Column(db.String(255), nullable=False)
    last_name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    newsletter = db.Column(db.Boolean, default=False, nullable=False)
    suscription_id = db.Column("suscription_id", db.Integer, default=1, nullable=False)
    created = db.Column(
        db.DateTime(timezone=True), default=datetime.now(), nullable=False
    )
    deleted = db.Column(db.Boolean, default=False, nullable=False)

    def __repr__(self):
        return f"{self.first_name}, {self.last_name} > ({self.email})"

    @property
    def serialize(self):
        """Return object data in easily serializable format"""
        return {
            "user_id": self.user_id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "email": self.email,
            "created": dump_datetime(self.created),
            "deleted": self.deleted
            # This is an example how to deal with Many2Many relations
            # 'many2many'  : self.serialize_many2many
        }

    @property
    def serialize_many2many(self):
        """
        Return object's relations in easily serializable format.
        NB! Calls many2many's serialize property.
        """
        return [item.serialize for item in self.many2many]


# app.secret_key = 'my_secret_key'


@app.route("/")
@app.route("/index/")
def home():
    """Home."""
    return "<h1>Home!</h1>"


@app.route("/returnjsonget/", methods=["GET"])
def return_json_get():
    """API Testing: Returning JSON object."""
    data = {
        "Title": "Testing API.",
        "Subject": "You made a GET Request!",
    }
    return jsonify(data)


@app.route("/returnjsonpost/", methods=["POST"])
def return_json_post():
    """API Testing: Returning JSON object."""
    data = {
        "Title": "Testing API.",
        "Subject": "You made a POST Request!",
    }
    return jsonify(data)


@app.route("/users/")
def users():
    """Listing users."""
    all_users = User.query.filter_by(deleted=False)
    return jsonify(users=[i.serialize for i in all_users.all()])


@app.route("/users/<int:user_id>/", methods=['GET'])
def user(user_id):
    """Displaying user info."""
    try:
        data = User.query.filter_by(user_id=user_id).first()
        if is_json(data.serialize):
            obj_dict = data.serialize
            if not obj_dict["deleted"]:
                res = obj_dict
            else:
                res = {"success": True,
                       "error": "User has been deleted.", "user_id": user_id}
        else:
            res = {"success": False,
                   "error": "Invalid JSON format.", "user_id": user_id}

        return jsonify(res)

    except (KeyError, TypeError, ValueError):
        res = {"success": False,
               "error": "Invalid JSON format. Missing value.", "user_id": user_id}
        return jsonify(res)


@app.route("/create/user/", methods=["POST"])
def create_user():
    """Creating user."""

    try:
        # We use 'force' to skip mimetype checking to have shorter curl command.
        data = request.get_json(force=True)
        first_name = str(data["first_name"])
        last_name = str(data["last_name"])
        email = str(data["email"])
        password = str(data["password"])

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            res = {"success": False, "error": "Existing user."}
            return jsonify(res)
        user_record = User(
            first_name=first_name, last_name=last_name, email=email, password=password
        )
        # Commit user.
        db.session.add(user_record)
        db.session.commit()
        res = {"success": True}
        return jsonify(res)
    except (KeyError, TypeError, ValueError):
        res = {"success": False, "error": "Invalid JSON format. Missing value."}
        return jsonify(res)


@app.route("/delete/user/<int:user_id>/", methods=['PUT'])
def delete_user(user_id):
    """Deleting user."""
    try:
        user_data = User.query.get(user_id)
        user_data.deleted = True
        db.session.commit()
        res = {"success": True, "message": "User has been deleted."}
        return jsonify(res)
    except (KeyError, TypeError, ValueError):
        res = {"success": False, "error": "Invalid JSON format or Missing id."}
        return jsonify(res)


@app.route("/update/user/<int:user_id>/", methods=["POST"])
def update_user(user_id):
    """Updating user."""
    try:
        # We use 'force' to skip mimetype checking to have shorter curl command.
        data = request.get_json(force=True)
        first_name = str(data["first_name"])
        last_name = str(data["last_name"])
        email = str(data["email"])
        password = str(data["password"])
        # existing_user = User.query.filter_by(user_id=user_id).first()
        existing_user = User.query.get(user_id)
        if existing_user:
            existing_user.first_name = first_name
            existing_user.last_name = last_name
            existing_user.password = password
            if email != existing_user.email:
                existing_email = User.query.filter_by(email=email).first()
                if existing_email:
                    if existing_user.user_id == user_id:
                        existing_user.email = email
                        db.session.commit()
                        res = {
                            "success": True,
                            "message": "User has been updated.",
                            "registered_email": existing_user.email,
                            "new_email": email,
                        }
                        return jsonify(res)
                    elif existing_email and existing_email.user_id != user_id:
                        res = {
                            "success": False,
                            "error": "Email already registered.",
                            "existing_email": email,
                        }
                        return jsonify(res)
                    else:
                        db.session.commit()
                        res = {"success": True, "message": "User has been updated."}
                        return jsonify(res)
                else:
                    res = {
                        "success": False,
                        "error": "Something went wrong. 1",
                        "registered_email": existing_user.email,
                        "new_email": email,
                        "comparisson": not existing_email,
                    }
                    return jsonify(res)
        else:
            res = {"success": False, "error": "User does not exist."}
            return jsonify(res)
    except (KeyError, TypeError, ValueError):
        res = {"success": False, "error": "Invalid JSON format or Missing value."}
        return jsonify(res)
    res = {
        "success": False,
        "error": "Something went wrong. 2",
        "registered_email": existing_user.email,
        "new_email": email,
    }
    return jsonify(res)


if __name__ == "__main__":
    app.run(debug=True)
