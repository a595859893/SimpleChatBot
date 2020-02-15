from flask import Flask
import json
from cmdui import CmdUI

app = Flask(__name__)
robot = CmdUI()

app.route('/')
def index():
    robot.cmd_input(inputs)
    return json.dump({
        messages:robot.get_outputs()
    })

if __name__=='__main__':
    app.run()