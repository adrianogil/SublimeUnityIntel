def print_popup(gameobject_model, view_factory):
    # print('print_popup - yaml_gameobject_popup')
    action_id = 1
    html = '<b>GameObject: ' + gameobject_model.get_name() + \
        '</b><br><a href="' + str(action_id) + '">Show definition </a> <br>'
    action = view_factory.get_goto_reference_action(gameobject_model.get_selected_text())
    view_factory.register_action(action_id, action)

    action_id = 2
    html = html + '<a href="'+ str(action_id) + \
                '">Show Transform component</a>'
    action = view_factory.get_goto_reference_action(gameobject_model.get_transform_id())
    view_factory.register_action(action_id, action)

    view_factory.show_popup(html)