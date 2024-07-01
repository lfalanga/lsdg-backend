"""WebApp Module"""

import os
from datetime import datetime

# from flask import Flask, render_template, request, url_for, redirect
from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy

# from sqlalchemy.sql import func

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(basedir, "main.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


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


# app.secret_key = 'my_secret_key'


@app.route("/")
@app.route("/index/")
def home():
    """Home."""
    return "<h1>Home!</h1>"


@app.route('/returnjsonget/', methods = ['GET'])
def return_json_get():
    """API Testing: Returning JSON object."""
    data = {
        'Title': 'Testing API.',
        'Subject': 'You made a GET Request!',
    }
    return jsonify(data)


@app.route('/returnjsonpost/', methods = ['POST'])
def return_json_post():
    """API Testing: Returning JSON object."""
    data = {
        'Title': 'Testing API.',
        'Subject': 'You made a POST Request!',
    }
    return jsonify(data)


@app.route("/users/")
def users():
    """Listing users."""
    all_users = User.query.all()
    return render_template("users.html", users=all_users)


@app.route("/users/<int:user_id>/")
def user(user_id):
    """Displaying user info."""
    user_record = User.query.get_or_404(user_id)
    return render_template("user.html", user=user_record)


@app.route("/create/user/", methods=["POST"])
def create_user():
    """Creating user."""
    if request.method == "POST":
        first_name = request.form["first_tname"]
        last_name = request.form["last_name"]
        email = request.form["email"]
        password = request.form["password"]
    elif request.method == "GET":
        first_name = request.args.get("first_name")
        last_name = request.args.get("last_name")
        email = request.args.get("email")
        password = request.args.get("password")
    user_record = User(
        first_name=first_name, last_name=last_name, email=email, password=password
    )
    # Commit user.
    db.session.add(user_record)
    db.session.commit()
    return render_template("user.html", user=user_record)


if __name__ == "__main__":
    app.run(debug=True)
