import os, sys
import yaml_parser
from os.path import join

def is_guid(text, yaml_data):
    return text in yaml_data['files_by_guid']

def is_gameobject_id(text, file_data):
    return text in file_data['gameobject_name_by_id']

def is_transform_id(text, file_data):
    return text in file_data['gameobject_id_by_transform_id']

def get_relative_path_from(guid, yaml_data):
    return yaml_data['relative_path_by_guid'][guid]

def get_file_path_from(guid, yaml_data):
    return yaml_data['files_by_guid'][guid]

def get_gameobject_name_from(go_id, file_data):
    return file_data['gameobject_name_by_id'][go_id]

def get_transform_id_from(go_id, file_data):
    return file_data['transform_id_by_gameobject_id'][go_id]

def get_gameobject_id_from(transform_id, file_data):
    return file_data['gameobject_id_by_transform_id'][transform_id]

def show_view(view_factory, selected_text, rowcol):
    yaml_data = view_factory.symbolic_parser.get_yaml_data()
    file_data = view_factory.symbolic_parser.get_current_file_data()

    html = ''
    action_id = -1
    action = None

    if is_guid(selected_text, yaml_data):
        action_id = 1
        html = '<b>' +get_relative_path_from(selected_text, yaml_data) + \
                   '</b><br><a href="' + str(action_id) + '">Open</a>'
        file = get_file_path_from(selected_text, yaml_data)
        action = view_factory.get_open_file_action(file)
        view_factory.register_action(action_id, action)
        view_factory.show_popup(html)
    elif is_gameobject_id(selected_text, file_data):
        action_id = 1
        html = '<b>GameObject: ' + get_gameobject_name_from(selected_text, file_data) + \
            '</b><br><a href="' + str(action_id) + '">Show definition </a> <br>'
        action = view_factory.get_goto_reference_action(selected_text)
        view_factory.register_action(action_id, action)

        action_id = 2
        html = html + '<a href="'+ str(action_id) + \
                    '">Show Transform component</a>'
        action = view_factory.get_goto_reference_action(get_transform_id_from(selected_text, file_data))
        view_factory.register_action(action_id, action)

        view_factory.show_popup(html)
    elif is_transform_id(selected_text, file_data):
        go_id = get_gameobject_id_from(selected_text, file_data)

        action_id = 1
        html = '<b>[Transform] GameObject: ' + get_gameobject_name_from(go_id, file_data) + \
            '</b><br><a href="' + str(action_id) + '">Show definition </a> <br>'
        action = view_factory.get_goto_reference_action(go_id)
        view_factory.register_action(action_id, action)

        action_id = 2
        html = html + '<a href="'+ str(action_id) + '">Show Transform component</a>'
        action = view_factory.get_goto_reference_action(selected_text)
        view_factory.register_action(action_id, action)
        view_factory.show_popup(html)
