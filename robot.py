import random

from knowledge import Knowledge
from encoder import Encoder
from decoder import Decoder


class Robot:
    def __init__(self, **kwargs):
        self.knowledge = Knowledge(**kwargs)
        self.encoder = Encoder()
        self.decoder = Decoder()

    def reply(self, chat: str) -> str:
        for que_tag in self.knowledge.get_dialog_question():
            ctx = self.encoder.encode(chat, que_tag, self.knowledge)
            # print(ctx)
            if ctx is not None:
                ctx.infer(self.knowledge)
                # print(ctx)
                choice = []
                for dialog in self.knowledge.get_dialog_answer(que_tag):
                    # print(dialog)
                    dialog = self.decoder.decode(dialog, ctx, self.knowledge)
                    if dialog is not None:
                        choice.append(dialog)

                if len(choice) == 0:
                    continue

                return random.choice(choice)

        return None

    def study_entity(self, tag: str, match: str):
        self.knowledge.study_entity(tag, match)

    def study_connect(self, pre: dict, post: dict, double: bool):
        self.knowledge.study_connect(pre, post, double)

    def study_dialog(self, question: str, answer: str):
        self.knowledge.study_dialog(question, answer)

    def save(self):
        self.knowledge.save()

    def load(self):
        self.knowledge.load()