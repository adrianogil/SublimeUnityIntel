import os, sys

__file__ = os.path.normpath(os.path.abspath(__file__))
__path__ = os.path.dirname(__file__)

# print(__path__)

if __path__ not in sys.path:
    sys.path.insert(0, __path__)

from csharp_element import CSharpElement

import csharp_utils

# class_region = (token_start, token_end) of enclosure class
def parse_tokens(tokens_data, class_region, class_name):

    tokens = tokens_data['tokens']
    semantic_tokens = tokens_data['semantic_tokens']
    enclosure_position = tokens_data['enclosure_position']

    start_region = class_region[0]
    end_region = class_region[1]

    t = start_region

    member_access_level = ''
    member_is_static = False
    member_is_const = False
    member_type = ''
    member_name = ''
    member_default_value = ''

    member_type_found = False
    member_name_found = False
    expected_default_value = False

    number_of_members = 0

    while t < end_region:

        if expected_default_value and tokens[t] == ';':
            print('\t +Member ' + member_name + " with type " + member_type + \
                " with default value " + member_default_value)
            expected_default_value = False
            member_default_value = ''
            t = t + 1
        elif expected_default_value:
            member_default_value = member_default_value + tokens[t];
            t = t + 1
        elif isinstance(semantic_tokens[t], CSharpElement):
            t = t + 1
        elif (t+4) < end_region and \
           not isinstance(semantic_tokens[t], CSharpElement) and \
           not isinstance(semantic_tokens[t+1], CSharpElement) and \
           not isinstance(semantic_tokens[t+2], CSharpElement) and \
           not isinstance(semantic_tokens[t+3], CSharpElement) and \
           csharp_utils.is_access_modifier(tokens[t]) and \
           csharp_utils.is_const_modifier(tokens[t+1]) and \
           (tokens[t+4] == ';' or tokens[t+4] == '='):
            member_access_level = tokens[t]
            member_is_const = True
            member_type = tokens[t+2]
            member_name = tokens[t+3]
            number_of_members = number_of_members + 1
            if tokens[t+4] == '=':
                expected_default_value = True
            t = t + 5
        elif (t+4) < end_region and \
             not isinstance(semantic_tokens[t], CSharpElement) and \
             not isinstance(semantic_tokens[t+1], CSharpElement) and \
             not isinstance(semantic_tokens[t+2], CSharpElement) and \
             not isinstance(semantic_tokens[t+3], CSharpElement) and \
             csharp_utils.is_access_modifier(tokens[t]) and \
             csharp_utils.is_static_modifier(tokens[t+1]) and \
             (tokens[t+4] == ';' or tokens[t+4] == '='):
            member_access_level = tokens[t]
            member_is_static = True
            member_type = tokens[t+2]
            member_name = tokens[t+3]
            number_of_members = number_of_members + 1
            if tokens[t+4] == '=':
                expected_default_value = True
            t = t + 5
        elif (t+3) < end_region and \
             not isinstance(semantic_tokens[t], CSharpElement) and \
             not isinstance(semantic_tokens[t+1], CSharpElement) and \
             not isinstance(semantic_tokens[t+2], CSharpElement) and \
             csharp_utils.is_access_modifier(tokens[t]) and \
             (tokens[t+3] == ';' or tokens[t+3] == '='):
            member_access_level = tokens[t]
            member_is_static = True
            member_type = tokens[t+2]
            member_name = tokens[t+3]
            number_of_members = number_of_members + 1
            if tokens[t+3] == '=':
                expected_default_value = True
            t = t + 5
        else:
            t = t + 1

    if number_of_members > 0:
        print('\t +Member ' + member_name + " with type " + member_type)

    return tokens_data


