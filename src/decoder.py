import re
from knowledge import Knowledge, Context


class Decoder:
    """
    利用上下文匹配替换模板关键字，并判断条件
    """

    def __init__(self):
        pass

    def decode(self, text: str, ctx: list, knowledge: Knowledge) -> str:
        # print(ctx)
        self.known = knowledge
        return self.match_dialog(text, ctx)

    def match_dialog(self, text: str, ctx: list) -> str:
        """
        将模板按照上下文填充为想要的样子
        """
        sub_succ = True

        def sub_func(match_obj):
            nonlocal sub_succ
            if sub_succ:
                match_str = match_obj.group(1)
                cond = None
                if match_str[0] == '?':
                    cond = True
                elif match_str[0] == '!':
                    cond = False

                if cond is not None:
                    # 条件匹配
                    words = match_str[1:].split(" ")
                    # print("match:", self.match_word(words, ctx), words)
                    if (self.match_word(words, ctx) is None) is cond:
                        sub_succ = False
                else:
                    # 实体填充
                    word = self.match_word([match_str], ctx)
                    if word is not None:
                        return word
                    sub_succ = False
            return ""

        dialog = re.sub(r"\[(.+?)\]", sub_func, text)

        return dialog if sub_succ else None

    def construct_evdience(self, evdi: str, ctx: Context) -> list:
        re_tag = re.compile(r"(.+?)\|(.+)")
        evdience = []
        for e in evdi.split(" "):
            match = re_tag.match(e)
            if match is not None:
                word = match.group(1)
                tag = match.group(2)

                entity = ctx.find(word, tag=tag)
                if entity is None:
                    return None
                evdience.append(entity)

        return evdience

    def match_word(self, words: list, ctx: Context) -> str:
        """
        判断words内的内容是否在上下文中存在且指向一文本
        """
        re_text = re.compile(r'"(.+?)"')
        re_evdi = re.compile(r'(.+?)\{(.+)\}')
        re_tag = re.compile(r"(.+?)\|(.+)")
        text = None
        for word in words:
            # print("word:", word, words)
            match = re_text.match(word)
            if match is not None:
                match = match.group(1)
            else:
                evdi, tag = None, None
                match = re_evdi.match(word)
                if match is not None:
                    word = match.group(1)
                    evdi = self.construct_evdience(match.group(2), ctx)
                    if evdi is None:
                        return None

                match = re_tag.match(word)
                if match is not None:
                    word = match.group(1)
                    tag = match.group(2)

                # print(word, tag, evdi)
                match = ctx.find(word, tag, evdi)
                if match is None:
                    return None
                match = match.get_text()

            # print(word, ":", text, match)
            if text is None:
                text = match
            elif text != match:
                return None

        return text
