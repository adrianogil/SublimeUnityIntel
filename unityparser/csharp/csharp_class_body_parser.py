import os, sys

__file__ = os.path.normpath(os.path.abspath(__file__))
__path__ = os.path.dirname(__file__)

# print(__path__)

if __path__ not in sys.path:
    sys.path.insert(0, __path__)

from csharp_element import CSharpElement

import csharp_class_method_parser
import csharp_class_member_parser

# class_region = (token_start, token_end) of enclosure class
def parse_tokens(tokens_data, class_region, class_name, class_instance):
    tokens_data = csharp_class_method_parser.parse_tokens(tokens_data, class_region, class_name, class_instance)
    tokens_data = csharp_class_member_parser.parse_tokens(tokens_data, class_region, class_name, class_instance)

    return tokens_data