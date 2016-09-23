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

class CSharpType(CSharpElement):
    type_name = ""

class CSharpTypeMember(CSharpElement):
    member_name = ""
    member_type = "type_definition" # type_definition, type_instance, method

class CSharpInstance(CSharpElement):
    instance_type = CSharpType('', [])

class CSharpParser:
    symbols = {}
    def parse_file(self, csharp_file):
        tokens_data = CSharpTokenParser().parse_file(csharp_file)

        tokens_data['parsed_tokens'] = tokens_data['tokens']

        tokens_data = csharp_importer_parser.parse_tokens(tokens_data)

        print(tokens_data)
            


