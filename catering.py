import os
from flask import (
    Flask,
    request,
    session,
    redirect,
    url_for,
    abort,
    render_template,
    flash,
)

from login import db, Login


# create our little application :)
app = Flask(__name__)

#Load default config and override config from an environment variable
app.config.update(
    dict(
        DEBUG=True,
        SECRET_KEY="development key",
        USERNAME="admin",
        PASSWORD="default",
        SQLALCHEMY_DATABASE_URI="sqlite:///" + os.path.join(app.root_path, "catering.db"),
    )
)
app.config.from_envvar("FLASKR_SETTINGS", silent=True)

db.init_app(app)


@app.cli.command("initdb")
def initdb_command():
    """Creates the database tables."""
    db.create_all()
    print("Initialized the database.")


@app.route("/", methods=["GET", "POST"])
def main():
    if not session.get("logged_in"):
        return redirect(url_for("login_screen"))
    logins = list(
        db.session.execute(
            db.select(Login).order_by(Login.id.desc())
        ).scalars()
    )
    return render_template("show_logins.html", logins=logins)


@app.route("/login_screen", methods=["GET", "POST"])
def login_screen():
    if request.method == "POST":
        new = Login(request.form["user"], request.form["password"], request.form["title"])
        db.session.add(new)
        db.session.commit()
        session["logged_in"] = True
        return redirect(url_for("main"))
    return render_template("login_screen.html")
    