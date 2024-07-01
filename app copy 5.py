"""WebApp Module"""

import os
from datetime import datetime
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy


basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(basedir, "main.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

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
    subscription_id = db.Column(db.Integer, default=1, nullable=False)
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
        data = request.get_json(force=True)
        first_name = str(data["first_name"])
        last_name = str(data["last_name"])
        email = str(data["email"])
        password = str(data["password"])
        if User.query.filter_by(email=email).first():
            res = {"success": False, "error": "Email address already registered."}
            return jsonify(res)
        user_record = User(
            first_name=first_name, last_name=last_name, email=email, password=password
        )
        # Committing user.
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
        data = request.get_json(force=True)
        first_name = str(data["first_name"])
        last_name = str(data["last_name"])
        email = str(data["email"])
        password = str(data["password"])
        if existing_user := User.query.get(user_id):
            if existing_user.email != email:
                if User.query.filter_by(email=email).first():
                    res = {"success": False, "error": "Email already registered."}
            else:
                existing_user.first_name = first_name
                existing_user.last_name = last_name
                existing_user.password = password
                existing_user.email = email
                db.session.commit()
                res = {"success": True, "message": "User data updated."}
        else:
            res = {"success": False, "error": "User hasn't been found."}
    except (KeyError, TypeError, ValueError):
        res = {"success": False, "error": "Invalid JSON format or Missing value."}
    return jsonify(res)


if __name__ == "__main__":
    app.run(debug=True)
