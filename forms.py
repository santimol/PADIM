# coding=utf-8
from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, PasswordField, SubmitField, IntegerField, SelectField, TimeField, TextAreaField, BooleanField, SelectMultipleField
from wtforms.validators import DataRequired, Length, EqualTo, Optional, Email, NumberRange


class Register_form(FlaskForm):
    email = StringField('Email',
                                    validators=[DataRequired(message="Se requiere un email"), Email()], render_kw={"placeholder": "Ej: nombre@mail.com"})

    id_padim = IntegerField('Id de padim',
                                    validators=[DataRequired(message="Se requiere un id")], render_kw={"placeholder": "Ej: 10047"})

    password = PasswordField('Contraseña',
                                    validators=[DataRequired(message="Se requiere una contraseña")])

    confirmPassword = PasswordField('Confirme la Contraseña',
                                    validators=[DataRequired(message="Se requiere una confirmacion de contraseña"), EqualTo('password')])
    submit_signup = SubmitField('Crear cuenta')

class Vaciar_tubo(FlaskForm):
    submit1 = SubmitField('Vaciar tubo')

class Deshabilitar_tubo(FlaskForm):
    submit2 = SubmitField('Deshabilitar')

class Habilitar_tubo(FlaskForm):
    submit3 = SubmitField('Habilitar')

class Login_form(FlaskForm):
    id_padim = StringField('Id de padim',
                                    validators=[DataRequired(message="Se requiere un id")])

    password = PasswordField('Contraseña',
                                    validators=[DataRequired(message="Se requiere una contraseña")])

    submit_login = SubmitField('Iniciá seción')

class Añadir_medicamento(FlaskForm):
    nombre = StringField('Nombre del medicamento',
                                    validators=[DataRequired(message="Se requiere un nombre"), Length(min=2)], render_kw={"placeholder": "Ej: Paracetamol 100mg"})

    horario = TimeField('Horario de toma',
                                    validators=[DataRequired(message="Se requiere un horario tipo: HH:MM")], render_kw={"placeholder": "Ej: 20:30"})

    dia = SelectMultipleField('Dias de toma',
                                    validators=[DataRequired(message="Se requieren dias de toma")], choices=[('L','Lunes'),('M','Martes'),('W','Miercoles'),('J','Jueves'),('V','Viernes'),('S','Sabado'),('D','Domingo')])

    cantidad = IntegerField('Cantidad por toma',
                                    validators=[DataRequired()], render_kw={"placeholder": "Ej: 1"})

    repeticion = SelectField('Repeticion',
                                    validators=[DataRequired()], choices=[('Diario','Diario'),('Semanal','Semanal'),('Mensual','Mensual')])

    mensaje = StringField('Mensaje al dispensar',
                                    validators=[Optional(), Length(max=100)])

    toma_libre = BooleanField('Toma libre?')

    submit_medicamento = SubmitField('Añadir a sus medicamentos')

class Contacto(FlaskForm):
    nombre = StringField('Nombre',
                                    validators=[DataRequired(message="Se requiere un nombre"), Length(min=4)])

    apellido = StringField('Apellido',
                                    validators=[DataRequired(message="Se requiere un apellido"), Length(min=4)])

    telefono = IntegerField('Telefono',
                                    validators=[DataRequired(message="Se requiere un numero de telefono"),NumberRange(min=10000000, max=99999999)], render_kw={"placeholder": "Sin 0 ni 11 ni 15"})

    mail = StringField('Email',
                                    validators=[DataRequired(message="Se requiere un mail para cntactar"), Email()])

    mensaje = TextAreaField('Mensaje',
                                    validators=[DataRequired(message="Necesitamos un mensaje"), Length(max=200)])

    enviar = SubmitField('Enviar mail')

class Ver_consultas(FlaskForm):
    id_consulta = IntegerField('id_consulta')

    respuesta = TextAreaField('Respuesta',
                                    validators=[DataRequired(message="Necesitamos una respuesta"), Length(max=500)])

    enviar = SubmitField('Enviar respuesta')