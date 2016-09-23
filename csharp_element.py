class CSharpElement:
    element_type = ""
    tokens = []

    def __init__(self, csharp_type, csharp_tokens):
        self.element_type = csharp_type
        self.tokens = csharp_tokens
