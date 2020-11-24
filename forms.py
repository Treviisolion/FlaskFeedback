"""Forms for Login Security"""

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField
from wtforms.validators import DataRequired, Email, Optional
from wtforms.fields.html5 import EmailField

class NewUserForm(FlaskForm):
    """Form for registering new users"""

    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    email = EmailField("Email", validators=[DataRequired(), Email()])
    first_name = StringField("First Name", validators=[DataRequired()])
    last_name = StringField("Given Name", validators=[DataRequired()])

class UserLoginForm(FlaskForm):
    """Form for logging in existing users"""

    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])

class NewFeedbackForm(FlaskForm):
    """Form for giving feedback on users"""

    title = StringField("Title", validators=[DataRequired()])
    content = TextAreaField("Content", validators=[DataRequired()])

class EditFeedbackForm(FlaskForm):
    """Form for editing feedback on users"""

    title = StringField("Title", validators=[Optional()])
    content = TextAreaField("Content", validators=[Optional()])