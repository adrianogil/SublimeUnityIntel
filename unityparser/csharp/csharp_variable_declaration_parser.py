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
        self.var_init = ''
        self.line_in_file = -1

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

    expect_init = False
    expect_new_declaration = False

    concat_var_init = ''

    last_type = None
    last_var_name = ''
    last_var_name_t = -1

    def create_var_init(var_type, var_name, t, var_init = ''):
        start_var_init = t
        end_var_init = t+2

        init_region = (start_var_init, end_var_init)

        var_instance = CSharpVariableDeclaration(init_region)
        var_instance.scope_parent = scope_parent_instance
        var_instance.var_type = var_type
        var_instance.var_name = var_name
        var_instance.var_init = var_init
        var_instance.line_in_file = positions[t]

        scope_parent_instance.add_var(var_instance)

        print("Found var " + var_instance.var_name + " with type " + str(var_type) + ' and init ' + var_init)

    def create_var_init_on_pos(t):
        create_var_init(symbols[tokens[t]], tokens[t+1], t)
    
    while t < end_region-2:
        if expect_new_declaration:
            if (tokens[t+1] == ';' or tokens[t+1] == '=' or tokens[t+1] == ',') and csharp_utils.is_valid_variable_name(tokens[t]):
                expect_new_declaration = False
                if tokens[t+1] == ';':
                    create_var_init(last_type, tokens[t], t)
                elif tokens[t+1] == ',':
                    expect_new_declaration = True
                    create_var_init(last_type, tokens[t], t)
                else:
                    expect_init = True
                    concat_var_init = ''
                    last_var_name = tokens[t]
                t = t + 2
        elif expect_init and (tokens[t] == ',' or tokens[t] == ';'):
            expect_init = False
            create_var_init(last_type, last_var_name, last_var_name_t, concat_var_init)
            if tokens[t] == ',':
                expect_new_declaration = True
        elif expect_init:
            concat_var_init = concat_var_init + tokens[t]
        if (tokens[t+2] == ';' or tokens[t+2] == '=' or tokens[t+2] == ',') and csharp_utils.is_valid_symbol(tokens[t], symbols) and csharp_utils.is_valid_variable_name(tokens[t+1]):
            last_type = symbols[tokens[t]]
            if tokens[t+2] == ';':
                create_var_init_on_pos(t)
            elif tokens[t+2] == ',':
                expect_new_declaration = True
                create_var_init(last_type, tokens[t+1])
            else:
                expect_init = True
                concat_var_init = ''
                last_var_name = tokens[t+1]
                last_var_name_t = t+1
            t = t + 3
        else:
            t = t + 1

    return tokens_data