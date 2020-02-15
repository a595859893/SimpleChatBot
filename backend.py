import json
from flask import Flask
from cmdui import CmdUI

app = Flask(__name__)
app.config.from_mapping(DEBUG=False, TESTING=False)
robot = CmdUI()

app.route('/')


def index():
    robot.cmd_input(inputs)
    return json.dump({messages: robot.get_outputs()})


if __name__ == '__main__':
    app.run()