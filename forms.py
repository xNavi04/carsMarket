from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField, FileField, IntegerField
from wtforms.validators import DataRequired, NumberRange, Length, Email
from flask_ckeditor import CKEditorField
from flask_wtf.file import FileRequired

class CreateCars(FlaskForm):
    brand = SelectField("Brand", choices=[("BMW", "BMW"), ("AUDI", "AUDI"), ("MERCEDES", "MERCEDES"), ("LAMBORGHINI", "LAMBORGHINI"), ("FERRARI", "FERRARI")])
    name = StringField("Name", validators=[DataRequired()])
    description = CKEditorField("Description", validators=[DataRequired()])
    price = IntegerField("Price in PLN", validators=[DataRequired(), NumberRange(10, 100000000, "Wrong number!")])
    file = FileField("image", validators=[FileRequired()])
    phone = StringField('Phone', validators=[DataRequired(), Length(9, 12)])
    submit = SubmitField("Confirm")



class ChooseBrand(FlaskForm):
    brand = SelectField("Brand", choices=[("BMW", "BMW"), ("AUDI", "AUDI"), ("MERCEDES", "MERCEDES"), ("LAMBORGHINI", "LAMBORGHINI"), ("FERRARI", "FERRARI")])
    submit = SubmitField("Confirm")


class EditProfile(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    email = StringField("Email")
    file = FileField("Image")
    submit = SubmitField("Confirm")