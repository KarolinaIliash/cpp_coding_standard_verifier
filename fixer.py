import verifier

class Fixer:
    def __init__(self, warning: verifier.Warning, file: str):
        self.warning = warning
        self.file = file

    def eat_spaces(self, text: str):
        for i in range(text.__len__()):
            if not text[i] == ' ':
                break
        return text[i:]

    def get_file_lines(self):
        f = open(self.file, 'r')
        lines = f.readlines()
        f.close()
        return lines

    def write_lines_to_file(self, lines):
        f = open(self.file, 'w')
        f.writelines(lines)
        f.flush()
        f.close()

class TabsFixer(Fixer):
    def __init__(self, warning: Warning, file: str):
        super().__init__(warning, file)

    def fix(self, write_immediately):
        lines = self.get_file_lines()
        line_to_fix = lines[self.warning.line] # type: str
        #line_without_spaces = self.eat_spaces(line_to_fix)
        #spaces_to_add = ' ' * self.warning.current_tab
        #changed_line = spaces_to_add + line_without_spaces
        changed_line = self.fix_line(line_to_fix)
        lines[self.warning.line] = changed_line
        if write_immediately:
            self.write_lines_to_file
        else:
            return lines

    def fix_line(self, line):
        line_without_spaces = self.eat_spaces(line)
        spaces_to_add = ' ' * self.warning.current_tab
        changed_line = spaces_to_add + line_without_spaces
        return changed_line

class BracketsTabsFixer(Fixer):
    def __init__(self, warning: Warning, file: str):
        super().__init__(warning, file)

    def find_first_bracket(self, line: str):
        for i in range(line.__len__()):
            if line[i] == '{' or line[i] == '}':
                return i
    #todo
    def fix(self):
        lines = self.get_file_lines()
        line_to_fix = lines[self.warning.line] # type: str
        pos_bracket = self.find_first_bracket(line_to_fix)






