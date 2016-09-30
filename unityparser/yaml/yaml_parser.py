import sublime, sublime_plugin

import os
import fnmatch
from os.path import join

files_by_guid = {}
filenames_by_guid = {}
relative_path_by_guid = {}
gameobject_name_by_id = {}
row_by_id = {}

transform_id_by_gameobject_id = {}
gameobject_id_by_transform_id = {}

class YamlGameObject:
    gameobject_name = ''
    definition_line = 0

    def __init__(self, gameobject_name, definition_line):
        self.gameobject_name = gameobject_name
        self.definition_line = definition_line

    def print_outline(self):
        object_outline = '<a href="' + str(self.definition_line) + '">GameObject ' + \
                                    self.gameobject_name + '</a>'
        return object_outline

def parse_yaml(filename, parse_data):
    with open(filename) as f:
            content = f.readlines()
    total_lines = len(content)

    file_data = {}
    file_data['row_by_id'] = {}
    file_data['gameobject_name_by_id'] = {}
    file_data['transform_id_by_gameobject_id'] = {}
    file_data['gameobject_id_by_transform_id'] = {}

    current_go_id = ''
    found_go = False
    current_go_line = 0

    current_transform_id = ''
    found_transform = False
    current_transform_line = 0

    outline_data = []

    for i in range(1, total_lines):
        line = content[i]
        last_line = content[i-1]

        # GameObject detection
        if last_line.find('--- !u!') != -1 and line.find("GameObject") != -1:
            current_go_id = last_line[10:-1]
            current_go_line = i
            found_go = True

        if found_go and line.find("m_Name") != -1:
            gameobject_name = line[9:-1]
            file_data['gameobject_name_by_id'][current_go_id] = gameobject_name
            file_data['row_by_id'][current_go_id] = current_go_line
            outline_data.append(YamlGameObject(gameobject_name, current_go_line))

            found_go = False
            current_go_id = ''

        # Transform detection
        if last_line.find('--- !u!') != -1 and line.find("Transform") != -1:
            current_transform_id = last_line[10:-1]
            current_transform_line = i
            found_transform = True

        if found_transform and line.find("m_GameObject: {fileID: ") != -1:
            line_size = len(line)
            start_go_id = 0
            end_go_id = 0
            for l in range(8, line_size):
                if line[l-8:l].find('fileID: ') != -1:
                    start_go_id = l
                elif line[l] == '}':
                    end_go_id = l
                    break
            go_id = line[start_go_id:end_go_id]
            file_data['transform_id_by_gameobject_id'][go_id] = current_transform_id
            file_data['gameobject_id_by_transform_id'][current_transform_id] = go_id
            file_data['row_by_id'][current_transform_id] = current_transform_line
            # print("Detected go_id: " + str(go_id) + " related to transform: " + str(current_transform_id))
            found_transform = False
            current_transform_id = ''
            current_transform_line = -1

    file_data['outline_data'] = outline_data
    parse_data['by_files'][filename] = file_data

    return parse_data

def get_all_guid_files(project_path, file_path):
    yaml_data = {}

    if project_path == "":
        if file_path == None:
            return yaml_data

        for i in range(0,len(file_path)):
            if file_path[i] == 'A' and \
               file_path[i+1] == 's' and \
               file_path[i+2] == 's' and \
               file_path[i+3] == 'e' and \
               file_path[i+4] == 't' and \
               file_path[i+5] == 's':
                potential_project_path = file_path[:i]
                if os.path.isdir(join(potential_project_path, "Assets")) and \
                   os.path.isdir(join(potential_project_path, "ProjectSettings")):
                    project_path = potential_project_path
                else:
                    return yaml_data

    yaml_data['files_by_guid'] = {}
    yaml_data['filenames_by_guid'] = {}
    yaml_data['relative_path_by_guid'] = {}


    for root, subFolders, files in os.walk(project_path):
        for filename in fnmatch.filter(files, '*.meta'):
            with open(join(root, filename)) as f:
                content = f.readlines()

            guid = ''
            for line in content:
                if line.find('guid:') != -1:
                    guid = line[6:(len(line)-1)]
            # print(filename + ": " + guid)
            yaml_data['files_by_guid'][guid] = join(root, filename)[:-5]
            yaml_data['filenames_by_guid'][guid] = filename[:-5]
            yaml_data['relative_path_by_guid'][guid] = join(root, filename)[len(project_path):-5]

    return yaml_data

def on_selection_modified_async(self, view):
    current_file = view.file_name()

    if current_file is None or (not current_file.lower().endswith(('.unity', '.prefab', '.meta'))):
        return

    if not self.get_all_guid_files(view):
        return

    self.parse_yaml(view)

    for region in view.sel():
        selected_text = view.substr(region)

        def open_file(file):
            view.window().open_file(file)

        def go_to_reference(id):
            if view.window().active_view():
                row = self.row_by_id[id]
                col = 1
                print("Trying to go to line " + str(row))
                view.window().active_view().run_command(
                        "goto_row_col",
                        {"row": row, "col": col}
                )

        if selected_text in self.files_by_guid:
            view.set_status('guid_info', self.files_by_guid[selected_text])
            view.show_popup('<b>' + self.relative_path_by_guid[selected_text] + '</b><br><a href="' + self.files_by_guid[selected_text] + '">Open</a>', on_navigate=open_file)

        if selected_text in self.gameobject_name_by_id:
            popup_text = '<b>GameObject: ' + self.gameobject_name_by_id[selected_text] + \
                '</b><br><a href="' + selected_text + '">Show definition </a> <br>' + \
                        '<a href="'+ self.transform_id_by_gameobject_id[selected_text] + \
                        '">Show Transform component</a>'
            view.set_status('guid_info', self.gameobject_name_by_id[selected_text])
            view.show_popup(popup_text, on_navigate=go_to_reference)

        if selected_text in self.gameobject_id_by_transform_id:
            selected_text = self.gameobject_id_by_transform_id[selected_text]
            popup_text = '<b>[Transform] GameObject: ' + self.gameobject_name_by_id[selected_text] + \
                '</b><br><a href="' + selected_text + '">Show definition </a> <br>' + \
                        '<a href="'+ self.transform_id_by_gameobject_id[selected_text] + \
                        '">Show Transform component</a>'
            view.set_status('guid_info', self.gameobject_name_by_id[selected_text])
            view.show_popup(popup_text, on_navigate=go_to_reference)

