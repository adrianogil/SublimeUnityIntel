import os, sys
import fnmatch
from os.path import join

import codecs

__file__ = os.path.normpath(os.path.abspath(__file__))
__path__ = os.path.dirname(__file__)

# print(__path__)


if __path__ not in sys.path:
    sys.path.insert(0, __path__)

from csharp_token_parser import CSharpTokenParser


class CSharpElement:
    name = ""

class CSharpParser:
    def parse_file(self, csharp_file):
        tokens_data = CSharpTokenParser().parse_file(csharp_file)

        print(tokens_data)
            


