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
    g,
)

from login import db, Login, Events, Staff

curr_user = " "
curr_events_to_staff = {}
curr_costumer_to_event = {}
curr_event_to_date = {}


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
    events = list(
        db.session.execute(
            db.select(Events).order_by(Events.id.desc())
        ).scalars()
    )
    return render_template("show_logins.html", logins=logins, events=events, curr_user = session["curr_user"])

@app.route("/event_add_cost", methods=["GET", "POST"])
def event_add_cost():
    if request.method == "POST":
        event_title = request.form["event_title"]
        event_date = request.form["event_date"]
        new = Events(session["curr_user"], event_title, event_date)
        db.session.add(new)
        db.session.commit()
        return redirect(url_for("main"))

@app.route("/login_screen", methods=["GET", "POST"])
def login_screen():
    if request.method == "POST":
        username = request.form["user"]
        password = request.form["password"]
        if username == "owner" and password == "pass":
            session["logged_in"] = True
            session["curr_user"] = "owner"
            return redirect(url_for("owner_page"))
        logins = list(
        db.session.execute(
            db.select(Login).order_by(Login.id.desc())
            ).scalars()
        )
        for users in logins:
            if users.user == username and users.password == password:
                session["logged_in"] = True
                session["curr_user"] = username
                if users.title == "staff":
                    return redirect(url_for("staff_page"))
                else:
                    return redirect(url_for("main"))
    return render_template("login_screen.html")
    
@app.route("/owner_page", methods=["GET", "POST"])
def owner_page():
    if request.method == "POST":
        return redirect(url_for("main"))
    return render_template("owner_page.html")

@app.route("/logout", methods=["GET", "POST"])
def logout():
    session.pop("logged_in", None)
    session.pop("curr_user", None)
    return redirect(url_for("main"))

@app.route("/create_but", methods=["GET", "POST"])
def create_but():
    return redirect(url_for("create_account"))

@app.route("/create_account", methods=["GET", "POST"])
def create_account():
    if request.method == "POST":
        username = request.form["user"]
        password = request.form["password"]
        new = Login(username, password, "customer", {})
        db.session.add(new)
        db.session.commit()
        return redirect(url_for("main"))
    return render_template("create_account.html")

@app.route("/create_staff_but", methods=["GET", "POST"])
def create_staff_but():
    return redirect(url_for("create_staff"))

@app.route("/create_staff", methods=["GET", "POST"])
def create_staff():
    if request.method == "POST":
        username = request.form["user"]
        password = request.form["password"]
        new = Login(username, password, "staff", {})
        db.session.add(new)
        db.session.commit()
        return redirect(url_for("owner_page"))
    return render_template("create_staff.html")

@app.route("/staff_page", methods=["GET", "POST"])
def staff_page():
    if request.method == "POST":
        return redirect(url_for("main"))
    return render_template("staff_page.html")

