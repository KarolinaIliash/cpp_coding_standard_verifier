from lexer import Lexer
import states
import verifier
import automatic_fixer

import json
import os

class MyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, states.State):
            d = {}
            d['_Type'] = obj.__class__.__name__
            d.update(obj.__dict__)
            return d
        if isinstance(obj, verifier.Verifier):
            d = {}
            d['File'] = obj.nm.name
            d['Warnings'] = obj.warnings
            return d
        if isinstance(obj, verifier.Warning):
            d = obj.__dict__
            d['type'] = d['type'].name
            return d
        if isinstance(obj, verifier.WarningType):
            d = obj.name
            return d
        if isinstance(obj, states.Scope):
            return obj.name
        return json.JSONEncoder.default(self, obj)

class CppFile:
    def __init__(self, path):
        self.path_ = path

    def scan(self):

        #try:
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

            ver = verifier.Verifier(nm, lex)
            ver.verify()

            f = open('out.txt', 'a')  # type: _io.TextIOWrapper
            f.write(MyEncoder().encode(nm))

            f = open('out2.txt', 'a')  # type: _io.TextIOWrapper
            f.write(MyEncoder().encode(ver))


            fixer = automatic_fixer.AutomaticTabsFixer(ver.warnings, r"D:\Downloads\QuantLib-master\ql\cashflow.hpp")
            fixer.fix_tabs()
        #except Exception:
        #    print('Skipping ' + self.path_)





