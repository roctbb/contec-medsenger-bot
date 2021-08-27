from flask import jsonify
from manage import *
from medsenger_api import AgentApiClient
from helpers import *
from models import *

medsenger_api = AgentApiClient(API_KEY, MAIN_HOST, AGENT_ID, API_DEBUG)


@app.route('/')
def index():
    return "Waiting for the thunder"


@app.route('/status', methods=['POST'])
@verify_json
def status(data):
    answer = {
        "is_tracking_data": True,
        "supported_scenarios": [],
        "tracked_contracts": [contract.id for contract in Contract.query.filter_by(active=True).all()]
    }

    return jsonify(answer)


@app.route('/init', methods=['POST'])
@verify_json
def init(data):
    contract = Contract.query.filter_by(id=data.get('contract_id')).first()
    if not contract:
        db.session.add(Contract(id=data.get('contract_id')))
    else:
        contract.active=True

    db.session.commit()
    return "ok"


@app.route('/remove', methods=['POST'])
@verify_json
def remove(data):
    c = Contract.query.filter_by(id=data.get('contract_id')).first()
    if c:
        contract.active=False
        db.session.commit()
    return "ok"


# settings and views
@app.route('/settings', methods=['GET'])
@verify_args
def get_settings(args, form):
    return "Этот интеллектуальный агент не требует настройки."


@app.route('/message', methods=['POST'])
@verify_json
def message(data):

    attachments = data.get('message', {}).get('attachments', [])

    for attachment in attachments:
        if ".csv" in attachment.get('name'):
            pass




    return "ok"




with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(HOST, PORT, debug=API_DEBUG)
