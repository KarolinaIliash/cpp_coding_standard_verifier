import files_util
import automatic_fixer

class UserSpeaker:
    @staticmethod
    def speak():
        path = input("Hello. Please enter path to directory or file.\n")
        files_list = files_util.get_files(path, path)

        import files
        import os

        cpp_files = []

        for f in files_list:
            fl = files.CppFile(path + f)
            fl.scan()
            cpp_files.append(fl)
        for fl in cpp_files:
            fl.verify()

        statistics = files.CppFile.get_statistic()

        sum = statistics[0]
        percents = statistics[1]

        print("we found ", sum, " warnings.")
        print(percents)

        mode = input("Choose how do you want to fix them:\n1.Automatic\n2.Interactive\n3.None\n")

        if mode == '1':
            for fl in cpp_files:
                fixer = automatic_fixer.AutomaticFixer(files.CppFile.verifiers[fl.nm.name].warnings, fl.nm.name)
                fixer.fix_tabs()
                fixer.fix_impl_comments()
                fixer.fix_brackets_tabs()
        elif mode == '2':
            pass
        else:
            return

        #print("we can fix next types:\n1.Tabulation\n2.Implementation comments\n3.Brackets")

UserSpeaker.speak()


