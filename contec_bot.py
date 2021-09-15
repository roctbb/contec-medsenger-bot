import base64

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
        contract.active = True

    medsenger_api.send_message(data.get('contract_id'),
                               'К каналу консультирования подключен интеллектуальный агент для спирометров Contec. Просто отправьте в чат CSV файл из мобильного приложения (через меню "поделиться"), и мы автоматически положим все измерения в вашу медицинскую карту.',
                               only_patient=True)

    db.session.commit()
    return "ok"


@app.route('/remove', methods=['POST'])
@verify_json
def remove(data):
    c = Contract.query.filter_by(id=data.get('contract_id')).first()
    if c:
        c.active = False
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
    contract = Contract.query.filter_by(id=data.get('contract_id')).first()

    if not contract or not contract.active:
        abort(404)

    for attachment_description in attachments:
        if ".csv" in attachment_description.get('name'):
            attachments = medsenger_api.get_attachment(attachment_description['id'])
            text = base64.b64decode(attachments['base64']).decode('utf-8')

            if "number,date,time,FVC(L),FEV1(L)" in text:
                lines = text.split('\n')

                header, data = lines[0], lines[1:]

                names = list(map(lambda x: x[:x.find('(')], header.split(',')[3:]))

                max_time = None
                count = 0

                for line in data:
                    if not line:
                        continue

                    packet = []

                    n, date, time, *values = line.split(',')
                    time = datetime.strptime(date + " " + time, '%Y/%m/%d %H:%M:%S')

                    if contract.last_import and time <= contract.last_import:
                        continue

                    if not max_time or max_time < time:
                        max_time = time

                    values = map(float, values)
                    for i, value in enumerate(values):
                        packet.append([names[i], value])

                    count += 1

                    medsenger_api.add_records(contract.id, packet, record_time=time.timestamp())

                if max_time:
                    contract.last_import = max_time
                    db.session.commit()

                    medsenger_api.send_message(contract.id,
                                               'Ага, похоже Вы прислали файл с данными спирометра. Спасибо, новые измерения ({}) добавлены в Вашу медицинскую карту.'.format(count),
                                               only_patient=True, forward_to_doctor=False)
                else:
                    medsenger_api.send_message(contract.id,
                                               'Вы прислали файл с данными спирометра, но все измерения в нем уже были добавлены в Вашу медицинскую карту. Как будут новые - присылайте снова!',
                                               only_patient=True, forward_to_doctor=False)
    return "ok"


with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(HOST, PORT, debug=API_DEBUG)
