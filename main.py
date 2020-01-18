import pickle
import re
import random
import os


class Robot:
    def __init__(self, path="./chat.data"):
        self.path = path
        if os.path.exists(path):
            with open(self.path, "rb") as data:
                self.seq = pickle.load(data)
        else:
            self.seq = {}

    def study_seq(self, que: str, ans: str):
        answers = self.seq.get(que, [])
        if ans not in answers:
            answers.append(ans)
        self.seq[que] = answers

        with open(self.path, "wb") as data:
            pickle.dump(self.seq, data)

    def reply(self, chat: str) -> str:
        for question in self.seq.keys():
            chat = "^%s$" % chat
            match = re.match(chat, question)
            # 随机选择一个匹配项进行回答
            if match:
                answers = self.seq.get(question, [])
                ans = random.choice(answers)
                return "{answer}".format(answer=ans)

        return None


if __name__ == "__main__":
    # 机器人初始化
    robot = Robot()

    # 聊天状态机状态初始化
    STATE_CHAT = 0
    STATE_UNKNOW = 1
    STATE_TEACH_SEQUENCE = 2

    state = STATE_CHAT
    buffer = None
    # 聊天时间
    while True:
        chat = input("你：")

        # 机器人状态转移
        if chat == "教导句子":
            state = STATE_TEACH_SEQUENCE
            buffer = None
            print("机器人：进入句子学习模式")
            continue
        elif chat == "聊天":
            state = STATE_CHAT
            print("机器人：进入聊天模式")
            continue

        if state == STATE_CHAT:
            answer = robot.reply(chat)
            if answer is not None:
                print("机器人：{answer}".format(answer=answer))
            else:
                state = STATE_UNKNOW
                buffer = chat
                print("机器人：我不太明白，遇上这样的句子我应该怎么回复？")
        elif state == STATE_TEACH_SEQUENCE:
            if buffer is None:
                buffer = chat
                print("机器人：我应该怎么回复？")
            else:
                robot.study_seq(buffer, chat)
                buffer = None
                print("机器人：我明白了！")
        elif state == STATE_UNKNOW:
            state = STATE_CHAT
            robot.study_seq(buffer, chat)
            print("机器人：我明白了！")
