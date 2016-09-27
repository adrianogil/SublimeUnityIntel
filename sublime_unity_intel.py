import sublime, sublime_plugin
import os
import sys

__file__ = os.path.normpath(os.path.abspath(__file__))
__path__ = os.path.dirname(__file__)

# print(__path__)


if __path__ not in sys.path:
    sys.path.insert(0, __path__)

from csharp_parser import CSharpParser

intel_data = {}

class SublimeUnityIntel(sublime_plugin.EventListener):
    def on_load(self, view):
        current_file = view.file_name()

        print(current_file)

        if current_file is None or not current_file.lower().endswith('.cs'):
            return

        parser = CSharpParser()
        intel_data['parse'] = parser.parse_file(current_file)

        

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
            class_outline = class_outline + '<a href="' + str(c.line_in_file) + '">Class ' + c.class_name + '</a>'
            for m in c.methods_data:
                class_outline = class_outline + '<br>'
                class_outline = class_outline + m.print_outline()
            index = index + 1

        # print(class_outline)
        view.show_popup(class_outline, on_navigate=go_to_reference)


