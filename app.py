"""Routes for Login Security"""

from os import path
from flask_debugtoolbar import DebugToolbarExtension
from flask import Flask, redirect, render_template, request, session, flash
from models import db, connect_db, User, Feedback
from forms import NewUserForm, UserLoginForm, NewFeedbackForm, EditFeedbackForm

if path.exists('secret.py'):
    from secret import SECRET_KEY
else:
    SECRET_KEY = 'missing secret key'

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///loginsecurity'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['SECRET_KEY'] = SECRET_KEY

connect_db(app)

# app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = True
# debug = DebugToolbarExtension(app)

db.create_all()

UNAUTHORIZED = 'You are not authorized to do this'

@app.route('/')
def redirect_register():
    """Redirects to user registration page"""

    return redirect('/register')


@app.route('/register', methods=['GET', 'POST'])
def register_user():
    """Registers a new user, making certain that the username and email are unique"""

    form = NewUserForm()

    if form.validate_on_submit():
        try:
            new_user = User.register(username=form.username.data, password=form.password.data, email=form.email.data,
                                     first_name=form.first_name.data.capitalize(), last_name=form.last_name.data.capitalize())
            db.session.add(new_user)
            db.session.commit()
            session['username'] = new_user.username
        except:
            db.session.rollback()
            test_username = User.query.get(form.username.data)
            if test_username:
                flash('Username is taken')
            else:
                flash('Email is taken')

            return render_template('register.html', form=form)
        else:
            return redirect(f'/users/{new_user.username}')
    else:
        return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login_user():
    """Logins to an existing user"""

    form = UserLoginForm()

    if form.validate_on_submit():
        user = User.authenticate(form.username.data, form.password.data)
        if user:
            session['username'] = user.username
            return redirect(f'/users/{user.username}')
        else:
            user = User.query.get(form.username.data)
            if not user:
                flash('Username does not exist')
            else:
                flash('Incorrect Password')
            return render_template('login.html', form=form)
    else:
        return render_template('login.html', form=form)


@app.route('/logout')
def logout():
    """Logouts the user"""

    session.pop('username')
    flash('Successfully Logged Out')
    return redirect('/')


@app.route('/users/<username>')
def show_user(username):
    """Shows the specified user's public info to other users"""

    if 'username' not in session:
        flash(UNAUTHORIZED)
        return redirect('/')
    else:
        current_user = User.query.get(session.get('username'))

        if current_user and current_user.username == username:
            user = User.query.get_or_404(username)
            feedbacks = user.feedbacks

            return render_template('user.html', user=user, feedbacks=feedbacks)
        else:
            flash(UNAUTHORIZED)
            return redirect('/')


@app.route('/users/<username>/delete', methods=['POST'])
def delete_user(username):
    """Deletes specified user"""

    if username == session.get('username'):
        user = User.query.get_or_404(username)
        db.session.delete(user)
        db.session.commit()
        session.pop('username')
        flash(f'{username} was deleted')
        return redirect('/')
    else:
        flash(UNAUTHORIZED)
        return redirect(f'/users/{username}')


@app.route('/feedback/<int:feedback_id>/delete', methods=['POST'])
def delete_feedback(feedback_id):
    """Deletes the specified feedback"""

    feedback = Feedback.query.get_or_404(feedback_id)
    if feedback.username == session.get('username'):
        db.session.delete(feedback)
        db.session.commit()
        flash(f'{feedback.title} was deleted')
    else:
        flash(UNAUTHORIZED)

    return redirect(f'/users/{feedback.username}')

@app.route('/users/<username>/feedback/add', methods=['GET', 'POST'])
def add_feedback(username):
    """Adds feedback on the specified user"""

    current_user = User.query.get(session.get('username'))
    if current_user and current_user.username == username:
        user = User.query.get_or_404(username)
        form = NewFeedbackForm()

        if form.validate_on_submit():
            new_feedback = Feedback(title=form.title.data.capitalize(), content=form.content.data.capitalize(), username=user.username)
            db.session.add(new_feedback)
            db.session.commit()
            flash('Feedback received')
            return redirect(f'/users/{username}')
        else:
            return render_template('new_feedback.html', form=form, username=username)
    else:
        flash(UNAUTHORIZED)
        return redirect('/')

@app.route('/feedback/<int:feedback_id>/update', methods=['GET', 'POST'])
def edit_feedback(feedback_id):
    """Edits the specified feedback"""

    current_user = User.query.get(session.get('username'))
    if current_user:
        feedback = Feedback.query.get_or_404(feedback_id)
        form = EditFeedbackForm(obj=feedback)

        if current_user.username == feedback.username:
            if form.validate_on_submit():
                feedback.title = form.title.data.capitalize()
                feedback.content = form.content.data.capitalize()
                db.session.commit()
                flash('Feedback updated')
                return redirect(f'/users/{feedback.username}')
            else:
                return render_template('update_feedback.html', form=form, username=feedback.username)
        else:
            flash(UNAUTHORIZED)
            return redirect('/')
    else:
        flash(UNAUTHORIZED)
        return redirect('/')