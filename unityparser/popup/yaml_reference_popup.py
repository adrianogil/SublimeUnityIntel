def print_popup(class_instance, view_factory):
    view_factory.clear_actions()

    action_id = 0
    html = '<b>YAML files that references <a href="' + str(action_id) + \
           '">' + class_instance.class_name + ' class</a></b>'
    def open_element_info():
        class_instance.print_element_info(view_factory)
    action = open_element_info
    view_factory.register_action(action_id, action)

    action_id = action_id + 1

    p_path_size = len(class_instance.project_path)

    yaml_usage = {}
    refs = {}

    for u in class_instance.usage:
        if u.reference_type == 'yaml':
            if u.reference_file_path in yaml_usage:
                yaml_usage[u.reference_file_path].append(u)
            else:
                yaml_usage[u.reference_file_path] = [u]

    for ypath in yaml_usage:
        total_ref = len(yaml_usage[ypath])
        yaml_path = ypath[p_path_size:]

        action_id = action_id + 1
        html = html + '<br><br><a href="' + str(action_id) + '">- ' + str(total_ref) + ' References from <br>' + yaml_path + "</a>"
        refs[action_id] = ypath
        def yaml_reference_selection():
            ypath = refs[view_factory.last_selected_action_id]
            print_yaml_references_from_file(class_instance, view_factory, ypath[p_path_size:], yaml_usage[ypath])
        action = yaml_reference_selection
        view_factory.register_action(action_id, action)

    view_factory.show_popup(html, 500)

def print_yaml_references_from_file(class_instance, view_factory, yaml_path, yaml_instance_list):
    view_factory.clear_actions()
    total_ref = len(yaml_instance_list)

    action_id = 0

    html = '<b><a href="' + str(action_id) + '">' + str(total_ref) + ' References from<br>' + yaml_path + ':</a></b><br>'
    def back_to_yaml_references():
        print_popup(class_instance, view_factory)
    action = back_to_yaml_references
    view_factory.register_action(action_id, action)

    for u in yaml_instance_list:
        action_id = action_id + 1
        html = html + '<br><a href="' + str(action_id) + '">From line ' + str(u.definition_line) + '</a>'
        action = view_factory.get_goto_file_reference_action(u.reference_file_path, u.definition_line)
        view_factory.register_action(action_id, action)

    view_factory.show_popup(html, 500)