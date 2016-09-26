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

    start_region = class_region[0]
    end_region = class_region[1]

    t = start_region

    parameter_type = ''
    parameter_name = ''
    parameter_default_value = ''

    parameter_type_found = False
    parameter_name_found = False
    expected_default_value = False

    number_of_parameters = 0

    while t < end_region:

        if tokens[t] == ',':
            # New parameter
            print('\t - parameter ' + parameter_name + " with type " + parameter_type)
            parameter_type = ''
            parameter_name = ''
            parameter_default_value = ''

            parameter_type_found = False
            parameter_name_found = False
            expected_default_value = False
        elif expected_default_value:
            parameter_default_value = parameter_default_value + tokens[t]
        elif parameter_name_found and tokens[t] == '=':
            expected_default_value = True
        elif parameter_type_found:
            parameter_name = tokens[t]
            parameter_name_found = True
        else:
            number_of_parameters = number_of_parameters + 1
            parameter_type = tokens[t]
            parameter_type_found = True
        
        t = t + 1

    if number_of_parameters > 0:
        print('\t - parameter ' + parameter_name + " with type " + parameter_type)

    return tokens_data

