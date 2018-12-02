
from lexer import Lexer, Token, TokenType

cur_line = 0
cur_token = 0
cur_lexer = None  # type: Lexer


id_keywords_in_file = \
    [
            'double', 'auto', 'bool', 'char', 'float', 'unsigned',
            'char16_t', 'char32_t', 'short', 'void', 'signed', 'volatile',
            'const', 'inline', 'wchar_t', 'constexpr',  'int', 'static', 'long',
    ]

id_keywords_in_class = \
    [
        'virtual'
    ]

def get_token_text(token : Token) -> str:
    return cur_lexer.str_[token.offset_:token.offset_ + token.size_]
#TODO add lines in state parse_me functions
class State:
    def __init__(self):

        global cur_line
        global cur_token
        global cur_lexer

        self.name = None  # type: str
        self.line = None  # type: int
        self.content = []

    def parse_me(self):
        pass

    # start_token will be incremented firstly in this func before searching
    def next_semicolon(self, start_token: int) -> int:
        start_token += 1
        while start_token < len(cur_lexer.tokens_):
            if get_token_text(cur_lexer.tokens_[start_token]) == ';':
                return start_token
            start_token += 1
        return -1

    def next_bracket(self, start_token: int) -> int:
        while True:
            if cur_lexer.tokens_[start_token].type_ == TokenType.bracket:
                return start_token
            start_token += 1

    def next_symbol(self, start_token: int, smb: str) -> int:
        last_token = cur_lexer.tokens_.__len__()
        while start_token < last_token:
            if get_token_text(cur_lexer.tokens_[start_token]) == smb:
                return start_token
            start_token += 1
        return -1


class StateInBrackets(State):
    def __init__(self):
        super().__init__()

# file consider as a global namespace
class Namespace(StateInBrackets):
    def __init__(self):
        super().__init__()
        self.is_file = False
        self.globals = []
        self.name = None  # type : str

    def parse_me(self):
        global cur_line
        global cur_token
        global cur_lexer

        if not self.is_file:
            while True:
                cur_token += 1
                t = cur_lexer.tokens_[cur_token]  # type: Token
                if t.type_ == TokenType.id:
                    self.name = get_token_text(t)
                if get_token_text(t) == '{':
                    break

        while True:
            # todo think about next line
            # todo how to align all inner parse_me changes of this global variable



            t = cur_lexer.tokens_[cur_token]  # type: Token
            if get_token_text(t) == '}' or get_token_text(t) == '\0':
                break
            new = None  # type: State
            if t.type_ == TokenType.keyword:
                #kw = cur_lexer.str_[t.offset_:t.offset_ + t.size_]
                kw = get_token_text(t)
                if kw == 'namespace':
                    new = Namespace()
                elif kw == 'class':
                    new = Class()
                elif kw == 'struct':
                    new = Struct()
                elif kw == 'template':
                    # new = Template()
                    '''self.'''
                    eat_template()
                elif kw == 'union':
                    new = Union()
                elif kw == 'typedef':
                    new = Typedef()
                elif kw == 'enum':
                    new = Enum()
                elif kw == 'using':
                    new = get_right_using()
                elif kw in id_keywords_in_file:
                    new = identifier()

            elif t.type_ == TokenType.id:
                new = identifier()

            elif t.type_ == TokenType.sharp:
                new = get_right_preprocessor_directive()  # Sharp()

            cur_token += 1

            if new is not None:
                self.content.append(new)
                new.parse_me()



    '''def eat_template(self):
        token = cur_token + 1

        def find_open(t):
            while True:
                if get_token_text(cur_lexer.tokens_[t]) == '<':
                    return t
                t += 1

        averaged_amount = 1
        token = find_open(token)
        while not averaged_amount == 0:
            if get_token_text(cur_lexer.tokens_[token]) == '<':
                averaged_amount += 1
            elif get_token_text(cur_lexer.tokens_[token]) == '>':
                averaged_amount -= 1
            token += 1
        global cur_token
        cur_token = token + 1'''


def eat_template():
    token = cur_token + 1

    def find_open(t):
        while True:
            if get_token_text(cur_lexer.tokens_[t]) == '<':
                return t
            t += 1

    averaged_amount = 1
    token = find_open(token)
    while not averaged_amount == 0:
        if get_token_text(cur_lexer.tokens_[token]) == '<':
            averaged_amount += 1
        elif get_token_text(cur_lexer.tokens_[token]) == '>':
            averaged_amount -= 1
        token += 1

    cur_token = token + 1

from enum import Enum
class Scope(Enum):
    private = 0,
    protected = 1,
    public = 2

# todo check it, i was writing it too late
# i think struct should be almost
class Class(StateInBrackets):
    def __init__(self):
        super().__init__()
        self.name = None

    def parse_me(self):
        global cur_line
        global cur_token
        global cur_lexer

        cur_scope = Scope.private

        while True:
            cur_token += 1
            t = cur_lexer.tokens_[cur_token]  # type: Token
            if t.type_ == TokenType.id and self.name is None:
                self.name = get_token_text(t)
            if get_token_text(t) == '{':
                break

        while True:


            cur_token += 1
            t = cur_lexer.tokens_[cur_token]  # type: Token
            if get_token_text(t) == '}':
                cur_token += 1
                break
            new = None  # type: State
            if t.type_ == TokenType.keyword:
                kw = get_token_text(t)
                if kw == 'private':
                    cur_scope = Scope.private
                elif kw == 'protected':
                    cur_scope = Scope.protected
                elif kw == 'public':
                    cur_scope = Scope.public
                elif kw == 'class':
                    new = Class()
                elif kw == 'struct':
                    new = Struct()
                elif kw == 'friend':
                    new = Friend()
                elif kw == 'virtual':
                    # function should resolve that it's virtual
                    new = Function()
                elif kw == 'template':
                    eat_template()
                elif kw in id_keywords_in_file:
                    new = identifier()

            elif t.type_ == TokenType.id:
                # also function should understand if it's ctor
                new = identifier()

            elif t.type_ == TokenType.operation and get_token_text(t) == '~':
                # function should understand if it's destructor
                new = Function()


            if not new is None:
                new.scope = cur_scope
                new.parse_me()
                self.content.append(new)



class Friend(State):
    def __init__(self):
        super().__init__()


class Struct(StateInBrackets):
    def __init__(self):
        super().__init__()


class Union(StateInBrackets):
    def __init__(self):
        super().__init__()

class Typedef(State):
    def __init__(self):
        super().__init__()


    def parse_me(self):
        last_token = self.next_semicolon(cur_token)
        token = last_token - 1
        while token > cur_token:
            if cur_lexer.tokens_[token].type_ == TokenType.id:
                self.type_name = get_token_text(token)
                break
            token -= 1

        cur_token = last_token + 1


def find_next_id(token_number: int) -> int:
    while True:
        if cur_lexer.tokens_[token_number].type_ == TokenType.id:
            return token_number
    token_number += 1


class Enum(StateInBrackets):
    def __init__(self):
        super().__init__()

    def parse_me(self):
        self.line = cur_lexer.tokens_[cur_token].line_

        name_t_number = find_next_id(cur_token + 1)
        name_t = cur_lexer.tokens_[name_t_number]  # type: Token
        self.name = get_token_text(name_t)
        bracket_t_number = self.next_bracket(name_t_number + 1)

        # enum A : short only integral types here
        colon_t_n = self.next_symbol(name_t_number + 1, bracket_t_number)
        if not colon_t_n == -1:
            type_t_n = find_next_id(colon_t_n + 1)
            self.type = get_token_text(cur_lexer.tokens_[type_t_n])

        self.labels = []
        cur_t = bracket_t_number + 1
        close_bracket_t_n = self.next_bracket(cur_t)
        while True:
            label_t_n = find_next_id(cur_t)
            cur_token = label_t_n
            if label_t_n < close_bracket_t_n:
                #label_t = cur_lexer.tokens_[label_t_n]
                #label = get_token_text(label_t)
                # if use this commented code, should be added comma search before next label search
                #self.labels.append(label)
                label = EnumLabel()
                label.parse_me()
                self.labels.append(label)
            else:
                break
        cur_token = close_bracket_t_n + 1

# TODO add check of name according to coding standard
class EnumLabel(State):
    def __init__(self):
        super().__init__()

    def parse_me(self):

        self.name = get_token_text(cur_lexer.tokens_[cur_token])
        comma_t_n = self.next_symbol(cur_token, ',')
        close_bracket_t_n = self.next_bracket(cur_token)
        if comma_t_n < close_bracket_t_n:
            cur_token = comma_t_n + 1
        else:
            cur_token = close_bracket_t_n


def identifier() -> State:

        t = cur_lexer.tokens_[cur_token]  # type: Token
        cur_t = get_token_text(t)
        # new = None  # type: State
        if cur_t == 'virtual':  # or t.type_ == 'inline':
            new = Function()
        # namespaces can be inline eg: inline namespace M
        elif cur_t == 'inline':
            next_token = cur_token + 1
            while True:
                cur_t_ = cur_lexer.tokens_[next_token] # type: Token
                if cur_t_.type_ == TokenType.id:
                    new = Function()
                    break
                elif cur_t_.type_ == TokenType.keyword and get_token_text(cur_t_) == 'namespace':
                    new = Namespace()
                    break
                next_token += 1
        else:
            next_token = cur_token + 1
            while True:
                cur_t = get_token_text(cur_lexer.tokens_[next_token])
                if cur_t == '(':
                    new = Function()
                    break
                elif cur_t == '=':
                    new = Variable()
                    break
                next_token += 1
        # parse will be done in parse_me in outer class
        # new.parse_me()
        return new


def get_right_using() -> State:
    cur_t = cur_token + 1
    while True:
        if cur_lexer.tokens_[cur_t].type_ == TokenType.id:
            return Using()
        elif cur_lexer.tokens_[cur_t].type_ == TokenType.keyword and get_token_text(cur_lexer.tokens_[cur_t]) == 'namespace':
            return UsingNamespace()
        cur_t += 1


class Using(State):
    def __init__(self):
        super().__init__()

    def parse_me(self):
        self.names = []
        general_id_t_n = find_next_id(cur_token + 1)
        self.names.append(get_token_text(cur_lexer.tokens_[general_id_t_n]))

        semicolon_t_n = self.next_semicolon(general_id_t_n + 1)
        cur_t = general_id_t_n + 1
        while True:
            id_t_n = find_next_id(cur_t)
            if id_t_n < semicolon_t_n:
                self.names.append(get_token_text(cur_lexer.tokens_[id_t_n]))
                cur_t = id_t_n
            else:

                cur_token = semicolon_t_n + 1
                break


class UsingNamespace(State):
    def __init__(self):
        super().__init__()


    # maybe this code should be in func and using in Using and in this class
    def parse_me(self):
        self.names = []
        namespace_t_n = self.next_symbol(cur_token + 1, 'namespace')
        general_id_t_n = find_next_id(namespace_t_n + 1)
        self.names.append(get_token_text(cur_lexer.tokens_[general_id_t_n]))

        semicolon_t_n = self.next_semicolon(general_id_t_n + 1)
        cur_t = general_id_t_n + 1
        while True:
            id_t_n = find_next_id(cur_t)
            if id_t_n < semicolon_t_n:
                self.names.append(get_token_text(cur_lexer.tokens_[id_t_n]))
                cur_t = id_t_n
            else:

                cur_token = semicolon_t_n + 1
                break

class Function(StateInBrackets):
    def __init__(self):
        super().__init__()

    def parse_me(self):
        text = get_token_text(cur_lexer.tokens_[cur_token])




# todo add support for pointers and references and name checking
class Variable(State):
    def __init__(self):
        super().__init__()

    def parse_me(self):
        self.type = get_token_text(cur_lexer.tokens_[cur_token])
        name_t_n = find_next_id(cur_token + 1)
        self.name = get_token_text(cur_lexer.tokens_[name_t_n])
        semicolon_t_n = self.next_semicolon(name_t_n + 1)

        cur_token = semicolon_t_n + 1

def get_right_preprocessor_directive():
    text = get_token_text(cur_lexer.tokens_[cur_token])
    if text.startswith("#define"):
        return Macros()
    elif text.startswith("#ifndef"):
        return IfNDefGuard()
    else:
        return OtherPreprocessorDirective()

'''class Sharp(State):
    def parse_me(self):
        text = get_token_text(cur_token)
        if text.startswith("#define"):


        global cur_token
        cur_token += 1
'''


def miss_spaces(text: str) -> str:
    i = 0
    while text[i] == ' ':
        i += 1
    return text[i:]

class Macros(State):
    def __init__(self):
        super().__init__()

    def parse_me(self):
        global cur_line
        global cur_token
        global cur_lexer


        text = get_token_text(cur_lexer.tokens_[cur_token])

        text_without_define = text[len("define"):]
        text_without_spaces = miss_spaces(text_without_define)

        name = ''
        is_func_macros = False
        with_value = True
        for letter in text_without_spaces:
            if letter == '(':
                is_func_macros = True
                break
            if letter == ' ':
                break
            if letter == '\n':
                with_value = False
                break
                # todo add logic with backslash in macros
            name += letter

        # TODO add checking name according to coding standard

        self.name = name

        if is_func_macros:
            name_end = text_without_spaces.find(')')
        elif with_value:
            name_end = text_without_spaces.find(' ')
        elif not with_value:
            name_end = text_without_spaces.find('\n')

        # TODO check if it's done: add analyse of situation when there is no value of macros
        # TODO add checking of parens in value. i think it's bad idea to check it because macros can be really complex
        # TODO (eg on multiple lines) and it'll be hard to parse it into values
        if with_value:
            self.value = text_without_spaces[name_end:]


        cur_token += 1


class IfNDefGuard(State):
    def __init__(self):
        super().__init__()

    def parse_me(self):
        global cur_line
        global cur_token
        global cur_lexer


        text = get_token_text(cur_lexer.tokens_[cur_token])
        text_without_ifndef = text[len('#ifndef'):]
        text_without_spaces = miss_spaces(text_without_ifndef)

        self.guard_name = text_without_spaces

        # TODO add logic how to find (or understand that there is no) #define which should be in the guard
        # TODO add changing token number after parsing guard
        # maybe first todo is not necessary, we can analyse it later: eg next content element should be define without value


        cur_token += 1


# i think we don't need info about them
class OtherPreprocessorDirective(State):
    def __init__(self):
        super().__init__()

    def parse_me(self):
        global cur_line
        global cur_token
        global cur_lexer

        self.text = get_token_text(cur_lexer.tokens_[cur_token])

        cur_token += 1

