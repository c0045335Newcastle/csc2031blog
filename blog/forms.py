from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import Required

class PostForm(FlaskForm):
    title = StringField(validators=[Required()])
    body = StringField(validators=[Required()])
    submit = SubmitField()
