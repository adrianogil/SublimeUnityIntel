import sublime, sublime_plugin
import os
import sys



# print(__path__)

__file__ = os.path.normpath(os.path.abspath(__file__))
__path__ = os.path.dirname(__file__)
__parser_path__ = os.path.join(__path__, 'unityparser')
if __path__ not in sys.path:
    sys.path.insert(0, __path__)
# print(__parser_path__)
if __parser_path__ not in sys.path:
    sys.path.insert(0, __parser_path__)

from unityparser.parser import SymbolicParser

intel_data = { \
    'parse': { \
        'by_files' : {} \
    } \
}

class SublimeUnityIntel(sublime_plugin.EventListener):
    def on_activated_async(self, view):
        current_file = view.file_name()

        print(current_file)

        if current_file is None or not current_file.lower().endswith('.cs'):
            return

        symbolicParser = SymbolicParser()
        intel_data['parse']['by_files'][current_file] = \
             symbolicParser.parse_file(current_file)


class DebugintelCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        print(intel_data)

class OutlineCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        print('Running command')
        view = self.view
        current_file = view.file_name()

        # parser = CSharpParser()
        # parser_data = parser.parse_file(current_file)
        # classes_data = parser_data['by_files'][current_file]['classes']

        classes_data = intel_data['parse']['by_files'][current_file]['classes']


        def go_to_reference(line):
            # file = ref[0]
            if view.window().active_view():
                row = int(line)+1
                col = 1
                print("Trying to go to line " + str(row))
                view.window().active_view().run_command(
                        "goto_row_col",
                        {"row": row, "col": col}
                )

        class_outline = ''

        index = 0

        for c in classes_data:
            if index > 0:
                class_outline = class_outline + '<br>'
            class_outline = class_outline + c.print_outline()
            index = index + 1

        # print(class_outline)
        view.show_popup(class_outline, on_navigate=go_to_reference)


