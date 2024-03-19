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


@app.route("/")
def show_logins():
    logins = list(
        db.session.execute(
            db.select(Login).order_by(Login.id.desc())
        ).scalars()
    )
    return render_template("show_logins.html", logins=logins)


@app.route("/add", methods=["POST"])
def add_logins():
    new = Login(request.form["user"], request.form["password"], request.form["title"])
    db.session.add(new)
    db.session.commit()
    return redirect(url_for("show_logins"))