import csharp_class_parser
import csharp_class_method_parser

def show_view(view_factory, selected_text, rowcol):
    file_data = view_factory.symbolic_parser.get_current_file_data()

    if is_guid(selected_text, yaml_data):
        semantic_object = view_factory.symbolic_parser.get_semantic_token(file, rowcol, True, True, True, selected_text)
        # print('parser.py::print_selection_info - received ' + str(type(semantic_object)) + " " + \
            # str(type(CSharpClassMethod("",[],[]))) + \
            # str(isinstance(semantic_object, type(CSharpClassMethod("",[],[])))))
        if semantic_object == None:
            # print('parser.py::print_selection_info - received None ')
            return
        if isinstance(semantic_object, csharp_class_parser.CSharpClass) or  \
           isinstance(semantic_object, csharp_class_method_parser.CSharpClassMethod):
            # print('parser.py::print_selection_info - show class_info ' + semantic_object.class_name)
            view_factory.get_showpopup()(semantic_object.print_element_info(), view_factory.get_goto_line())
        else:
            # print('parser.py::print_selection_info - It is not a CSharpClass instance')
            return