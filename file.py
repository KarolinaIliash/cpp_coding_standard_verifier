from lexer import Lexer
import states

import json


class MyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, states.State):
            d = {}
            d['_Type'] = obj.__class__.__name__
            d.update(obj.__dict__)
            return d
        if isinstance(obj, states.Scope):
            return obj.name
        return json.JSONEncoder.default(self, obj)

class CppFile:
    def __init__(self, path):
        self.path_ = path

    def scan(self):
        file = open(self.path_, 'r')
        s = file.read()
        lex = Lexer(s)
        lex.parse()

        states.cur_lexer = lex
        states.cur_token = 0
        nm = states.Namespace()
        nm.is_file = True
        nm.name = self.path_
        nm.parse_me()

        print(MyEncoder().encode(nm))

