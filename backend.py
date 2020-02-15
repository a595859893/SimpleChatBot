import json
from flask import Flask, request
from cmdui import CmdUI

app = Flask(__name__)
app.config.from_mapping(DEBUG=False, TESTING=False)
robot = CmdUI()


@app.route('/chat')
def chat():
    data = request.get_data()
    json_re = json.loads(data)
    print(json_re)
    robot.cmd_input(json_re["message"])
    return json.dump({messages: robot.get_outputs()})


if __name__ == '__main__':
    from waitress import serve
    serve(app, host="0.0.0.0", port=3001)