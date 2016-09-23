import os, sys

__file__ = os.path.normpath(os.path.abspath(__file__))
__path__ = os.path.dirname(__file__)

# print(__path__)

if __path__ not in sys.path:
    sys.path.insert(0, __path__)

from csharp_element import CSharpElement

# class_region = (token_start, token_end) of enclosure class
def parse_tokens(tokens_data, class_region):

    tokens = tokens_data['tokens']
    semantic_tokens = tokens_data['semantic_tokens']
    enclosure_position = tokens_data['enclosure_position']

    method_access_level = ''
    return_type = ''
    method_name = ''
    expected_method = False

    start_region = class_region[0]
    end_region = class_region[1]

    t = start_region

    while t < end_region:
        
        if tokens[t] == '(' and tokens[enclosure_position[t]+1] == '{':
            if t > 2 and is_access_modifier(tokens[t-3]):
                method_access_level = tokens[t-3]
            else:
                method_access_level = 'default'
            return_type = tokens[t-2]
            method_name = tokens[t-1]
            t = enclosure_position[enclosure_position[t]+1]
            print('Found method ' + method_name + " with return type '" + return_type + "' and access level " + method_access_level)
        else:
            t = t + 1

    return tokens_data


def is_access_modifier(token):
    return is_public_modifier(token) or is_private_modifier(token) or is_protected_modifier(token)

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

def is_protected_modifier(token):
    return len(token) == 9 and \
        token[0] == 'p' and \
        token[1] == 'r' and \
        token[2] == 'o' and \
        token[3] == 't' and \
        token[4] == 'e' and \
        token[5] == 'c' and \
        token[6] == 't' and \
        token[7] == 'e' and \
        token[8] == 'd'