import sys
import os

import ply.lex
import ply.yacc

class Entity:
    def __init__(self, data):
        self.data = data

    def __str__(self):
        return "{}({})".format(
            ".".join([type(self).__module__, type(self).__qualname__]),
            self.data
        )

    def __repr__(self):
        return str(self)

class Node(Entity):
    pass

class Comment(Entity):
    pass

class Parser:
    def __init__(self, **kwargs):
        self._debug = kwargs.get("debug", False)

        self._text = ""
        self._val_start = 0

        self.tokens = (
            "ID",
            "LCOMMENT",
            "RCOMMENT",
            "COMMENTA",
            "COMMENTB",
            "LQUOTE",
            "RQUOTE",
            "NEWLINE",
            "NEGATE",
            "WHITESPACE",
            "NODE",
            "VALUE",
            "COMMENT",
            "LBRACE", "RBRACE",
            "SYNTAX_ERROR"
        )

        self.lexer = ply.lex.lex(
            module=self,
            debug=self._debug
        )

        self.tokens = (
            "NODE",
            "VALUE",
            "COMMENT",
            "LBRACE", "RBRACE",
            "SYNTAX_ERROR"
        )

        self.parser = ply.yacc.yacc(
            module=self,
            debug=self._debug,
        )


    def parse(self, s):
        return self.parser.parse(s)

    def debug(self, what, p):
        if self._debug:
            print(what + ":", [p[i] for i in range(len(p))])

    states = (
        ("sComment", "exclusive"),
        ("sID", "exclusive"),
        ("sValue", "exclusive"),
        ("sQStr", "exclusive"),
    )

    ID = r"([-\w_]+)"
    SPACE = r"(?!\n)\s"

    def t_LCOMMENT(self, t):
        r"/\*"
        t.lexer.begin("sComment")

    def t_sComment_COMMENTA(self, t):
        r"[^*\n]+"
        self._text = t.value.strip()

    def t_sComment_COMMENTB(self, t):
        r"\*(?!(/))"

    def t_sComment_NEWLINE(self, t):
        r"\n"

    def t_sComment_RCOMMENT(self, t):
        r"\*/"
        t.lexer.begin("INITIAL")
        t.type = "COMMENT"
        t.value = self._text
        return t

    t_NEGATE = r"!"

    @ply.lex.TOKEN("{}+".format(SPACE))
    def t_ANY_WHITESPACE(self, t):
        pass

    def t_NEWLINE(self, t):
        r"\n"
        t.lexer.lineno += len(t.value)

    def t_LBRACE(self, t):
        r"{"
        t.type = "LBRACE"
        return t

    def t_RBRACE(self, t):
        r"}"
        t.type = "RBRACE"
        return t

    @ply.lex.TOKEN(ID)
    def t_ID(self, t):
        t.lexer.begin("sID")
        t.type = "NODE"
        return t

    @ply.lex.TOKEN(r":?(" + SPACE + r")*[^{\n]")
    def t_sID_VALUE(self, t):
        t.lexer.begin("sValue")
        self._val_start = t.lexer.lexpos - 1
        return None

    def t_sID_LBRACE(self, t):
        r"{"
        t.lexer.begin("INITIAL")
        return t

    def t_sID_NEWLINE(self, t):
        r"\n"
        t.lexer.lineno += len(t.value)
        self.lexer.begin("INITIAL")

    def t_sValue_LQUOTE(self, t):
        r'"'
        t.lexer.begin("sQStr")
        return t

    t_sQStr_VALUE = r"[^\"\\\n]+"
    t_sQStr_RQUOTE = r"\\."

    def t_sQStr_NEWLINE(self, t):
        r"\n"

    def t_sQStr_QUOTE(self, t):
        r'"'
        t.lexer.begin("sValue")
        t.type = "VALUE"
        return t

    def t_sValue_VALUE(self, t):
        r'[^{"\s][^{\s]*'
        t.value = t.lexer.lexdata[self._val_start:t.lexer.lexpos]
        t.type = "VALUE"
        return t

    def t_sValue_LBRACE(self, t):
        r"{"
        t.lexer.begin("INITIAL")
        t.type = "LBRACE"
        return t

    def t_sValue_NEWLINE(self, t):
        r"\n"
        t.lexer.lineno += len(t.value)
        self.lexer.begin("INITIAL")

    # Error handling rule
    def t_ANY_error(self, t):
        print("Illegal character '%s'" % t.value[0])
        t.type = "SYNTAX_ERROR"
        return t


    # Parsing rules
    start = "input"

    def p_input(self, p):
        '''input   : forest comment'''

        if p[2]:
            p[0] = ('INPUT', p[1], p[2])
        else:
            p[0] = dict(p[1])

        self.debug("input", p[0])

    def p_forest(self, p):
        '''forest  :'''
        p[0] = []

        self.debug("forest", p)

    def p_forest_tree(self, p):
        '''forest  : forest tree'''

        p[0] = p[1]
        p[0].append(p[2])
        self.debug("forest_tree", p)

    def p_tree(self, p):
        '''tree    : node'''

        p[0] = p[1]
        self.debug("tree", p)

    def p_tree_node(self, p):
        '''tree    : node LBRACE forest comment RBRACE'''

        if p[4]:
            # p[4] is comment
            p[0] = {p[1]: p[3]}
        else:
            p[0] = (p[1], dict(p[3]))

        self.debug("tree_node", p)

    def p_node(self, p):
        '''node    : nodec'''

        p[0] = p[1]

        self.debug("node", p)

    def p_nodec_nodec_VALUE(self, p):
        '''node    : nodec VALUE'''

#        p[0] = (p[1][1], p[2])
         # comment is p[1][1]
        if p[1][0] == 'NODEC':
            p[0] = ('NODEA', (p[1][2], p[2]))
        else:
            p[0] = (p[1], p[2])


        self.debug("node", p)

    def p_nodec_NODE(self, p):
        '''nodec   : NODE'''

        p[0] = p[1]
        self.debug("nodec_NODE", p)

    def p_nodec_COMMENT(self, p):
        '''nodec   : COMMENT comment NODE'''

#        p[0] = (p[1], p[3])
        p[0] = p[3]
        self.debug("nodec_COMMENT", p)


    def p_comment(self, p):
        '''comment : '''
        self.debug("comment", p)

    def p_comment_COMMENT(self, p):
        '''comment : COMMENT comment'''
        p[0] = p[2]
        self.debug("comment_COMMENT", p)

    # Error rule for syntax errors
    def p_error(self, p):
        print("Syntax error in input at {} ({})!".format(p.value, p))
