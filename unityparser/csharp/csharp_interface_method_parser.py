import os, sys

__file__ = os.path.normpath(os.path.abspath(__file__))
__path__ = os.path.dirname(__file__)

# print(__path__)

if __path__ not in sys.path:
    sys.path.insert(0, __path__)

from csharp_element import CSharpElement
import csharp_class_method_param_parser

import csharp_utils

class CSharpInterfaceMethod(CSharpElement):

    def __init__(self, csharp_method_name, tokens, token_pos):
        super(CSharpInterfaceMethod, self).__init__('interface_method', tokens, token_pos)
        self.method_name = csharp_method_name
        self.method_type = ''
        self.interface_object = None
        self.params = []

    def add_param(self, param_object):
        self.params.append(param_object)
        param_object.method_object = self

    def print_element_info(self):
        method_info = '<b><a href="' + str(self.line_in_file) + '">Method ' + self.method_name + '</a></b>'
        # print(method_info)
        return method_info

    def print_outline(self):
        access_notation = '+ '
        return '    <a href="' + str(self.line_in_file) + '">' + \
                access_notation + 'method ' + self.method_name + '</a>'


# class_region = (token_start, token_end) of enclosure class
def parse_tokens(tokens_data, class_region, interface_object):

    tokens = tokens_data['tokens']
    semantic_tokens = tokens_data['semantic_tokens']
    enclosure_position = tokens_data['enclosure_position']

    method_data = []

    return_type = 'None'
    method_name = ''
    expected_method = False
    start_region = class_region[0]
    end_region = class_region[1]

    t = start_region

    start_method_pos = -1

    def create_method_instance(t):
        method_instance = CSharpInterfaceMethod(method_name, tokens[start_method_pos:t], \
                                            start_method_pos)
        method_instance.method_type = return_type
        method_instance.line_in_file = tokens_data['token_position'][start_method_pos][0]
        method_instance.class_object = interface_object
        method_data.append(method_instance)

        for i in range(start_method_pos-1, enclosure_position[enclosure_position[t]+1]):
            semantic_tokens[i] = method_instance

        return method_instance

    while t < end_region:

        if tokens[t] == '(' and tokens[enclosure_position[t]+1] == ';':
            start_method_pos = t-2
            return_type = tokens[t-2]
            method_name = tokens[t-1]
            print('Found method ' + method_name + " with return type '" + return_type)

            method_instance = create_method_instance(t)
            tokens_data = csharp_class_method_param_parser.parse_tokens(tokens_data, (t+1, enclosure_position[t]), method_instance)

            method_type = 'None'

            t = enclosure_position[t]+2
        else:
            t = t + 1

    tokens_data['method_data'] = method_data
    tokens_data['semantic_tokens'] = semantic_tokens

    return tokens_data