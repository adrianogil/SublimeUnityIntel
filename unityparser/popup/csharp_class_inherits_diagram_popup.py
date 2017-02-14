import subprocess

def print_popup(class_instance, view_factory):
    try:
        view_factory.clear_actions()

        A = class_instance.base_info[0]
        B = class_instance.class_name

        graphviz_cmd = 'python -c \'import graphviz; g1 = graphviz.Graph(format="png"); '
        graphviz_cmd = graphviz_cmd + 'g1.node("' + A + '"); '
        graphviz_cmd = graphviz_cmd + 'g1.node("' + B + '"); '
        graphviz_cmd = graphviz_cmd + 'g1.edge("' + A + '", "' + B + '"); '
        graphviz_cmd = graphviz_cmd + 'print(g1.source); '
        graphviz_cmd = graphviz_cmd + '\' > test.dot && /usr/local/bin/dot -Tpng test.dot -o /Users/SIDIA/tmp_diagram.png'

        graphviz_cmd_output = subprocess.check_output(graphviz_cmd, stderr=subprocess.STDOUT, shell=True)

        print(graphviz_cmd_output)

        # g1 = graphviz.Graph(format='png')
        # g1.node('A')
        # g1.node('B')
        # g1.edge('A', 'B')
        # g1.render(filename='/Users/SIDIA/Library/Application Support/Sublime Text 3/Packages/SublimeUnityIntel/tmp_diagram.png')

        html = '<b>Inheritage Diagram></b><br><img src="file://Users/SIDIA/tmp_diagram.png" style="width:150px;height:200px">'

        view_factory.show_popup(html)
    except subprocess.CalledProcessError as e:
        output = e.output
        returncode = e.returncode
        print(output)
    except:
             print("Unexpected error:" + str(sys.exc_info()[0]))