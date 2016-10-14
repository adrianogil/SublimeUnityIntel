import os, sys

__file__ = os.path.normpath(os.path.abspath(__file__))
__path__ = os.path.dirname(__file__)

# print(__path__)

if __path__ not in sys.path:
    sys.path.insert(0, __path__)

from csharp_element import CSharpElement

import csharp_interface_method_parser
import csharp_utils

class CSharpInterface(CSharpElement):

    def __init__(self, csharp_interface_name, tokens, token_pos):
        super(CSharpInterface, self).__init__('class', tokens, token_pos)
        self.namespace = ''
        self.interface_name = csharp_interface_name
        self.symbol_name = csharp_interface_name
        self.base_interface_info = []
        self.implements = []
        self.implemented_by = []
        self.methods_data = []
        self.usage = []

    def add_usage(self, referee):
        # print('Added usage to ' + self.class_name + ' from ' + str(referee))
        for u in self.usage:
            if referee.reference_file_path == u.reference_file_path and referee.definition_line == u.definition_line:
                return
        self.usage.append(referee)

    def print_simple_element_info(self):
        return 'Interface ' + self.interface_name

    def print_element_info(self):
        element_info = '<b><a href="' + str(self.line_in_file) + '">Interface ' + self.interface_name + '</a></b>' + \
                       '<br>' + str(len(self.methods_data)) + " methods "
        for b in self.implements:
            if isinstance(b, CSharpInterface):
                element_info = element_info + '<br>Implements ' + b.Interface_name + ' '
        for c in self.implemented_by:
            element_info = element_info + '<br>Implemented by ' + c.print_simple_element_info() + ' '
        # print(element_info)
        return element_info

    def print_outline(self):
        element_outline = '<a href="' + str(self.line_in_file) + '">Interface ' + self.interface_name + '</a>'
        for m in self.methods_data:
            element_outline = element_outline + '<br>'
            element_outline = element_outline + m.print_outline()
        return element_outline

    def recycle(self, new_class_instance):
        new_class_instance.usage = self.usage
        new_class_instance.base_interface_info = self.base_interface_info
        new_class_instance.inherited_by = self.inherited_by

def  parse_tokens(tokens_data):
    tokens = tokens_data['tokens']
    semantic_tokens = tokens_data['semantic_tokens']
    positions = tokens_data['token_position']
    outline_data = tokens_data['outline_data']

    total_tokens = len(tokens)

    interfaces_data = []

    interface_name = ''

    interface_identified = False
    interfaceinfo_expected = False # A base class or an interface
    interfaceinfo_identified = False

    interfaceinfo_tokens = []

    start_interface_pos = 0

    for t in range(1, total_tokens):
        # Can't consider importers inside strings
        if isinstance(semantic_tokens[t], CSharpElement):
            continue

        if interface_identified and tokens[t] == '{':
            interface_identified = False
            interfaceinfo_expected = False

            interface_end_position = tokens_data['enclosure_position'][t]

            print('Interface identified: ' + interface_name + " with interfaces: " + str(interfaceinfo_tokens))
            interface_instance = CSharpInterface(interface_name, tokens[t:interface_end_position], interface_end_position)

            tokens_data = csharp_interface_method_parser.parse_tokens(tokens_data, (t+1, tokens_data['enclosure_position'][t]), interface_instance)
            interface_instance.line_in_file = positions[start_interface_pos][0]
            interface_instance.methods_data = tokens_data['method_data']
            interface_instance.base_info = interfaceinfo_tokens
            interfaces_data.append(interface_instance)
            outline_data.append(interface_instance)
            for i in range(start_interface_pos, t):
                semantic_tokens[i] = interface_instance
            interface_name = ''
            interfaceinfo_tokens = []

        elif interface_identified and len(interfaceinfo_tokens) > 0 and tokens[t] == ',':
            interfaceinfo_expected = True
        elif interface_identified and interfaceinfo_expected:
            interfaceinfo_tokens.append(tokens[t])
            interfaceinfo_expected = False
        if interface_identified and tokens[t] == ':':
            interfaceinfo_expected = True
        elif csharp_utils.is_interface_keyword(tokens[t-1]):
            interface_name = tokens[t]
            start_interface_pos = t-2
            interface_identified = True

    tokens_data['interfaces'] = interfaces_data
    tokens_data['outline_data'] = outline_data

    return tokens_data