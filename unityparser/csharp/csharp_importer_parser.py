import os, sys

__file__ = os.path.normpath(os.path.abspath(__file__))
__path__ = os.path.dirname(__file__)

# print(__path__)

if __path__ not in sys.path:
    sys.path.insert(0, __path__)

from csharp_element import CSharpElement

class CSharpImporter(CSharpElement):
    imported_namespace = ""

    def __init__(self, csharp_namespace, tokens, token_pos):
        super(CSharpImporter, self).__init__('importer', tokens, token_pos)
        self.imported_namespace = csharp_namespace

def parse_tokens(tokens_data):

    tokens = tokens_data['tokens']
    semantic_tokens = tokens_data['semantic_tokens']

    total_tokens = len(tokens)

    inside_using = False
    current_imported_namespace = ''
    importer_tokens = []
    start_using_token_pos = -1

    # print(str(len(tokens)) + ' x ' + str(len(semantic_tokens)))
    # print(tokens)
    # print(semantic_tokens)

    # diff = []

    # for t in range(0, len(semantic_tokens)):
    #     # Can't consider importers inside strings
    #     if semantic_tokens[t] != tokens[t]:
    #          diff.append(str(semantic_tokens[t]) + ' x ' + tokens[t])

    # print(diff)

    for t in range(0, total_tokens):
        # Can't consider importers inside strings
        if isinstance(semantic_tokens[t], CSharpElement):
            continue
        if not inside_using and is_using_token(tokens[t]):
            inside_using = True
            start_using_token_pos = t
            importer_tokens.append(tokens[t])
        elif inside_using and tokens[t] == ';':
            inside_using = False

            importer_tokens.append(tokens[t])
            # print(current_imported_namespace)
            importer_instance = CSharpImporter(current_imported_namespace, importer_tokens, start_using_token_pos)

            for s in range(start_using_token_pos, t+1):
                semantic_tokens[s] = importer_instance

            current_imported_namespace = ''
            start_using_token_pos = -1
            importer_tokens = []
        elif inside_using:
            current_imported_namespace = current_imported_namespace + tokens[t]
            importer_tokens.append(tokens[t])

    tokens_data['semantic_tokens'] = semantic_tokens

    return tokens_data

def is_using_token(token):
    return len(token) == 5 and \
        token[0] == 'u' and \
        token[1] == 's' and \
        token[2] == 'i' and \
        token[3] == 'n' and \
        token[4] == 'g'

