import verifier
import fixer
import enum

class AutomaticTabsFixer:
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
        tabs_warnings = [w for w in warnings if w.type == verifier.WarningType.tabs.name]
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
