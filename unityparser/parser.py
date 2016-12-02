import os, sys, time
import fnmatch
from os.path import join
import codecs

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

from token_parser import TokenParser
import yaml_parser

from csharp_class_method_parser import CSharpClassMethod
from csharp.csharp_element import CSharpElement
# from csharp import csharp_class_method_parser
from csharp import csharp_importer_parser
from csharp import csharp_class_parser
from csharp import csharp_interface_parser

import csharp
import parser_utils
import pickle

import selection_parser
import view_factory

class SymbolicParser:
    def __init__(self):
        self.symbolic_data = { \
            'parse': { \
                'symbols' : {}, \
                'by_files' : {} \
            } \
        }
        self.parse_file_by_filetype = { \
            ('.cs') : self.parse_csharp_file, \
            ('.unity','.prefab','.asset') : self.parse_yaml_file \
        }
        self.last_parse_time = {}
        self.current_file = ''
        self.current_project_path = ''

    def parse_project(self, file_path):
        project_path = parser_utils.get_project_path('', file_path)
        if project_path != '' and (not project_path in self.last_parse_time or (time.time() - self.last_parse_time[project_path]) > 6000):
            self.current_project_path = project_path
            print('parser::parse_project ' + project_path)
            self.last_parse_time[project_path] = time.time()
            self.symbolic_data['parse']['yaml'] = yaml_parser.get_all_guid_files(project_path, parser_utils.parse_project)
            self.symbolic_data['parse'] = parser_utils.parse_project(project_path, self.symbolic_data['parse'], '*.cs', self.parse_csharp_project_wise, False)
            self.symbolic_data['parse'] = parser_utils.parse_project(project_path, self.symbolic_data['parse'], '*.unity', self.parse_yaml_project_wise, False)
            self.symbolic_data['parse'] = parser_utils.parse_project(project_path, self.symbolic_data['parse'], '*.prefab', self.parse_yaml_project_wise, False)
            self.parse_csharp_internal_symbols()
            self.parse_csharp_behaviors_events()
            pickle.dump(self.symbolic_data, open(join(project_path, 'code_data.symbolic'), 'wb'))
            # print(self.symbolic_data['parse']['symbols'])

    def parse_yaml_project_wise(self, content, parse_data, root, filename, project_path):
        file = join(root, filename)
        print("Parsing file " + file)
        self.parse_yaml_file(file)
        return self.symbolic_data['parse']

    def parse_csharp_project_wise(self, content, parse_data, root, filename, project_path):
        file = join(root, filename)
        print("Parsing file " + file)
        self.parse_csharp_file(file)
        return self.symbolic_data['parse']


    def parse_csharp_internal_symbols(self):
        csharp_symbols = self.symbolic_data['parse']['symbols']
        for s in csharp_symbols:
            c = csharp_symbols[s]
            if isinstance(c, csharp.csharp_class_parser.CSharpClass):#c.element_type == "class":
                symbol_base_info = []
                for b in c.base_info:
                    symbol = b
                    if b in self.symbolic_data['parse']['symbols']:
                        print(b)
                        symbol = self.symbolic_data['parse']['symbols'][b]
                        if isinstance(symbol, csharp.csharp_class_parser.CSharpClass):
                            symbol.inherited_by.append(c)
                        elif isinstance(symbol, csharp.csharp_interface_parser.CSharpInterface):
                            symbol.implemented_by.append(c)
                    symbol_base_info.append(symbol)
                c.base_info = symbol_base_info

    def parse_csharp_behaviors_events(self):
        print('parse_csharp_behaviors_events - Start')
        csharp_symbols = self.symbolic_data['parse']['symbols']
        behaviors_events = { 'Awake' : [],  'Start' : [], 'Update' : [], 'OnEnable' : [], 'OnDisable' : [] }
        for s in csharp_symbols:
            c = csharp_symbols[s]
            if self.is_monobehavior(c):
                print(c.class_name + ' is monobehaviour')
                for m in c.methods_data:
                    if self.is_behavior_event(m.method_name):
                        print('Added ' + c.class_name + ' to event ' + m.method_name)
                        event_list = behaviors_events[m.method_name]
                        event_list.append(m)
                        behaviors_events[m.method_name] = event_list
        self.symbolic_data['parse']['behaviors_events'] = behaviors_events
        print('parse_csharp_behaviors_events - Finish')


    def is_monobehavior(self, symbol):
        base_class = symbol
        while hasattr(base_class, 'base_info') and len(base_class.base_info) > 0:
            base_class = base_class.base_info[0]
            if base_class == 'MonoBehaviour':
                return True
        return False

    def is_behavior_event(self, method_name):
        return method_name == 'Awake' or \
            method_name == 'Start' or \
            method_name == 'Update' or \
            method_name == 'OnEnable' or \
            method_name == 'OnDisable'

    def parse_csharp_file(self, file):
        try:
            # Parse file into a set of tokens
            tokens_data = TokenParser().parse_file(file)
            # print(tokens_data) # For debug purposes
            tokens_data = csharp_importer_parser.parse_tokens(tokens_data)
            tokens_data = csharp_class_parser.parse_tokens(tokens_data)
            tokens_data = csharp_interface_parser.parse_tokens(tokens_data)
            # Save data
            self.symbolic_data['parse']['by_files'][file] = tokens_data

            if 'classes' in tokens_data:
                for c in tokens_data['classes']:
                    symbol_name = c.namespace + c.symbol_name
                    if symbol_name in self.symbolic_data['parse']['symbols']:
                        self.symbolic_data['parse']['symbols'][symbol_name].recycle(c)
                    self.symbolic_data['parse']['symbols'][symbol_name] = c
                    c.file_name = file
                    c.project_path = self.current_project_path
            if 'interfaces' in tokens_data:
                for c in tokens_data['interfaces']:
                    symbol_name = c.namespace + c.symbol_name
                    if symbol_name in self.symbolic_data['parse']['symbols']:
                        self.symbolic_data['parse']['symbols'][symbol_name].recycle(c)
                    self.symbolic_data['parse']['symbols'][symbol_name] = c
        except:
             print("Unexpected error:" + str(sys.exc_info()[0]))

    def parse_yaml_file(self, file):
        # yaml_parser
        if not 'yaml' in self.symbolic_data['parse']:
            self.symbolic_data['parse']['yaml'] = yaml_parser.get_all_guid_files(parser_utils.get_project_path('', file), parser_utils.parse_project)
        self.symbolic_data['parse'] = yaml_parser.parse_yaml(file, self.symbolic_data['parse'])

    def parse_file(self, file):
        if file is None:
            return
        for t in self.parse_file_by_filetype:
            if file.lower().endswith(t):
                self.parse_file_by_filetype[t](file)

    def debugself(self):
        print('debugself')

    def print_selection_info(self, view):
        file = view.file_name()

        if file == None:
            return

        self.current_file = file

        selection_parser.handle_selection(view, self)

    def get_yaml_data(self):
        return self.symbolic_data['parse']['yaml']

    def get_current_file_data(self):
        return self.symbolic_data['parse']['by_files'][self.current_file]

    # Print outline for current file
    # @param show_outline - method to exhibit outline
    #                       should receive a text and navigation method
    def print_outline(self, file, view, font):
        file_data = self.symbolic_data['parse']['by_files'][file]

        class_field = []
        current_class_fields = []

        if 'outline_data' in file_data:
            outline_data = file_data['outline_data']
            index = 0

            for c in outline_data:
                elements, element_info = c.get_elements_info()
                for i in range(0, len(elements)):
                    class_field.append(elements[i])
                    current_class_fields.append(element_info[i])

            def choice_field(choice):
                if choice < 0 or choice >= len(class_field):
                    return

                view.window().active_view().run_command(
                        "goto_row_col",
                        {"row": class_field[choice].definition_line+1, "col": 1}
                )

            view.window().show_quick_panel(current_class_fields, choice_field, font)

    # Print class variable outline for current class
    # @param show_outline - method to exhibit outline
    #                       should receive a text and navigation method
    def print_fields_outline(self, file, view, font):
        if not file.lower().endswith(('.cs')):
            return

        file_data = self.symbolic_data['parse']['by_files'][file]

        class_field = []
        current_class_fields = []

        if 'outline_data' in file_data:
            outline_data = file_data['outline_data']
            index = 0

            for c in outline_data:
                for f in c.fields_data:
                    class_field.append(f.field_name)
                    current_class_fields.append(f.print_element_info())

            def choice_field(choice):
                if choice < 0 or choice >= len(class_field):
                    return

                view.window().active_view().run_command(
                        "insert_text_on_selection",
                        {"text": class_field[choice]}
                )

            view.window().show_quick_panel(current_class_fields, choice_field, font)


    def get_semantic_token(self, file, rowcol, usingcol = False, sameLine=False, token_verification=False, token_selected=''):
        file_data = self.symbolic_data['parse']['by_files'][file]
        if 'token_position' in file_data:
            token_position = file_data['token_position']
            tokens = file_data['tokens']
            row, col = rowcol
            # print('parser.py::get_semantic_token - searching in position ' + str(row) + ',' + str(col))
            total_tokens = len(token_position)
            for i in list(reversed(range(0, total_tokens))):
                token_row,  token_col = token_position[i]
                token_size = len(tokens[i])

                if ((not sameLine and row > token_row) or \
                    (sameLine and row == token_row)) and \
                    (not usingcol or (col <= token_col and col >= (token_col - token_size))) \
                    and (not token_verification or (len(token_selected) > 1 and tokens[i].find(token_selected) != -1) ):
                    # print('parser.py::get_semantic_token - found semantic token: ' + str(i) + \
                    #     ' - ' + str(file_data['semantic_tokens'][i]) + ' in position ' +  \
                    #     str(token_row) + ',' + str(token_col) + " which token is " + \
                    #     tokens[i] + ' and token_verification ' + str(token_selected))
                    return file_data['semantic_tokens'][i]
        else:
            return None

    def print_debuglog(self, file, rowcol):
        file_data = self.symbolic_data['parse']['by_files'][file]
        semantic_object = self.get_semantic_token(file, rowcol)

        if semantic_object == None:
            return ''
        if isinstance(semantic_object, CSharpClassMethod):
            return semantic_object.get_debug_log()
        else:
            return ""

    def show_unity_behaviors_events(self, view, font):

        # Allow user to choose a behavior event
        view_factory_instance = view_factory.ViewFactory(view, self)

        events = ['Awake', 'Start', 'Update', 'OnEnable', 'OnDisable']
        def choice_field(choice):
                if choice < 0 or choice >= len(events):
                    return

                print('show_unity_behaviors_events::choice_field')

                if 'behaviors_events' in self.symbolic_data['parse']:

                    def get_class_name(method):
                        return method.class_object.class_name

                    events_method = self.symbolic_data['parse']['behaviors_events'][events[choice]]
                    events_method = sorted(events_method, key=get_class_name)

                    html = '<b> Methods attached to ' + events[choice] + ' event: </b> <br> Found <b>' + str(len(events_method)) + \
                            '</b> Monobehaviours <br> '
                    action_id = 0
                    for m in events_method:
                        c = m.class_object
                        html = html + '<a href="' + str(action_id) + '">'  + c.class_name + '.' + events[choice] + '</a><br>'
                        # print(c.file_name)
                        action = view_factory_instance.get_goto_file_reference_action(c.file_name, int(m.line_in_file)+1)
                        view_factory_instance.register_action(action_id, action)
                        action_id = action_id + 1
                        # print(c.class_name)
                    view_factory_instance.show_popup(html)


        # popup_text = '<b>GameObject: ' + parser_data['by_files'][file]['gameobject_name_by_id'][selected_text] + \
        #     '</b><br><a href="' + selected_text + '">Show definition </a> <br>' + \
        #             '<a href="'+ parser_data['by_files'][file]['transform_id_by_gameobject_id'][selected_text] + \
        #             '">Show Transform component</a>'

        view.window().show_quick_panel(events, choice_field, font)

        # Create a buffer with the result

        #
