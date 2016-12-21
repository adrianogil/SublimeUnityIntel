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
        def yaml_reference_selection():
            class_instance.print_yaml_references_from_file(view_factory, yaml_path, yaml_usage[ypath])
        action = yaml_reference_selection
        view_factory.register_action(action_id, action)

        # for u in yaml_usage[ypath]:
        #     action_id = action_id + 1
        #     html = html + '<br><a href="' + str(action_id) + '">Referenced from line ' + str(u.definition_line) + '</a>'
        #     action = view_factory.get_goto_file_reference_action(u.reference_file_path, u.definition_line)
        #     view_factory.register_action(action_id, action)

    view_factory.show_popup(html, 500)