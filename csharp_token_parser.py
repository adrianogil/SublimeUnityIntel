import os
import fnmatch
from os.path import join

import codecs


class CSharpTokenParser:
    def parse_file(self, csharp_file):
        with codecs.open(csharp_file, encoding="utf-8-sig") as f:
            content = f.readlines()
        total_lines = len(content)

        #tokenize
        tokens = []

        enclosure_position = []
        enclosure_elements = {}
        opposite_enclosure = {'}':'{', ')':'(', ']':'[', '\'':'\'', '\"':'\"' }

        current_token = ''

        inside_string = False
        inside_stream_comments = False
        string_element = ''

        for i in range(0, total_lines):
            line_size = len(content[i])

            for j in range(0, line_size):
                if not inside_stream_comments and self.is_inside_stream_comment(content[i], j):
                    inside_stream_comments = True
                elif inside_stream_comments and self.is_outside_stream_comment(content[i], j):
                    inside_stream_comments = False
                elif inside_stream_comments:
                    continue
                elif inside_string and content[i][j] == string_element:
                    inside_string = False
                    string_element = ''
                    tokens.append(content[i][j])
                elif content[i][j] == "\"" or content[i][j] == "\'":
                    inside_string = True
                    string_element = content[i][j]
                    tokens.append(content[i][j])
                elif not inside_string and self.is_inside_inline_comment(content[i], j):
                    break
                elif self.is_empty(content[i][j]):
                    if current_token != '':
                        tokens.append(current_token)
                        current_token = ''
                elif not inside_string and self.is_special_token(content[i][j]):
                    if current_token != '':
                        tokens.append(current_token)
                        current_token = ''
                    tokens.append("" + content[i][j])
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
                    print('Match ' + tokens[pos] + " and " + tokens[t])

        token_data = { "tokens" : tokens, 'enclosure_position' : enclosure_position}

        return token_data
    def is_empty(self, char_content):
        return char_content == ' ' or char_content == '\n'

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


