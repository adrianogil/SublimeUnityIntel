import os, sys
import fnmatch
from os.path import join

import codecs

__file__ = os.path.normpath(os.path.abspath(__file__))
__path__ = os.path.dirname(__file__)

# print(__path__)

if __path__ not in sys.path:
    sys.path.insert(0, __path__)

from csharp_element import CSharpElement
from csharp_token_parser import CSharpTokenParser

import csharp_importer_parser
import csharp_class_parser

class CSharpParser:
    symbols = {}
    def parse_file(self, csharp_file):
        tokens_data = CSharpTokenParser().parse_file(csharp_file)

        # print(tokens_data)

        tokens_data = csharp_importer_parser.parse_tokens(tokens_data)
        tokens_data = csharp_class_parser.parse_tokens(tokens_data)

        # print(tokens_data)

        parser_data = { \
            'by_files': { \
                csharp_file: { \
                    'classes': tokens_data['classes'] \
                } \
            } \
        }

        return parser_data
            


