from flask_wtf import Form
from app import models
from wtforms import StringField, BooleanField, PasswordField, IntegerField, SelectField, RadioField, SubmitField, SelectMultipleField, HiddenField, DateTimeField, widgets, DecimalField, TextField, FloatField, TextAreaField
from wtforms.validators import DataRequired, Length, EqualTo, NumberRange, Email, Required, InputRequired, Optional

class LoginForm(Form):
    username = StringField('username', validators=[DataRequired(), Length(min = 4, max = 25)])
    password = PasswordField('password', validators=[DataRequired()])
    submit = SubmitField()

    def validate_on_submit(self):
        if not Form.validate_on_submit(self):
            return False
        user_to_check = models.User.query.filter_by(username = self.username.data).first()
        if not user_to_check:
            self.username.errors.append("No user with this username exists")
            return False
        if not user_to_check.check_password(self.password.data):
            self.password.errors.append("Authentication failed")
            return False
        return True

class CreateForm(Form):
    username = StringField('username', validators=[DataRequired(), Length(min = 4, max = 25)])
    nickname = StringField('nickname', validators=[DataRequired(), Length(max = 25)])
    password = PasswordField('password', validators=[DataRequired()])
    password2 = PasswordField('password2', validators=[DataRequired(), EqualTo('password', message='Passwords must match')])
    email = StringField('email', validators=[DataRequired(), Email()])
    submit = SubmitField()

    def validate_on_submit(self):
        if not Form.validate_on_submit(self):
            return False
        
        user = models.User.query.filter_by(email = self.email.data).first()
        if user:
            self.email.errors.append("This email is already registered")
            return False

        user = models.User.query.filter_by(username = self.username.data).first()
        if user:
            self.username.errors.append("This username is already registered")
            return False

        return True
