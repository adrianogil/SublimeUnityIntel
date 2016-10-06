import os, sys

__file__ = os.path.normpath(os.path.abspath(__file__))
__path__ = os.path.dirname(__file__)

# print(__path__)

if __path__ not in sys.path:
    sys.path.insert(0, __path__)

from csharp_element import CSharpElement

class CSharpClassParamMethod(CSharpElement):

    def __init__(self, csharp_param_name, tokens, token_pos):
        super(CSharpClassParamMethod, self).__init__('class_method_param', tokens, token_pos)
        self.param_name = csharp_param_name
        self.param_type = ''
        self.param_default_value = ''
        self.method_object = None

# class_region = (token_start, token_end) of enclosure class
def parse_tokens(tokens_data, class_region, method_instance):

    tokens = tokens_data['tokens']
    semantic_tokens = tokens_data['semantic_tokens']
    enclosure_position = tokens_data['enclosure_position']

    params_data = []

    start_region = class_region[0]
    end_region = class_region[1]

    t = start_region

    start_method_pos = -1

    parameter_type = ''
    parameter_name = ''
    parameter_default_value = ''

    parameter_type_found = False
    parameter_name_found = False
    expected_default_value = False

    number_of_parameters = 0

    def create_method_instance(t):
        param_instance = CSharpClassParamMethod(parameter_name, \
                                                 tokens[start_method_pos:t], \
                                                 start_method_pos)
        param_instance.param_type = parameter_type
        param_instance.param_default_value = parameter_default_value
        method_instance.add_param(param_instance)
        params_data.append(param_instance)

        return param_instance

    while t < end_region:

        if tokens[t] == ',':
            # New parameter
            print('\t - parameter ' + parameter_name + " with type " + parameter_type)
            create_method_instance(t)
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
            start_method_pos = t
            number_of_parameters = number_of_parameters + 1
            parameter_type = tokens[t]
            parameter_type_found = True

        t = t + 1

    if number_of_parameters > 0:
        print('\t - parameter ' + parameter_name + " with type " + parameter_type)
        create_method_instance(t)

    tokens_data['params_data'] = params_data

    return tokens_data

