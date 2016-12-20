import os, sys

__file__ = os.path.normpath(os.path.abspath(__file__))
__path__ = os.path.dirname(__file__)

# print(__path__)

if __path__ not in sys.path:
    sys.path.insert(0, __path__)

from csharp_element import CSharpElement
import csharp_utils

class CSharpVariableDeclaration():
    def __init__(self, parse_region):
        self.parse_region = parse_region
        self.scope_parent = None
        self.var_type = None
        self.var_name = ''

# class_region = (token_start, token_end) of enclosure class
def parse_tokens(tokens_data, parse_region, scope_parent_instance, symbols):
    tokens = tokens_data['tokens']
    semantic_tokens = tokens_data['semantic_tokens']
    positions = tokens_data['token_position']
    enclosure_position = tokens_data['enclosure_position']

    total_tokens = len(tokens)

    start_region = parse_region[0]
    end_region = parse_region[1]

    t = start_region

    def create_var_init(t):
        start_var_init = t
        end_var_init = t+2

        init_region = (start_var_init, end_var_init)

        var_instance = CSharpVariableDeclaration(init_region)
        var_instance.scope_parent = scope_parent_instance
        var_instance.var_type = symbols[tokens[t]]
        var_instance.var_name = tokens[t+1]

        scope_parent_instance.add_var(var_instance)

        print("Found var " + var_instance.var_name + " with type " + tokens[t])

        # parse_tokens(tokens_data, scope_region, scope_instance)
    
    while t < end_region-2:
        if tokens[t+2] == ';' and csharp_utils.is_valid_symbol(tokens[t], symbols) and csharp_utils.is_valid_variable_name(tokens[t+1]):
            create_var_init(t)
            t = t + 2
        else:
            t = t + 1

    return tokens_data