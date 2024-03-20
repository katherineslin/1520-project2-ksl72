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
    if session["curr_user"] == "owner":
        return redirect(url_for("owner_page"))
    if session["title"] == "staff":
        return redirect(url_for("staff_page"))
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
        if event_title.strip() =="" or event_date.strip()  =="":
            flash("invalid title or date")
            return redirect(url_for("main"))
        events = list(
            db.session.execute(
                db.select(Events).order_by(Events.id.desc())
            ).scalars()
        )
        date_overlap = False
        for e in events:
            if e.event_date == event_date:
                date_overlap = True
                flash("this date has an event already, select again")
        if not date_overlap:
            new = Events(session["curr_user"], event_title, event_date, 0)
            db.session.add(new)
            db.session.commit()
        return redirect(url_for("main"))

@app.route("/event_delete", methods=["GET", "POST"])
def event_delete():
    if request.method == "POST":
        event_date = request.form["event_date"]
        d = db.session.execute(db.select(Events).where(Events.event_date == event_date)).scalar()
        for x in range(d.event_staff_count):
            b = db.session.execute(db.select(Staff).where(Staff.event_date == event_date)).scalar()
            db.session.delete(b)
            db.session.commit()
        db.session.delete(d)
        db.session.commit()
        return redirect(url_for("main"))

@app.route("/login_screen", methods=["GET", "POST"])
def login_screen():
    if request.method == "POST":
        username = request.form["user"]
        password = request.form["password"]
        if username == "owner" and password == "pass":
            session["logged_in"] = True
            session["title"] = "owner"
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
                    session["title"] = users.title
                    return redirect(url_for("staff_page"))
                else:
                    session["title"] = users.title
                    return redirect(url_for("main"))
        flash("invalid user or password")
    return render_template("login_screen.html")
    
@app.route("/owner_page", methods=["GET", "POST"])
def owner_page():
    events = list(
        db.session.execute(
            db.select(Events).order_by(Events.id.desc())
        ).scalars()
    )
    curr_staff = list(
        db.session.execute(
            db.select(Staff).order_by(Staff.id.desc())
        ).scalars()
    )
    for e in events:
        if e.event_staff_count == 0:
            flash("one or more events have no staff")

    return render_template("owner_page.html", events = events, staff = curr_staff)

@app.route("/logout", methods=["GET", "POST"])
def logout():
    session.pop("logged_in", None)
    session.pop("curr_user", None)
    session.pop("title", None)
    return redirect(url_for("main"))

@app.route("/create_but", methods=["GET", "POST"])
def create_but():
    return redirect(url_for("create_account"))

@app.route("/create_account", methods=["GET", "POST"])
def create_account():
    if request.method == "POST":
        logins = list(
            db.session.execute(
                db.select(Login).order_by(Login.id.desc())
                ).scalars()
            )
        username = request.form["user"]
        password = request.form["password"]
        if username.strip() =="" or password.strip()  =="":
            flash("invalid user or password")
        elif db.session.execute(db.select(Login).where(Login.user == username)).scalar() in logins:
            flash("username already exists, select again")
        else:
            new = Login(username, password, "customer")
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
        logins = list(
            db.session.execute(
                db.select(Login).order_by(Login.id.desc())
                ).scalars()
            )
        username = request.form["user"]
        password = request.form["password"]
        if username.strip() =="" or password.strip()  =="":
            flash("invalid user or password")
        elif db.session.execute(db.select(Login).where(Login.user == username)).scalar() in logins:
            flash("username already exists, select again")
        else:
            new = Login(username, password, "staff")
            db.session.add(new)
            db.session.commit()
            return redirect(url_for("owner_page"))
    return render_template("create_staff.html")

@app.route("/staff_page", methods=["GET", "POST"])
def staff_page():
    events = list(
        db.session.execute(
            db.select(Events).order_by(Events.id.desc())
        ).scalars()
    )
    curr_staff = list(
        db.session.execute(
            db.select(Staff).order_by(Staff.id.desc())
        ).scalars()
    )
    atl = False
    for e in events:
        if e.event_staff_count < 3:
            atl = True
    return render_template("staff_page.html", events=events, staff=curr_staff, atl = atl)

@app.route("/sign_up", methods=["GET", "POST"])
def sign_up():
    if request.method == "POST":
        event_date = request.form["event_date"]
        curr_staff = list(
            db.session.execute(
                db.select(Staff).order_by(Staff.id.desc())
                ).scalars()
         )
        signedup = False
        for c in curr_staff:
            if c.event_date == event_date:
                if c.event_staff == session["curr_user"]:
                    flash("already signed up for this, select again")
                    signedup = True
        d = db.session.execute(db.select(Events).where(Events.event_date == event_date)).scalar()
        if not signedup:
            if d.event_staff_count < 3:
                d.event_staff_count = d.event_staff_count + 1
                new = Staff(event_date, session["curr_user"])
                db.session.add(new)
                db.session.commit()
        return redirect(url_for("staff_page"))

@app.route("/back_login", methods=["GET", "POST"])
def back_login():
    return redirect(url_for("main"))

@app.route("/back_owner", methods=["GET", "POST"])
def back_owner():
    return redirect(url_for("owner_page"))