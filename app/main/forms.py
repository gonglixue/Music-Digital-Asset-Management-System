from flask.ext.wtf import Form
from wtforms import StringField, SubmitField
from wtforms.validators import Required


class NameForm(Form):
    name = StringField('What is your name?', validators=[Required()])
    submit = SubmitField('Submit')
	

class CommentForm(Form):
	body = StringField('',validators=[Required()])
	submit = SubmitField('Submit')
	
class SearchForm(Form):
	keyword = StringField('',validators=[Required()])
	submit = SubmitField('Search')
