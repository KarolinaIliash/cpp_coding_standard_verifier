import states
import enum
import lexer

import files

class WarningType(enum.Enum):
    none = 0
    guard = 1
    naming = 2
    access = 3
    using_namespace = 4
    formatting = 5
    tabs = 6
    one_class_in_file = 7
    name_file_after_class = 8
    doc_above_method = 9
    brackets_tabs = 10
    impl_comment = 11

file_endings = [".cpp", ".hpp", ".c", ".h"]

class Warning:
    def __init__(self):
        self.type = WarningType.none
        self.line = None #  type: int
        self.text = None #  type: str


class Verifier:
    #def __init__(self):
    #    self.warnings = []

    def __init__(self, file_namespace: states.Namespace, lexer: lexer.Lexer):
        self.nm = file_namespace
        self.warnings = []
        self.lexer = lexer

    def get_token_text(self, token: lexer.Token):
        return self.lexer.str_[token.offset_:token.offset_ + token.size_]

    def verify(self):
        self.verify_file(self.nm)

    def verify_file(self, obj: states.Namespace):
        if obj.name.endswith('.hpp') or obj.name.endswith('.h'):
            for state in obj.content:
                if type(state) is states.IfNDefGuard:
                    break
                else:
                    war = Warning()
                    war.type = WarningType.guard
                    war.line = 0
                    war.text = 'Header file should starts with include guard'
                    self.warnings.append(war)
                    break

        self.verify_one_class_in_file(obj)
        self.verify_namespace(obj)
        self.verify_tabulation()
        self.verify_line_length()
        self.verify_tabs()
        self.verify_line_end()

    def verify_one_class_in_file(self, obj):
        class_amount = self.class_amount_in_namespace(obj)
        if class_amount > 1:
            war = Warning()
            war.type = WarningType.one_class_in_file
            war.line = 0
            war.text = "Don't put more than one class in a file"
            self.warnings.append(war)
        elif class_amount == 1:
            class_name = self.first_class_in_namespace(obj).name
            if obj.name not in [class_name + x for x in file_endings]:
                war = Warning()
                war.type = WarningType.name_file_after_class
                war.line = 0
                war.text = "Name your file after class"
                self.warnings.append(war)

    def class_amount_in_namespace(self, namespace: states.Namespace):
        amount = 0
        for state in namespace.content:
            if isinstance(state, states.Class):
                amount += 1
            elif type(state) is states.Namespace:
                amount += self.class_amount_in_namespace(state)
        return amount

    def first_class_in_namespace(self, obj):
        for state in obj.content:
            if isinstance(state, states.Class):
                return state
            if type(state) is states.Namespace and not self.first_class_in_namespace(state) is None:
                return self.first_class_in_namespace(state)
        return None

    def verify_tabulation(self):
        cur_token = 0
        tokens = self.lexer.tokens_

        tab_size = 4
        current_tab = 0

        while True:

            new_line = False
            for i in range(0, current_tab):

                if tokens[cur_token].type_ == lexer.TokenType.end:
                    return

                if self.get_token_text(tokens[cur_token]) == '\r' \
                        or self.get_token_text(tokens[cur_token]) == '\n':
                    cur_token += 1
                    if self.get_token_text(tokens[cur_token]) == '\n':
                        cur_token += 1
                    new_line = True
                    break

                if tokens[cur_token].type_ == lexer.TokenType.end:
                    return

                if self.get_token_text(tokens[cur_token]) == '}':
                    #current_tab -= tab_size
                    if not i == current_tab - tab_size:
                        war = Warning()
                        war.type = WarningType.tabs
                        war.line = tokens[cur_token].line_
                        war.text = 'Wrong amount of spaces'
                        war.current_tab = current_tab - tab_size
                        self.warnings.append(war)
                    break

                if not self.get_token_text(tokens[cur_token]) == ' ':
                    war = Warning()
                    war.type = WarningType.tabs
                    war.line = tokens[cur_token].line_
                    war.text = 'Wrong amount of spaces'
                    war.current_tab = current_tab
                    self.warnings.append(war)
                    break
                    #nonlocal has_warn
                    #has_warn = True

                cur_token += 1
            else:
                #if not current_tab == 0 and self.get_token_text(tokens[cur_token]) == ' ':
                if self.get_token_text(tokens[cur_token]) == ' ':
                    war = Warning()
                    war.type = WarningType.tabs
                    war.line = tokens[cur_token].line_
                    war.text = 'Wrong amount of spaces'
                    war.current_tab = current_tab
                    self.warnings.append(war)

                    token = cur_token
                    while self.get_token_text(tokens[token]) == ' ':
                        token += 1

                    if self.get_token_text(tokens[token]) == '}':
                        war.current_tab = current_tab - tab_size

                    cur_token += 1

            if not new_line:
                if self.get_token_text(tokens[cur_token]) == '{' or self.get_token_text(tokens[cur_token]) == '}':


                    if self.get_token_text(tokens[cur_token]) == '}':
                        current_tab -= tab_size

                    if not (self.get_token_text(tokens[cur_token + 1]) == '\r'
                            or self.get_token_text(tokens[cur_token + 1]) == '\n'):

                        if not self.get_token_text(tokens[cur_token + 1]) == ';':
                            war = Warning()
                            war.type = WarningType.brackets_tabs
                            war.line = tokens[cur_token].line_
                            war.text = 'There should be new line after bracket'
                            war.current_tab = current_tab
                            self.warnings.append(war)

                    if self.get_token_text(tokens[cur_token]) == '{':
                        current_tab += tab_size

                while not (self.get_token_text(tokens[cur_token]) == '\r'
                    or self.get_token_text(tokens[cur_token]) == '\n'
                    or tokens[cur_token].type_ == lexer.TokenType.end):

                    cur_token += 1
                    if self.get_token_text(tokens[cur_token]) == '{':

                        war = Warning()
                        war.type = WarningType.brackets_tabs
                        war.line = tokens[cur_token].line_
                        war.text = 'There should be new line before and after bracket'
                        war.current_tab = current_tab
                        self.warnings.append(war)

                        current_tab += tab_size

                    elif self.get_token_text(tokens[cur_token]) == '}':
                        current_tab -= tab_size

                        #if not self.get_token_text(tokens[cur_token + 1]) == ';':
                        war = Warning()
                        war.type = WarningType.brackets_tabs
                        war.line = tokens[cur_token].line_
                        war.text = 'There should be new line before and after bracket'
                        war.current_tab = current_tab
                        self.warnings.append(war)

                else:
                    if self.get_token_text(tokens[cur_token]) == '\r':
                        cur_token += 1
                    if self.get_token_text(tokens[cur_token]) == '\n':
                        cur_token += 1

                if tokens[cur_token].type_ == lexer.TokenType.end:
                    return

            #cur_token += 1

    def verify_line_length(self):
        file = open(self.nm.name, 'r')
        lines = file.readlines()
        num = 1
        for line in lines:
            if len(line) > 78:
                war = Warning()
                war.type = WarningType.formatting
                war.line = num
                war.text = 'A line should not exceed 78 characters'
                self.warnings.append(war)
            num += 1

    def verify_tabs(self):
        tokens = self.lexer.tokens_

        for token in tokens:

            if self.get_token_text(token) == '\t':
                war = Warning()
                war.type = WarningType.formatting
                war.line = token.line_
                war.text = 'Do not use tabs, use spaces'
                self.warnings.append(war)
                return

    def verify_line_end(self):
        cur_token = 0
        tokens = self.lexer.tokens_

        while True:

            if self.get_token_text(tokens[cur_token]) == ';':
                next_text = self.get_token_text(tokens[cur_token + 1])
                if next_text == '\r' or next_text == '\n':
                    cur_token += 2
                    continue

                while not (self.get_token_text(tokens[cur_token]) == '\n'
                        or tokens[cur_token].type_ == lexer.TokenType.end):
                    cur_token += 1

                    t = tokens[cur_token]
                    text = self.get_token_text(t)

                    if not (t.type_ == lexer.TokenType.comment or text == ' '):
                        war = Warning()
                        war.type = WarningType.formatting
                        war.line = t.line_
                        war.text = 'There should be only one statement per line'
                        self.warnings.append(war)

                    while not (self.get_token_text(tokens[cur_token]) == '\n'
                               or tokens[cur_token].type_ == lexer.TokenType.end):
                        cur_token += 1

            if tokens[cur_token].type_ == lexer.TokenType.end:
                break

            cur_token += 1

    def verify_namespace(self, obj: states.Namespace):
        standart_processing = [states.Namespace, states.Class,
                               states.Struct, states.Union,
                               states.Typedef, states.Enum,
                               states.Using, states.UsingNamespace,
                               states.Macros, states.IfNDefGuard,
                               states.OtherPreprocessorDirective
                               ]

        previous_state = None

        for state in obj.content:
            tp = type(state)
            if tp in standart_processing:
                getattr(Verifier, 'verify_' + tp.__name__.lower())(self, state)
            elif tp is states.Function:
                self.verify_arg_amount(state)
                if '::' in state.name:
                    self.verify_function(state)
                else:
                    if not state.fwd_decl:
                        self.verify_doc_above_method(state, previous_state)
                    self.verify_global_function(state)
            elif tp is states.Variable:
                if '::' in state.name:
                    continue
                else:
                    self.verify_global_varible(state)
            elif tp is states.Comment:
                pass
            else:
                print('Unexpected token')
                previous_state = state

    def verify_doc_above_method(self, state, previous_state: states.State):
        warning = False
        if previous_state is not None and type(previous_state) is states.Comment:
            if not previous_state.block and not previous_state.name.startswith("*"):
                warning = True
        else:
            warning = True
        if warning:
            war = Warning()
            war.type = WarningType.doc_above_method
            war.line = state.line
            war.text = 'There should be doc /** ... */ above func.'
            self.warnings.append(war)

    # todo
    def verify_arg_amount(self, state: states.Function):
        pass#if state.args.__len__() > 3:


    def verify_class(self, obj: states.Class):
        if obj.is_decl:
            return

        if obj.name is not None and '_' in obj.name:
            war = Warning()
            war.type = WarningType.naming
            war.line = obj.line
            war.text = 'Class name should not has \'_\' in name'
            self.warnings.append(war)

        if obj.name is not None and obj.name[0:1].islower():
            war = Warning()
            war.type = WarningType.naming
            war.line = obj.line
            war.text = 'Class name should starts with capital letter'
            self.warnings.append(war)

        standart_processing = [states.Class,
                               states.Struct, states.Union,
                               states.Typedef, states.Enum,
                               states.Using,
                               states.Macros, states.IfNDefGuard,
                               states.OtherPreprocessorDirective,
                               states.Friend
                               ]
        prev_scope = states.Scope.private

        previous_state = None

        for state in obj.content:
            tp = type(state)
            if tp in standart_processing:
                getattr(Verifier, 'verify_' + tp.__name__.lower())(self, state)
            elif tp is states.Function:
                self.verify_arg_amount(state)
                self.verify_doc_above_method(state, previous_state)
                self.verify_member_function(state, obj.name)
            elif tp is states.Variable:
                self.verify_member_varible(state)
            elif tp is states.Comment:
                pass
            elif tp is states.Scope:
                if not state.value == (prev_scope + 1):
                    war = Warning()
                    war.type = WarningType.access
                    war.line = state.line
                    war.text = 'In class or structure access modifiers should be in order: public, protected, private'
                    self.warnings.append(war)
                prev_scope = state.value
            else:
                print('Unexpected token')
            previous_state = state

    def verify_friend(self, obj):
        pass

    def verify_struct(self, obj):
        self.verify_class(obj)

    def verify_union(self, obj):
        self.verify_class(obj)

    def verify_typedef(self, obj):
        if '_' in obj.type_name:
            war = Warning()
            war.type = WarningType.naming
            war.line = obj.line
            war.text = 'Typedef name should not has \'_\' in name'
            self.warnings.append(war)

        if obj.type_name[0:1].islower():
            war = Warning()
            war.type = WarningType.naming
            war.line = obj.line
            war.text = 'Typedef name should starts with uppercase letter'
            self.warnings.append(war)

        if not obj.type_name.endswith('Type'):
            war = Warning()
            war.type = WarningType.naming
            war.line = obj.line
            war.text = 'Typedef name should ends with \'Type\''
            self.warnings.append(war)

    def verify_enum(self, obj):
        for label in obj.labels:
            self.verify_enumlabel(label)

    def verify_enumlabel(self, obj):
        if not obj.name.isupper():
            war = Warning()
            war.type = WarningType.naming
            war.line = obj.line
            war.text = 'Enum label should contains only uppercase. Use \'_\' as separator'
            self.warnings.append(war)

    def verify_using(self, obj):
        if '_' in obj.names[0]:
            war = Warning()
            war.type = WarningType.naming
            war.line = obj.line
            war.text = 'Using name should not has \'_\' in name'
            self.warnings.append(war)

        if obj.names[0][0:1].islower():
            war = Warning()
            war.type = WarningType.naming
            war.line = obj.line
            war.text = 'Using name should starts with uppercase letter'
            self.warnings.append(war)

        if not obj.names[0].endswith('Type'):
            war = Warning()
            war.type = WarningType.naming
            war.line = obj.line
            war.text = 'Using name should ends with \'Type\''
            self.warnings.append(war)

    def verify_usingnamespace(self, obj):
        if self.nm.name.endswith('.hpp') or self.nm.name.endswith('.h'):
            war = Warning()
            war.type = WarningType.using_namespace
            war.line = obj.line
            war.text = 'Do not use \'using namespace\' inside header files'
            self.warnings.append(war)

    def verify_argument(self, obj):
        if obj.name == '':
            war = Warning()
            war.type = WarningType.naming
            war.line = obj.line
            war.text = 'Argument should has name'
            self.warnings.append(war)
            return

        if obj.name[0:1].isupper():
            war = Warning()
            war.type = WarningType.naming
            war.line = obj.line
            war.text = 'Argument ' + obj.name + ' should start with lowercase letter'
            self.warnings.append(war)

        if obj.mod == '&':
            if not obj.name.startswith('r'):
                war = Warning()
                war.type = WarningType.naming
                war.line = obj.line
                war.text = 'Reference argument ' + obj.name + ' should start with \'r\''
                self.warnings.append(war)
            else:
                if not obj.name[1:2].isupper():
                    war = Warning()
                    war.type = WarningType.naming
                    war.line = obj.line
                    war.text = 'Reference argument ' + obj.name + ' second letter should be uppercase'
                    self.warnings.append(war)

        if obj.mod == '*':
            if not obj.name.startswith('p'):
                war = Warning()
                war.type = WarningType.naming
                war.line = obj.line
                war.text = 'Pointer argument ' + obj.name + ' should start with \'p\''
                self.warnings.append(war)
            else:
                if not obj.name[1:2].isupper():
                    war = Warning()
                    war.type = WarningType.naming
                    war.line = obj.line
                    war.text = 'Pointer argument ' + obj.name + ' second letter should be uppercase'
                    self.warnings.append(war)

    def verify_block(self, obj):
        standart_processing = [states.Class,
                               states.Struct, states.Union,
                               states.Typedef, states.Enum,
                               states.Using, states.Block,
                               states.Macros, states.IfNDefGuard,
                               states.OtherPreprocessorDirective, states.If,
                               states.For, states.Switch,
                               states.Else, states.Do
                               ]

        for state in obj.content:
            tp = type(state)
            if tp in standart_processing:
                getattr(Verifier, 'verify_' + tp.__name__.lower())(self, state)
            elif tp is states.UsingNamespace:
                continue
            elif tp is states.Variable:
                self.verify_stack_varible(state)
            else:
                print('Unexpected token')

    def look_for_function_impl_(self, fun_name: str, state: states.State):
        if hasattr(state, 'content'):
            prev_state = None
            for obj in state.content:
                if isinstance(obj, states.Function) and obj.name == fun_name:
                    return obj.line, prev_state
                else:
                    ret = self.look_for_function_impl_(fun_name, obj)
                    if ret is not None:
                        return ret
                prev_state = obj
        return None

    def look_for_function_impl(self, fun_name: str):
        for nm in files.CppFile.file_states:
            ret = self.look_for_function_impl_(fun_name, nm)
            if ret is not None:
                return nm.name, ret
        return None

    def verify_member_function(self, obj: states.Function, class_name: str):
        if not (obj.name == 'dtor' or obj.name == 'ctor'):
            if not obj.name == 'operator':
                if '_' in obj.name:
                    war = Warning()
                    war.type = WarningType.naming
                    war.line = obj.line
                    war.text = 'Method name should not has \'_\' in name'
                    self.warnings.append(war)

                if obj.name[0:1].islower():
                    war = Warning()
                    war.type = WarningType.naming
                    war.line = obj.line
                    war.text = 'Method name should starts with capital letter'
                    self.warnings.append(war)

        self.verify_function(obj)

        if obj.fwd_decl and ('virtual' in obj.ftype or 'static' in obj.ftype):
            ret = self.look_for_function_impl(class_name + "::" + obj.name)
            if ret is not None:
                if not (isinstance(ret[1][1], states.Comment) and ret[1][1].name == obj.ftype):
                    war = Warning()
                    war.type = WarningType.impl_comment
                    war.line = ret[1][0]
                    war.text = 'Method implementation should has /*' + obj.ftype + '*/ comment according to declaration '
                    war.comment = '/*'+obj.ftype+'*/'

                    if not ret[0] in files.CppFile.verifiers:
                        files.CppFile.verifiers[ret[0]] = Verifier(None, None)

                    files.CppFile.verifiers[ret[0]].warnings.append(war)



    def verify_global_function(self, obj):
        if not obj.name == obj.name.lower():
            war = Warning()
            war.type = WarningType.naming
            war.line = obj.line
            war.text = 'C functions should not has uppercase letters in name. Use \'_\' as words delimiter'
            self.warnings.append(war)

        self.verify_function(obj)

    def verify_function(self, obj):
        for arg in obj.args:
            self.verify_argument(arg)

        if len(obj.args) > 3:
            for i in range(1, len(obj.args)):
                if not obj.args[i].line == obj.args[i - 1].line + 1:
                    war = Warning()
                    war.type = WarningType.formatting
                    war.line = obj.line
                    war.text = 'If function has more than 3 parameters, they should be formatted (each on new line)'
                    self.warnings.append(war)
                    break

        if not len(obj.content) == 0:
            self.verify_block(obj.content[0])
            if obj.content[0].end_line - obj.content[0].line > 100:
                war = Warning()
                war.type = WarningType.formatting
                war.line = obj.line
                war.text = 'Functions should limit themselves to a single page of code (100 lines)'
                self.warnings.append(war)

    def verify_global_varible(self, obj):
        self.verify_varible(obj)
        variables = obj.name.split(',')
        for var in variables:
            var.replace(' ', '')
            if obj.type is not None and ' const ' in obj.type:
                if not var == var.lower():
                    war = Warning()
                    war.type = WarningType.naming
                    war.line = obj.line
                    war.text = 'Global constants should not has uppercase letters in name. Use \'_\' as words delimiter'
                    self.warnings.append(war)
            else:
                if not var.startswith('g'):
                    war = Warning()
                    war.type = WarningType.naming
                    war.line = obj.line
                    war.text = 'Global variables names should be prepended with \'g\'.' \
                               ' Use uppercase letters as words separator'
                    self.warnings.append(war)
                else:
                    if var[1:2].islower():
                        war = Warning()
                        war.type = WarningType.naming
                        war.line = obj.line
                        war.text = 'Global variables should be in camel case after \'g\''
                        self.warnings.append(war)



    def verify_stack_varible(self, obj):
        self.verify_varible(obj)
        variables = obj.name.split(',')
        for var in variables:
            var.replace(' ', '')
            if not var == var.lower():
                war = Warning()
                war.type = WarningType.naming
                war.line = obj.line
                war.text = 'Variables names on stack should not has uppercase letters in name' \
                           '. Use \'_\' as words delimiter'
                self.warnings.append(war)
            if obj.mod == '&':
                if not var.startswith('r'):
                    war = Warning()
                    war.type = WarningType.naming
                    war.line = obj.line
                    war.text = 'Reference variable ' + obj.name + ' should start with \'r\''
                    self.warnings.append(war)

            if obj.mod == '*':
                if not var.startswith('p'):
                    war = Warning()
                    war.type = WarningType.naming
                    war.line = obj.line
                    war.text = 'Pointer variable ' + obj.name + ' should start with \'p\''
                    self.warnings.append(war)

    def verify_member_varible(self, obj):
        self.verify_varible(obj)
        variables = obj.name.split(',')
        for var in variables:
            var.replace(' ', '')

            if obj.mod == '&':
                if not obj.name.startswith('mr'):
                    war = Warning()
                    war.type = WarningType.naming
                    war.line = obj.line
                    war.text = 'Reference class field ' + obj.name + ' should start with \'mr\''
                    self.warnings.append(war)
                else:
                    if not obj.name[2:3].isupper():
                        war = Warning()
                        war.type = WarningType.naming
                        war.line = obj.line
                        war.text = 'Reference class field  ' + obj.name + ' third letter should be uppercase'
                        self.warnings.append(war)

            elif obj.mod == '*':
                if not obj.name.startswith('mp'):
                    war = Warning()
                    war.type = WarningType.naming
                    war.line = obj.line
                    war.text = 'Pointer class field ' + obj.name + ' should start with \'mp\''
                    self.warnings.append(war)
                else:
                    if not obj.name[2:3].isupper():
                        war = Warning()
                        war.type = WarningType.naming
                        war.line = obj.line
                        war.text = 'Pointer class field ' + obj.name + ' third letter should be uppercase'
                        self.warnings.append(war)
            else:
                if not obj.name.startswith('m'):
                    war = Warning()
                    war.type = WarningType.naming
                    war.line = obj.line
                    war.text = 'Pointer class field ' + obj.name + ' should start with \'m\''
                    self.warnings.append(war)
                else:
                    if not obj.name[1:2].isupper():
                        war = Warning()
                        war.type = WarningType.naming
                        war.line = obj.line
                        war.text = 'Pointer class field ' + obj.name + ' second letter should be uppercase'
                        self.warnings.append(war)




    def verify_varible(self, obj):
        if ',' in obj.name:
            war = Warning()
            war.type = WarningType.formatting
            war.line = obj.line
            war.text = 'Do not put more than one variable in one declaration'
            self.warnings.append(war)

    def verify_macros(self, obj):
        if not obj.name.upper() == obj.name:
            war = Warning()
            war.type = WarningType.naming
            war.line = obj.line
            war.text = 'Put #defines names in all upper using \'_\' separators.'
            self.warnings.append(war)

    def verify_ifndefguard(self, obj):
        pass

    def verify_otherpreprocessordirective(self, obj):
        pass

    def verify_if(self, obj):
        if not obj.has_space:
            war = Warning()
            war.type = WarningType.formatting
            war.line = obj.line
            war.text = 'Put space after \'if\''
            self.warnings.append(war)

        if not obj.has_brackets:
            war = Warning()
            war.type = WarningType.formatting
            war.line = obj.line
            war.text = 'Put brackets after \'if\''
            self.warnings.append(war)

        if obj.has_assign:
            war = Warning()
            war.type = WarningType.formatting
            war.line = obj.line
            war.text = '\'if\' has \'=\' inside condition'
            self.warnings.append(war)



    def verify_for(self, obj):
        if not obj.has_space:
            war = Warning()
            war.type = WarningType.formatting
            war.line = obj.line
            war.text = 'Put space after \'for\''
            self.warnings.append(war)

        if not obj.has_brackets:
            war = Warning()
            war.type = WarningType.formatting
            war.line = obj.line
            war.text = 'Put brackets after \'for\''
            self.warnings.append(war)


    def verify_switch(self, obj):
        if not obj.has_space:
            war = Warning()
            war.type = WarningType.formatting
            war.line = obj.line
            war.text = 'Put space after \'switch\''
            self.warnings.append(war)


    def verify_else(self, obj):
        if not obj.has_brackets:
            war = Warning()
            war.type = WarningType.formatting
            war.line = obj.line
            war.text = 'Put brackets after \'else\''
            self.warnings.append(war)


    def verify_do(self, obj):
        if not obj.has_space:
            war = Warning()
            war.type = WarningType.formatting
            war.line = obj.line
            war.text = 'Put space after \'do\''
            self.warnings.append(war)
