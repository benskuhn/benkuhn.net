from django import template
import markdown
import md5, re
from markdown.treeprocessors import Treeprocessor
from markdown.inlinepatterns import Pattern
from markdown.extensions import Extension

register = template.Library()

class Nofollow(Extension):
    def extendMarkdown(self, md, md_globals):
        # Insert instance of 'mypattern' before 'references' pattern
        md.treeprocessors['nofollow'] = Cleaner()

class Cleaner(Treeprocessor):
    def run(self, root):
        for a in root.findall('.//a'):
            a.attrib['rel'] = 'nofollow'

class Texer(Extension):
    def extendMarkdown(self, md, md_globals):
        md.inlinePatterns['inlineMath'] = InlineMath(md)

class InlineMath(Pattern):
    def __init__(self, markdown):
        Pattern.__init__(self, r'((?P<display>\$\$[^\s](.*?[^\s])??\$\$)|\$(?P<inline>[^\s](.*?[^\s])??)\$(?=[^\d]|$))', markdown_instance=markdown)
    def handleMatch(self, m):
        if m.group('inline'):
            return r'\(' + self.unescape(m.group('inline')).replace("\0292\03", '\\\\\\\\') + r'\)'
        else:
            return self.unescape(m.group('display')).replace("\0292\03", '\\\\\\\\')

@register.tag(name='markdown')
def do_markdown(parser, token):
    nodelist = parser.parse(('endmarkdown',))
    parser.delete_first_token()
    return MarkdownNode(nodelist, safe=False)

@register.tag(name='usermarkdown')
def do_markdown(parser, token):
    nodelist = parser.parse(('endusermarkdown',))
    parser.delete_first_token()
    return MarkdownNode(nodelist, safe=True)

@register.filter(name='gravatar')
def gravatar(string):
    param = md5.md5(string).hexdigest()
    return 'http://www.gravatar.com/avatar/' + param

stripper = re.compile(r'<.*?>')
@register.filter(name='stripmd')
def stripmd(string):
    tmp = unsafe_parser.reset().convert(string)
    return stripper.sub('', tmp)

unsafe_parser = markdown.Markdown(extensions=[Texer(), 'footnotes', 'smartypants'])
safe_parser = markdown.Markdown(safe_mode='escape', extensions=['smartypants', Nofollow(), Texer()])
class MarkdownNode(template.Node):
    def __init__(self, nodelist, **kwargs):
        self.nodelist = nodelist
        self.opts = kwargs
    def render(self, context):
        output = self.nodelist.render(context)
        if self.opts['safe']:
            parser = safe_parser
        else:
            parser = unsafe_parser
        return parser.reset().convert(output)
