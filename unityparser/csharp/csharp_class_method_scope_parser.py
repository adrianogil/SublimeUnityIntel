import os, sys

__file__ = os.path.normpath(os.path.abspath(__file__))
__path__ = os.path.dirname(__file__)

# print(__path__)

if __path__ not in sys.path:
    sys.path.insert(0, __path__)

from csharp_element import CSharpElement
from csharp_reference import CSharpReference
import csharp_variable_declaration_parser

class CSharpMethodScope():
    def __init__(self, parse_region, method):
        self.parse_region = parse_region
        self.scope_children = []
        self.variable_instances = []
        self.method_instance = method

    def add_scope(self, scope_instance):
        self.scope_children.append(scope_instance)

    def add_var(self, var_instance):
        if var_instance != None:
            if var_instance.var_type != None:
                if var_instance.var_type.element_type == 'class':
                    ref = CSharpReference()
                    ref.reference_object = var_instance
                    ref.line_in_file = var_instance.line_in_file
                    ref.file_name = self.method_instance.class_object.file_name
                    print(var_instance.var_type.class_name + ' is instantiated at method: ' + self.method_instance.method_name)
                    var_instance.var_type.referenced.append(ref)
            self.variable_instances.append(var_instance)

# class_region = (token_start, token_end) of enclosure class
def parse_tokens(tokens_data, parse_region, scope_parent_instance, symbols, method):

    tokens = tokens_data['tokens']
    semantic_tokens = tokens_data['semantic_tokens']
    token_position = tokens_data['token_position']
    enclosure_position = tokens_data['enclosure_position']

    total_tokens = len(tokens)

    start_region = parse_region[0]
    end_region = parse_region[1]

    t = start_region

    last_region_start = 0

    def create_scope(t):
        start_scope = t
        end_scope = enclosure_position[t]

        scope_region = (start_scope, end_scope)

        scope_instance = CSharpMethodScope(scope_region, method)
        scope_parent_instance.add_scope(scope_instance)

        scope_debug_str = ''

        for i in range(start_scope, end_scope):
            scope_debug_str = scope_debug_str + tokens[i] +  ' '

        print("Found scope: " + scope_debug_str)

        parse_tokens(tokens_data, scope_region, scope_instance, symbols, method)

        return scope_instance

    def parse_inside_scope(t):
        if t <= 1:
            return
        scope_snippet_region = (last_region_start, t-1)
        t1 = scope_snippet_region[0]
        t2 = scope_snippet_region[1]
        scope_snippet_tokens = {"tokens" : tokens[t1:t2], \
                                "semantic_tokens" : semantic_tokens[t1:t2], \
                                "token_position" : token_position[t1:t2], \
                                "enclosure_position" : enclosure_position[t1:t2]}
        csharp_variable_declaration_parser.parse_tokens(scope_snippet_tokens, (0, t2-t1), scope_parent_instance, symbols)
    
    while t < end_region:
        # print('enclosure_position: ' + str(enclosure_position[t]))
        if tokens[t] == '{' and enclosure_position[t] < end_region and tokens[enclosure_position[t]] == '}':
            parse_inside_scope(t)
            create_scope(t)
            t = enclosure_position[t] + 1
        else:
            t = t + 1