from lexer import Lexer
import states
import verifier
import automatic_fixer

import json
from typing import Dict

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
    file_states = []
    verifiers = {}  # type: Dict[verifier.Verifier]

    def __init__(self, path):
        self.path_ = path


    def scan(self):

        #try:
            file = open(self.path_, 'r')
            s = file.read()
            self.lex = Lexer(s)
            self.lex.parse()

            states.cur_lexer = self.lex
            states.cur_token = 0

            self.nm = states.Namespace()
            self.nm.is_file = True
            self.nm.name = self.path_
            self.nm.parse_me()

            CppFile.file_states.append(self.nm)

            f = open('out.txt', 'a')  # type: _io.TextIOWrapper
            f.write(MyEncoder(indent=4, separators=(',', ': ')).encode(self.nm))

    def verify(self):

            ver = verifier.Verifier(self.nm, self.lex)
            ver.verify()

            if self.nm.name in CppFile.verifiers:
                ver.warnings += CppFile.verifiers[self.nm.name].warnings

            CppFile.verifiers[self.nm.name] = ver



            #f = open('out2.txt', 'a')  # type: _io.TextIOWrapper
            #f.write(MyEncoder().encode(ver))


            #fixer = automatic_fixer.AutomaticFixer(ver.warnings, self.nm.name)
            #fixer.fix_tabs()
            #fixer.fix_impl_comments()
            #fixer.fix_brackets_tabs()
        #except Exception:
        #    print('Skipping ' + self.path_)

    @staticmethod
    def get_statistic():
        statistics = {}

        for type in verifier.WarningType:
            statistics[type.name] = 0

        for ver in CppFile.verifiers:
            warnings = CppFile.verifiers[ver].warnings
            for warning in warnings:
                statistics[warning.type.name] += 1

        sum_ = sum(statistics.values())

        statistics.pop('none', None)

        for type in verifier.WarningType:
            if not sum_ == 0:
                statistics[type.name] = ('%.2f' % (statistics[type.name] / sum_ * 100)) + '%'
            else:
                statistics[type.name] = 0

        return sum_, statistics

