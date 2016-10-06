import os, sys
import fnmatch
from os.path import join

import codecs

__file__ = os.path.normpath(os.path.abspath(__file__))
__path__ = os.path.dirname(__file__)
__csharp_path__ = join(__path__, 'csharp')
__yaml_path__ = join(__path__, 'yaml')
print(__csharp_path__)

if __path__ not in sys.path:
    sys.path.insert(0, __path__)
if __csharp_path__ not in sys.path:
    sys.path.insert(0, __csharp_path__)
if __yaml_path__ not in sys.path:
    sys.path.insert(0, __yaml_path__)

from token_parser import TokenParser
import yaml_parser

from csharp_class_method_parser import CSharpClassMethod
from csharp.csharp_element import CSharpElement
# from csharp import csharp_class_method_parser
from csharp import csharp_importer_parser
from csharp import csharp_class_parser



class SymbolicParser:
    symbolic_data = {}
    def __init__(self):
        self.symbolic_data = { \
            'parse': { \
                'by_files' : {} \
            } \
        }

    def parse_project(self, project_path, file_path):
        print('parse_project')
        self.symbolic_data['parse']['yaml'] = yaml_parser.get_all_guid_files(project_path, file_path)

    def parse_file(self, file):
        if file is None:
            return
        elif file.lower().endswith('.cs'):
            # Parse file into a set of tokens
            tokens_data = TokenParser().parse_file(file)
            # print(tokens_data) # For debug purposes
            tokens_data = csharp_importer_parser.parse_tokens(tokens_data)
            tokens_data = csharp_class_parser.parse_tokens(tokens_data)
            # Save data
            self.symbolic_data['parse']['by_files'][file] = tokens_data
        elif file.lower().endswith(('.unity','.prefab','.asset')):
            # yaml_parser
            if not 'yaml' in self.symbolic_data['parse']:
                self.symbolic_data['parse']['yaml'] = yaml_parser.get_all_guid_files('', file)
            self.symbolic_data['parse'] = yaml_parser.parse_yaml(file, self.symbolic_data['parse'])

    def debugself(self):
        print('debugself')

    def print_selection_info(self, view):
        file = view.file_name()

        if file == None:
            return

        def open_file(file):
            view.window().open_file(file)

        def go_to_reference(id):
            if view.window().active_view():
                row = self.symbolic_data['parse']['by_files'][file]['row_by_id'][id]
                col = 1
                print("Trying to go to line " + str(row))
                view.window().active_view().run_command(
                        "goto_row_col",
                        {"row": row, "col": col}
                )

        def show_popup(text, action):
            view.show_popup(text, on_navigate=action)

        if file.lower().endswith(('.unity','.prefab','.asset', '.meta')):
            for region in view.sel():
                selected_text = view.substr(region)

                if not yaml_parser.print_yaml_file_info(file, selected_text, self.symbolic_data['parse'], open_file, show_popup):
                    if not yaml_parser.print_yaml_gameobject_info(file, selected_text, self.symbolic_data['parse'], go_to_reference, show_popup):
                        yaml_parser.print_yaml_transform_info(file, selected_text, self.symbolic_data['parse'], go_to_reference, show_popup)
        elif file.lower().endswith('.cs'):
            for region in view.sel():
                rowcol = view.rowcol(region.begin())
                semantic_object = self.get_semantic_token(file, rowcol, True, True)
                # print('parser.py::print_selection_info - received ' + str(type(semantic_object)) + " " + \
                    # str(type(CSharpClassMethod("",[],[]))) + \
                    # str(isinstance(semantic_object, type(CSharpClassMethod("",[],[])))))
                if semantic_object == None:
                    # print('parser.py::print_selection_info - received None ')
                    return
                if isinstance(semantic_object, csharp_class_parser.CSharpClass) or  \
                   isinstance(semantic_object, CSharpClassMethod):
                    # print('parser.py::print_selection_info - show class_info ' + semantic_object.class_name)
                    show_popup(semantic_object.print_element_info(), go_to_reference)
                else:
                    # print('parser.py::print_selection_info - It is not a CSharpClass instance')
                    return

    # Print outline for current file
    # @param show_outline - method to exhibit outline
    #                       should receive a text and navigation method
    def print_outline(self, file, show_outline):
        file_data = self.symbolic_data['parse']['by_files'][file]

        if 'outline_data' in file_data:
            outline_data = file_data['outline_data']
            text_outline = ''
            index = 0

            for c in outline_data:
                if index > 0:
                    text_outline = text_outline + '<br>'
                text_outline = text_outline + c.print_outline()
                index = index + 1

            # print(class_outline)
            show_outline(text_outline)

    def get_semantic_token(self, file, rowcol, usingcol = False, sameLine=False):
        file_data = self.symbolic_data['parse']['by_files'][file]
        if 'token_position' in file_data:
            token_position = file_data['token_position']
            tokens = file_data['tokens']
            row, col = rowcol
            print('parser.py::get_semantic_token - searching in position ' + str(row) + ',' + str(col))
            total_tokens = len(token_position)
            for i in list(reversed(range(0, total_tokens))):
                token_row,  token_col = token_position[i]
                token_size = len(tokens[i])

                if ((not sameLine and row > token_row) or \
                    (sameLine and row == token_row)) and \
                    (not usingcol or (col <= token_col and col >= (token_col - token_size))):
                    print('parser.py::get_semantic_token - found semantic token: ' + str(i) + \
                        ' - ' + str(file_data['semantic_tokens'][i]) + ' in position ' +  \
                        str(token_row) + ',' + str(token_col) + " which token is " + \
                        tokens[i])
                    return file_data['semantic_tokens'][i]
        else:
            return None

    def print_debuglog(self, file, rowcol):
        file_data = self.symbolic_data['parse']['by_files'][file]
        semantic_object = self.get_semantic_token(file, rowcol)

        if semantic_object == None:
            return ''
        if isinstance(semantic_object, CSharpClassMethod):
            return semantic_object.get_debug_log()
        else:
            return ""
