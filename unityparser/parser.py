import os, sys, time
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

import csharp
import view_factory
import parser_utils

class SymbolicParser:
    def __init__(self):
        self.symbolic_data = { \
            'parse': { \
                'symbols' : {}, \
                'by_files' : {} \
            } \
        }
        self.parse_file_by_filetype = { \
            ('.cs') : self.parse_csharp_file, \
            ('.unity','.prefab','.asset') : self.parse_yaml_file \
        }
        self.last_parse_time = {}

    def parse_project(self, file_path):
        project_path = parser_utils.get_project_path('', file_path)
        if project_path != '' and (not project_path in self.last_parse_time or (time.time() - self.last_parse_time[project_path]) > 6000):
            print('parser::parse_project ' + project_path)
            self.last_parse_time[project_path] = time.time()
            self.symbolic_data['parse']['yaml'] = yaml_parser.get_all_guid_files(project_path, parser_utils.parse_project)
            self.symbolic_data['parse'] = parser_utils.parse_project(project_path, self.symbolic_data['parse'], '*.cs', self.parse_csharp_project_wise, False)
            self.symbolic_data['parse'] = parser_utils.parse_project(project_path, self.symbolic_data['parse'], '*.unity', self.parse_yaml_project_wise, False)
            self.symbolic_data['parse'] = parser_utils.parse_project(project_path, self.symbolic_data['parse'], '*.prefab', self.parse_yaml_project_wise, False)
            self.parse_csharp_internal_symbols()
            # print(self.symbolic_data['parse']['symbols'])

    def parse_yaml_project_wise(self, content, parse_data, root, filename, project_path):
        file = join(root, filename)
        print("Parsing file " + file)
        self.parse_yaml_file(file)
        return self.symbolic_data['parse']

    def parse_csharp_project_wise(self, content, parse_data, root, filename, project_path):
        file = join(root, filename)
        print("Parsing file " + file)
        self.parse_csharp_file(file)
        return self.symbolic_data['parse']


    def parse_csharp_internal_symbols(self):
        csharp_symbols = self.symbolic_data['parse']['symbols']
        for s in csharp_symbols:
            c = csharp_symbols[s]
            if isinstance(c, csharp.csharp_class_parser.CSharpClass):#c.element_type == "class":
                symbol_base_info = []
                for b in c.base_info:
                    symbol = b
                    if b in self.symbolic_data['parse']['symbols']:
                        print(b)
                        symbol = self.symbolic_data['parse']['symbols'][b]
                        symbol.inherited_by.append(c)
                    symbol_base_info.append(symbol)
                c.base_info = symbol_base_info

    def parse_csharp_file(self, file):
        try:
            # Parse file into a set of tokens
            tokens_data = TokenParser().parse_file(file)
            # print(tokens_data) # For debug purposes
            tokens_data = csharp_importer_parser.parse_tokens(tokens_data)
            tokens_data = csharp_class_parser.parse_tokens(tokens_data)
            # Save data
            self.symbolic_data['parse']['by_files'][file] = tokens_data

            if 'classes' in tokens_data:
                for c in tokens_data['classes']:
                    symbol_name = c.namespace + c.class_name
                    if symbol_name in self.symbolic_data['parse']['symbols']:
                        self.symbolic_data['parse']['symbols'][symbol_name].recycle(c)
                    self.symbolic_data['parse']['symbols'][symbol_name] = c
        except:
             print("Unexpected error:" + str(sys.exc_info()[0]))

    def parse_yaml_file(self, file):
        # yaml_parser
        if not 'yaml' in self.symbolic_data['parse']:
            self.symbolic_data['parse']['yaml'] = yaml_parser.get_all_guid_files(parser_utils.get_project_path('', file), parser_utils.parse_project)
        self.symbolic_data['parse'] = yaml_parser.parse_yaml(file, self.symbolic_data['parse'])

    def parse_file(self, file):
        if file is None:
            return
        for t in self.parse_file_by_filetype:
            if file.lower().endswith(t):
                self.parse_file_by_filetype[t](file)

    def debugself(self):
        print('debugself')

    def print_selection_info(self, view):
        file = view.file_name()

        if file == None:
            return

        open_file = view_factory.get_open_file(view)
        go_to_reference = view_factory.get_goto_reference(view, self.symbolic_data)
        show_popup = view_factory.get_showpopup(view)


        if file.lower().endswith(('.unity','.prefab','.asset', '.meta')):
            for region in view.sel():
                selected_text = view.substr(region)

                if not yaml_parser.print_yaml_file_info(file, selected_text, self.symbolic_data['parse'], open_file, show_popup):
                    if not yaml_parser.print_yaml_gameobject_info(file, selected_text, self.symbolic_data['parse'], go_to_reference, show_popup):
                        yaml_parser.print_yaml_transform_info(file, selected_text, self.symbolic_data['parse'], go_to_reference, show_popup)
        elif file.lower().endswith('.cs'):
            for region in view.sel():
                rowcol = view.rowcol(region.begin())
                semantic_object = self.get_semantic_token(file, rowcol, True, True, True, view.substr(region))
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

    def get_semantic_token(self, file, rowcol, usingcol = False, sameLine=False, token_verification=False, token_selected=''):
        file_data = self.symbolic_data['parse']['by_files'][file]
        if 'token_position' in file_data:
            token_position = file_data['token_position']
            tokens = file_data['tokens']
            row, col = rowcol
            # print('parser.py::get_semantic_token - searching in position ' + str(row) + ',' + str(col))
            total_tokens = len(token_position)
            for i in list(reversed(range(0, total_tokens))):
                token_row,  token_col = token_position[i]
                token_size = len(tokens[i])

                if ((not sameLine and row > token_row) or \
                    (sameLine and row == token_row)) and \
                    (not usingcol or (col <= token_col and col >= (token_col - token_size))) \
                    and (not token_verification or (len(token_selected) > 1 and tokens[i].find(token_selected) != -1) ):
                    # print('parser.py::get_semantic_token - found semantic token: ' + str(i) + \
                    #     ' - ' + str(file_data['semantic_tokens'][i]) + ' in position ' +  \
                    #     str(token_row) + ',' + str(token_col) + " which token is " + \
                    #     tokens[i] + ' and token_verification ' + str(token_selected))
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
