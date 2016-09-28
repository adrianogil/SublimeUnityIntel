import sys, os
import fnmatch
from os.path import join

import codecs

__file__ = os.path.normpath(os.path.abspath(__file__))
__path__ = os.path.dirname(__file__)

# print(__path__)

if __path__ not in sys.path:
    sys.path.insert(0, __path__)

from csharp_instance import CSharpInstance
import csharp_type

class CSharpTokenParser:
    def parse_file(self, csharp_file):
        with codecs.open(csharp_file, encoding="utf-8-sig") as f:
            content = f.readlines()
        total_lines = len(content)

        #tokenize
        tokens = []
        semantic_tokens = []

        token_position = []

        enclosure_position = []
        enclosure_elements = {}
        opposite_enclosure = {'}':'{', ')':'(', ']':'[', '\'':'\'', '\"':'\"' }

        current_token = ''

        inside_string = False
        inside_stream_comments = False
        string_element = ''

        def add_token(t, pos):
            tokens.append(t)
            semantic_tokens.append(t)
            token_position.append(pos)


        for i in range(0, total_lines):
            line_size = len(content[i])

            for j in range(0, line_size):
                if not inside_string and not inside_stream_comments and self.is_inside_stream_comment(content[i], j):
                    inside_stream_comments = True
                elif inside_stream_comments and self.is_outside_stream_comment(content[i], j):
                    inside_stream_comments = False
                elif inside_stream_comments:
                    continue
                elif inside_string and content[i][j] == string_element:
                    inside_string = False
                    string_element = ''
                    string_instance = CSharpInstance('literal_instance', csharp_type.get_string(), \
                                                     [content[i][j], current_token, content[i][j]], len(tokens)-1)
                    
                    semantic_tokens.append(string_instance)
                    semantic_tokens.append(string_instance)
                    semantic_tokens.append(string_instance)

                    tokens.append(current_token)
                    tokens.append(content[i][j])
                    token_position.append((i,j))
                    token_position.append((i,j))
                    current_token = ''
                elif content[i][j] == "\"" or content[i][j] == "\'":
                    inside_string = True
                    string_element = content[i][j]
                    tokens.append(content[i][j])
                    token_position.append((i,j))
                elif not inside_string and self.is_inside_inline_comment(content[i], j):
                    break
                elif not inside_string and self.is_empty(content[i][j]):
                    if current_token != '':
                        add_token(current_token, (i,j))
                        current_token = ''
                elif not inside_string and self.is_special_token(content[i][j]):
                    if current_token != '':
                        add_token(current_token, (i,j))
                        current_token = ''
                    add_token("" + content[i][j], (i, j))
                else:
                    current_token = current_token + content[i][j]

        total_tokens = len(tokens)

        for t in range(0, total_tokens):

            enclosure_position.append(-1)

            if self.is_opening_element(tokens[t]):
                if tokens[t] in enclosure_elements:
                    list = enclosure_elements[tokens[t]]
                    list.append(t)
                    enclosure_elements[tokens[t]] = list
                else:
                    enclosure_elements[tokens[t]] = [t]
            elif self.is_enclosure_element(tokens[t]):
                if opposite_enclosure[tokens[t]] in enclosure_elements:
                    list = enclosure_elements[opposite_enclosure[tokens[t]]]
                    pos = list.pop()
                    enclosure_elements[opposite_enclosure[tokens[t]]] = list
                    enclosure_position[pos] = t
                    enclosure_position[t] = pos
                    # print('Match ' + tokens[pos] + " and " + tokens[t])

        token_data = { "tokens" : tokens, \
                      'enclosure_position' : enclosure_position, \
                      'semantic_tokens': semantic_tokens, \
                      'token_position': token_position}

        return token_data
    def is_empty(self, char_content):
        return char_content == ' ' or char_content == '\n' or char_content == '\t'

    def is_opening_element(self, char_content):
        return char_content == '{' or \
            char_content == '(' or \
            char_content == '[' or \
            char_content == '\"' or \
            char_content == '\''

    def is_enclosure_element(self, char_content):
        return char_content == '}' or \
            char_content == ')' or \
            char_content == ']"' or \
            char_content == '\"' or \
            char_content == '\''

    def is_special_token(self, char_content):
        return char_content == '.' or \
            char_content == ',' or \
            char_content == '{' or \
            char_content == '}' or \
            char_content == '(' or \
            char_content == ')' or \
            char_content == '#' or \
            char_content == '%' or \
            char_content == '+' or \
            char_content == '-' or \
            char_content == '/' or \
            char_content == '*' or \
            char_content == '<' or \
            char_content == '>' or \
            char_content == ';' or \
            char_content == '\"' or \
            char_content == '\''

    def is_inside_inline_comment(self, line, pos):
        line_size = len(line)
        return pos < line_size-2 and \
            line[pos] == '/' and \
            line[pos+1] == '/'

    def is_inside_stream_comment(self, line, pos):
        line_size = len(line)
        return pos < line_size-2 and \
            line[pos] == '/' and \
            line[pos+1] == '*'

    def is_outside_stream_comment(self, line, pos):
        line_size = len(line)
        return pos > 0 and \
            line[pos-1] == '*' and \
            line[pos] == '/'    


