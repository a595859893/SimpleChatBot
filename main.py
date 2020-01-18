import pickle
import re
import random
import os
import argparse
from typing import Union

FILENAME_SEQ = "chatbot.seq"
FILENAME_WORD = "chatbot.word"


class Robot:
    def __init__(self, path="./data/", load=True):
        self.path = path
        self.seq = {}
        self.word = {}
        if load:
            self.load()

    def reply(self, chat: str) -> str:
        for question in self.seq.keys():
            que_word = re.findall(r"\[(.+?)\][^\[]", question)
            que = "^%s$" % re.sub(r"\[(.+?)\]([^\[])", r"(.+?)\2", question)
            match = re.match(que, chat)
            # 随机选择一个匹配项进行回答
            if match:
                # 检查单词是否符合类型
                match_succ = True
                for word, word_type in zip(match.groups(), que_word):
                    if not self.is_word_type(word, word_type):
                        match_succ = False
                    break

                if match_succ:
                    answers = self.seq.get(question, [])
                    ans = random.choice(answers)
                    return "{answer}".format(answer=ans)

        return None

    def study_seq(self, que: str, ans: str):
        answers = self.seq.get(que, [])

        if ans not in answers:
            answers.append(ans)
        self.seq[que] = answers

        self.save()

    def study_word(self, word_type: str, word: str):
        word_list = self.word.get(word_type, [])

        if word not in word_list:
            word_list.append(word)
        self.word[word_type] = word_list

        self.save()

    def is_word_type(self, word: str, word_type: Union[str, list]):
        # 目前是倒数匹配，从最后一个开始匹配起
        # 效率有点低，考虑启发式算法是先从word_type里单词最少的找起
        # 不过待填（也可能不填？）
        if isinstance(word_type, str):
            word_type = word_type.split("][")
        elif len(word_type) == 0 and word == "":
            return True

        word_list = self.word.get(word_type[-1], [])
        for i in range(len(word) - 1, -1, -1):
            if word[i:] in word_list:
                temp_type = word_type.pop()
                if self.is_word_type(word[:i], word_type):
                    return True
                word_list.append(temp_type)

        return False

    def save(self):
        seq_path = "%s%s" % (self.path, FILENAME_SEQ)
        word_path = "%s%s" % (self.path, FILENAME_WORD)

        with open(seq_path, "wb") as data:
            pickle.dump(self.seq, data)
        with open(word_path, "wb") as data:
            pickle.dump(self.word, data)

    def load(self):
        seq_path = "%s%s" % (self.path, FILENAME_SEQ)
        word_path = "%s%s" % (self.path, FILENAME_WORD)

        if os.path.exists(seq_path):
            with open(seq_path, "rb") as data:
                self.seq = pickle.load(data)
        if os.path.exists(word_path):
            with open(word_path, "rb") as data:
                self.word = pickle.load(data)


if __name__ == "__main__":
    arg = argparse.ArgumentParser()
    arg.add_argument("-test", action="store_true")
    arg = arg.parse_args()
    test_bag = []
    if arg.test:
        with open("./test/text_inputs.txt", "r", encoding="utf8") as text:
            for line in text:
                test_bag.append(line.replace("\n", ''))
        test_bag.reverse()

    # 机器人初始化
    robot = Robot(load=not arg.test)
    ROBOT_NAME = "机器人"
    YOUR_NAME = "你"
    # 聊天状态机状态初始化
    STATE_CHAT = 0
    STATE_UNKNOW = 1
    STATE_TEACH_SEQ = 2
    STATE_TEACH_WORD = 3

    state = STATE_CHAT
    buffer = None
    # 聊天时间
    while True:
        if arg.test:
            if len(test_bag) == 0:
                exit()

            chat = test_bag.pop()
            print("%s:%s" % (YOUR_NAME, chat))
        else:
            chat = input("%s：" % YOUR_NAME)

        # 机器人状态转移
        if chat == "教导句子":
            state = STATE_TEACH_SEQ
            buffer = None
            print("%s：进入句子学习模式" % ROBOT_NAME)
            continue
        elif chat == "教导词语":
            state = STATE_TEACH_WORD
            buffer = None
            print("%s：进入词语学习模式" % ROBOT_NAME)
            print("%s：你想教我什么类型的词语？" % ROBOT_NAME)
            continue
        elif chat == "聊天":
            state = STATE_CHAT
            print("%s：进入聊天模式" % ROBOT_NAME)
            continue

        # 处理消息
        if state == STATE_CHAT:
            answer = robot.reply(chat)
            if answer is not None:
                print("%s：{answer}".format(answer=answer) % ROBOT_NAME)
            else:
                state = STATE_UNKNOW
                buffer = chat
                print("%s：我不太明白，遇上这样的句子我应该怎么回复？" % ROBOT_NAME)
        elif state == STATE_UNKNOW:
            state = STATE_CHAT
            robot.study_seq(buffer, chat)
            print("%s：我明白了！" % ROBOT_NAME)
        elif state == STATE_TEACH_SEQ:
            if buffer is None:
                buffer = chat
                print("%s：我应该怎么回复？" % ROBOT_NAME)
            else:
                robot.study_seq(buffer, chat)
                buffer = None
                print("%s：我明白了！" % ROBOT_NAME)
        elif state == STATE_TEACH_WORD:
            if buffer is None:
                buffer = chat
                print("%s：这种类型的词语有哪些呢？(使用空格分隔)" % ROBOT_NAME)
            else:
                words = chat.split(' ')
                for word in words:
                    robot.study_word(buffer, word)
                buffer = None
                print("%s：我明白了！你还想教我什么类型的单词吗？" % ROBOT_NAME)
