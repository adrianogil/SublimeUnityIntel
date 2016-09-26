import os, sys

__file__ = os.path.normpath(os.path.abspath(__file__))
__path__ = os.path.dirname(__file__)

# print(__path__)

if __path__ not in sys.path:
    sys.path.insert(0, __path__)

from csharp_element import CSharpElement
import csharp_class_method_param_parser

import csharp_utils

# class_region = (token_start, token_end) of enclosure class
def parse_tokens(tokens_data, class_region):

    tokens = tokens_data['tokens']
    semantic_tokens = tokens_data['semantic_tokens']
    enclosure_position = tokens_data['enclosure_position']

    method_access_level = ''
    return_type = ''
    method_name = ''
    expected_method = False
    is_static_method = False

    start_region = class_region[0]
    end_region = class_region[1]

    t = start_region

    while t < end_region:
        
        if tokens[t] == '(' and tokens[enclosure_position[t]+1] == '{':
            if t > 3 and csharp_utils.is_access_modifier(tokens[t-4]) and csharp_utils.is_static_modifier(tokens[t-3]):
                method_access_level = tokens[t-4]
                is_static_method = True
            elif t > 2 and csharp_utils.is_access_modifier(tokens[t-3]):
                method_access_level = tokens[t-3]
            elif t > 2 and csharp_utils.is_static_modifier(tokens[t-3]):
                method_access_level = 'default'
                is_static_method = True
            else:
                method_access_level = 'default'

            return_type = tokens[t-2]
            method_name = tokens[t-1]
            
            if is_static_method:
                print('Found static method ' + method_name + " with return type '" + return_type + "' and access level " + method_access_level)
            else:
                print('Found method ' + method_name + " with return type '" + return_type + "' and access level " + method_access_level)
            tokens_data = csharp_class_method_param_parser.parse_tokens(tokens_data, (t+1, enclosure_position[t]))

            is_static_method = False

            t = enclosure_position[enclosure_position[t]+1]+1
        else:
            t = t + 1

    return tokens_data