from flask_wtf import FlaskForm
from wtforms import SubmitField, TextAreaField, IntegerField, StringField
from wtforms.validators import DataRequired


class TransactionForm(FlaskForm):
    sender_public_key = TextAreaField('Sender Public Key',
                                      validators=[DataRequired()],
                                      render_kw={'placeholder': 'Sender Public Key',
                                                 'class': 'form-control',
                                                 'rows': 9})
    recipient_public_key = TextAreaField('Recipient Public Key',
                                         validators=[DataRequired()],
                                         render_kw={'placeholder': 'Recipient Public Key',
                                                    'class': 'form-control',
                                                    'rows': 9})
    s_private_key = TextAreaField('Sender Private Key',
                                  validators=[DataRequired()],
                                  render_kw={'class': 'form-control',
                                             'rows': 7})
    value = IntegerField('Value',
                         validators=[DataRequired()],
                         render_kw={'class': 'form-control'})
    fee = IntegerField('Fee',
                       validators=[DataRequired()],
                       render_kw={'class': 'form-control'})
    submit = SubmitField('Submit',
                         validators=[DataRequired()],
                         render_kw={'class': 'form-control btn btn-primary'})


class ClaimForm(FlaskForm):
    unhashed_id = StringField('ID',
                              validators=[DataRequired()],
                              render_kw={'class': 'form-control',
                                         'placeholder': 'Unhashed ID'})
    submit = SubmitField('Submit',
                         validators=[DataRequired()],
                         render_kw={'class': 'form-control btn btn-primary'})
