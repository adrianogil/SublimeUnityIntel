def print_popup(class_instance, view_factory):
    view_factory.clear_actions()

    # Header and link to go back to last popup
    action_id = 0
    html = '<b>CSharp files that references <a href="' + str(action_id) + \
           '">' + class_instance.class_name + ' class</a></b>'
    def open_element_info():
        class_instance.print_element_info(view_factory)
    action = open_element_info
    view_factory.register_action(action_id, action)
    action_id = action_id + 1

    p_path_size = len(class_instance.project_path)

    files_usage = {}
    refs_by_path = {}

    file_path = ''

    for R in class_instance.referenced:
        file_path = R.file_name[p_path_size:]
        if file_path in files_usage:
            files_usage[file_path] = files_usage[file_path] + 1
            refs_by_path[file_path] = refs_by_path[file_path].append(R)
        else:
            files_usage[file_path] = 1
            refs_by_path[file_path] = [R]

    for file_path in files_usage:
        total_ref = files_usage[file_path]

        if total_ref <= 0:
            continue
        ref_str = ' References'
        if total_ref == 1:
            ref_str = ' Reference'

        action_id = action_id + 1
        html = html + '<br><br><a href="' + str(action_id) + '">' + str(total_ref) + ref_str + ' from <br>' + file_path + "</a>"
        def show_ref_popup():
            print_reference(class_instance, view_factory, file_path, refs_by_path[file_path])
        view_factory.register_action(action_id, show_ref_popup)

    view_factory.show_popup(html, 500)

def print_reference(class_instance, view_factory, csharp_path, ref_list):
    view_factory.clear_actions()
    total_ref = len(ref_list)

    action_id = 0
    html = '<b><a href="' + str(action_id) + '">' + str(total_ref) + ' References from<br>' + csharp_path + ':</a></b><br>'
    def back_to_charp_references():
        print_popup(class_instance, view_factory)
    view_factory.register_action(action_id, back_to_charp_references)

    for ref in ref_list:
        action_id = action_id + 1
        html = html + '<br><a href="' + str(action_id) + '">From line ' + str(ref.line_in_file) + '</a>'
        action = view_factory.get_goto_file_reference_action(ref.file_name, ref.line_in_file)
        view_factory.register_action(action_id, action)

    view_factory.show_popup(html, 500)