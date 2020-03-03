import re
import utils
from knowledge import Knowledge, Context, Instance


class Encoder:
    """
    分析语句的匹配情况，并解析语句中关注的上下文
    """

    def __init__(self):
        pass

    def encode(self, text: str, entity: str, knowledge: Knowledge) -> list:
        self.known = knowledge
        ctx = Context()
        if self.match_single_entity(text, entity, ctx):
            return ctx
        return None

    def match_single_entity(self, text: str, entity: str,
                            ctx: Context) -> bool:
        """
        匹配单个entity，如果单tag有规则能拆成多个entity，则转为匹配多个entity
        """
        # print(text, entity, self.known.get_sub(entity))
        # 处理entity，将其中的标记标签去除
        tag = re.match(r"^([^\[\]]+?)\|([^\[\]]+)$", entity)
        if tag is not None:
            entity, tag = tag.group(1), tag.group(2)
            # 确定匹配到的是否符合上下文要求
            ctx_entity = ctx.find(entity, tag)
            # 此处匹配不会改变Context，所以可以直接返回
            if ctx_entity is not None:
                return (text == ctx_entity)

        # 编译正则表达式，供后取使用
        match_regex = re.compile(r"\[(.+?)\](?=[^\[]|$)")
        # 遍历需要匹配的entity下所有的子实体
        for sub_entity in self.known.get_sub(entity):
            # 获取子实体
            match_text = sub_entity.get_text()
            # 符号转移，避免文本中原有的符号被当成正则表达式处理
            match_escape = utils.escape(match_text)
            # 构造entity的正则表达式，将需要进行实体判断的部分用通配符取代
            match_re = "^%s$" % match_regex.sub(r"(.+?)", match_escape)

            match = re.match(match_re, text)
            if match:
                match_succ = True
                ctx.new_stack()

                # 判断实体匹配中是否存在子实体需要匹配
                match_entity = match_regex.findall(match_text)
                # 弱存在子实体，则下述循环会逐一判断每个子实体
                for sub_text, sub_entity in zip(match.groups(), match_entity):
                    # 判断是否存在相邻子实体情况
                    sub_entities = sub_entity.split("][")
                    if len(sub_entities) == 1:
                        # 不存在，可以直接进行单个匹配
                        match_succ = self.match_single_entity(
                            sub_text, sub_entities[0], ctx)
                    else:
                        # 存在相邻子实体，需要进行分词匹配
                        match_succ = self.match_multi_entities(
                            sub_text, sub_entities, ctx)

                    # 若无法匹配成功，则不属于此实体
                    if not match_succ:
                        break

                if match_succ:
                    # 成功匹配，记录上下文
                    ctx.append(Instance(entity, text, None, tag=tag))
                    ctx.apply_stack()
                    return True
                else:
                    # 匹配失败，抛弃上下文
                    ctx.aborat_stack()
                    print("aborat")

        return False

    def match_multi_entities(self, text: str, entities: list,
                             ctx: Context) -> bool:
        """
        匹配多个tag相邻的情况，通过遍历每种分割情况来确定结果
        """
        # 目前是倒数匹配，从最后一个开始匹配起
        # 效率有点低，考虑启发式算法是先从word_type里单词最少的找起
        # 不过待填（也可能不填？）

        # 递归基
        if len(entities) == 0 and text == "":
            return True

        # 递归步
        for i in range(len(text) - 1, -1, -1):
            if self.match_single_entity(text[i:], entities[-1], ctx):
                temp_tag = entities.pop()
                if self.match_multi_entities(text[:i], entities, ctx):
                    ctx.append(Instance(entities, text[i:], None))
                    # print("muti:", ctx)
                    return True
                entities.append(temp_tag)

        return False
