"""# DocBox Format
---
Rather simple file format to generate 2 sided content+note style documentation/web pages from a given template.
;Which means I was lazy.
---
## Different types of content that's allowed
---
*`RAW_HTML` - Any line that starts with `!!` read all lines until another `!!`, whole thing is raw HTML section
**Alternatively line starting with `!!!` is a single line of raw html.
*`HEADER` - Any line that starts with a `#` is `h2`, `##` is `h3`, `###` is `h4`, and so forth until `h6`.
*`BULLET` - Any line that starts with `*` is a bullet point, `**` is a bullet point inside a bullet point
*`SEPARATOR` - if line contains `---` only (otherwise it's a normal line), this separate notes
*`NOTE` - if a line starts with `;` it is a note, which we will add to same cell on right side
*`NOTE_RAW_HTML` - if a line starts with `;!` same as note but in raw HTML
*`CODE` - lines between two triple backticks.
*`DEFAULT` - default lines.
*All lines without RAW HTML content are also treated as markdown.
;I wanted a quick and dirty solution, so this does not show any errors for bad input.
;If all content doesn't show up you probably made a mistake.
---
## Output HTML file format
---
We basically just replace `$TITLE$` with title, `$DESCRIPTION$` with description.
Table of contents are generated from headers and should go to `$TOC$`.
Also, `$STYLES$` is replaced with pygments style.
Each section of the document is written as below.
---
```text
+-----------+-------------+------------+
|           |             |            |
| Table     | Content     |  Note      |
| of        | Part 01     |  Part 01   |
| Contents  |             |            |
|           |             |            |
|           |             |            |
|           +-------------+------------+
|           |             |            |
|           | Content     |  Note      |
|           | Part 02     |  Part 02   |
|           |             |            |
|           |             |            |
+-----------+-------------+------------+
```
;I created this from asciiflow site.
---
##  Template files
---
Template directory should contain following
*`cell.html` - Format of a single content+note cell.
*`main0.html` - HTML before cells.
*`main1.html` - HTML after cells.
;All content goes between `main0.html` and `main1.html`
---
"""
import argparse
import html
import keyword
import os.path
import re
import subprocess
from datetime import datetime
from enum import Enum
from typing import List, Tuple

import markdown
from pygments import highlight
from pygments import unistring as uni
from pygments.formatters.html import HtmlFormatter
from pygments.lexer import include, bygroups, using, \
    default, combined, this
from pygments.lexer import words, RegexLexer
from pygments.lexers import get_lexer_by_name, guess_lexer
from pygments.styles import get_style_by_name
from pygments.token import Keyword, String
from pygments.token import Text, Comment, Operator, Name, Number, Punctuation
from pygments.util import shebang_matches

WEBSITE_DEFAULT_DESC = "Personal website of Bhathiya Perera. I use this as both a micro blog and a place to " \
                       "publish structured articles. I mostly write about software " \
                       "engineering and programming."
WEBSITE_DEFAULT_TITLE = "Bhathiya's Site 😸"
MINIFIER_COMMAND = "html-minifier --collapse-whitespace --remove-comments --remove-optional-tags " \
                   "--remove-redundant-attributes --remove-script-type-attributes " \
                   "--remove-tag-whitespace --use-short-doctype " \
                   "--minify-css true --minify-js true -o \"$OUT$\" \"$OUT$\""
GIT_FILE_HISTORY_DAYS = "git log --follow --pretty=format:\"%ad\" --date=short -- $FILE$"
NEWLINE = '\n'  # Unix newline character
NOT_ALLOWED = re.compile(r"[^a-z\d]")
TWO_OR_MORE_DASHES = re.compile(r"-+")
PYG_STYLE = get_style_by_name('dracula')
PYG_FORMATTER = HtmlFormatter(style=PYG_STYLE)
ALL_HEADER_MAX_WIDTH = 9


class YakshaLexer(RegexLexer):
    name = 'Yaksha'
    aliases = ['yaksha', 'yaka']
    filenames = [
        '*.yaka',
    ]
    mimetypes = ['text/x-yaksha']

    flags = re.MULTILINE | re.UNICODE

    uni_name = "[%s][%s]*" % (uni.xid_start, uni.xid_continue)

    def innerstring_rules(ttype):
        return [
            # the old style '%s' % (...) string formatting (still valid in Py3)
            (r'%(\(\w+\))?[-#0 +]*([0-9]+|[*])?(\.([0-9]+|[*]))?'
             '[hlL]?[E-GXc-giorsaux%]', String.Interpol),
            # the new style '{}'.format(...) string formatting
            (r'\{'
             r'((\w+)((\.\w+)|(\[[^\]]+\]))*)?'  # field name
             r'(\![sra])?'  # conversion
             r'(\:(.?[<>=\^])?[-+ ]?#?0?(\d+)?,?(\.\d+)?[E-GXb-gnosx%]?)?'
             r'\}', String.Interpol),

            # backslashes, quotes and formatting signs must be parsed one at a time
            (r'[^\\\'"%{\n]+', ttype),
            (r'[\'"\\]', ttype),
            # unhandled string formatting sign
            (r'%|(\{{1,2})', ttype)
            # newlines are an error (use "nl" state)
        ]

    def fstring_rules(ttype):
        return [
            # Assuming that a '}' is the closing brace after format specifier.
            # Sadly, this means that we won't detect syntax error. But it's
            # more important to parse correct syntax correctly, than to
            # highlight invalid syntax.
            (r'\}', String.Interpol),
            (r'\{', String.Interpol, 'expr-inside-fstring'),
            # backslashes, quotes and formatting signs must be parsed one at a time
            (r'[^\\\'"{}\n]+', ttype),
            (r'[\'"\\]', ttype),
            # newlines are an error (use "nl" state)
        ]

    tokens = {
        'root': [
            (r'\n', Text),
            (r'^(\s*)([rRuUbB]{,2})("""(?:.|\n)*?""")',
             bygroups(Text, String.Affix, String.Doc)),
            (r"^(\s*)([rRuUbB]{,2})('''(?:.|\n)*?''')",
             bygroups(Text, String.Affix, String.Doc)),
            (r'\A#!.+$', Comment.Hashbang),
            (r'#.*$', Comment.Single),
            (r'\\\n', Text),
            (r'\\', Text),
            include('keywords'),
            include('soft-keywords'),
            (r'(def)((?:\s|\\\s)+)', bygroups(Keyword, Text), 'funcname'),
            (r'(class)((?:\s|\\\s)+)', bygroups(Keyword, Text), 'classname'),
            (r'(struct)((?:\s|\\\s)+)', bygroups(Keyword, Text), 'classname'),
            (r'(from)((?:\s|\\\s)+)', bygroups(Keyword.Namespace, Text),
             'fromimport'),
            (r'(import)((?:\s|\\\s)+)', bygroups(Keyword.Namespace, Text),
             'import'),
            include('expr'),
        ],
        'expr': [
            # raw f-strings
            ('(?i)(rf|fr)(""")',
             bygroups(String.Affix, String.Double),
             combined('rfstringescape', 'tdqf')),
            ("(?i)(rf|fr)(''')",
             bygroups(String.Affix, String.Single),
             combined('rfstringescape', 'tsqf')),
            ('(?i)(rf|fr)(")',
             bygroups(String.Affix, String.Double),
             combined('rfstringescape', 'dqf')),
            ("(?i)(rf|fr)(')",
             bygroups(String.Affix, String.Single),
             combined('rfstringescape', 'sqf')),
            # non-raw f-strings
            ('([fF])(""")', bygroups(String.Affix, String.Double),
             combined('fstringescape', 'tdqf')),
            ("([fF])(''')", bygroups(String.Affix, String.Single),
             combined('fstringescape', 'tsqf')),
            ('([fF])(")', bygroups(String.Affix, String.Double),
             combined('fstringescape', 'dqf')),
            ("([fF])(')", bygroups(String.Affix, String.Single),
             combined('fstringescape', 'sqf')),
            # raw strings
            ('(?i)(rb|br|r)(""")',
             bygroups(String.Affix, String.Double), 'tdqs'),
            ("(?i)(rb|br|r)(''')",
             bygroups(String.Affix, String.Single), 'tsqs'),
            ('(?i)(rb|br|r)(")',
             bygroups(String.Affix, String.Double), 'dqs'),
            ("(?i)(rb|br|r)(')",
             bygroups(String.Affix, String.Single), 'sqs'),
            # non-raw strings
            ('([uUbB]?)(""")', bygroups(String.Affix, String.Double),
             combined('stringescape', 'tdqs')),
            ("([uUbB]?)(''')", bygroups(String.Affix, String.Single),
             combined('stringescape', 'tsqs')),
            ('([uUbB]?)(")', bygroups(String.Affix, String.Double),
             combined('stringescape', 'dqs')),
            ("([uUbB]?)(')", bygroups(String.Affix, String.Single),
             combined('stringescape', 'sqs')),
            (r'[^\S\n]+', Text),
            include('numbers'),
            (r'!=|==|<<|>>|:=|[-~+/*%=<>&^|.!]', Operator),
            (r'[]{}:(),;[]', Punctuation),
            (r'(in|is|and|or|not)\b', Operator.Word),
            include('expr-keywords'),
            include('builtins'),
            include('magicfuncs'),
            include('magicvars'),
            include('name'),
        ],
        'expr-inside-fstring': [
            (r'[{([]', Punctuation, 'expr-inside-fstring-inner'),
            # without format specifier
            (r'(=\s*)?'  # debug (https://bugs.python.org/issue36817)
             r'(\![sraf])?'  # conversion
             r'\}', String.Interpol, '#pop'),
            # with format specifier
            # we'll catch the remaining '}' in the outer scope
            (r'(=\s*)?'  # debug (https://bugs.python.org/issue36817)
             r'(\![sraf])?'  # conversion
             r':', String.Interpol, '#pop'),
            (r'\s+', Text),  # allow new lines
            include('expr'),
        ],
        'expr-inside-fstring-inner': [
            (r'[{([]', Punctuation, 'expr-inside-fstring-inner'),
            (r'[])}]', Punctuation, '#pop'),
            (r'\s+', Text),  # allow new lines
            include('expr'),
        ],
        'expr-keywords': [
            # Based on https://docs.python.org/3/reference/expressions.html
            (words((
                'async for', 'await', 'else', 'for', 'if', 'lambda',
                'yield', 'yield from'), suffix=r'\b'),
             Keyword),
            (words(('True', 'False', 'None'), suffix=r'\b'), Keyword.Constant),
        ],
        'keywords': [
            (words((
                'assert', 'async', 'await', 'break', 'continue', 'del', 'elif',
                'else', 'except', 'finally', 'for', 'global', 'if', 'lambda',
                'pass', 'raise', 'nonlocal', 'return', 'try', 'while', 'yield',
                'defer', '@native', '@template', '@device', '@nativedefine', '@nativemacro', '@dotaccess', 'ccode',
                'yield from', 'as', 'with', 'macros'), suffix=r'\b'),
             Keyword),
            (words(('True', 'False', 'None'), suffix=r'\b'), Keyword.Constant),
        ],
        'soft-keywords': [
            # `match`, `case` and `_` soft keywords
            (r'(^[ \t]*)'  # at beginning of line + possible indentation
             r'(match|case)\b'  # a possible keyword
             r'(?![ \t]*(?:'  # not followed by...
             r'[:,;=^&|@~)\]}]|(?:' +  # characters and keywords that mean this isn't
             r'|'.join(keyword.kwlist) + r')\b))',  # pattern matching
             bygroups(Text, Keyword), 'soft-keywords-inner'),
        ],
        'soft-keywords-inner': [
            # optional `_` keyword
            (r'(\s+)([^\n_]*)(_\b)', bygroups(Text, using(this), Keyword)),
            default('#pop')
        ],
        'builtins': [
            (words((
                'bool', 'float', 'f32', 'f64', 'int', 'i32', 'u32', 'i8', 'u8', 'i16', 'u16', 'i64', 'u64', 'str',
                'len', 'print', 'println',
                'sizeof', 'format', 'reversed', 'sorted', 'charat',
                'getref', 'unref',
                'arrput', 'arrpop',
                'shget', 'shgeti', 'shput', 'shnew',
                'hmget', 'hmgeti', 'hmput', 'hmnew',
                'Array', 'SMEntry', 'MEntry', 'Ptr', 'Const', 'PtrConst', 'Function', 'Input', 'Output'),
                prefix=r'(?<!\.)', suffix=r'\b'),
             Name.Builtin),
            (r'(?<!\.)(self|Ellipsis|NotImplemented|cls)\b', Name.Builtin.Pseudo),
            (words((
                'ArithmeticError', 'AssertionError', 'AttributeError',
                'BaseException', 'BufferError', 'BytesWarning', 'DeprecationWarning',
                'EOFError', 'EnvironmentError', 'Exception', 'FloatingPointError',
                'FutureWarning', 'GeneratorExit', 'IOError', 'ImportError',
                'ImportWarning', 'IndentationError', 'IndexError', 'KeyError',
                'KeyboardInterrupt', 'LookupError', 'MemoryError', 'NameError',
                'NotImplementedError', 'OSError', 'OverflowError',
                'PendingDeprecationWarning', 'ReferenceError', 'ResourceWarning',
                'RuntimeError', 'RuntimeWarning', 'StopIteration',
                'SyntaxError', 'SyntaxWarning', 'SystemError', 'SystemExit',
                'TabError', 'TypeError', 'UnboundLocalError', 'UnicodeDecodeError',
                'UnicodeEncodeError', 'UnicodeError', 'UnicodeTranslateError',
                'UnicodeWarning', 'UserWarning', 'ValueError', 'VMSError',
                'Warning', 'WindowsError', 'ZeroDivisionError',
                # new builtin exceptions from PEP 3151
                'BlockingIOError', 'ChildProcessError', 'ConnectionError',
                'BrokenPipeError', 'ConnectionAbortedError', 'ConnectionRefusedError',
                'ConnectionResetError', 'FileExistsError', 'FileNotFoundError',
                'InterruptedError', 'IsADirectoryError', 'NotADirectoryError',
                'PermissionError', 'ProcessLookupError', 'TimeoutError',
                # others new in Python 3
                'StopAsyncIteration', 'ModuleNotFoundError', 'RecursionError'),
                prefix=r'(?<!\.)', suffix=r'\b'),
             Name.Exception),
        ],
        'magicfuncs': [
            (words((
                '__abs__', '__add__', '__aenter__', '__aexit__', '__aiter__',
                '__and__', '__anext__', '__await__', '__bool__', '__bytes__',
                '__call__', '__complex__', '__contains__', '__del__', '__delattr__',
                '__delete__', '__delitem__', '__dir__', '__divmod__', '__enter__',
                '__eq__', '__exit__', '__float__', '__floordiv__', '__format__',
                '__ge__', '__get__', '__getattr__', '__getattribute__',
                '__getitem__', '__gt__', '__hash__', '__iadd__', '__iand__',
                '__ifloordiv__', '__ilshift__', '__imatmul__', '__imod__',
                '__imul__', '__index__', '__init__', '__instancecheck__',
                '__int__', '__invert__', '__ior__', '__ipow__', '__irshift__',
                '__isub__', '__iter__', '__itruediv__', '__ixor__', '__le__',
                '__len__', '__length_hint__', '__lshift__', '__lt__', '__matmul__',
                '__missing__', '__mod__', '__mul__', '__ne__', '__neg__',
                '__new__', '__next__', '__or__', '__pos__', '__pow__',
                '__prepare__', '__radd__', '__rand__', '__rdivmod__', '__repr__',
                '__reversed__', '__rfloordiv__', '__rlshift__', '__rmatmul__',
                '__rmod__', '__rmul__', '__ror__', '__round__', '__rpow__',
                '__rrshift__', '__rshift__', '__rsub__', '__rtruediv__',
                '__rxor__', '__set__', '__setattr__', '__setitem__', '__str__',
                '__sub__', '__subclasscheck__', '__truediv__',
                '__xor__'), suffix=r'\b'),
             Name.Function.Magic),
        ],
        'magicvars': [
            (words((
                '__annotations__', '__bases__', '__class__', '__closure__',
                '__code__', '__defaults__', '__dict__', '__doc__', '__file__',
                '__func__', '__globals__', '__kwdefaults__', '__module__',
                '__mro__', '__name__', '__objclass__', '__qualname__',
                '__self__', '__slots__', '__weakref__'), suffix=r'\b'),
             Name.Variable.Magic),
        ],
        'numbers': [
            (r'(\d(?:_?\d)*\.(?:\d(?:_?\d)*)?f?|(?:\d(?:_?\d)*)?\.\d(?:_?\d)*)'
             r'([eE][+-]?\d(?:_?\d)*)?f?', Number.Float),
            (r'\d(?:_?\d)*[eE][+-]?\d(?:_?\d)*j?f?', Number.Float),
            (r'0[oO](?:_?[0-7])+', Number.Oct),
            (r'0[bB](?:_?[01])+', Number.Bin),
            (r'0[xX](?:_?[a-fA-F0-9])+', Number.Hex),
            (r'\d(?:_?\d)*([iu](8|16|32|64))?', Number.Integer),
        ],
        'name': [
            (r'@' + uni_name, Name.Decorator),
            (r'@', Operator),  # new matrix multiplication operator
            (uni_name, Name),
        ],
        'funcname': [
            include('magicfuncs'),
            (uni_name, Name.Function, '#pop'),
            default('#pop'),
        ],
        'classname': [
            (uni_name, Name.Class, '#pop'),
        ],
        'import': [
            (r'(\s+)(as)(\s+)', bygroups(Text, Keyword, Text)),
            (r'\.', Name.Namespace),
            (uni_name, Name.Namespace),
            (r'(\s*)(,)(\s*)', bygroups(Text, Operator, Text)),
            default('#pop')  # all else: go back
        ],
        'fromimport': [
            (r'(\s+)(import)\b', bygroups(Text, Keyword.Namespace), '#pop'),
            (r'\.', Name.Namespace),
            # if None occurs here, it's "raise x from None", since None can
            # never be a module name
            (r'None\b', Name.Builtin.Pseudo, '#pop'),
            (uni_name, Name.Namespace),
            default('#pop'),
        ],
        'rfstringescape': [
            (r'\{\{', String.Escape),
            (r'\}\}', String.Escape),
        ],
        'fstringescape': [
            include('rfstringescape'),
            include('stringescape'),
        ],
        'stringescape': [
            (r'\\([\\abfnrtv"\']|\n|N\{.*?\}|u[a-fA-F0-9]{4}|'
             r'U[a-fA-F0-9]{8}|x[a-fA-F0-9]{2}|[0-7]{1,3})', String.Escape)
        ],
        'fstrings-single': fstring_rules(String.Single),
        'fstrings-double': fstring_rules(String.Double),
        'strings-single': innerstring_rules(String.Single),
        'strings-double': innerstring_rules(String.Double),
        'dqf': [
            (r'"', String.Double, '#pop'),
            (r'\\\\|\\"|\\\n', String.Escape),  # included here for raw strings
            include('fstrings-double')
        ],
        'sqf': [
            (r"'", String.Single, '#pop'),
            (r"\\\\|\\'|\\\n", String.Escape),  # included here for raw strings
            include('fstrings-single')
        ],
        'dqs': [
            (r'"', String.Double, '#pop'),
            (r'\\\\|\\"|\\\n', String.Escape),  # included here for raw strings
            include('strings-double')
        ],
        'sqs': [
            (r"'", String.Single, '#pop'),
            (r"\\\\|\\'|\\\n", String.Escape),  # included here for raw strings
            include('strings-single')
        ],
        'tdqf': [
            (r'"""', String.Double, '#pop'),
            include('fstrings-double'),
            (r'\n', String.Double)
        ],
        'tsqf': [
            (r"'''", String.Single, '#pop'),
            include('fstrings-single'),
            (r'\n', String.Single)
        ],
        'tdqs': [
            (r'"""', String.Double, '#pop'),
            include('strings-double'),
            (r'\n', String.Double)
        ],
        'tsqs': [
            (r"'''", String.Single, '#pop'),
            include('strings-single'),
            (r'\n', String.Single)
        ],
    }

    def analyse_text(text):
        return shebang_matches(text, r'pythonw?(3(\.\d)?)?') or \
            'import ' in text[:1000]


def pyg_highlight(code: str, lexer: str) -> str:
    if lexer == "yaksha":
        lex = YakshaLexer()
    elif lexer:
        lex = get_lexer_by_name(lexer)
    else:
        lex = guess_lexer(code)
    return highlight(code, lex, PYG_FORMATTER)


class IdGen:
    def __init__(self):
        self._unique = set()

    def reset(self):
        self._unique = set()

    def generate(self, text: str):
        counter = 1
        result = TWO_OR_MORE_DASHES.sub("-", NOT_ALLOWED.sub("-", text.lower())).strip("-")
        if result and result not in self._unique:
            return result
        new_result = result + str(counter)
        while new_result in self._unique:
            counter += 1
            new_result = result + str(counter)
        return new_result


class TitleNumGen:
    def __init__(self):
        self._prev_level = -1
        self._counters = []

    def reset(self):
        self._prev_level = -1
        self._counters = []

    def generate(self, level):
        if level == 1:
            if self._counters:
                self._counters = self._counters[:1]
            else:
                self._counters = [0]
        elif self._prev_level < level:
            for _ in range(level - self._prev_level):
                self._counters.append(0)
        elif self._prev_level > level:
            for _ in range(self._prev_level - level):
                self._counters.pop()

        self._counters[-1] = self._counters[-1] + 1
        self._prev_level = level
        return self._conv()

    def _conv(self):
        return ".".join([str(x) for x in self._counters]) + " "


class NullNumGen:
    def generate(self, _):
        return ""

    def reset(self):
        pass


# NOTE: All token type data should be html escaped see --> https://docs.python.org/3/library/html.html
# however, RAW_HTML & NOTE_RAW_HTML is written as it is
class TokenType(Enum):
    """
    Token types
    """
    RAW_HTML = 1  # Any line that starts with `!!` read all lines until another `!!`, whole thing is raw HTML section
    # Alternatively line starting with !!! is a single line of raw html.
    HEADER = 2  # Any line that starts with a `#` is <h1>, `##` is h2, `###` is h3, and so forth until h6.
    BULLET = 3  # Any line that starts with `*` is a bullet point, `**` is a bullet point inside a bullet point
    SEPARATOR = 4  # if line contains `---` only (otherwise it's a normal line), this separate notes
    NOTE = 5  # if a line starts with `;` it is a note, which we will add to same cell on right side
    NOTE_RAW_HTML = 6  # if a line starts with `;!` same as note but in raw HTML
    CODE = 7  # lines between two ```
    DEFAULT = 10  # Normal line


class Token:
    def __init__(self, token_type_: TokenType, data_: str, raw_data_: str, level_: int = 0):
        """
        Create a token object
        :param token_type_: type of the token
        :param data_: data for the token
        :param raw_data_: un processed data
        :param level_: level used for header and bullets (* is 1, ** is 2, # is 1 and ## is two)
        """
        self.token_type: TokenType = token_type_
        self.data: str = data_
        self.raw_data: str = raw_data_
        self.level: int = level_
        self.header_id: str = ""
        self.header_num: str = ""
        self.header_indent: str = ""


def count_and_strip(text: str, char: str) -> (int, str):
    output = []
    count = 0
    counting = True
    for x in text:
        if counting and x == char:
            count += 1
            continue
        counting = False
        output.append(x)
    return count, "".join(output)


class DocBoxFile:
    """
    A DocBox file object
    * This reads and breaks a file to tokens that HtmlConverter can write as HTML
    """

    def __init__(self, file_path: str, num_gen, id_gen, text: str = "", md: bool = False):
        self.file_path = file_path
        self._num_gen = num_gen
        self._id_gen = id_gen
        self._text = text
        self.limit = -1
        self.read_more = ""
        self._markdown_mode = md

    def _get_lines(self):
        if self._markdown_mode:
            yield "---"
        if self._text:
            for line in self._text.splitlines():
                yield line
        else:
            with open(self.file_path, "r+", encoding="utf-8") as f:
                for line in f:
                    yield line
        if self._markdown_mode:
            yield "---"

    def parse(self) -> List[Token]:
        tokens: List[Token] = []
        mode = "any"
        html_lines = []
        code_lines = []
        possible_type = "python"
        sections = 0
        for line in self._get_lines():
            if 0 < self.limit <= sections:
                read_more = '<a class="read-more" href="{}">Read More</a>'.format(self.read_more)
                tokens.append(Token(TokenType.SEPARATOR, "", ""))
                tokens.append(Token(TokenType.RAW_HTML, read_more, read_more))
                tokens.append(Token(TokenType.SEPARATOR, "", ""))
                break
            # remove all spaces from left side of the line
            # as we do ignore those
            stripped_line = line.lstrip()
            if mode != "code" and not stripped_line:
                continue
            if mode == "html":
                if stripped_line.startswith("!!"):
                    tokens.append(Token(TokenType.RAW_HTML, NEWLINE.join(html_lines), NEWLINE.join(html_lines)))
                    mode = "any"
                    continue
                html_lines.append(stripped_line)
            elif mode == "code":
                if stripped_line.startswith("```"):
                    code = NEWLINE.join(code_lines)
                    tokens.append(Token(TokenType.RAW_HTML, pyg_highlight(code, possible_type), code))
                    mode = "any"
                    possible_type = "python"
                    continue
                code_lines.append(line.rstrip())
            elif stripped_line.startswith("*"):
                level, text = count_and_strip(stripped_line, "*")
                tokens.append(Token(TokenType.BULLET, markdown.markdown(text), text, level))
            elif stripped_line.startswith("#"):
                level, text = count_and_strip(stripped_line, "#")
                num = self._num_gen.generate(level)
                id_ = self._id_gen.generate(text)
                # Title just uses HTML escape, no need for fancy markdown for titles
                token = Token(TokenType.HEADER, html.escape(text), text, level)
                token.header_id = id_
                token.header_num = num
                token.header_indent = "&nbsp;" * ((len(num) // 2) - 1)
                tokens.append(token)
            elif stripped_line.startswith(";!"):
                tokens.append(Token(TokenType.NOTE_RAW_HTML, stripped_line[2:], stripped_line[2:]))
            elif stripped_line.startswith(";"):
                tokens.append(
                    Token(TokenType.NOTE, markdown.markdown((stripped_line[1:])), stripped_line[1:]))
            elif stripped_line.startswith("!!!"):
                tokens.append(Token(TokenType.RAW_HTML, stripped_line[3:], stripped_line[3:]))
            elif stripped_line.startswith("!!"):
                mode = "html"  # TokenType.RAW_HTML
                html_lines = []  # this clears our temporary buffer
            elif stripped_line.startswith("```"):
                mode = "code"
                if len(stripped_line) > 3:
                    type_ = stripped_line[3:].strip().lower()
                    if type_:
                        possible_type = type_
                code_lines = []
            elif stripped_line.rstrip() == "---":
                tokens.append(Token(TokenType.SEPARATOR, "", ""))
                sections += 1
            else:
                tokens.append(
                    Token(TokenType.DEFAULT, markdown.markdown((stripped_line)), stripped_line))

        return tokens

    def extract_created_last_mod(self) -> Tuple[str, str]:
        cmd = GIT_FILE_HISTORY_DAYS.replace("$FILE$", self.file_path)
        text = subprocess.check_output(cmd, shell=True, universal_newlines=True)
        days = text.splitlines()
        if not days:
            today_str = datetime.now().strftime("%Y-%m-%d")
            return today_str, today_str
        # Return created and last modified days
        if len(days) > 1:
            return days[-1], days[0]
        return days[0], days[0]


class Cell:
    def __init__(self, content_: str, note_: str):
        """
        Constructor for cell object
        :param content_: content html
        :param note_: note html
        """
        self.content = content_
        self.note = note_


class HtmlConverter:
    def __init__(self, files: List[DocBoxFile], target: str, template_cell: str, template_start: str,
                 template_end: str, minifier_command: str, title: str, desc: str, all_headers: bool,
                 include_meta_after_first_header=True):
        """
        Html Converter - convert set of docbox files to a single html
        :param files: list of DocBoxFile objects
        :param target: target file
        :param template_cell: how a single cell is converted to HTML
        :param template_start: start of template before we put all cells in target
        :param template_end: end of template
        :param minifier_command: shell command to minify html
        :param title: html title
        :param desc: html description
        :param all_headers: All headers in ToC?
        :param include_meta_after_first_header: include meta data such as created time after first header
        """
        self._files = files
        self._target = target
        with open(template_cell, "r+", encoding="utf-8") as h:
            self._cell_template = h.read()
        with open(template_start, "r+", encoding="utf-8") as h:
            self._main_template0 = h.read()
        with open(template_end, "r+", encoding="utf-8") as h:
            self._main_template1 = h.read()
        self._minifier_command = minifier_command
        self._title = title
        self._desc = desc
        self._all_headers = all_headers
        self._toc = ""
        self._include_meta_after_first_header = include_meta_after_first_header

    def convert(self):
        """
        Capture tokens to cells with content and notes
        write cells to html format
        """
        cells: List[Cell] = []
        content: List[str] = []
        note: List[str] = []
        toc: List[str] = []
        prev_bullet = -1
        doc_file = None
        possible_first_header = True
        for section, doc in self._get_sections():
            if doc_file != doc.file_path:
                doc_file = doc.file_path
                possible_first_header = True
            if section.token_type == TokenType.BULLET:
                # depend on level place bullet points
                # see below example
                #
                # [[input]]
                #
                # * banana 1
                # * banana 2
                # ** this is a special banana
                # ** very special indeed
                # * banana 3
                # * banana 4
                #
                # [[output]]
                #
                # <ul>
                # <li>banana 1</li>
                # <li>banana 2
                #     <ul>
                #         <li>this is a special banana</li>
                #         <li>very special indeed</li>
                #     </ul>
                # </li>
                # <li>banana 3</li>
                # <li>banana 4</li>
                # </ul>
                #
                if prev_bullet == -1:
                    content.append("<ul>")
                elif prev_bullet > section.level:
                    content.append("</ul>")
                elif prev_bullet < section.level:
                    content.append("<ul>")
                else:
                    content.append("</li>")
                content.append("<li>{0}".format(section.data))
                prev_bullet = section.level
            else:
                if prev_bullet != -1:
                    content.append("</li></ul>")
                prev_bullet = -1
                if section.token_type == TokenType.NOTE or section.token_type == TokenType.NOTE_RAW_HTML:
                    note.append(section.data)
                elif section.token_type == TokenType.RAW_HTML:
                    content.append(section.data)
                elif section.token_type == TokenType.HEADER:
                    if self._all_headers or section.level == 1:
                        if len(section.header_num) <= ALL_HEADER_MAX_WIDTH:
                            toc.append(
                                "<div class=\"toc-item\"><a href=\"#{id_}\">{indent}{title}</a></div>".format(
                                    id_=section.header_id,
                                    title=section.data, indent=section.header_indent))
                    content.append(
                        "<h{level} id=\"{id_}\">{num}{title}</h{level}>".format(id_=section.header_id,
                                                                                title=section.data,
                                                                                level=section.level + 1,
                                                                                num=section.header_num))
                    if self._include_meta_after_first_header and possible_first_header:
                        created_dt, last_mod_dt = doc.extract_created_last_mod()
                        content.append(
                            "<span class=\"timestamp\">Created {}, Last Updated {}</span>".format(
                                created_dt, last_mod_dt)
                        )
                    possible_first_header = False
                elif section.token_type == TokenType.SEPARATOR:
                    # You can create a cell now with acquired content and note stuffs
                    cells.append(Cell(NEWLINE.join(content), NEWLINE.join(note)))
                    content = []
                    note = []
                else:  # SectionType.DEFAULT
                    content.append(section.data)
        self._toc = NEWLINE.join(toc)
        self._write_html(cells)

    def _write_html(self, cells: List[Cell]):
        with open(self._target, "w+", encoding="utf-8") as h:
            h.write(self._fill_main_template(self._main_template0))
            for cell in self._put_cell_in_template(cells):
                h.write(cell)
            h.write(self._fill_main_template(self._main_template1))
        subprocess.run(self._minifier_command, shell=True, check=True)

    def _fill_main_template(self, template_text: str):
        return template_text.replace("$TITLE$", self._title) \
            .replace("$DESCRIPTION$", self._desc).replace("$TOC$", self._toc) \
            .replace("$STYLES$", PYG_FORMATTER.get_style_defs('.highlight'))

    def _put_cell_in_template(self, cells):
        for cell in cells:
            yield self._cell_template.replace("$CONTENT$", cell.content) \
                .replace("$NOTE$", cell.note)

    def _get_sections(self):
        for doc in self._files:
            for section in doc.parse():
                yield section, doc
            yield Token(TokenType.RAW_HTML, "<hr />", "<hr />"), doc
            yield Token(TokenType.NOTE_RAW_HTML, "<hr />", "<hr />"), doc


DOC_BOX_ROOT = os.path.dirname(os.path.abspath(__file__))


class DocBoxApp:
    def __init__(self, root=DOC_BOX_ROOT):
        self._root = root
        self._input_dir = os.path.join(self._root, "posts")
        self._template_root = os.path.join(self._root, "template")
        self._template_cell = os.path.join(self._template_root, "cell.html")
        self._template_main0 = os.path.join(self._template_root, "main0.html")
        self._template_main1 = os.path.join(self._template_root, "main1.html")
        self._output_file = os.path.join(self._root, "docs", "index.html")
        self._title = html.escape(WEBSITE_DEFAULT_TITLE)
        self._desc = html.escape(WEBSITE_DEFAULT_DESC)
        self._minifier_command = MINIFIER_COMMAND
        self._id_gen = IdGen()
        self._num_gen = TitleNumGen()

    def convert(self, arguments):
        parsed_args = self._parse_arguments(arguments)
        self._use_args(parsed_args)
        if parsed_args.posts:
            self._convert_posts(parsed_args.r, parsed_args.allheaders, parsed_args.posts)
        else:
            self._convert(parsed_args.r, parsed_args.allheaders)

    def convert_text(self, arguments, single_file_text: str):
        parsed_args = self._parse_arguments(arguments)
        self._use_args(parsed_args)
        doc_objects = [DocBoxFile("-", self._num_gen, self._id_gen, text=single_file_text, md=self._use_markdown_files)]
        HtmlConverter(doc_objects, self._output_file, self._template_cell,
                      self._template_main0, self._template_main1,
                      self._minifier_command, self._title, self._desc, parsed_args.allheaders).convert()

    def _parse_arguments(self, arguments):
        parser = argparse.ArgumentParser("docbox", description="Docbox HTML Generator")
        parser.add_argument("-o,--output", dest="out", type=str, default=self._output_file, help="Output file")
        parser.add_argument("--input", dest="inp", type=str, default=self._input_dir, help="Input dir")
        parser.add_argument("--template", dest="template", type=str, default=self._template_root,
                            help="Use a different template directory")
        parser.add_argument("--title", dest="title", type=str, default=WEBSITE_DEFAULT_TITLE, help="Set a title")
        parser.add_argument("--desc", dest="desc", type=str, default=WEBSITE_DEFAULT_DESC, help="Set a description")
        parser.add_argument("-r,--reverse", dest="r", default=False, action="store_true",
                            help="Create output using input files in reverse order")
        parser.add_argument("--no-number", dest="nonum", default=False, action="store_true",
                            help="Do not put numbers in titles")
        parser.add_argument("--all-headers-in-toc", dest="allheaders", default=False, action="store_true",
                            help="Include all levels of headers in ToC and not just level 1 headers")
        parser.add_argument("--posts", dest="posts", default=None, type=str, help="Use posts mode.")
        parser.add_argument("--md", dest="md", default=False, action="store_true", help="Use .md files instead of .docbox files")
        if arguments:
            result = parser.parse_args(arguments)
        else:
            result = parser.parse_args()
        return result

    def _use_args(self, result):
        self._input_dir = result.inp
        self._output_file = result.out
        self._minifier_command = MINIFIER_COMMAND.replace("$OUT$", self._output_file)
        self._title = html.escape(result.title)
        self._desc = html.escape(result.title)
        self._template_root = result.template
        if result.nonum:
            self._num_gen = NullNumGen()
        self._template_cell = os.path.join(self._template_root, "cell.html")
        self._template_main0 = os.path.join(self._template_root, "main0.html")
        self._template_main1 = os.path.join(self._template_root, "main1.html")
        self._id_gen.reset()
        self._num_gen.reset()
        self._use_markdown_files = result.md

    def _convert(self, reversed_=False, all_headers=False):
        doc_objects = self._get_docs(reversed_)
        HtmlConverter(doc_objects, self._output_file, self._template_cell,
                      self._template_main0, self._template_main1,
                      self._minifier_command, self._title, self._desc, all_headers).convert()

    def _convert_posts(self, reversed_=False, all_headers=False, posts: str = "posts"):
        doc_objects = self._get_docs(reversed_)
        # Limit posts to just 2 sections
        for d in doc_objects:
            d.limit = 2
            if self._use_markdown_files:
                d.read_more = os.path.join(posts, os.path.basename(d.file_path)[5:].replace(".md", ".html"))
            else:
                d.read_more = os.path.join(posts, os.path.basename(d.file_path)[5:].replace(".docbox", ".html"))
            d.read_more = d.read_more.replace("\\", "/")
        parent_dir = os.path.dirname(self._output_file)
        HtmlConverter(doc_objects, self._output_file, self._template_cell,
                      self._template_main0, self._template_main1,
                      self._minifier_command, self._title, self._desc, all_headers).convert()
        for d in doc_objects:
            d.limit = -1
            target = os.path.join(parent_dir, d.read_more)
            self._id_gen.reset()
            self._num_gen.reset()
            HtmlConverter([d], target, self._template_cell,
                          self._template_main0, self._template_main1,
                          MINIFIER_COMMAND.replace("$OUT$", target),
                          self._title, self._desc, all_headers=True).convert()

    def _get_docs(self, reversed_):
        if self._use_markdown_files:
            ext = ".md"
        else:
            ext = ".docbox"
        docs = [x for x in os.listdir(self._input_dir) if x.endswith(ext)]
        if reversed_:
            docs = sorted(docs, key=lambda x: -int(x[:4]))
        else:
            docs = sorted(docs, key=lambda x: int(x[:4]))
        docs = [os.path.join(self._input_dir, x) for x in docs]
        doc_objects = [DocBoxFile(x, self._num_gen, self._id_gen, md=self._use_markdown_files) for x in docs]
        return doc_objects


def conv(arguments=None, root=DOC_BOX_ROOT):
    DocBoxApp(root).convert(arguments)


if __name__ == '__main__':
    conv()
