import requests
from flask import render_template, redirect, flash

from blockchain import app, my_chain, chain_settings, MY_URL, log, me
from blockchain.classes import *
from blockchain.forms import TransactionForm, ClaimForm
from blockchain.views.api import find_user


def spread_message(api_url, json_data, success_url, fail_url):
    acceptance = {'yes': 0, 'no': 0}
    for node in NODES:
        r = requests.post(f'{node}/api/{api_url}', json=json_data)
        response = r.json()
        log.append({'message': response['message'], 'time': timestamp()})
        if r.status_code == 200:
            acceptance['yes'] += 1
        else:
            acceptance['no'] += 1
    if acceptance['yes'] > acceptance['no']:
        flash('Success!', 'success')
        return redirect(success_url)
    else:
        flash('The majority did not accept. Your reason: ' + log[-1]['message'], 'danger')
        return redirect(fail_url)


@app.context_processor
def name():
    return {'name': chain_settings.CHAIN_NAME}


@app.context_processor
def base_reward():
    return {'base_reward': chain_settings.BASE_MINER_REWARD}


@app.context_processor
def my_url():
    return {'my_url': MY_URL}


@app.route('/', methods=['GET'])
@app.route('/index', methods=['GET'])
def index():
    return render_template('index.html', selected='home', blocks=my_chain.chain)


@app.route('/claim', methods=['GET', "POST"])
def claim_user():
    form = ClaimForm()
    if form.validate_on_submit():
        return spread_message(api_url='accept_user',
                              json_data=to_json({
                                  'id': form.unhashed_id.data,
                                  'alias': me.alias,
                                  'node_url': MY_URL,
                                  'public_key': me.public_key,
                              }),
                              success_url='/profile',
                              fail_url='/claim')
    return render_template('claim.html', selected='claim', form=form)


@app.route('/profile', methods=['GET'])
def view_profile():
    return render_template('profile.html', selected='profile')


@app.route('/submit', methods=['GET', 'POST'])
def submit():
    form = TransactionForm()
    if form.validate_on_submit():
        fields = {'value': form.value.data,
                  'fee': form.fee.data,
                  'signature': 'None'}
        sender = find_user(form.sender_public_key.data.encode().decode('unicode_escape'))
        if not sender:
            flash('Sender does not exist', 'danger')
            return redirect('/submit')
        else:
            fields['sender'] = to_dict(sender)
            sender.private_key = form.s_private_key.data.encode().decode('unicode_escape')
        recipient = find_user(form.recipient_public_key.data.encode().decode('unicode_escape'))
        if not recipient:
            flash('Recipient does not exist', 'danger')
            return redirect('/submit')
        else:
            fields['recipient'] = to_dict(recipient)
        fields['time'] = timestamp()
        transaction = transaction_from_dict(fields)
        sender.sign(transaction)
        return spread_message(api_url='accept_transaction',
                              json_data=to_json(transaction),
                              success_url='/',
                              fail_url='/submit')
    return render_template('submit.html', selected='submit', form=form)
