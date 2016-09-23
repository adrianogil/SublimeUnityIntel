import os, sys

__file__ = os.path.normpath(os.path.abspath(__file__))
__path__ = os.path.dirname(__file__)

# print(__path__)

if __path__ not in sys.path:
    sys.path.insert(0, __path__)

from csharp_element import CSharpElement

class CSharpImporter(CSharpElement):
    imported_namespace = ""

    def __init__(self, csharp_namespace, tokens):
        super(CSharpImporter, self).__init__('importer', tokens)
        self.imported_namespace = csharp_namespace

def parse_tokens(tokens_data):

    tokens = tokens_data['parsed_tokens']

    parsed_tokens = []

    total_tokens = len(tokens)

    inside_using = False
    current_imported_namespace = ''
    importer_tokens = []

    for t in range(0, total_tokens):
        if not inside_using and is_using_token(tokens[t]):
            inside_using = True
            importer_tokens.append(tokens[t])
        elif not inside_using:
            parsed_tokens.append(tokens[t])
        elif inside_using and tokens[t] == ';':
            inside_using = False
            
            importer_tokens.append(tokens[t])
            
            parsed_tokens.append(CSharpImporter(current_imported_namespace, importer_tokens))

            current_imported_namespace = ''
            importer_tokens = []
        elif inside_using:
            current_imported_namespace = current_imported_namespace + tokens[t]
            importer_tokens.append(tokens[t])

    tokens_data['parsed_tokens'] = parsed_tokens

    return tokens_data

def is_using_token(token):
    return len(token) == 5 and \
        token[0] == 'u' and \
        token[1] == 's' and \
        token[2] == 'i' and \
        token[3] == 'n' and \
        token[4] == 'g'

