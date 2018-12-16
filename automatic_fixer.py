import verifier
import fixer
import enum

class AutomaticFixer:
    def __init__(self, warnings, file):
        self.warnings = warnings
        self.file = file

    def tabs_warnings(self):
        warnings = []
        for w in self.warnings:
            if w.type == verifier.WarningType.tabs:
                warnings.append(w)
        return warnings

    def fix_tabs(self):
        warnings = self.warnings
        #tabs_warnings = [w for w in warnings if w.type == verifier.WarningType.tabs.name]
        tabs_warnings = [w for w in warnings if w.type == verifier.WarningType.tabs]
        #tabs_warnings = self.tabs_warnings()
        f = open(self.file, 'r')
        lines = f.readlines()
        f.close()
        for w in tabs_warnings:
            fixer_ = fixer.TabsFixer(w, self.file)
            line = lines[w.line]
            line = fixer_.fix_line(line)
            lines[w.line] = line
        f = open(self.file, 'w')
        f.writelines(lines)
        f.flush()
        f.close()

    def fix_impl_comments(self):
        warnings = self.warnings
        impl_comments_warnings = [w for w in warnings if w.type == verifier.WarningType.impl_comment]
        f = open(self.file, 'r')
        lines = f.readlines()
        f.close()
        for w in impl_comments_warnings:
            fixer_ = fixer.ImplCommentFixer(w, self.file)
            line = lines[w.line]
            line = fixer_.fix_line(line)
            lines[w.line] = line
        f = open(self.file, 'w')
        f.writelines(lines)
        f.flush()
        f.close()

    def fix_brackets_tabs(self):
        warnings = self.warnings
        brackets_tabs_warnings = [w for w in warnings if w.type == verifier.WarningType.brackets_tabs]
        f = open(self.file, 'r')
        lines = f.readlines()
        f.close()
        for w in reversed(brackets_tabs_warnings):
            fixer_ = fixer.BracketsTabsFixer(w, self.file)
            line = lines[w.line]
            lines_ = fixer_.fix_line(line)
            lines[w.line] = lines_[0]
            for i in range(1, len(lines_)):
                lines.insert(w.line + i, lines_[i])
        f = open(self.file, 'w')
        f.writelines(lines)
        f.flush()
        f.close()

