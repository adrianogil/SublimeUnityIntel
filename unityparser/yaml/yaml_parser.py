import sublime, sublime_plugin

import os
import fnmatch
from os.path import join


class YamlElement:

    def __init__(self):
        self.yaml_id = ''

class YamlTransform(YamlElement):


    game_object = None
    children = []
    parent = None

    def __init__(self):
        super(YamlTransform, self).__init__()
        self.go_id = ''
        self.definition_line = 0
        self.children_ids = []
        self.game_object = None
        self.children = []
        self.parent = None

    def add_child(self, child_transform):
        self.children.append(child_transform)
        child_transform.parent = self

class YamlGameObject(YamlElement):

    def __init__(self, gameobject_name, definition_line):
        super(YamlGameObject, self).__init__()
        self.gameobject_name = gameobject_name
        self.definition_line = definition_line
        # self.gameobject_name = ''
        # self.definition_line = 0
        self.transform = None

    def print_outline(self, prefix=''):
        # print(self.gameobject_name)
        object_outline = '<a href="' + str(self.definition_line) + '">' + prefix + ' GameObject ' + \
                                    self.gameobject_name + '</a>'
        # print(object_outline)
        if self.transform != None:
            # print(self.transform.yaml_id)
            for c in self.transform.children:
                if c.game_object != None:
                    object_outline = object_outline + "<br>" +  c.game_object.print_outline(prefix + '-')
                    # object_outline = object_outline + "<br>\n" +  c.game_object.yaml_id
        return object_outline

class YamlPrefab(YamlElement):
    guid = ''
    target_id = ''

    game_object = None
    transform = None

    # def __init__(self, gameobject_name, definition_line):
    #     super(YamlPrefab, self).__init__(gameobject_name, definition_line)
    # def print_outline(self):
    #     object_outline = '<a href="' + str(self.definition_line) + '">Prefab ' + \
    #                                 self.gameobject_name + '</a>'
    #     return object_outline

def parse_yaml(filename, parse_data):
    with open(filename) as f:
            content = f.readlines()
    total_lines = len(content)

    file_data = {}
    file_data['row_by_id'] = {}
    file_data['gameobject_name_by_id'] = {}
    file_data['transform_id_by_gameobject_id'] = {}
    file_data['gameobject_id_by_transform_id'] = {}

    transform_instances = []
    gameobject_instances = []

    current_go_id = ''
    found_go = False
    current_go_line = 0

    current_transform_id = ''
    found_transform = False
    current_transform_line = 0
    transform_go_id = ""
    transform_children_id = []
    found_transform_children_property = False

    current_prefab_id = ''
    current_prefab_guid = ''
    found_prefab = False
    current_prefab_line = 0

    outline_data = []

    for i in range(1, total_lines):
        line = content[i]
        line_size = len(line)
        last_line = content[i-1]

        #  End of a section detected
        if line.find("--- !u!") != -1 and \
           (found_go or found_prefab or found_transform):
            if found_transform:
                file_data['transform_id_by_gameobject_id'][transform_go_id] = current_transform_id
                file_data['gameobject_id_by_transform_id'][current_transform_id] = transform_go_id
                file_data['row_by_id'][current_transform_id] = current_transform_line
                # print("Detected go_id: " + str(go_id) + " related to transform: " + str(current_transform_id))

                transform = YamlTransform()
                transform.yaml_id = current_transform_id
                transform.go_id = transform_go_id
                transform.definition_line = current_transform_line
                transform.children_ids = transform_children_id
                transform_instances.append(transform)

                transform_children_id = []
                current_transform_id = ''
                transform_go_id = ""
                current_transform_line = -1
            found_go = False
            found_prefab = False
            found_transform = False

        # GameObject detection
        if last_line.find('--- !u!') != -1 and line.find("GameObject") != -1:
            current_go_id = last_line[10:-1]
            current_go_line = i
            found_go = True

        if found_go and line.find("m_Name") != -1:
            gameobject_name = line[9:-1]
            file_data['gameobject_name_by_id'][current_go_id] = gameobject_name
            file_data['row_by_id'][current_go_id] = current_go_line
            go_instance = YamlGameObject(gameobject_name, current_go_line)
            go_instance.yaml_id = current_go_id
            outline_data.append(go_instance)
            gameobject_instances.append(go_instance)

            found_go = False
            current_go_id = ''

        # if found_go and line.find("m_PrefabParentObject:") != -1 and line.find("m_PrefabParentObject: {fileID: 0}") == -1:
        #     guid = ''
        #     found_guid = False
        #     for l in range(21, line_size):

        #Prefab detection
        if last_line.find('--- !u!') != -1 and line.find("Prefab") != -1:
            current_prefab_id = last_line[14:-1]
            current_prefab_line = i
            found_prefab = True

        if found_prefab and line.find("target: {") != -1:
            start_prefab_guid = 0
            end_prefab_guid = 0
            for l in range(20, line_size):
                if line[l-6:l].find("guid: ") != -1:
                    start_prefab_guid = l
                if start_prefab_guid > 0 and line[l] == ",":
                    end_prefab_guid = l
                    break
            current_prefab_guid = line[start_prefab_guid:end_prefab_guid]
            # print("found prefab with guid: " + current_prefab_guid)
            if current_prefab_guid in parse_data['yaml']['filenames_by_guid']:
                prefab_filename = parse_data['yaml']['filenames_by_guid'][current_prefab_guid]
                # outline_data.append(YamlPrefab(prefab_filename, current_prefab_line))
            found_prefab = False
            current_prefab_line = 0
            current_prefab_id = ''
            current_prefab_guid = ''

        # Transform detection
        if last_line.find('--- !u!') != -1 and line.find("Transform") != -1:
            current_transform_id = last_line[10:-1]
            current_transform_line = i
            found_transform = True

        if found_transform and line.find("m_GameObject: {fileID: ") != -1:
            start_go_id = 0
            end_go_id = 0
            for l in range(8, line_size):
                if line[l-8:l].find('fileID: ') != -1:
                    start_go_id = l
                elif line[l] == '}':
                    end_go_id = l
                    break
            transform_go_id = line[start_go_id:end_go_id]

        if not found_transform_children_property and \
           found_transform and line.find("m_Children:") != -1 and line.find("m_Children: []") == -1:
            found_transform_children_property = True
            transform_children_id = []
        elif found_transform_children_property and (line.find("- {fileID: ") == -1 or line.find("m_Father:") != -1):
            found_transform_children_property = False
        elif found_transform_children_property:
            start_child_id = 0
            end_child_id = 0
            for l in range(13, line_size):
                if line[l-13:l].find("  - {fileID: ") != -1:
                    start_child_id = l
                if start_child_id > 0 and line[l] == "}":
                    end_child_id = l
                    break
            # Add a child to current transform
            transform_children_id.append(line[start_child_id:end_child_id])

    for t1 in transform_instances:
        # print(t1.go_id)
        # print(t1.children_ids)
        # print(t1.yaml_id + " has " + str(len(t1.children)) + ' children')
        for c in t1.children_ids:
            for t2 in transform_instances:
                if t1 != t2 and t1.yaml_id != t2.yaml_id and t2.yaml_id == c:
                    # print('Add child ' + t2.yaml_id + " to transform " + t1.yaml_id)
                    t1.add_child(t2)
                    break
        # print(t1.yaml_id + " got " + str(len(t1.children)) + ' children')
        for go in gameobject_instances:
            if go.yaml_id == t1.go_id:
                t1.game_object = go
                go.transform = t1
                # print("Add transform " + t1.yaml_id + " to gameobject " + go.yaml_id)
                break

    outline_data = []
    for go in gameobject_instances:
        if go.transform.parent == None:
            outline_data.append(go)

    file_data['game_objects'] = gameobject_instances
    file_data['transforms'] = transform_instances
    file_data['outline_data'] = outline_data
    parse_data['by_files'][filename] = file_data

    return parse_data

def is_valid_unity_project_path(project_path):
    if project_path == "":
        return False
    return os.path.isdir(join(project_path, "Assets")) and \
                   os.path.isdir(join(project_path, "ProjectSettings"))

def get_all_guid_files(project_path, file_path):
    yaml_data = {}

    print('yaml_parser::get_all_guid_files - received project_path: ' + project_path)
    print('yaml_parser::get_all_guid_files - received file_path: ' + file_path)

    if not is_valid_unity_project_path(project_path):
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

    print('yaml_parser::get_all_guid_files - using: ' + project_path)

    if not is_valid_unity_project_path(project_path):
        print('yaml_parser::get_all_guid_files - invalid project path')
        return

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

def print_yaml_file_info(file, selected_text, parser_data, open_file, show_info):
    if selected_text in parser_data['yaml']['files_by_guid']:
        show_info('<b>' + parser_data['yaml']['relative_path_by_guid'][selected_text] + \
                   '</b><br><a href="' + parser_data['yaml']['files_by_guid'][selected_text] + \
                   '">Open</a>', open_file)
        return True
    return False

def print_yaml_gameobject_info(file, selected_text, parser_data, go_to_reference, show_info):
    if selected_text in  parser_data['by_files'][file]['gameobject_name_by_id']:
        popup_text = '<b>GameObject: ' + parser_data['by_files'][file]['gameobject_name_by_id'][selected_text] + \
            '</b><br><a href="' + selected_text + '">Show definition </a> <br>' + \
                    '<a href="'+ parser_data['by_files'][file]['transform_id_by_gameobject_id'][selected_text] + \
                    '">Show Transform component</a>'
        show_info(popup_text, go_to_reference)
        return True
    return False

def print_yaml_transform_info(file, selected_text, parser_data, go_to_reference, show_info):
    if selected_text in parser_data['by_files'][file]['gameobject_id_by_transform_id']:
        selected_text = parser_data['by_files'][file]['gameobject_id_by_transform_id'][selected_text]
        popup_text = '<b>[Transform] GameObject: ' + parser_data['by_files'][file]['gameobject_name_by_id'][selected_text] + \
            '</b><br><a href="' + selected_text + '">Show definition </a> <br>' + \
                    '<a href="'+ parser_data['by_files'][file]['transform_id_by_gameobject_id'][selected_text] + \
                    '">Show Transform component</a>'
        show_info(popup_text, go_to_reference)
        return True
    return False

