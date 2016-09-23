class CSharpElement:
    element_type = ""
    tokens = []
    start_token_position = 0

    def __init__(self, csharp_type, csharp_tokens, token_pos):
        self.element_type = csharp_type
        self.tokens = csharp_tokens
        self.start_token_position = token_pos
