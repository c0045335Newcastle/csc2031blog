import re
from flask_wtf import FlaskForm, RecaptchaField
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import Required, Email, Length, EqualTo, ValidationError


def char_check(form, field):
    excluded_chars = "*?"
    for char in field.data:
        if char in excluded_chars:
            raise ValidationError(
                f"Character {char} is not allowed in your password."
            )


class RegisterForm(FlaskForm):
    username = StringField( validators=[Required(), Email()] )
    password = PasswordField( validators=[Required(), Length(min=8, max=15, message='Password must be between 8 and 15 '
                                                                                    'characters'), char_check] )
    confirm_pass = PasswordField( validators=[Required(), EqualTo('password', 'Both password fields must be equal!')] )
    pinkey = StringField(validators=[Required(), char_check, Length(max=32, min=32, message="Length of the PIN key" +
                                                                                              " must be 32.")])
    submit = SubmitField()

    def validate_password(self, password):
        p = re.compile(r'(?=.*\d)(?=.*[A-Z])')
        if not p.match(self.password.data):
            raise ValidationError("Password must contain at least 1 digit and 1 uppercase letter.")

class LoginForm(FlaskForm):
    username = StringField(validators=[Required(), Email()])
    password = PasswordField(validators=[Required()])
    pinkey = StringField(validators=[Required()])
    submit = SubmitField()
