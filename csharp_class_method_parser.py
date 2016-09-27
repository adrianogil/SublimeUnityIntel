import os, sys

__file__ = os.path.normpath(os.path.abspath(__file__))
__path__ = os.path.dirname(__file__)

# print(__path__)

if __path__ not in sys.path:
    sys.path.insert(0, __path__)

from csharp_element import CSharpElement
import csharp_class_method_param_parser

import csharp_utils

class CSharpClassMethod(CSharpElement):
    method_name = ''
    method_type = ''
    method_access_level = ''
    is_static = False

    def __init__(self, csharp_method_name, tokens, token_pos):
        super(CSharpClassMethod, self).__init__('importer', tokens, token_pos)
        self.method_name = csharp_method_name

# class_region = (token_start, token_end) of enclosure class
def parse_tokens(tokens_data, class_region):

    tokens = tokens_data['tokens']
    semantic_tokens = tokens_data['semantic_tokens']
    enclosure_position = tokens_data['enclosure_position']

    method_data = []

    method_access_level = ''
    return_type = ''
    method_name = ''
    expected_method = False
    is_static_method = False

    start_region = class_region[0]
    end_region = class_region[1]

    t = start_region

    start_method_pos = -1

    def create_method_instance(t):
        method_instance = CSharpClassMethod(method_name, tokens[start_method_pos:t], \
                                            start_method_pos)
        method_instance.method_type = return_type
        method_instance.method_access_level = method_access_level
        method_instance.line_in_file = tokens_data['token_position'][start_method_pos]
        method_instance.is_static = is_static_method
        method_data.append(method_instance)

    while t < end_region:
        
        if tokens[t] == '(' and tokens[enclosure_position[t]+1] == '{':
            if t > 3 and csharp_utils.is_access_modifier(tokens[t-4]) and csharp_utils.is_static_modifier(tokens[t-3]):
                method_access_level = tokens[t-4]
                is_static_method = True
                start_method_pos = t-4
            elif t > 2 and csharp_utils.is_access_modifier(tokens[t-3]):
                method_access_level = tokens[t-3]
                start_method_pos = t-3
            elif t > 2 and csharp_utils.is_static_modifier(tokens[t-3]):
                method_access_level = 'default'
                is_static_method = True
                start_method_pos = t-3
            else:
                method_access_level = 'default'
                start_method_pos = t-2

            return_type = tokens[t-2]
            method_name = tokens[t-1]
            
            if is_static_method:
                print('Found static method ' + method_name + " with return type '" + return_type + "' and access level " + method_access_level)
            else:
                print('Found method ' + method_name + " with return type '" + return_type + "' and access level " + method_access_level)
            tokens_data = csharp_class_method_param_parser.parse_tokens(tokens_data, (t+1, enclosure_position[t]))

            create_method_instance(t)

            is_static_method = False

            t = enclosure_position[enclosure_position[t]+1]+1
        else:
            t = t + 1

    tokens_data['method_data'] = method_data

    return tokens_data