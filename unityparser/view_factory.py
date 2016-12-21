import os, sys

__file__ = os.path.normpath(os.path.abspath(__file__))
__path__ = os.path.dirname(__file__)
__popup_path__ = os.path.join(__path__, 'popup')

# print(__path__)

if __path__ not in sys.path:
    sys.path.insert(0, __path__)

if __popup_path__ not in sys.path:
    sys.path.insert(0, __popup_path__)

from csharp_element import CSharpElement
from csharp_reference import CSharpReference

import popup.yaml_reference_popup

class ViewFactory:
    def __init__(self, view, symbolic_parser):
        self.view = view
        self.symbolic_parser = symbolic_parser
        self.symbolic_data = symbolic_parser.symbolic_data
        self.view_actions = {}
        def load_action(action_id):
            action_id = int(action_id)
            if action_id in self.view_actions:
                self.view_actions[action_id]()
        self.selection_action = load_action

    def clear_actions(self):
        self.view_actions = {}

    def register_action(self, action_id, action):
        self.view_actions[action_id] = action

    def show_popup(self, html, width=300):
        self.view.show_popup(html, on_navigate=self.selection_action, max_width=width)

    def get_showpopup(self):
        def show_popup(text, action):
            self.view.show_popup(text, on_navigate=action)
        return show_popup

    def get_open_file_action(self, file):
        def open_file():
            self.view.window().open_file(file)
        return open_file

    def get_open_file(self):
        def open_file(file):
            self.view.window().open_file(file)
        return open_file

    def get_goto_file_reference_action(self, file, line):
        def go_to_reference():
            if self.view.window().active_view():
                row = line
                col = 1
                print("Trying to go to line " + str(row))
                self.view.window().active_view().run_command(
                        "goto_row_col",
                        {"row": row, "col": col, "file": file}
                )
        return go_to_reference

    def get_goto_reference_action(self, yaml_id):
        def go_to_reference():
            if self.view.window().active_view():
                row = self.symbolic_parser.get_current_file_data()['row_by_id'][yaml_id]
                col = 1
                print("Trying to go to line " + str(row))
                self.view.window().active_view().run_command(
                        "goto_row_col",
                        {"row": row, "col": col}
                )
        return go_to_reference

    def get_goto_reference(self):
        def go_to_reference(id):
            if self.view.window().active_view():
                row = self.symbolic_parser.get_current_file_data()['row_by_id'][id]
                col = 1
                print("Trying to go to line " + str(row))
                self.view.window().active_view().run_command(
                        "goto_row_col",
                        {"row": row, "col": col}
                )
        return go_to_reference

    def get_goto_line_action(self, line):
        def go_to_line():
            if self.view.window().active_view():
                row = line
                col = 1
                print("Trying to go to line " + str(row))
                self.view.window().active_view().run_command(
                        "goto_row_col",
                        {"row": row, "col": col}
                )
        return go_to_line

    def get_goto_line(self):
        def go_to_line(line):
            if self.view.window().active_view():
                row = line
                col = 1
                print("Trying to go to line " + str(row))
                self.view.window().active_view().run_command(
                        "goto_row_col",
                        {"row": row, "col": col}
                )
        return go_to_line

    def print_yaml_ref_popup(self, class_instance):
        popup.yaml_reference_popup.print_popup(class_instance, self)