import json
from flask import Flask, request
from cmdui import CmdUI

app = Flask(__name__)
app.config.from_mapping(DEBUG=False, TESTING=False)
robot = CmdUI()


@app.route('/api/chat')
def chat():
    try:
        data = request.get_data()
        json_re = json.loads(data)
        robot.cmd_input(json_re["message"])
        return json.dumps({
            "ok":True,
            "messages": robot.get_outputs()
        })
    except Exception as e:
        return json.dumps({
            "ok":False
        })


if __name__ == '__main__':
    from waitress import serve
    serve(app, host="0.0.0.0", port=3001)