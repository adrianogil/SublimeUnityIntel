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

    def __init__(self, csharp_method_name, tokens, token_pos):
        super(CSharpClassMethod, self).__init__('importer', tokens, token_pos)
        self.method_name = csharp_method_name
        self.method_type = ''
        self.method_access_level = ''
        self.is_static = False
        self.is_constructor = False
        self.is_override = False
        self.is_virtual = False
        self.class_object = None

    def print_outline(self):
        access_notation = '* '
        if self.method_access_level == 'public':
            access_notation = '+ '
        elif self.method_access_level == 'protected':
            access_notation = '# '
        elif self.method_access_level == 'private':
            access_notation = '- '
        return '    <a href="' + str(self.line_in_file) + '">' + \
                access_notation + 'method ' + self.method_name + '</a>'

    def get_debug_log(self):
        return 'Debug.Log("' + self.class_object.class_name + '::' + self.method_name + '");'


# class_region = (token_start, token_end) of enclosure class
def parse_tokens(tokens_data, class_region, class_name, class_object):

    tokens = tokens_data['tokens']
    semantic_tokens = tokens_data['semantic_tokens']
    enclosure_position = tokens_data['enclosure_position']

    method_data = []

    method_access_level = ''
    return_type = 'None'
    method_name = ''
    expected_method = False
    is_static_method = False
    is_constructor = False
    is_override = False
    is_virtual = False

    start_region = class_region[0]
    end_region = class_region[1]

    t = start_region

    start_method_pos = -1

    def create_method_instance(t):
        method_instance = CSharpClassMethod(method_name, tokens[start_method_pos:t], \
                                            start_method_pos)
        method_instance.method_type = return_type
        method_instance.method_access_level = method_access_level
        method_instance.line_in_file = tokens_data['token_position'][start_method_pos][0]
        method_instance.is_static = is_static_method
        method_instance.is_constructor = is_constructor
        method_instance.is_virtual = is_virtual
        method_instance.is_override = is_override
        method_instance.class_object = class_object
        method_data.append(method_instance)

        for i in range(start_method_pos, enclosure_position[enclosure_position[t]+1]):
            semantic_tokens[i] = method_instance

    while t < end_region:
        
        if tokens[t] == '(' and tokens[enclosure_position[t]+1] == '{':
            if csharp_utils.is_base_keyword(tokens[t-1]):
                is_constructor = True
                if t > 5 and csharp_utils.is_access_modifier(tokens[t-6]):
                    method_access_level = tokens[t-6]
                start_method_pos = t-6
            elif t > 3 and csharp_utils.is_access_modifier(tokens[t-4]) and csharp_utils.is_static_modifier(tokens[t-3]):
                method_access_level = tokens[t-4]
                is_static_method = True
                start_method_pos = t-4
            elif t > 3 and csharp_utils.is_access_modifier(tokens[t-4]) and csharp_utils.is_virtual_modifier(tokens[t-3]):
                method_access_level = tokens[t-4]
                start_method_pos = t-4
                is_virtual = True
            elif t > 3 and csharp_utils.is_access_modifier(tokens[t-4]) and csharp_utils.is_override_modifier(tokens[t-3]):
                method_access_level = tokens[t-4]
                start_method_pos = t-4
                is_override = True
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

            if tokens[t-1] == class_name:
                is_constructor = True

            if not is_constructor:
                return_type = tokens[t-2]
                method_name = tokens[t-1]
            else:
                method_name = 'constructor' #tokens[t-5]
            
            if is_static_method:
                print('Found static method ' + method_name + " with return type '" + return_type + "' and access level " + method_access_level)
            else:
                print('Found method ' + method_name + " with return type '" + return_type + "' and access level " + method_access_level)
            tokens_data = csharp_class_method_param_parser.parse_tokens(tokens_data, (t+1, enclosure_position[t]))

            semantic_tokens

            create_method_instance(t)

            is_static_method = False
            is_constructor = False
            method_type = 'None'
            is_override = False
            is_virtual = False

            t = enclosure_position[enclosure_position[t]+1]+1
        else:
            t = t + 1

    tokens_data['method_data'] = method_data
    tokens_data['semantic_tokens'] = semantic_tokens

    return tokens_data