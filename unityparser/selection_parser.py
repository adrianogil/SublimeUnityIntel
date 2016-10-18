import os, sys
from os.path import join

__file__ = os.path.normpath(os.path.abspath(__file__))
__path__ = os.path.dirname(__file__)
__csharp_path__ = join(__path__, 'csharp')
__yaml_path__ = join(__path__, 'yaml')

print(__csharp_path__)

if __path__ not in sys.path:
    sys.path.insert(0, __path__)
if __csharp_path__ not in sys.path:
    sys.path.insert(0, __csharp_path__)
if __yaml_path__ not in sys.path:
    sys.path.insert(0, __yaml_path__)

from yaml import yaml_selection
from csharp import csharp_selection

from view_factory import ViewFactory

def handle_selection(view, symbolic_parser):
    view_factory_instance = ViewFactory(view, symbolic_parser)

    file = view.file_name()

    show_view_method = None
    if file.lower().endswith(('.unity','.prefab','.asset', '.meta')):
        show_view_method = yaml_selection.show_view
    elif file.lower().endswith('.cs'):
        show_view_method = csharp_selection.show_view
    else:
        return

    for region in view.sel():
            selected_text = view.substr(region)
            rowcol = view.rowcol(region.begin())
            show_view_method(view_factory_instance, selected_text, rowcol)