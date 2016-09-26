
def is_access_modifier(token):
    return is_public_modifier(token) or is_private_modifier(token) or is_protected_modifier(token)

def is_const_modifier(token):
    return len(token) == 5 and \
        token[0] == 'c' and \
        token[1] == 'o' and \
        token[2] == 'n' and \
        token[3] == 's' and \
        token[4] == 't'

def is_static_modifier(token):
    return len(token) == 6 and \
        token[0] == 's' and \
        token[1] == 't' and \
        token[2] == 'a' and \
        token[3] == 't' and \
        token[4] == 'i' and \
        token[5] == 'c'

def is_public_modifier(token):
    return len(token) == 6 and \
        token[0] == 'p' and \
        token[1] == 'u' and \
        token[2] == 'b' and \
        token[3] == 'l' and \
        token[4] == 'i' and \
        token[5] == 'c'

def is_private_modifier(token):
    return len(token) == 7 and \
        token[0] == 'p' and \
        token[1] == 'r' and \
        token[2] == 'i' and \
        token[3] == 'v' and \
        token[4] == 'a' and \
        token[5] == 't' and \
        token[6] == 'e'

def is_protected_modifier(token):
    return len(token) == 9 and \
        token[0] == 'p' and \
        token[1] == 'r' and \
        token[2] == 'o' and \
        token[3] == 't' and \
        token[4] == 'e' and \
        token[5] == 'c' and \
        token[6] == 't' and \
        token[7] == 'e' and \
        token[8] == 'd'