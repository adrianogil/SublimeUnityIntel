import csharp

def show_view(view_factory, selected_text, rowcol):
    file_data = view_factory.symbolic_parser.get_current_file_data()
    file = view_factory.symbolic_parser.current_file

    semantic_object = view_factory.symbolic_parser.get_semantic_token(file, rowcol, True, True, True, selected_text)
    print('parser.py::print_selection_info - received ' + str(type(semantic_object)) + " ") # + \
        # str(type( csharp.csharp_class_method_parser.CSharpClassMethod("",[],[]))) + \
        # str(isinstance(semantic_object, type( charp.csharp_class_method_parser.CSharpClassMethod("",[],[])))))
    if semantic_object == None:
        # print('parser.py::print_selection_info - received None ')
        return
    if semantic_object.element_type == "class" or semantic_object.element_type == "class-method":
    # //if isinstance(semantic_object, csharp.csharp_class_parser.CSharpClass) or  \
       # isinstance(semantic_object, csharp.csharp_class_method_parser.CSharpClassMethod):
        # print('parser.py::print_selection_info - show class_info ' + semantic_object.class_name)
        semantic_object.print_element_info(view_factory)
        # view_factory.get_showpopup()(semantic_object.print_element_info(), view_factory.get_goto_line())
    else:
        # print('parser.py::print_selection_info - It is not a CSharpClass instance')
        return