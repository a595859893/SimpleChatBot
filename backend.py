import json
from flask import Flask, request
from cmdui import CmdUI

app = Flask(__name__)
app.config.from_mapping(DEBUG=False, TESTING=False)
robot = CmdUI()


@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.get_data()
        json_re = json.loads(data)
        print(data,json_re)
        context = {
            "state":json_re["state"],
            "buffer":json_re["buffer"]
        }

        context = robot.context_input(json_re["message"],context)
        print(context)
        return json.dumps({
            "ok":True,
            "state":context["state"],
            "buffer":context["buffer"],
            "messages": robot.get_outputs()
        })

    except Exception as e:
        print(e)
        return json.dumps({
            "ok":False
        })


if __name__ == '__main__':
    from waitress import serve
    serve(app, host="0.0.0.0", port=3001)