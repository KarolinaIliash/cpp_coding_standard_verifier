from enum import Enum
class TokenType(Enum):
    not_set = 0
    number = 1
    delim = 2
    string = 3
    keyword = 4
    id = 5
    comment = 6
    operation = 7
    bracket = 8
    sharp = 9
    line = 10

class Token:
    def __init__(self):
        self.type_ = TokenType.not_set # type: TokenType
        self.offset_ = None # type: int
        self.size_ = None # type: int



class Lexer:
    def __init__(self, text: str):
        self.str_ = text
        self.tokens_ = [] # List[Token]
        self.keywords_ = \
            [
            'alignas',    'decltype',     'namespace',        'struct',
            'alignof',    'default',      'new',              'switch',
            'and',        'delete',       'noexcept',         'template',
            'and_eq',     'do',           'not',              'this',
            'asm',        'double',       'not_eq',           'thread_local',
            'auto',       'dynamic_cast', 'nullptr',          'throw',
            'bitand',     'else',         'operator',         'true',
            'bitor',      'enum',         'or',               'try',
            'bool',       'explicit',     'or_eq',            'typedef',
            'break',      'export',       'private',          'typeid',
            'case',       'extern',       'protected',        'typename',
            'catch',      'false',        'public',           'union',
            'char',       'float',        'register',         'unsigned',
            'char16_t',   'for',          'reinterpret_cast', 'using',
            'char32_t',   'friend',       'return',           'virtual',
            'class',      'goto',         'short',            'void',
            'compl',      'if',           'signed',           'volatile',
            'const',      'inline',       'sizeof',           'wchar_t',
            'constexpr',  'int',          'static',           'while',
            'const_cast', 'long',         'static_assert',    'xor',
            'continue',   'mutable',      'static_cast',      'xor_eq'
            ]

        self.operators_ = \
            [
            "not_eq", "not", "and", "or"
            , "compl", "bitand", "bitor", "xor"
            , "and_eq", "or_eq", "xor_eq"
            ]

        self.delimiters_ = \
            [
                ' ',
                '\r',
                '\n',
                '\t',
                ';',
                '\0',
                ','
            ]

        self.line_ = '\n'

        self.operations_ = \
            ['+', '++', '+=', '-', '--', '-=', '->', '*', '*=', '/',
             '/=', '%', '%=', '=', '==', '!', '!=', '>', '>=', '>>=',
             '>>', '<', '<<', '<=', '<<=', '&', '&&', '&=', '|', '||',
             '|=', '^', '^=', '~', '.', '?', ':'
             ]

    def next_delimiter(self, offset: int) -> int:
        cur = self.str_[offset:]
        i = 0
        while True:
            if (self.is_delimiter(cur[i]) or (self.str_[i] == '/' and self.str_[i + 1] == '*') or (
                    self.str_[i] == '/' and self.str_[i + 1] == '/')):
                return offset + i
            i += 1


    def is_delimiter(self, ch:str) -> bool:
        return ch in self.delimiters_


    def parse_string(self, offset: int) -> Token:
        result = Token()
        result.offset_ = offset
        result.type_ = TokenType.string

        end = offset

        while True:
            end += 1
            if self.str_[end] == '"':
                end += 1
                break
            elif self.str_[end] == '\\':
                end += 1

        result.size_ = end - offset
        return result

    def parse_char(self, offset: int) -> Token:
        result = Token()
        result.offset_ = offset
        result.type_ = TokenType.string

        end = offset + 1

        if self.str_[end] == '\\':
            result.size_ = 4
        else:
            result.size_ = 3

        return result

    def parse_id(self, offset: int) -> Token:
        result = Token()
        result.offset_ = offset
        result.type_ = TokenType.id

        end = offset

        while True:
            end += 1
            if not (self.str_[end] == '_' or self.str_[end] == '$' or (self.str_[end] >= 'a' and self.str_[end] <= 'z') or (
                    self.str_[end] >= 'A' and self.str_[end] <= 'Z') or (self.str_[end] >= '0' and self.str_[end] <= '9')):
                break


        id = self.str_[offset:end]

        if id in self.keywords_:
            result.type_ = TokenType.keyword

        if id in self.operators_:
            result.type_ = TokenType.operation

        result.size_ = end - offset
        return result

    def parse_comment(self, offset: int) -> Token:
        result = Token()
        result.offset_ = offset
        result.type_ = TokenType.comment

        end = offset

        if self.str_[end] == '/' and self.str_[end + 1] == '*':
            while True:
                if self.str_[end] == '*' and self.str_[end + 1] == '/':
                    end += 2
                    break
                end += 1
        elif self.str_[end] == '/' and self.str_[end + 1] == '/':
            while True:
                    if self.str_[end] == '\0' or self.str_[end] == '\n':
                        end += 1
                        break
                    end += 1

        result.size_ = end - offset
        return result


    def parse_operation(self, offset: int) -> Token:
        result = Token()
        result.offset_ = offset
        result.type_ = TokenType.operation
        if self.str_[offset:offset + 1] in self.operations_:
            result.size_ = 1
            if self.str_[offset:offset + 2] in self.operations_:
                result.size_ = 2
                if self.str_[offset:offset + 3] in self.operations_:
                    result.size_ = 3
        return result


    def end_of_number(self, ch):
        if (self.is_delimiter(ch) or ch == '+' or ch == '-' or ch == '*' or ch == '/' or ch == '='
             or ch == '<' or ch == '>' or ch == '!' or ch == '(' or ch == ')' or ch == '[' or ch == ']'
             or ch == '{' or ch == '}' or ch == '%' or ch == '&' or ch == '|' or ch == '^'
             or ch == '?' or ch == ':' or ch == '~'):
            return True

        return False

    def parse_number(self, offset: int) -> Token:
        result = Token()
        result.offset_ = offset
        result.type_ = TokenType.number

        end = offset
        while not self.end_of_number(self.str_[end]):
            end += 1

        result.size_ = end - offset
        return result

    def parse_sharp(self, offset: int) -> Token:
        result = Token()
        result.offset_ = offset
        result.type_ = TokenType.sharp

        end = offset

        while True:
            # first if should be checked and rethink another time
            if self.str_[end] == '\\' and self.str_[end] == '\n':
                end += 1  # another +1 will be done at the end of the cycle
            elif self.str_[end] == '\0' or self.str_[end] == '\n':
                end += 1
                break
            end += 1

        result.size_ = end - offset
        return result


    def parse(self):
        i = 0
        line = 0
        while True:
            if i == self.str_.__len__():
                break

            if self.str_[i] == '.':
                t = Token()
                if self.str_[i + 1] >= '0' and self.str_[i + 1] <= '9':
                    t = self.parse_number(i)
                else:
                    t = self.parse_operation(i)
                i += t.size_
                self.tokens_.append(t)
                continue
            elif self.str_[i] >= '0' and self.str_[i] <= '9':
                t = self.parse_number(i)
                i += t.size_
                self.tokens_.append(t)
                continue
            elif self.str_[i] == '"':
                t = self.parse_string(i)
                i += t.size_
                self.tokens_.append(t)
                continue
            elif self.str_[i] == '\'':
                t = self.parse_char(i)
                i += t.size_
                self.tokens_.append(t)
                continue
            elif self.str_[i] == '#':
                t = self.parse_sharp(i)
                i += t.size_
                self.tokens_.append(t)
                continue
            elif self.str_[i] == '_' or self.str_[i] == '$' or (self.str_[i] >= 'a' and self.str_[i] <= 'z') or (self.str_[i] >= 'A' and self.str_[i] <= 'Z'):
                t = self.parse_id(i)
                i += t.size_
                self.tokens_.append(t)
                continue
            elif (self.str_[i] == '/' and self.str_[i + 1] == '/') or (self.str_[i] == '/' and self.str_[i + 1] == '*') :
                t = self.parse_comment(i)
                i += t.size_
                self.tokens_.append(t)
                continue
            elif (self.str_[i] == '+' or self.str_[i] == '-' or self.str_[i] == '*' or self.str_[i] == '/' or self.str_[i] == '%' or
                    self.str_[i] == '=' or self.str_[i] == '!' or self.str_[i] == '>' or self.str_[i] == '<' or self.str_[i] == '&' or
                    self.str_[i] == '|' or self.str_[i] == '^' or self.str_[i] == '~' or self.str_[i] == '?' or self.str_[i] == ':' ) :
                t = self.parse_operation(i)
                i += t.size_
                self.tokens_.append(t)
                continue
            elif self.is_delimiter(self.str_[i]):
                t = Token()
                t.offset_ = i
                t.size_ = 1
                if self.str_[i] == self.line_:
                    t.type_ = TokenType.line
                else:
                    t.type_ = TokenType.delim
                self.tokens_.append(t)
                i += t.size_
                continue
            elif self.str_[i] == '(' or self.str_[i] == ')' or self.str_[i] == '[' or self.str_[i] == ']' or self.str_[i] == '{' or self.str_[i] == '}':
                t = Token()
                t.offset_ = i
                t.size_ = 1
                t.type_ = TokenType.bracket
                self.tokens_.append(t)
                i += t.size_
                continue
