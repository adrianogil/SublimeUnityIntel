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
from csharp import csharp_interface_parser

import csharp
import parser_utils
import pickle

import selection_parser

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
        self.current_file = ''
        self.current_project_path = ''

    def parse_project(self, file_path):
        project_path = parser_utils.get_project_path('', file_path)
        if project_path != '' and (not project_path in self.last_parse_time or (time.time() - self.last_parse_time[project_path]) > 6000):
            self.current_project_path = project_path
            print('parser::parse_project ' + project_path)
            self.last_parse_time[project_path] = time.time()
            self.symbolic_data['parse']['yaml'] = yaml_parser.get_all_guid_files(project_path, parser_utils.parse_project)
            self.symbolic_data['parse'] = parser_utils.parse_project(project_path, self.symbolic_data['parse'], '*.cs', self.parse_csharp_project_wise, False)
            self.symbolic_data['parse'] = parser_utils.parse_project(project_path, self.symbolic_data['parse'], '*.unity', self.parse_yaml_project_wise, False)
            self.symbolic_data['parse'] = parser_utils.parse_project(project_path, self.symbolic_data['parse'], '*.prefab', self.parse_yaml_project_wise, False)
            self.parse_csharp_internal_symbols()
            pickle.dump(self.symbolic_data, open(join(project_path, 'code_data.symbolic'), 'wb'))
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
                        if isinstance(symbol, csharp.csharp_class_parser.CSharpClass):
                            symbol.inherited_by.append(c)
                        elif isinstance(symbol, csharp.csharp_interface_parser.CSharpInterface):
                            symbol.implemented_by.append(c)
                    symbol_base_info.append(symbol)
                c.base_info = symbol_base_info

    def parse_csharp_file(self, file):
        try:
            # Parse file into a set of tokens
            tokens_data = TokenParser().parse_file(file)
            # print(tokens_data) # For debug purposes
            tokens_data = csharp_importer_parser.parse_tokens(tokens_data)
            tokens_data = csharp_class_parser.parse_tokens(tokens_data)
            tokens_data = csharp_interface_parser.parse_tokens(tokens_data)
            # Save data
            self.symbolic_data['parse']['by_files'][file] = tokens_data

            if 'classes' in tokens_data:
                for c in tokens_data['classes']:
                    symbol_name = c.namespace + c.symbol_name
                    if symbol_name in self.symbolic_data['parse']['symbols']:
                        self.symbolic_data['parse']['symbols'][symbol_name].recycle(c)
                    self.symbolic_data['parse']['symbols'][symbol_name] = c
                    c.file_name = file
                    c.project_path = self.current_project_path
            if 'interfaces' in tokens_data:
                for c in tokens_data['interfaces']:
                    symbol_name = c.namespace + c.symbol_name
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

        self.current_file = file

        selection_parser.handle_selection(view, self)

    def get_yaml_data(self):
        return self.symbolic_data['parse']['yaml']

    def get_current_file_data(self):
        return self.symbolic_data['parse']['by_files'][self.current_file]

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
