import sublime, sublime_plugin
import os
import sys

__file__ = os.path.normpath(os.path.abspath(__file__))
__path__ = os.path.dirname(__file__)

# print(__path__)


if __path__ not in sys.path:
    sys.path.insert(0, __path__)

from csharp_parser import CSharpParser

class SublimeUnityIntel(sublime_plugin.EventListener):
    def on_load(self, view):
        current_file = view.file_name()

        print(current_file)

        if current_file is None or not current_file.lower().endswith('.cs'):
            return

        parser = CSharpParser()
        parser.parse_file(current_file)