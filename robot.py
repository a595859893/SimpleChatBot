import pickle
import re
import random
import os


class Robot:
    FILENAME_KNOW = "chatbot.know"
    FILENAME_DIALOG = "chatbot.dialog"

    def __init__(self, path="./data/", load=True):
        self.path = path
        self.known = {}
        self.dialog = {}

        if load:
            self.load()

    def study_knowledge(self, tag: str, match: str):
        if tag not in self.known:
            self.known[tag] = []

        knowledge = self.known[tag]
        knowledge.append(match)

    def study_dialog(self, question: str, answer: str):
        que_tag = None
        for tag in self.known.keys():
            if question in self.known.get(tag, []):
                que_tag = tag
                break
        if que_tag is None:
            que_tag = "问题 %d" % len(self.dialog.keys())

        if que_tag not in self.dialog:
            self.dialog[que_tag] = []

        self.study_knowledge(que_tag, question)
        self.dialog[que_tag].append(answer)

    def match_single_tag(self, text: str, tag: str, ctx: list) -> bool:
        for match_text in self.known.get(tag, []):
            match_tags = re.findall(r"\[(.+?)\]([^\[]|$)", match_text)
            match_re = "^%s$" % re.sub(r"\[(.+?)\]([^\[]|$)", r"(.+?)\2",
                                       match_text)
            match = re.match(match_re, text)

            if match:
                match_succ = True
                temp_ctx = []
                for sub_text, sub_tag in zip(match.groups(), match_tags):
                    # 括号导致匹配是个元组，从里面拆出我们想要的
                    sub_tag = sub_tag[0]
                    sub_tags = sub_tag.split("][")
                    if len(sub_tags) == 1:
                        match_succ = self.match_single_tag(
                            sub_text, sub_tags[0], temp_ctx)
                    else:
                        match_succ = self.match_multi_tag(
                            sub_text, sub_tags, temp_ctx)

                    if not match_succ:
                        break

                if match_succ:
                    temp_ctx.append((text, tag))
                    ctx.extend(temp_ctx)
                    # print("single:", ctx)
                    return True

    def match_multi_tag(self, text: str, tags: list, ctx: list) -> bool:
        # 目前是倒数匹配，从最后一个开始匹配起
        # 效率有点低，考虑启发式算法是先从word_type里单词最少的找起
        # 不过待填（也可能不填？）

        # 递归基
        if len(tags) == 0 and text == "":
            return True

        # 递归步
        for i in range(len(text) - 1, -1, -1):
            if self.match_single_tag(text[i:], tags[-1], ctx):
                temp_tag = tags.pop()
                if self.match_multi_tag(text[:i], tags, ctx):
                    ctx.append((text[i:], temp_tag))
                    # print("muti:", ctx)
                    return True
                tags.append(temp_tag)

        return False

    def match_dialog(self, text: str, ctx: list) -> str:
        sub_succ = True

        def sub_func(match_obj):
            nonlocal sub_succ
            if sub_succ:
                for ctx_text, ctx_tag in ctx:
                    if match_obj.groups(0)[0] == ctx_tag:
                        return ctx_text
                sub_succ = False
            return ""

        dialog = re.sub(r"\[(.+?)\]", sub_func, text)

        return dialog if sub_succ else None

    def reply(self, chat: str) -> str:
        for que_tag in self.dialog.keys():
            ctx = []
            if self.match_single_tag(chat, que_tag, ctx):
                choice = []
                for dialog in self.dialog[que_tag]:
                    dialog = self.match_dialog(dialog, ctx)
                    if dialog is not None:
                        choice.append(dialog)

                if len(choice) == 0:
                    continue

                return random.choice(choice)

        return None

    def save(self):
        if not os.path.exists(self.path):
            os.makedirs(self.path)

        dialog_path = "%s%s" % (self.path, Robot.FILENAME_DIALOG)
        know_path = "%s%s" % (self.path, Robot.FILENAME_KNOW)

        with open(dialog_path, "wb") as data:
            pickle.dump(self.dialog, data)
        with open(know_path, "wb") as data:
            pickle.dump(self.known, data)

    def load(self):
        dialog_path = "%s%s" % (self.path, Robot.FILENAME_DIALOG)
        know_path = "%s%s" % (self.path, Robot.FILENAME_KNOW)

        if os.path.exists(dialog_path):
            with open(dialog_path, "rb") as data:
                self.dialog = pickle.load(data)
        if os.path.exists(know_path):
            with open(know_path, "rb") as data:
                self.known = pickle.load(data)
