import subprocess
import sys

def print_popup(class_instance, view_factory):
    view_factory.clear_actions()

    action_id = 1
    class_info = '<b><a href="' + str(action_id) + '">Class ' + class_instance.class_name + '</a></b>' + \
                '<br>' + str(len(class_instance.methods_data)) + " methods " + \
                '<br>' + str(len(class_instance.fields_data)) + " fields " + \
                '<br>' + str(len(class_instance.properties_data)) + " properties "
    action = view_factory.get_goto_line_action(class_instance.line_in_file)
    view_factory.register_action(action_id, action)

    for b in class_instance.base_info:
        if hasattr(b, 'element_type') and b.element_type == "class":
            action_id = action_id + 1
            class_info = class_info + '<br>Inherits from <a href="' + str(action_id) + '">' + b.class_name + '</a> '
            action = view_factory.get_goto_file_reference_action(b.file_name, b.line_in_file)
            view_factory.register_action(action_id, action)
        elif b == "MonoBehaviour":
            class_info = class_info + '<br>Inherits from MonoBehaviour '
    for c in class_instance.inherited_by:
        action_id = action_id + 1
        class_info = class_info + '<br>Inherited by <a href="' + str(action_id) + '">' + c.class_name + '</a> '
        action = view_factory.get_goto_file_reference_action(c.file_name, c.line_in_file)
        view_factory.register_action(action_id, action)
    yaml_reference_count = 0
    for u in class_instance.usage:
        if u.reference_type == 'yaml':
            yaml_reference_count = yaml_reference_count + 1
        # class_info = class_info + '<br> Referencied by line ' + str(u.definition_line) + '<br>' + u.reference_file_path
    if yaml_reference_count > 0:
        action_id = action_id + 1
        class_info = class_info + '<br>  <a href="' + str(action_id) + '">' + str(yaml_reference_count) + ' references from YAML files</a>'
        def show_yaml_references_popup():
            view_factory.print_yaml_ref_popup(class_instance)
        action = show_yaml_references_popup
        view_factory.register_action(action_id, action)

    total_referenced = len(class_instance.referenced)
    if total_referenced > 0:
        ref_label = ' references'
        if total_referenced == 1:
            ref_label =' reference'
        action_id = action_id + 1
        class_info = class_info + '<br><a href="' + str(action_id) + '">' + str(total_referenced) + ref_label + ' from another classes </a>'
        def show_csharp_ref_popup():
            view_factory.print_csharp_ref_popup(class_instance)
        action = show_csharp_ref_popup
        view_factory.register_action(action_id, action)

    git_hashes_cmd = 'cd "' + class_instance.project_path + '" && git log --oneline ' + class_instance.file_name + '| cut -d " " -f 1'
    try:
        git_hashes_output = subprocess.check_output(git_hashes_cmd, shell=True)
        git_hashes_output = git_hashes_output.decode('UTF-8')
        git_hashes = git_hashes_output.split('\n')
        # print(git_hashes[0])
        # print(git_hashes[len(git_hashes)-2])
        last_updated_commit = git_hashes[0]
        first_commit = git_hashes[len(git_hashes)-2]

        def setup_git_whatchanged_popup(commit, git_action_id):
            def show_git_whatchanged():
                git_data = {}
                git_data['commit'] = commit
                git_data['project_path'] = class_instance.project_path
                view_factory.print_git_whatchanged_commit_popup(git_data)
            view_factory.register_action(git_action_id, show_git_whatchanged)

        action_id = action_id + 1
        class_info = class_info + '<br>Last updated at commit: <a href="' + str(action_id) + \
                    '">' + last_updated_commit + "</a>"
        setup_git_whatchanged_popup(last_updated_commit, action_id)

        action_id = action_id + 1
        class_info = class_info + '<br>Created at commit: <a href="' + str(action_id) + \
            '">' + first_commit + "</a>"
        setup_git_whatchanged_popup(first_commit, action_id)

        action_id = action_id + 1
        class_info = class_info + '<br><a href="' + str(action_id) + \
            '">See all changes in this file</a>'
        def show_git_summary():
            git_data = {}
            git_data['popup_title'] = None
            git_data['hash_list'] = git_hashes[:len(git_hashes)-1]
            git_data['project_path'] = class_instance.project_path
            view_factory.print_git_summary_list_popup(git_data)
        view_factory.register_action(action_id, show_git_summary)

    except:
        print("Unexpected error:" + str(sys.exc_info()[0]))

    def back_to_this_popup():
        print_popup(class_instance, view_factory)
    view_factory.last_popup_action = back_to_this_popup

    # print(class_info)
    view_factory.show_popup(class_info)