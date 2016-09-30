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

symbolic_parser = SymbolicParser()

class SublimeUnityIntel(sublime_plugin.EventListener):
    # Parse current file whenever the view gains focus
    def on_activated_async(self, view):
        current_file = view.file_name()
        print("SublimeUnityIntel -> parse file " + str(current_file))

        if current_file is None:
            return
        symbolic_parser.parse_file(current_file)

        # Parse the whole project one single time
        window_variables = view.window().extract_variables()
        project_path = ''
        if 'project_path' in window_variables:
            project_path = window_variables["project_path"]
        file_name = view.file_name()
        symbolic_parser.parse_project(project_path, file_name)

    def on_selection_modified_async(self, view):
        symbolic_parser.print_selection_info(view)

class DebugintelCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        symbolic_parser.debugself()

class OutlineCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        print('Running command')
        view = self.view
        current_file = view.file_name()

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

        def show_popup(text):
            view.show_popup(text, on_navigate=go_to_reference)

        symbolic_parser.print_outline(current_file, show_popup)

class GotoRowColCommand(sublime_plugin.TextCommand):
        def run(self, edit, row, col):
                print("INFO: Input: " + str({"row": row, "col": col}))
                # rows and columns are zero based, so subtract 1
                # convert text to int
                (row, col) = (int(row) - 1, int(col) - 1)
                if row > -1 and col > -1:
                        # col may be greater than the row length
                        col = min(col, len(self.view.substr(self.view.full_line(self.view.text_point(row, 0))))-1)
                        print("INFO: Calculated: " + str({"row": row, "col": col})) # r1.01 (->)
                        self.view.sel().clear()
                        self.view.sel().add(sublime.Region(self.view.text_point(row, col)))
                        self.view.show(self.view.text_point(row, col))
                else:
                        print("ERROR: row or col are less than zero")


