import subprocess
import sys

def print_popup(git_data, view_factory):
    view_factory.clear_actions()

    action_id = 0

    git_info = ''
    git_info = git_info + '<b>What changed in Commit: ' + git_data['commit'] + '</b><br>'

    try:
        git_files_cmd = 'cd "' + git_data['project_path'] + '" && git diff-tree --no-commit-id --name-status -r ' + git_data['commit']
        git_files_output = subprocess.check_output(git_files_cmd, shell=True)

        git_files_output = git_files_output.decode('UTF-8')
        git_files_output = git_files_output.split('\n')

        files_added = []
        files_removed = []
        files_updated = []

        for i in range(0, len(git_files_output)):
            # print(git_files_output[i])
            if git_files_output[i] == '':
                break;
            if git_files_output[i][0] == 'D':
                git_file = git_files_output[i][1:].strip()
                # print('Deleted ' + git_file)
                files_removed.append(git_file)
            if git_files_output[i][0] == 'A':
                git_file = git_files_output[i][1:].strip()
                # print('Added ' + git_file)
                files_added.append(git_file)
            else:
                git_file = git_files_output[i][1:].strip()
                # print('Added ' + git_file)
                files_updated.append(git_file)

        if len(files_added) > 0:
            git_info = git_info + '<br>Added ' + str(len(files_added)) + ' files'
        for i in range(0, len(files_added)):
            git_info = git_info + '<br>Added ' + files_added[i][7:]

        if len(files_updated) > 0:
            git_info = git_info + '<br><br>Updated ' + str(len(files_updated)) + ' files'
        for i in range(0, len(files_updated)):
            git_info = git_info + '<br>Updated ' + files_updated[i][7:]

        if len(files_removed) > 0:
            git_info = git_info + '<br><br>Removed ' + str(len(files_removed)) + ' files'
        for i in range(0, len(files_removed)):
            git_info = git_info + '<br>Removed ' + files_removed[i][7:]

    except:
        print("Unexpected error:" + str(sys.exc_info()[0]))

    if view_factory.last_popup_action != None:
        action_id = action_id + 1
        git_info = git_info + '<br><br><a href="' + str(action_id) + '">Back to last popup</a>'
        view_factory.register_action(action_id, view_factory.last_popup_action)

    view_factory.show_popup(git_info, 500)