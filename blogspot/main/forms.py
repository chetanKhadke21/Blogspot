from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, TextAreaField, SelectField, MultipleFileField, SubmitField
from wtforms.validators import DataRequired, Length

class PostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(min=2, max=100)])
    content = TextAreaField('Content', validators=[DataRequired()])
    category = SelectField('Category', choices=[
        ('entertainment', 'Entertainment'),
        ('food', 'Food'),
        ('lifestyle', 'Lifestyle'),
        ('travel', 'Travel'),
        ('technology', 'Technology'),
        ('sports', 'Sports')
    ])
    images = MultipleFileField('Upload Images', validators=[
        FileAllowed(['jpg', 'jpeg', 'png'], 'Only images are allowed!')
    ])
    submit = SubmitField('Create Post')

class CommentForm(FlaskForm):
    content = TextAreaField('Comment', validators=[DataRequired()])
    submit = SubmitField('Post Comment')
