from robot import Robot
import argparse
import re


class CmdUI:
    STATE_CHAT = 0
    STATE_UNKNOW = 1
    STATE_TEACH_ENTITY = 2
    STATE_TEACH_CONN = 3
    STATE_TEACH_DIAG = 4

    def __init__(self, **kwargs):
        self.robot = Robot(**kwargs)
        self.state = CmdUI.STATE_CHAT
        self.buffer = None
        self.output = []

    def append_output(self, output: str):
        self.output.append(output)

    def get_outputs(self):
        out = self.output
        out.reverse()
        self.output = []
        return out

    def cmd_input(self, chat: str):
        if self.cmd_parse(chat):
            return

        # 处理消息
        if self.state == CmdUI.STATE_CHAT:
            answer = self.robot.reply(chat)
            if answer is not None:
                self.append_output(answer)
            else:
                self.state = CmdUI.STATE_UNKNOW
                self.buffer = chat
                self.append_output("我不太明白，遇上这样的句子我应该怎么回复？")
        elif self.state == CmdUI.STATE_UNKNOW:
            self.state = CmdUI.STATE_CHAT
            self.robot.study_dialog(self.buffer, chat)
            self.append_output("我明白了！")
        elif self.state == CmdUI.STATE_TEACH_DIAG:
            if self.buffer is None:
                self.buffer = chat
                self.append_output("我应该怎么回复？")
            else:
                for answer in chat.split(";"):
                    # print(self.buffer, answer)
                    self.robot.study_dialog(self.buffer, answer)
                self.buffer = None
                self.append_output("我明白了！")
        elif self.state == CmdUI.STATE_TEACH_ENTITY:
            for teach in chat.split(';'):
                part = teach.split(":")
                if len(part) != 2:
                    continue
                tag = part[0]
                for known in part[1].split(" "):
                    self.robot.study_entity(tag, known)

            self.append_output("我明白了！")
        elif self.state == CmdUI.STATE_TEACH_CONN:
            part = re.match(r"(.+?)(<->|->)(.+)", chat)
            if part is not None:
                pre_dict = self.make_parse_dict(part.group(1))
                post_dict = self.make_parse_dict(part.group(3))
                # print(pre_dict, post_dict)
                if pre_dict is not None and post_dict is not None:
                    double = part.group(2) == "<->"
                    self.robot.study_connect(pre_dict, post_dict, double)
            self.append_output("我明白了！")

    def make_parse_dict(self, part: str) -> dict:
        post_dict = {}
        for pair in part.split(" "):
            pair = pair.split(":")
            if len(pair) == 2:
                post_dict[pair[0]] = pair[1]
            elif len(pair) == 1:
                post_dict[pair[0]] = None
            else:
                return None
        return post_dict

    def cmd_parse(self, cmd: str) -> bool:
        # 机器人状态转移
        if cmd == "教导实体":
            self.state = CmdUI.STATE_TEACH_ENTITY
            self.buffer = None
            self.append_output("进入实体学习模式")
            return True
        elif cmd == "教导联系":
            self.state = CmdUI.STATE_TEACH_CONN
            self.buffer = None
            self.append_output("进入联系学习模式")
            return True
        elif cmd == "教导对话":
            self.state = CmdUI.STATE_TEACH_DIAG
            self.buffer = None
            self.append_output("进入对话学习模式")
            return True
        elif cmd == "聊天":
            self.state = CmdUI.STATE_CHAT
            self.append_output("进入聊天模式")
            return True
        return False


if __name__ == "__main__":
    # 参数
    arg = argparse.ArgumentParser()
    arg.add_argument("-test", action="store_true")
    arg = arg.parse_args()
    test_bag = []
    if arg.test:
        with open("./test/text_inputs.txt", "r", encoding="utf8") as text:
            for line in text:
                test_bag.append(line.replace("\n", ''))
        test_bag.reverse()

    # 界面
    ROBOT_NAME = "机器人"
    YOUR_NAME = "你"
    ui = CmdUI(load=not arg.test)

    # 聊天
    while True:
        if arg.test:
            if len(test_bag) == 0:
                exit()
            inputs = test_bag.pop()
            print("%s\t%s" % (YOUR_NAME, inputs))
        else:
            inputs = input("%s\t" % YOUR_NAME)

        ui.cmd_input(inputs)
        for output in ui.get_outputs():
            print("%s\t%s" % (ROBOT_NAME, output))
