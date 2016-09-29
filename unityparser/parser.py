import os, sys
import fnmatch
from os.path import join

import codecs

__file__ = os.path.normpath(os.path.abspath(__file__))
__path__ = os.path.dirname(__file__)
__csharp_path__ = join(__path__, 'csharp')
print(__csharp_path__)

if __path__ not in sys.path:
    sys.path.insert(0, __path__)
if __csharp_path__ not in sys.path:
    sys.path.insert(0, __csharp_path__)

from token_parser import TokenParser

from csharp.csharp_element import CSharpElement
from csharp import csharp_importer_parser
from csharp import csharp_class_parser

class SymbolicParser:
    symbols = {}
    def parse_file(self, csharp_file):
        tokens_data = TokenParser().parse_file(csharp_file)

        # print(tokens_data)

        tokens_data = csharp_importer_parser.parse_tokens(tokens_data)
        tokens_data = csharp_class_parser.parse_tokens(tokens_data)

        return tokens_data



