import markdown
from markdown.inlinepatterns import Pattern
from markdown.util import etree
from markdown.extensions import Extension
from mongoengine.context_managers import switch_db
from flask_login import current_user
from ..models import WikiPage, WikiFile, WikiUser, WikiCache,\
    render_wiki_link, render_wiki_file, render_wiki_image

page_regex = r'\[\[(.+?)\]\]'
file_regex = r'\[(file|image):(\d+)(@(\d+)x(\d+))?\]'
at_regex = r'\[@(.+?)\]'


# Parse wiki page
class WikiPagePattern(Pattern):
    wiki_group = None
    wiki_refs = []

    def handleMatch(self, m):
        page_title = m.group(2)
        # parse comments on wiki pages
        with switch_db(WikiPage, self.wiki_group) as _WikiPage:
            _wp = _WikiPage.objects(title=page_title).only('id').first()
            if _wp is None:
                _wp = _WikiPage(title=page_title, md='', html='', toc='',\
                    modified_by=current_user.name).save()
                with switch_db(WikiCache, self.wiki_group) as _WikiCache:
                    _cache = _WikiCache.objects.only('changes_id_title').first()
                    _cache.add_changed_page(_wp.id, _wp.title, _wp.modified_on)
            self.wiki_refs.append(_wp)
            
            return render_wiki_link(self.wiki_group, _wp.id, 
                                    page_title, tostring=False)


class WikiPageExtension(Extension):
    def extendMarkdown(self, md, md_globals):
        md.inlinePatterns['wiki_page'] = WikiPagePattern(page_regex)


# Parse wiki file & image
class WikiFilePattern(Pattern):
    wiki_group = None
    wiki_files = []

    def handleMatch(self, m):
        _, _, file_type, file_id, wh, w, h = [m.group(i) for i in range(7)]

        # parse comments on wiki pages
        with switch_db(WikiFile, self.wiki_group) as _WikiFile:
            _wf = _WikiFile.objects(id=file_id).first()
        if _wf:
            self.wiki_files.append(_wf)
            if file_type == 'image':
                el = render_wiki_image(self.wiki_group, file_id, 
                                       _wf.name, tostring=False)
                if w is not None and int(w) != 0:
                    el.attrib['width'] = w
                if h is not None and int(h) != 0:
                    el.attrib['height'] = h
            elif file_type == 'file' and wh is None:
                el = render_wiki_file(self.wiki_group, file_id, 
                                      _wf.name, tostring=False)
            return el


class WikiFileExtension(Extension):
    def extendMarkdown(self, md, md_globals):
        md.inlinePatterns['wiki_file'] = WikiFilePattern(file_regex)


# Parse `@` notification in comments
class WikiAtPattern(Pattern):
    is_wiki_comment = False
    wiki_group = None
    wiki_users = []

    def handleMatch(self, m):
        if self.is_wiki_comment:
            username = m.group(2)
            u = WikiUser.objects(name=username).first()
            if u and self.wiki_group in u.permissions:
                el = etree.Element('strong')
                el.text = '[@{}]'.format(username)
                self.wiki_users.append(u)
                el.attrib['class'] = 'wiki-user-notification'
                return el


class WikiAtExtension(Extension):
    def extendMarkdown(self, md, md_globals):
        md.inlinePatterns['wiki_at'] = WikiAtPattern(at_regex)


class WikiMarkdown(markdown.Markdown):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, extensions=[WikiPageExtension(), WikiFileExtension(), WikiAtExtension(),
                                            'markdown.extensions.toc', 'pymdownx.github'], **kwargs)

    def __call__(self, group, md, is_comment=False):
        self.inlinePatterns['wiki_page'].wiki_group = group
        self.inlinePatterns['wiki_page'].wiki_refs = []
        self.inlinePatterns['wiki_file'].wiki_group = group
        self.inlinePatterns['wiki_file'].wiki_files = []
        self.inlinePatterns['wiki_at'].is_wiki_comment = is_comment
        self.inlinePatterns['wiki_at'].wiki_group = group
        self.inlinePatterns['wiki_at'].wiki_users = []

        try:
            self.toc = ''
            html = super().convert(md)
        except RecursionError:
            html = md
        return self.toc, html

    def get_refs_and_files(self, group, md):
        self.__call__(group, md)
        return self.inlinePatterns['wiki_page'].wiki_refs, \
            self.inlinePatterns['wiki_file'].wiki_files

    @property
    def wiki_refs(self):
        return self.inlinePatterns['wiki_page'].wiki_refs

    @property
    def wiki_files(self):
        return self.inlinePatterns['wiki_file'].wiki_files

    @property
    def users_to_notify(self):
        return self.inlinePatterns['wiki_at'].wiki_users
