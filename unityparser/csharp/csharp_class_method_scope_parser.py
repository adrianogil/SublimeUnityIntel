import os, sys

__file__ = os.path.normpath(os.path.abspath(__file__))
__path__ = os.path.dirname(__file__)

# print(__path__)

if __path__ not in sys.path:
    sys.path.insert(0, __path__)

from csharp_element import CSharpElement

class CSharpMethodScope():
    def __init__(self, parse_region):
        self.parse_region = parse_region
        self.scope_children = []

    def add_scope(self, scope_instance):
        self.scope_children.append(scope_instance)


# class_region = (token_start, token_end) of enclosure class
def parse_tokens(tokens_data, parse_region, scope_parent_instance):
    tokens = tokens_data['tokens']
    semantic_tokens = tokens_data['semantic_tokens']
    positions = tokens_data['token_position']
    enclosure_position = tokens_data['enclosure_position']

    total_tokens = len(tokens)

    start_region = parse_region[0]
    end_region = parse_region[1]

    t = start_region

    def create_scope(t):
        start_scope = t
        end_scope = enclosure_position[t]

        scope_region = (start_scope, end_scope)

        scope_instance = CSharpMethodScope(scope_region)
        scope_parent_instance.add_scope(scope_instance)

        scope_debug_str = ''

        for i in range(start_scope, end_scope):
            scope_debug_str = scope_debug_str + tokens[i] +  ' '

        print("Found scope: " + scope_debug_str)

        # parse_tokens(tokens_data, scope_region, scope_instance)
    
    while t < end_region:
        if tokens[t] == '{' and tokens[enclosure_position[t]] == '}':
            create_scope(t)
            t = enclosure_position[t] + 1
        else:
            t = t + 1

    return tokens_data