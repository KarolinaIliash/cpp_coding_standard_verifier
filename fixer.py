import verifier
import os

class Fixer:
    def __init__(self, warning: verifier.Warning, file: str):
        self.warning = warning
        self.file = file

    def eat_spaces(self, text: str):
        for i in range(text.__len__()):
            if not text[i] == ' ':
                return text[i:], i


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

    def flush_fix_line(self):
        lines = self.get_file_lines()
        line_to_fix = lines[self.warning.line]  # type: str
        changed_line = self.fix_line(line_to_fix)
        lines[self.warning.line] = changed_line
        self.write_lines_to_file

    def flush_fix_lines(self):
        lines = self.get_file_lines()
        line_to_fix = lines[self.warning.line]  # type: str
        lines_ = self.fix_line(line_to_fix)
        lines[self.warning.line] = lines_[0]
        for i in range(1, len(lines_)):
            lines.insert(self.warning.line + i, lines_[i])

class TabsFixer(Fixer):
    def __init__(self, warning: Warning, file: str):
        super().__init__(warning, file)

    # def flush_fix(self):
    #     lines = self.get_file_lines()
    #     line_to_fix = lines[self.warning.line] # type: str
    #     #line_without_spaces = self.eat_spaces(line_to_fix)
    #     #spaces_to_add = ' ' * self.warning.current_tab
    #     #changed_line = spaces_to_add + line_without_spaces
    #     changed_line = self.fix_line(line_to_fix)
    #     lines[self.warning.line] = changed_line
    #     self.write_lines_to_file

    def fix_line(self, line):
        line_without_spaces = self.eat_spaces(line)[0]
        spaces_to_add = ' ' * self.warning.current_tab
        changed_line = spaces_to_add + line_without_spaces
        return changed_line

class ImplCommentFixer(Fixer):
    def __init__(self, warning: Warning, file: str):
        super().__init__(warning, file)

    def fix_line(self, line: str):
        rest, i = self.eat_spaces(line)
        fixed_line = ' ' * i + self.warning.comment + ' ' + rest
        return fixed_line




class BracketsTabsFixer(Fixer):
    def __init__(self, warning: Warning, file: str):
        super().__init__(warning, file)

    def find_last_bracket(self, line: str):
        for i in reversed(range(line.__len__())):
            if line[i] == '{' or line[i] == '}':
                return i
    #todo
    def fix(self):
        lines = self.get_file_lines()
        line_to_fix = lines[self.warning.line] # type: str
        pos_bracket = self.find_first_bracket(line_to_fix)
        changed_line = line_to_fix[0:pos_bracket] + os.linesep + ' ' * self.warning.current_tab + line_to_fix[pos_bracket:]
        lines[self.warning.line] = changed_line
        self.write_lines_to_file(lines)

    def fix_line(self, line):
        pos_bracket = self.find_last_bracket(line)
        if line[pos_bracket] == '{':
            return self.fix_open_bracket(line, pos_bracket)
        else:
            return self.fix_close_bracket(line, pos_bracket)

    def fix_open_bracket(self, line, pos_bracket):
        if not pos_bracket == self.warning.current_tab:
            line = line[0:pos_bracket] + '\n' + ' ' * self.warning.current_tab + self.eat_spaces(line[pos_bracket:])
            pos_bracket += 1 + self.warning.current_tab

        if len(line) > pos_bracket + 1 and not line[pos_bracket + 1] == '\n':
            line = line[0:pos_bracket + 1] + '\n' + ' ' * (self.warning.current_tab + 4) + self.eat_spaces(line[pos_bracket + 1:])

        lines = line.split('\n')
        for i in range(0, len(lines) - 1):  # split makes redundant empty string after last \n
            lines[i] = lines[i] + '\n'
        return lines[:-1]

    def fix_close_bracket(self, line, pos_bracket):
        if not pos_bracket == self.warning.current_tab:
            line = line[0:pos_bracket] + '\n' + ' ' * self.warning.current_tab + self.eat_spaces(line[pos_bracket:])
            pos_bracket += 1 + self.warning.current_tab

        if len(line) > pos_bracket + 1 and not line[pos_bracket + 1] == '\n' and not (line[pos_bracket + 1] == ';' and line[pos_bracket + 2] == '\n'):
            pos = pos_bracket + 1
            if line[pos_bracket + 1] == ';':
                pos = pos_bracket + 2
            line = line[0:pos] + '\n' + ' ' * self.warning.current_tab + self.eat_spaces(line[pos:])

        lines = line.split('\n')
        for i in range(0, len(lines) - 1):  # split makes redundant empty string after last \n
            lines[i] = lines[i] + '\n'
        return lines[:-1]

    def eat_spaces(self, str):
        for i in range(len(str)):
            if not str[i] == ' ':
                break
        return str[i:]

