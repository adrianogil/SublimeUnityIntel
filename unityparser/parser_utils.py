import os
import fnmatch
from os.path import join

def parse_project(project_path, content_data, file_extension, parse_function):
    for root, subFolders, files in os.walk(project_path):
        for filename in fnmatch.filter(files, file_extension):
            with open(join(root, filename)) as f:
                content = f.readlines()

            content_data = parse_function(content, content_data, root, filename, project_path)
    return content_data

def is_valid_unity_project_path(project_path):
    if project_path == "":
        return False
    return os.path.isdir(join(project_path, "Assets")) and \
                   os.path.isdir(join(project_path, "ProjectSettings"))

def get_project_path(project_path, file_path):
    print('yaml_parser::get_all_guid_files - received project_path: ' + project_path)
    print('yaml_parser::get_all_guid_files - received file_path: ' + file_path)

    if not is_valid_unity_project_path(project_path):
        if file_path == None:
            return ''

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

                    print('parser_utils::get_project_path - ' + project_path)

                    return project_path
                else:
                    return ''

    return ''

