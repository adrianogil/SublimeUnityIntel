import os, sys

__file__ = os.path.normpath(os.path.abspath(__file__))
__path__ = os.path.dirname(__file__)

# print(__path__)

if __path__ not in sys.path:
    sys.path.insert(0, __path__)

from csharp_element import CSharpElement
from csharp_reference import CSharpReference

import csharp_class_body_parser

class CSharpClass(CSharpElement):

    def __init__(self, csharp_class_name, tokens, token_pos):
        super(CSharpClass, self).__init__('class', tokens, token_pos)
        self.namespace = ''
        self.class_name = csharp_class_name
        self.symbol_name = csharp_class_name
        self.base_info = []
        self.inherited_by = []
        self.methods_data = []
        self.fields_data = []
        self.properties_data = []
        self.usage = []
        self.file_name = ''
        self.project_path = ''
        self.referenced = []

    def add_usage(self, referee):
        # print('Added usage to ' + self.class_name + ' from ' + str(referee))
        for u in self.usage:
            if referee.reference_file_path == u.reference_file_path and referee.definition_line == u.definition_line:
                return
        self.usage.append(referee)

    # Add a CSharp semantic object that references this class
    def add_referenced(self, ref):
        found_ref = False
        for r in self.referenced:
            if r.file_name == ref.file_name and r.line_in_file == ref.line_in_file:
                found_ref = True
                break
        if not found_ref:
            self.referenced.append(ref)

    def add_property(self, property_instance):
        self.properties_data.append(property_instance)
        property_instance.class_object = self

    def add_field(self, field_instance):
        self.fields_data.append(field_instance)
        field_instance.class_object = self

    def print_simple_element_info(self):
        return 'Class ' + self.class_name

    def get_elements_info(self):
        elements = [self]
        elements_info = [self.print_simple_element_info()]

        for m in self.methods_data:
            elements.append(m)
            elements_info.append(m.print_simple_element_info())

        return (elements, elements_info)

    def parse_symbols(self, symbols_list):
        symbol_base_info = []
        for f in self.fields_data:
            symbol = f.field_type
            if symbol in symbols_list:
                element = symbols_list[symbol]
                if element.element_type == 'class':
                    ref = CSharpReference()
                    ref.reference_object = f
                    ref.line_in_file = f.line_in_file+1
                    ref.file_name = self.file_name
                    print(self.class_name + ' has a field that references ' + symbol)
                    element.referenced.append(ref)

        for b in self.base_info:
            symbol = b
            if b in symbols_list:
                print(b)
                symbol = symbols_list[b]
                if symbol.element_type == 'class':
                    symbol.inherited_by.append(self)
                elif symbol.element_type == 'interface':
                    symbol.implemented_by.append(self)
            symbol_base_info.append(symbol)
        self.base_info = symbol_base_info

        for m in self.methods_data:
            m.parse_symbols(symbols_list)

    def print_element_info(self, view_factory):
        view_factory.clear_actions()

        action_id = 1
        class_info = '<b><a href="' + str(action_id) + '">Class ' + self.class_name + '</a></b>' + \
                    '<br>' + str(len(self.methods_data)) + " methods " + \
                    '<br>' + str(len(self.fields_data)) + " fields " + \
                    '<br>' + str(len(self.properties_data)) + " properties "
        action = view_factory.get_goto_line_action(self.line_in_file)
        view_factory.register_action(action_id, action)

        for b in self.base_info:
            if isinstance(b, CSharpClass):
                action_id = action_id + 1
                class_info = class_info + '<br>Inherits from <a href="' + str(action_id) + '">' + b.class_name + '</a> '
                action = view_factory.get_goto_file_reference_action(b.file_name, b.line_in_file)
                view_factory.register_action(action_id, action)
            elif b == "MonoBehaviour":
                class_info = class_info + '<br>Inherits from MonoBehaviour '
        for c in self.inherited_by:
            action_id = action_id + 1
            class_info = class_info + '<br>Inherited by <a href="' + str(action_id) + '">' + c.class_name + '</a> '
            action = view_factory.get_goto_file_reference_action(c.file_name, c.line_in_file)
            view_factory.register_action(action_id, action)
        yaml_reference_count = 0
        for u in self.usage:
            if u.reference_type == 'yaml':
                yaml_reference_count = yaml_reference_count + 1
            # class_info = class_info + '<br> Referencied by line ' + str(u.definition_line) + '<br>' + u.reference_file_path
        if yaml_reference_count > 0:
            action_id = action_id + 1
            class_info = class_info + '<br>  <a href="' + str(action_id) + '">' + str(yaml_reference_count) + ' references from YAML files</a>'
            def show_yaml_references_popup():
                view_factory.print_yaml_ref_popup(self)
            action = show_yaml_references_popup
            view_factory.register_action(action_id, action)

        total_referenced = len(self.referenced)
        if total_referenced > 0:
            ref_label = ' references'
            if total_referenced == 1:
                ref_label =' reference'
            action_id = action_id + 1
            class_info = class_info + '<br><a href="' + str(action_id) + '">' + str(total_referenced) + ref_label + ' from another classes </a>'
            def show_csharp_ref_popup():
                view_factory.print_csharp_ref_popup(self)
            action = show_csharp_ref_popup
            view_factory.register_action(action_id, action)

        # print(class_info)
        view_factory.show_popup(class_info)

        return class_info

    def print_outline(self):
        class_outline = '<a href="' + str(self.line_in_file) + '">Class ' + self.class_name + '</a>'
        for m in self.methods_data:
            class_outline = class_outline + '<br>'
            class_outline = class_outline + m.print_outline()
        return class_outline

    def recycle(self, new_class_instance):
        new_class_instance.usage = self.usage
        new_class_instance.base_info = self.base_info
        new_class_instance.inherited_by = self.inherited_by
        new_class_instance.referenced = self.referenced

        for m1 in new_class_instance.methods_data:
            for m2 in self.methods_data:
                if m2.method_name == m1.method_name and \
                   m2.method_type == m1.method_type and \
                   m2.method_access_level == m1.method_access_level and \
                   m2.is_static == m1.is_static and \
                   len(m2.params) == len(m1.params):
                    same_method = False
                    for p in range(0, len(m2.params)):
                        if m2.params[p].param_name != m1.params[p].param_name or \
                           m2.params[p].param_type != m1.params[p].param_type or \
                           m2.params[p].param_default_value != m2.params[p].param_default_value:
                           same_method = False
                           break
                        else:
                            same_method = True
                    if same_method:
                        m1.variable_instances = m2.variable_instances
                        m1.scope_children = m2.scope_children
                

def  parse_tokens(tokens_data):
    tokens = tokens_data['tokens']
    semantic_tokens = tokens_data['semantic_tokens']
    positions = tokens_data['token_position']

    total_tokens = len(tokens)

    classes_data = []

    class_name = ''

    class_identified = False
    classinfo_expected = False # A base class or an interface
    classinfo_identified = False

    classinfo_tokens = []

    start_class_pos = 0

    for t in range(1, total_tokens):
        # Can't consider importers inside strings
        if isinstance(semantic_tokens[t], CSharpElement):
            continue

        if class_identified and tokens[t] == '{':
            class_identified = False
            classinfo_expected = False

            class_end_position = tokens_data['enclosure_position'][t]

            print('Class identified: ' + class_name + " with baseclass/interfaces: " + str(classinfo_tokens))
            class_instance = CSharpClass(class_name, tokens[t:class_end_position], class_end_position)

            tokens_data = csharp_class_body_parser.parse_tokens(tokens_data, (t+1, tokens_data['enclosure_position'][t]), class_name, class_instance)
            class_instance.line_in_file = positions[start_class_pos][0]
            class_instance.methods_data = tokens_data['method_data']
            class_instance.base_info = classinfo_tokens
            classes_data.append(class_instance)
            for i in range(start_class_pos, t):
                semantic_tokens[i] = class_instance
            class_name = ''
            classinfo_tokens = []

        elif class_identified and len(classinfo_tokens) > 0 and tokens[t] == ',':
            classinfo_expected = True
        elif class_identified and classinfo_expected:
            classinfo_tokens.append(tokens[t])
            classinfo_expected = False
        if class_identified and tokens[t] == ':':
            classinfo_expected = True
        elif t > 2 and is_access_modifier(tokens[t-2]) and is_class_keyword(tokens[t-1]):
            class_name = tokens[t]
            start_class_pos = t-2
            class_identified = True
        elif is_class_keyword(tokens[t-1]):
            class_name = tokens[t]
            start_class_pos = t-2
            class_identified = True

    tokens_data['classes'] = classes_data
    tokens_data['outline_data'] = classes_data

    return tokens_data

def is_access_modifier(token):
    return is_public_modifier(token) or is_private_modifier(token)

def is_public_modifier(token):
    return len(token) == 6 and \
        token[0] == 'p' and \
        token[1] == 'u' and \
        token[2] == 'b' and \
        token[3] == 'l' and \
        token[4] == 'i' and \
        token[5] == 'c'

def is_private_modifier(token):
    return len(token) == 7 and \
        token[0] == 'p' and \
        token[1] == 'r' and \
        token[2] == 'i' and \
        token[3] == 'v' and \
        token[4] == 'a' and \
        token[5] == 't' and \
        token[6] == 'e'

def is_class_keyword(token):
    return len(token) == 5 and \
        token[0] == 'c' and \
        token[1] == 'l' and \
        token[2] == 'a' and \
        token[3] == 's' and \
        token[4] == 's'