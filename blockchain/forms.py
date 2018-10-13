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
                                             'placeholder': 'Sender Private Key',
                                             'rows': 7})
    value = IntegerField('Value',
                         validators=[DataRequired()],
                         render_kw={'class': 'form-control',
                                    'placeholder': 'Value'})
    fee = IntegerField('Fee',
                       validators=[DataRequired()],
                       render_kw={'class': 'form-control',
                                  'placeholder': 'Fee'})
    submit = SubmitField('Submit',
                         validators=[DataRequired()],
                         render_kw={'class': 'form-control btn btn-primary'})


class ClaimForm(FlaskForm):
    unhashed_id = StringField('Register your ID on the blockchain',
                              validators=[DataRequired()],
                              render_kw={'class': 'form-control',
                                         'placeholder': 'Unhashed ID'})
    alias = StringField('Alias',
                              validators=[DataRequired()],
                              render_kw={'class': 'form-control',
                                         'placeholder': 'Alias'})

    node_url = StringField('ID',
                              validators=[DataRequired()],
                              render_kw={'class': 'form-control',
                                         'placeholder': 'Node URL'})
    public_key = TextAreaField('Alias',
                               validators=[DataRequired()],
                               render_kw={'class': 'form-control',
                                          'placeholder': 'Public Key',
                                          'rows': 15})
    submit = SubmitField('Submit',
                         validators=[DataRequired()],
                         render_kw={'class': 'form-control btn btn-primary'})
