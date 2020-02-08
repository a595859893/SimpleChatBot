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
        conn = Connect(pre, post, double)
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


class Connect:
    def __init__(self, pre: dict, post: dict, double: bool):
        self.pre = pre
        self.post = post
        self.double = double

    def infer(self, ctx) -> list:
        evdience = []
        # print("====")
        for entity, sub in self.pre.items():
            succ = False
            for trace in ctx.findAll(entity):
                if sub is None or trace.get_text() == sub:
                    succ = True
                    evdience.append(trace)
                    break
            # print(evdience, entity, sub)
            if succ is False:
                return None

        infer = []
        for entity, sub in self.post.items():
            infer.append(Trace(entity, sub, evdience))

        return infer

    def __repr__(self):
        return repr(self.pre) + repr(self.post)

    def __eq__(self, other):
        if not isinstance(other, Connect):
            return False
        if self.double != other.double:
            return False

        if self.pre == other.pre and self.post == other.post:
            return True
        if self.double and self.pre == other.post and self.post == other.pre:
            return True
        return False


class Entity:
    def __init__(self, tag: str):
        self.tag = tag
        self.sub = []
        self.conn = []

    def append(self, sub):
        self.sub.append(sub)

    def get_text(self) -> str:
        return self.tag

    def get_sub(self) -> list:
        return self.sub

    def add_conn(self, conn: Connect):
        if conn not in self.conn:
            self.conn.append(conn)

    def get_conn(self):
        return self.conn

    def has_sub(self, sub: str):
        for entity in self.sub:
            if sub == entity.get_text():
                return True
        return False

    def __repr__(self):
        return repr(self.tag) + repr(self.conn) + repr(self.sub)


class Trace:
    def __init__(self, entity: str, text: str, evidence: list):
        self.entity = entity
        self.text = text
        self.evidence = evidence

    def get_entity(self):
        return self.entity

    def get_text(self):
        return self.text

    def get_evidence(self):
        return self.evidence

    def __eq__(self, other):
        if not isinstance(other, Trace):
            return False

        if self.entity == other.entity and self.text == other.text:
            # print(set(self.evidence), set(other.evidence))
            # print(set(self.evidence) == set(other.evidence))
            # return set(self.evidence) == set(other.evidence)
            return True
        # evidence 是否要算入相等判断内呢？
        return False

    def __repr__(self):
        return "%s-%s(%s)" % (self.entity, self.text, repr(self.evidence))


class Context:
    def __init__(self):
        self.trace_stack = [{}]

    def find(self, entity: str, tag=None, cond=None) -> Trace:
        """
        返回满足tag和cond的entity的Trace
        """
        for stack in self.trace_stack:
            if (entity, tag) in stack:
                return stack[(entity, tag)]
        return None

    def findAll(self, entity: str) -> list:
        result = []
        for stack in self.trace_stack:
            for stack_entity, stack_sub in stack.items():
                if stack_entity[0] == entity:
                    result.append(stack_sub)

        return result

    def new_stack(self):
        self.trace_stack.append({})

    def apply_stack(self):
        trace = self.trace_stack.pop()
        self.trace_stack[-1].update(trace)

    def aborat_stack(self):
        self.trace_stack.pop()

    def append(self, entity: str, text: str, tag: str, evidence=None):
        self.trace_stack[-1][(entity, tag)] = Trace(entity, text, evidence)

    def infer(self, known: Knowledge):
        assert len(self.trace_stack) == 1, "上下文栈未全退出"
        inference = []
        traces = self.trace_stack[0]
        # 获取context中所有trace对应的conn
        # 用于后续遍历conn从而推导出新的trace
        for key in traces.keys():
            entity = traces[key].get_entity()
            for conn in known.get_conn(entity):
                if conn not in inference:
                    inference.append(conn)

        more = True
        temp_infer = []
        # print("====start====")
        while more:
            # 只要有新的trace出现，就需要重新进行一次推导
            # 可以优化，待填
            more = False
            # print("====\n", '\n'.join([repr(i) for i in inference]))
            for conn in inference:
                infer = conn.infer(self)
                if infer is not None:
                    for trace in infer:
                        entity = trace.get_entity()
                        text = trace.get_text()
                        evidence = trace.get_evidence()
                        # 同推导可能因为tag问题而覆盖，待解决
                        self.append(entity, text, None, evidence)
                        more = True
                        # 推导可能成环，待解决
                        # print("New:", trace)
                        for conn in known.get_conn(entity):
                            # 可以剪枝
                            if conn not in inference:
                                temp_infer.append(conn)
                else:
                    temp_infer.append(conn)

            inference = temp_infer
            temp_infer = []

        # print(self.trace_stack)

    def __repr__(self):
        text = []
        for stack in self.trace_stack:
            for trace in stack.items():
                text.append(repr(trace))

        return ' '.join(text)
