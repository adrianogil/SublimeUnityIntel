class CSharpElement:

    def __init__(self, csharp_type, csharp_tokens, token_pos):
        self.element_type = csharp_type
        self.tokens = csharp_tokens
        self.start_token_position = token_pos
        self.line_in_file = 1
