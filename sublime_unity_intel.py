import sublime, sublime_plugin
import os, sys, time

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

    def on_selection_modified_async(self, view):
        symbolic_parser.print_selection_info(view)

class ParseUnityProjectCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        current_file = self.view.file_name()
        print("ParseUnityProjectCommand -> parse project from " + str(current_file))

        if current_file is None:
            return
        # Parse the whole project one single time
        symbolic_parser.parse_project(current_file)

class DebugintelCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        symbolic_parser.debugself()

class OutlineCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        print('Running command "Outline"')
        view = self.view
        current_file = view.file_name()

        symbolic_parser.print_outline(current_file, view, sublime.MONOSPACE_FONT)

class FieldoutlineCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        print('Running command "Outline"')
        view = self.view
        current_file = view.file_name()

        symbolic_parser.print_fields_outline(current_file, view, sublime.MONOSPACE_FONT)

class InsertTextOnSelectionCommand(sublime_plugin.TextCommand):
    def run(self, edit, text):
        for region in self.view.sel():
            self.view.replace(edit, region, text)

class InsertTextOnPositionCommand(sublime_plugin.TextCommand):
    def run(self, edit, text, line):
        line = int(line)

        print('InsertTextOnPositionCommand tried to insert text "' + text + '" into line ' + str(line))

        # Negative line numbers count from the end of the buffer
        if line < 0:
            lines, _ = self.view.rowcol(self.view.size())
            line = lines + line + 1

        point = self.view.text_point(line, 0)
        indent_point = self.view.text_point(line-1, 0)

        view_line = self.view.line(point)
        indent_line = self.view.line(indent_point)

        line_str = self.view.substr(indent_line)
        indent = len(line_str) - len(line_str.lstrip())

        for i in range(0, indent):
            text = ' ' + text;

        self.view.insert(edit, view_line.begin(), text)

class SelectTextOnPosition(sublime_plugin.TextCommand):
    def run(self, edit, line, begin_text, end_text):
        if line < 0:
            lines, _ = self.view.rowcol(self.view.size())
            line = lines + line + 1

        point = self.view.text_point(line, 0)

        view_line = self.view.line(point)
        line_str = self.view.substr(view_line)
        indent = len(line_str) - len(line_str.lstrip())

        target_region = sublime.Region(point + indent + begin_text, point + indent + end_text)
        self.view.sel().clear()
        self.view.sel().add(target_region)

class UnityInterfaceFromClassCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        print('Running command "DebugLog"')
        view = self.view
        file = view.file_name()


        if file.lower().endswith(('.cs')):
            debug_log = ""
            regions = view.sel()
            if len(regions) == 1:
                main_region = regions[0]
                rowcol = view.rowcol(main_region.begin())
                class_interface = symbolic_parser.create_interface_from_class(file, rowcol)
                sublime.set_clipboard(class_interface)


class SmartdebugCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        print('Running command "DebugLog"')
        view = self.view
        file = view.file_name()
        if file.lower().endswith(('.cs')):
            debug_log = ""
            regions = view.sel()
            if len(regions) == 1:
                main_region = regions[0]
                rowcol = view.rowcol(main_region.begin())
                debug_log = symbolic_parser.print_debuglog(file, rowcol)
            elif len(regions) > 1:
                variables = []
                main_region = None
                for i in range(0, len(regions)):
                    region = regions[i]
                    selected_text = view.substr(region)
                    if selected_text == '':
                        main_region = region
                    else:
                        variables.append(selected_text)
                rowcol = view.rowcol(main_region.begin())
                debug_log = symbolic_parser.print_debuglog_with_vars(file, rowcol, variables)
            print('Running command "DebugLog" - ' + debug_log)
            view.replace(edit, main_region, debug_log)

class UnityBehaviorsEvents(sublime_plugin.TextCommand):
    def run(self, edit):
        print('Running command "DebugLog"')
        symbolic_parser.show_unity_behaviors_events(self.view, sublime.MONOSPACE_FONT)

class GotoRowColCommand(sublime_plugin.TextCommand):
        def run(self, edit, row, col, file=None):
            print("INFO: Input: " + str({"row": row, "col": col}))

            view = self.view
            if file != None:
                print('Opening file ' + file)
                file_loc = "%s:%s" % (file, row)
                view = self.view.window().open_file(file_loc, sublime.ENCODED_POSITION)
            else:
                # rows and columns are zero based, so subtract 1
                # convert text to int
                (row, col) = (int(row) - 1, int(col) - 1)
                if row > -1 and col > -1:
                        # col may be greater than the row length
                        col = min(col, len(view.substr(view.full_line(view.text_point(row, 0))))-1)
                        print("INFO: Calculated: " + str({"row": row, "col": col})) # r1.01 (->)
                        view.sel().clear()
                        view.sel().add(sublime.Region(view.text_point(row, col)))
                        view.show(view.text_point(row, col))
                else:
                        print("ERROR: row or col are less than zero")


