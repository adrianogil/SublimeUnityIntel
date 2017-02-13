import subprocess
import sys

def print_popup(git_data, view_factory):
    view_factory.clear_actions()

    action_id = 0

    git_info = ''
    if git_data['popup_title'] == None:
        git_info = git_info + '<b>Summary of Git Commits'
    else:
        git_info = git_info + git_data['popup_title']
        git_data['popup_title_action']()

    git_info = git_info + '<br><br>' + str(len(git_data['hash_list'])) + ' changes registered<br>'

    try:
        go_to_path = 'cd "' + git_data['project_path'] + '" && '

        git_hash_list = git_data['hash_list']

        for i in range(0, len(git_hash_list)):
            git_title_cmd = go_to_path + "git --no-pager show -s --format='%s' " + git_hash_list[i]
            git_title = subprocess.check_output(git_title_cmd, shell=True)
            git_title = git_title.decode('UTF-8')

            git_date_cmd = go_to_path + "git --no-pager show -s --format='%ai' " + git_hash_list[i]
            git_date = subprocess.check_output(git_date_cmd, shell=True)
            git_date = git_date.decode('UTF-8')

            def setup_git_whatchanged_popup(commit, git_action_id, project_path):
                def show_git_whatchanged():
                    git_commit_data = {}
                    git_commit_data['commit'] = commit
                    git_commit_data['project_path'] = project_path
                    view_factory.print_git_whatchanged_commit_popup(git_commit_data)
                view_factory.register_action(git_action_id, show_git_whatchanged)

            action_id = action_id + 1
            git_info = git_info + '<br><br>' + git_date +  '<br> <a href="' + str(action_id) + '">' + git_hash_list[i] + ': ' + git_title + '</a>'
            setup_git_whatchanged_popup(git_hash_list[i], action_id, git_data['project_path'])

    except:
        print("Unexpected error:" + str(sys.exc_info()[0]))

    if view_factory.last_popup_action != None:
        last_popup_action = view_factory.last_popup_action
        action_id = action_id + 1
        git_info = git_info + '<br><br><a href="' + str(action_id) + '">Back to last popup</a>'
        view_factory.register_action(action_id, last_popup_action)

    def back_to_this_popup():
        print_popup(git_data, view_factory)
    view_factory.last_popup_action = back_to_this_popup

    view_factory.show_popup(git_info, 500)
