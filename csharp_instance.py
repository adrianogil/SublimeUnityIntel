import os, sys

__file__ = os.path.normpath(os.path.abspath(__file__))
__path__ = os.path.dirname(__file__)

# print(__path__)

if __path__ not in sys.path:
    sys.path.insert(0, __path__)

from csharp_element import CSharpElement
from csharp_type import CSharpType

class CSharpInstance(CSharpElement):
    # Instance modes:
    #  - literal_instance (string, numbers)
    #  - variable_instance
    instance_mode = 'variable_instance'
    instance_type = CSharpType('', [], 0)

    def __init__(self, csharp_instance_type, tokens, tokens_pos):
        super(CSharpInstance, self).__init__('instance', tokens, tokens_pos)
        self.instance_mode = 'variable_instance'
        self.instance_type = csharp_instance_type

    def __init__(self, csharp_instance_mode, csharp_instance_type, tokens, tokens_pos):
        super(CSharpInstance, self).__init__('instance', tokens, tokens_pos)
        self.instance_mode = csharp_instance_mode
        self.instance_type = csharp_instance_type