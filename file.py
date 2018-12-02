from lexer import Lexer
import states


class CppFile:
    def __init__(self, path):
        self.path_ = path

    def scan(self):
        file = open(self.path_, 'r')
        s = file.read()
        l = Lexer(s)
        l.parse()

        states.cur_lexer = l
        nm = states.Namespace()
        nm.is_file = True
        nm.parse_me()
