import os, sys

__file__ = os.path.normpath(os.path.abspath(__file__))
__path__ = os.path.dirname(__file__)

# print(__path__)

if __path__ not in sys.path:
    sys.path.insert(0, __path__)

from csharp_element import CSharpElement

class CSharpType(CSharpElement):
    type_name = ""
    
    # tokens -> tokens where type is defined
    def __init__(self, csharp_type_name, tokens, tokens_pos):
        super(CSharpType, self).__init__('type', tokens, tokens_pos)
        self.type_name = csharp_type_name

class CSharpTypeMember(CSharpElement):
    member_name = ""
    member_type = "type_definition" # type_definition, type_instance, method

def get_string():
    return CSharpType('string', [], 0)