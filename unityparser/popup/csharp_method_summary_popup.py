import subprocess

def print_popup(method_instance, view_factory):
    view_factory.clear_actions()

    action_id = 1
    html = '<b><a href="' + str(action_id) + '">Method ' + method_instance.method_name + '</a></b>'
    action = view_factory.get_goto_line_action(method_instance.line_in_file)
    view_factory.register_action(action_id, action)

    def show_changes():
        show_changes_on_method(method_instance, view_factory)

    action_id = action_id + 1
    html = html + '<br><a href="' + str(action_id) + '">Show git changes at Method</a><br>'
    view_factory.register_action(action_id, show_changes)

    html = html + '<br>'

    # params = method_instance.params
    # if len(params) > 0:
    #     html = html + '<br><br>Params:'
    # for i in range(0, len(params)):
    #     html = html + '<br>' + params[i].param_name

    # method_vars = method_instance.variable_instances

    # if len(method_vars) > 0:
    #     html = html + '<br><br>Variables:'

    # for i in range(0, len(method_vars)):
    #     html = html + '<br>' + method_vars[i].var_name

    view_factory.show_popup(html)

def show_changes_on_method(method_instance, view_factory):

    project_path = method_instance.class_object.project_path
    file_name = method_instance.class_object.file_name

    # try:
    go_to_path = 'cd "' + project_path + '" && '

    git_changes_cmd = go_to_path + "git log -L :" + method_instance.method_name + ":" + file_name[len(project_path):]
    print(git_changes_cmd)
    git_changes = subprocess.check_output(git_changes_cmd, shell=True)
    git_changes = git_changes.decode('UTF-8')

    scratch_file = view_factory.view.window().new_file()
    scratch_file.set_name('Git changes')
    scratch_file.set_scratch(True)
    args = {
        'text': git_changes,
        'line': 0
    }
    scratch_file.run_command('insert_text_on_position', args)
    scratch_file.set_read_only(True)
    scratch_file.settings().set('word_wrap', False)
    scratch_file.set_syntax_file("Packages/Diff/Diff.tmLanguage")
    # except:
    #     print('Error')

