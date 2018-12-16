import files_util
import automatic_fixer
import json

class UserSpeaker:
    @staticmethod
    def speak():
        path = input("Hello. Please enter path to directory or file.\n")
        files_list = files_util.get_files(path, path)

        import files
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

        print("We found ", sum, " warnings.")
        print("Brackets and tabulation warnings will be right if you don't have tabs in code.")

        print(json.JSONEncoder(indent=4, separators=(',', ': ')).encode(percents))

        mode = input("Do you want to save warnings in json format into file? (y/n)\n")

        if mode == 'y':
            while True:
                file = input("Input path to file\nPath: ")
                try:
                    f = open(file, 'w')
                    from files import MyEncoder
                    f.write(MyEncoder(indent=4, separators=(',', ': ')).encode(files.CppFile.verifiers))
                    f.flush()
                    f.close()
                    break
                except:
                    print("Bad input")

        mode = input("Do you want to start automatic fix? (y/n)\n")

        if mode == 'y':
            for fl in cpp_files:
                fixer = automatic_fixer.AutomaticFixer(files.CppFile.verifiers[fl.nm.name].warnings, fl.nm.name)
                fixer.fix_tabs_to_spaces()

            files.CppFile.file_states = []
            files.CppFile.verifiers = {}

            for fl in cpp_files:
                fl.scan()

            for fl in cpp_files:
                fl.verify()

            for fl in cpp_files:
                fixer = automatic_fixer.AutomaticFixer(files.CppFile.verifiers[fl.nm.name].warnings, fl.nm.name)
                fixer.fix_tabs()
                fixer.fix_impl_comments()
                fixer.fix_brackets_tabs()



