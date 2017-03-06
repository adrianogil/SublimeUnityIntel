import sys

def print_popup(method_instance, view_factory):
    view_factory.clear_actions()

    action_id = 1
    method_info = '<b><a href="' + str(action_id) + '">Method ' + method_instance.method_name + '</a></b>'
    action = view_factory.get_goto_line_action(method_instance.line_in_file)
    view_factory.register_action(action_id, action)

    method_info = method_info + '<br>'

    def open_last_popup():
            print_popup(method_instance, view_factory)
    view_factory.last_popup_action = open_last_popup

    print_scope_popup(method_instance, view_factory, method_info, action_id)

def print_scope_popup(scope_instance, view_factory, scope_info = '', action_id = 0):

    if action_id == 0:
        view_factory.clear_actions()

    scope_info = scope_info + 'Current scope variables from a Total of ' + str(len(scope_instance.variable_instances))

    for v in scope_instance.variable_instances:
        scope_info = scope_info + '<br>' + v.var_name

    scope_info = scope_info + '<br><br>Current sub-scope: from a Total of ' + str(len(scope_instance.scope_children))

    scope_index = 0

    for s in scope_instance.scope_children:
        action_id = action_id + 1
        scope_info = scope_info + "<br><a href='" + str(action_id) + "'> Sub-scope " + str(scope_index) + "</a>"
        scope_index = scope_index + 1 

        def open_scope():
            print_scope_popup(s, view_factory)

        view_factory.register_action(action_id, open_scope)

    if view_factory.last_popup_action != None:
        action_id = action_id + 1
        scope_info = scope_info + '<br><br><a href="' + str(action_id) + '">Back to method popup</a>'
        view_factory.register_action(action_id, view_factory.last_popup_action)

    view_factory.show_popup(scope_info)