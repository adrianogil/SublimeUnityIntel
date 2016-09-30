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

from csharp.csharp_element import CSharpElement
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

    def print_selection_info(self):
        print("print_selection_info")

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



