import requests
import requests.exceptions
import json

from app import SendPulseToken, db, app

URL = 'https://api.sendpulse.com'


def send(path, *, data, method):

    def _send(token):
        headers = {'Authorization': '{0} {1}'.format(token.token_type, token.access_token)}
        return requests.request(method, URL + path, json=data, headers=headers)

    resp = _send(get_token())
    if resp.status_code == 401:  # UNAUTHORIZED, token expired.
        resp = _send(authorize())

    try:
        resp.raise_for_status()
    except requests.exceptions.HTTPError:
        app.logger.error('*' * 80)
        app.logger.error('This request lead to error: headers={0}, body={1}'
                         .format(resp.request.headers, resp.request.body))
        app.logger.error('-' * 80)
        app.logger.error('Error response: [{}] {}'.format(resp.status_code, resp.text))
        app.logger.error('*' * 80)
        raise

    return resp.json()


def authorize():
    data = {
        'grant_type': 'client_credentials',
        'client_id': app.config['SENDPULSE_CLIENT_ID'],
        'client_secret': app.config['SENDPULSE_CLIENT_SECRET'],
    }
    response = requests.post(URL + '/oauth/access_token', json=data)
    token = SendPulseToken(**response.json())
    try:
        db.session.add(token)
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise
    return token


def get_token():
    token = SendPulseToken.query.order_by(SendPulseToken.gotten.desc()).first()
    return authorize() if token is None else token


def add_address(address):
    abook_id = app.config['SENDPULSE_ADDRESSBOOK_ID']

    data = {
        'emails': json.dumps([{'email': address}])
    }
    response = send('/addressbooks/{}/emails'.format(abook_id), data=data, method='POST')

    if response['result'] is not True:
        raise RuntimeError("Address '{0}' not submitted to SendPulse: {1}."
                           .format(address, response))

    app.logger.info("Address '{}' submitted to SendPulse.".format(address))
