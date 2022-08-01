from flask import Flask, redirect, session, render_template, flash
from forms import RegisterForm, LoginForm
from models import User, Feedback, db, connect_db
from flask_debugtoolbar import DebugToolbarExtension


app = Flask(__name__)

app.config["SECRET_KEY"] = "terces"
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///feedback'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

# TESTING
app.config['WTF_CSRF_ENABLED'] = False
toolbar = DebugToolbarExtension(app)

connect_db(app)
db.create_all()


@app.route("/", methods=["GET"])
def to_register():
  return redirect("/register")


@app.route("/register", methods=["GET", "POST"])
def handle_register():

  form = RegisterForm()

  if form.validate_on_submit():
    # create new user

    user = User.register(form.username.data, form.password.data, form.email.data, form.first_name.data, form.last_name.data)

    # add to session, commit
    db.session.add(user)
    db.session.commit()

    # login
    session["username"] = user.username

    # redirect to secret
    return redirect("/users")

  else:
    return render_template("register.html", form=form)


@app.route("/login", methods=["GET", "POST"])
def handle_login():
  form = LoginForm()

  if form.validate_on_submit():
    user_check = User.login(form.username.data, form.password.data)
    print(user_check)
    if user_check:
      session["username"] = form.username.data
      return redirect("/users")
    else:
      flash("Invalid Credentials. Please try again.")
      return render_template("login.html", form=form)


  else:
    return render_template("login.html", form=form)


@app.route("/users", methods=["GET"])
def get_users():
  if "username" in session:
    user = User.query.get(session["username"])
    found_feedback = db.session.query(Feedback).filter_by(username=user.username).all()

    return render_template("user.html", first_name=user.first_name, last_name=user.last_name, email=user.email, feedback=found_feedback)
  else:
    flash("You must be logged in to access users")
    return redirect("/login")


@app.route("/logout", methods=["GET", "POST"])
def logout():

  session.pop("username")
  return redirect("/")
