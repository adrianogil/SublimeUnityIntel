
def get_showpopup(view):
    def show_popup(text, action):
        view.show_popup(text, on_navigate=action)
    return show_popup


def get_open_file(view):
    def open_file(file):
        view.window().open_file(file)
    return open_file

def get_goto_reference(view, symbolic_data):
    def go_to_reference(id):
        if view.window().active_view():
            row = symbolic_data['parse']['by_files'][file]['row_by_id'][id]
            col = 1
            print("Trying to go to line " + str(row))
            view.window().active_view().run_command(
                    "goto_row_col",
                    {"row": row, "col": col}
            )
    return go_to_reference