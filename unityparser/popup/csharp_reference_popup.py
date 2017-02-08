import codecs

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
        if file_path == '':
            continue
        # print(file_path)
        if file_path in files_usage:
            files_usage[file_path] = files_usage[file_path] + 1
            # print('Refs: ' + str(refs_by_path[file_path]))
            ref_list = refs_by_path[file_path]
            ref_list.append(R)
            refs_by_path[file_path] = ref_list
        else:
            files_usage[file_path] = 1
            refs_by_path[file_path] = [R]

    list_paths = []

    for file_path in files_usage:
        total_ref = files_usage[file_path]

        list_paths.append(file_path)

        if total_ref <= 0:
            continue

        ref_str = ' References'
        if total_ref == 1:
            ref_str = ' Reference'

        action_id = action_id + 1
        # Removes 'Assets/' from path
        html = html + '<br><br><a href="' + str(action_id) + '">' + file_path[7:] + "</a>"
        html = html + '<br>[' + str(total_ref) + ref_str + ']'

        def show_ref_popup():
            file_path = list_paths[view_factory.last_selected_action_id - 2]
            ref = refs_by_path[file_path]
            print_reference(class_instance, view_factory, file_path, ref)
        view_factory.register_action(action_id, show_ref_popup)

        for ref in refs_by_path[file_path]:
            action_id = action_id + 1
            html = html + '<br><a href="' + str(action_id) + '">Line ' + str(ref.line_in_file) + ":</a>"
            html = html + ' ' + get_line_in_reference(ref) + '<br>'
            action = view_factory.get_goto_file_reference_action(ref.file_name, ref.line_in_file)
            view_factory.register_action(action_id, action)

    view_factory.show_popup(html, 500)

def get_line_in_reference(ref):
    csharp_file = ref.file_name
    with codecs.open(csharp_file, encoding="utf-8-sig", errors='ignore') as f:
        content = f.readlines()
    total_lines = len(content)

    line_number = ref.line_in_file - 1

    if line_number < 0 or line_number >= total_lines:
        return ""

    return content[line_number]

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
        html = html + '<br><a href="' + str(action_id) + '">Line ' + str(ref.line_in_file) + ":</a>"
        html = html + '<br>' + get_line_in_reference(ref) + '<br>'
        action = view_factory.get_goto_file_reference_action(ref.file_name, ref.line_in_file)
        view_factory.register_action(action_id, action)

    view_factory.show_popup(html, 700)
