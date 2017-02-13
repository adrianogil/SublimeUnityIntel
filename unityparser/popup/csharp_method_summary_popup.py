def print_popup(method_instance, view_factory):
    view_factory.clear_actions()

    action_id = 1
    html = '<b><a href="' + str(action_id) + '">Method ' + method_instance.method_name + '</a></b>'
    action = view_factory.get_goto_line_action(method_instance.line_in_file)
    view_factory.register_action(action_id, action)

    params = method_instance.params
    if len(params) > 0:
        html = html + '<br><br>Params:'
    for i in range(0, len(params)):
        html = html + '<br>' + params[i].param_name

    method_vars = method_instance.variable_instances

    if len(method_vars) > 0:
        html = html + '<br><br>Variables:'

    for i in range(0, len(method_vars)):
        html = html + '<br>' + method_vars[i].var_name

    view_factory.show_popup(html)