import pickle
import os


class Knowledge:
    """
    先验知识的保存
    """
    FILENAME_KNOW = "chatbot.know"
    FILENAME_DIALOG = "chatbot.dialog"

    def __init__(self, path="./data/", load=True):
        self.path = path
        self.known = {}
        self.dialog = {}

        if load:
            self.load()

    def study_entity(self, entity: str, sub: str):
        if entity not in self.known:
            self.known[entity] = Entity(entity)

        if sub not in self.known:
            self.known[sub] = Entity(sub)

        if not self.known[entity].has_sub(sub):
            self.known[entity].append(self.known[sub])

    def study_connect(self, pre: dict, post: dict, double: bool):
        conn = Statement(pre, post, double)
        for entity in pre:
            if entity not in self.known:
                self.known[entity] = Entity(entity)
            self.known[entity].add_conn(conn)

        if double:
            for entity in post:
                if entity not in self.known:
                    self.known[entity] = Entity(entity)
                self.known[entity].add_conn(conn)

    def study_dialog(self, question: str, answer: str):
        que_tag = None
        for entity in self.known.keys():
            if self.known.get(entity, Entity(entity)).has_sub(question):
                que_tag = entity
                break
        if que_tag is None:
            que_tag = "问题 %d" % len(self.dialog.keys())

        if que_tag not in self.dialog:
            self.dialog[que_tag] = []

        self.study_entity(que_tag, question)
        self.dialog[que_tag].append(answer)

    def get_dialog_question(self) -> dict:
        return self.dialog.keys()

    def get_dialog_answer(self, question: str) -> dict:
        return self.dialog.get(question, [])

    def get_conn(self, entity: str) -> list:
        return self.known.get(entity, Entity(entity)).get_conn()

    def get_sub(self, entity: str) -> list:
        return self.known.get(entity, Entity(entity)).get_sub()

    def save(self):
        if not os.path.exists(self.path):
            os.makedirs(self.path)

        dialog_path = "%s%s" % (self.path, Knowledge.FILENAME_DIALOG)
        know_path = "%s%s" % (self.path, Knowledge.FILENAME_KNOW)

        with open(dialog_path, "wb") as data:
            pickle.dump(self.dialog, data)
        with open(know_path, "wb") as data:
            pickle.dump(self.known, data)

    def load(self):
        dialog_path = "%s%s" % (self.path, Knowledge.FILENAME_DIALOG)
        know_path = "%s%s" % (self.path, Knowledge.FILENAME_KNOW)

        if os.path.exists(dialog_path):
            with open(dialog_path, "rb") as data:
                self.dialog = pickle.load(data)
        if os.path.exists(know_path):
            with open(know_path, "rb") as data:
                self.known = pickle.load(data)


class Instance:
    """
    entity(string):抽象
    tag(string):区分抽象的标签
    text(string):实例
    evidence(list):推导依据
    """

    def __init__(self, entity: str, text: str, evidence: list, tag=None):
        self.entity = entity
        self.text = text
        self.evidence = evidence
        self.tag = tag

    def get_entity(self): return self.entity
    def get_text(self): return self.text
    def get_evidence(self): return self.evidence
    def get_tag(self): return self.tag

    def __eq__(self, other):
        if not isinstance(other, Instance):
            return False
        if self.entity != other.entity:
            return False
        if self.text != other.text:
            return False
        if self.tag != other.tag:
            return False

        # evidence 是否要算入相等判断内呢？
        return True

    def __repr__(self):
        return "%s(%s)-%s\t(%s)" % (self.entity, self.tag, self.text, repr(self.evidence))


class Statement:
    """
    pre(dict[string]sting): key为抽象，value为具体
    post(dict[string]sting):  key为抽象，value为具体
    double(Connection): 是否是双向推导
    """

    def __init__(self, pre: dict, post: dict, double: bool):
        self.pre = pre
        self.post = post
        self.double = double

    def infer(self, ctx) -> list:
        evdience = []
        # print("====")
        for entity_str, sub in self.pre.items():
            succ = False
            for entity in ctx.findAll(entity_str):
                if sub is None or entity.get_text() == sub:
                    succ = True
                    evdience.append(entity)
                    break
            # print(evdience, entity, sub)
            if succ is False:
                return None

        infer = []
        for entity, sub in self.post.items():
            infer.append(Instance(entity, sub, evdience))

        return infer

    def __repr__(self):
        return repr(self.pre) + repr(self.post)

    def __eq__(self, other):
        if not isinstance(other, Statement):
            return False
        if self.double != other.double:
            return False

        if self.pre == other.pre and self.post == other.post:
            return True
        if self.double and self.pre == other.post and self.post == other.pre:
            return True
        return False


class Entity:
    """
    tag(string): 用于表示实体的文字，带[]的场合意味着联系其它实体
    sub(Entity): 该实体的子实体，意味着该实体可以转化为的其它实体
    conn(Connection): 用于知识推导的记录
    """

    def __init__(self, tag: str):
        self.tag = tag
        self.sub = []
        self.conn = []

    def append(self, sub): self.sub.append(sub)
    def get_text(self) -> str: return self.tag
    def get_sub(self) -> list: return self.sub
    def get_conn(self): return self.conn

    def add_conn(self, conn: Statement):
        if conn not in self.conn:
            self.conn.append(conn)

    def has_sub(self, sub: str):
        for entity in self.sub:
            if sub == entity.get_text():
                return True
        return False

    def __repr__(self):
        return repr(self.tag) + repr(self.conn) + repr(self.sub)


class Context:
    def __init__(self):
        self.inst_stack = [{}]

    def find(self, entity_str: str, tag=None, evdience=None) -> Instance:
        """
        返回满足tag和cond的entity的Instance
        """
        for stack in self.inst_stack:
            for entity in stack.get(entity_str, []):
                if entity.get_tag() != tag:
                    continue

                if evdience is not None and entity.get_evidence() != evdience:
                    continue

                return entity

        return None

    def findAll(self, entity_str: str) -> list:
        result = []
        for stack in self.inst_stack:
            for stack_entity_str, stack_entities in stack.items():
                if stack_entity_str == entity_str:
                    result.extend(stack_entities)

        return result

    def new_stack(self): self.inst_stack.append({})
    def aborat_stack(self): self.inst_stack.pop()

    def apply_stack(self):
        stack = self.inst_stack.pop()
        for key in stack.keys():
            if key in self.inst_stack[-1]:
                self.inst_stack[-1][key].extend(stack[key])
            else:
                self.inst_stack[-1][key] = stack[key]

    def append(self, inst: Instance) -> bool:
        entity = inst.get_entity()
        tag = inst.get_tag()
        evdience = inst.get_evidence()
        if self.find(entity, tag=tag, evdience=evdience) is not None:
            return False

        if entity not in self.inst_stack[-1]:
            self.inst_stack[-1][entity] = []

        self.inst_stack[-1][entity].append(inst)
        return True

    def iter_all_inst(self):
        for stack in self.inst_stack:
            for _, inst_list in stack.items():
                for inst in inst_list:
                    yield inst

    def get_known_stat(self, known: Knowledge):
        assert len(self.inst_stack) == 1, "上下文栈未全退出"
        known_stat = []

        for inst in self.iter_all_inst():
            entity = inst.get_entity()
            for stat in known.get_conn(entity):
                if stat not in known_stat:
                    known_stat.append(stat)
        return known_stat

    def apply_closure(self, append_stat: list, known: Knowledge):
        new_stat = []
        for stat in append_stat:
            infer = stat.infer(self)
            if infer is None:
                continue

            for inst in infer:
                entity = inst.get_entity()
                text = inst.get_text()
                evidence = inst.get_evidence()

                # TODO:解决同推导的tag覆盖问题
                if self.append(Instance(entity, text, evidence, tag=None)):
                    # TODO:解决推导可能成环的问题，尝试剪枝
                    for stat in known.get_conn(entity):
                        new_stat.append(stat)

        if len(new_stat) > 0:
            self.apply_closure(new_stat, known)

    def infer(self, known: Knowledge):
        assert len(self.inst_stack) == 1, "上下文栈未全退出"
        known_stat = self.get_known_stat(known)
        self.apply_closure(known_stat, known)

    def __repr__(self):
        text = ["Context:"]
        for stack in self.inst_stack:
            text.append("==stack==")
            for inst in stack.items():
                text.append(repr(inst))

        return '\n'.join(text)
