from flask import Flask, redirect, session, render_template, flash
from forms import RegisterForm, LoginForm, FeedbackForm
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
  """Redirect to /register."""
  return redirect("/register")


@app.route("/register", methods=["GET", "POST"])
def handle_register():
  """
  GET:
  Show a form that when submitted will register/create a user. This form should accept a username, password, email, first_name, and last_name.

  Make sure you are using WTForms and that your password input hides the characters that the user is typing!
  
  POST:
  Process the registration form by adding a new user. Then redirect to /secret
  """
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
    return redirect(f"/users/{session['username']}")

  else:
    return render_template("register.html", form=form)


@app.route("/login", methods=["GET", "POST"])
def handle_login():
  """
  GET:
  Show a form that when submitted will login a user. This form should accept a username and a password.

  Make sure you are using WTForms and that your password input hides the characters that the user is typing!

  POST:
  Process the registration form by adding a new user. Then redirect to /secret
  """
  form = LoginForm()

  if form.validate_on_submit():
    user_check = User.login(form.username.data, form.password.data)
    print(user_check)
    if user_check:
      session["username"] = form.username.data
      return redirect(f"/users/{session['username']}")
    else:
      flash("Invalid Credentials. Please try again.")
      return render_template("login.html", form=form)

  else:
    return render_template("login.html", form=form)


@app.route("/users/<username>", methods=["GET"])
def get_user(username):
  """
  Show information about the given user.

  Show all of the feedback that the user has given.

  For each piece of feedback, display with a link to a form to edit the feedback and a button to delete the feedback.

  Have a link that sends you to a form to add more feedback and a button to delete the user Make sure that only the user who is logged in can successfully view this page.
  """
  
  if "username" in session:
    if session["username"].lower() == username.lower():
      user = User.query.get(session["username"])
      found_feedback = db.session.query(Feedback).filter_by(username=user.username).all()

      return render_template("user.html", first_name=user.first_name, last_name=user.last_name, email=user.email, feedback=found_feedback)
       
    else:
      flash("You are not authorized to view this page")
      return redirect(f"/users/{session['username']}")

  else:
    flash("You must be logged in to access users")
    return redirect("/login")



@app.route("/logout", methods=["GET", "POST"])
def logout():
  """Clear any information from the session and redirect to /"""
  session.pop("username")
  return redirect("/")


@app.route("/users/<username>/delete", methods=["POST"])
def delete_user(username):
  """
  Remove the user from the database and make sure to also delete all of their feedback. Clear any user information in the session and redirect to /. 
  
  Make sure that only the user who is logged in can successfully delete their account
  """
  if "username" in session:
    if session["username"].lower() == username:
      user = User.query.get(session["username"])
      user.delete()
      flash(f"{session['username']} has been deleted")
      return redirect("/")

    else:
      flash("You are not authorized to delete {username}")
      return redirect(f"{session['username']}")

  else:
    flash("You must be logged in to access users")
    return redirect("/login")


@app.route("/users/<username>/feedback/add", methods=["GET", "POST"])
def handle_feedback(username):
  """
  GET:
  Display a form to add feedback Make sure that only the user who is logged in can see this form
  
  POST:
  Add a new piece of feedback and redirect to /users/<username> — Make sure that only the user who is logged in can successfully add feedback
  """
  form=FeedbackForm()

  if "username" in session:
    if session["username"].lower() == username.lower():

      if form.validate_on_submit():
        if form.username.data.lower() != session["username"].lower():
          flash("Form error. Please make sure you are logged in correctly.")
          return redirect(f"/users/{session['username']}")
        
        else:
          feedback = Feedback(title=form.title.data, content=form.content.data, username=form.username.data)
          db.session.add(feedback)
          db.session.commit()
          return redirect(f"/users/{username}")

      else:
        return render_template("add_feedback.html", form=form)

    else:
      flash("You are not authorized to view this page")
      return redirect(f"/users/{session['username']}")

  else:
    flash("You must be logged in to access users")
    return redirect("/login")


@app.route("/feedback/<int:feedback_id>/update", methods=["GET", "POST"])
def handle_feedback_update(feedback_id):
  """
  GET:
  Display a form to edit feedback — **Make sure that only the user who has written that feedback can see this form **

  POST:
  Update a specific piece of feedback and redirect to /users/ — Make sure that only the user who has written that feedback can update it
  """
  form=FeedbackForm()

  if "username" in session:
    feedback = Feedback.query.get(feedback_id)
    if not feedback:
      flash("That feedback does not exist")
      return redirect(f"/users/{session['username']}")

    if session["username"].lower() == feedback.username.lower():

      if form.validate_on_submit():
        if form.username.data.lower() != session["username"].lower():
          flash("Form error. Please make sure you are logged in correctly.")
          return redirect(f"/users/{session['username']}")
        
        else:
          feedback.title = form.title.data
          feedback.content = form.content.data, 

          db.session.commit()
          return redirect(f"/users/{feedback.username}")

      else:
        return render_template("update_feedback.html", form=form, title=feedback.title, content=feedback.content)

    else:
      flash("You are not authorized to view this page")
      return redirect(f"/users/{session['username']}")

  else:
    flash("You must be logged in to access users")
    return redirect("/login")



@app.route("/feedback/<int:feedback_id>/delete", methods=["GET"])
def delete_feedback(feedback_id):
  """
  Delete a specific piece of feedback and redirect to /users/ — Make sure that only the user who has written that feedback can delete it
  """
  
  if "username" in session:
    feedback = Feedback.query.get(feedback_id)
    if not feedback:
      flash("That feedback does not exist")
      return redirect(f"/users/{session['username']}")

    if session["username"].lower() == feedback.username.lower():
      db.session.delete(feedback)
      db.session.commit()
      return redirect(f"/users/{session['username']}")

    else:
      flash("You are not authorized to view this page")
      return redirect(f"/users/{session['username']}")

  else:
    flash("You must be logged in to access users")
    return redirect("/login")
