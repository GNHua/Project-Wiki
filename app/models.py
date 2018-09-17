from collections import OrderedDict
from datetime import datetime
from flask_login import UserMixin, AnonymousUserMixin, current_user
from mongoengine.context_managers import switch_db
from markdown.util import etree
import difflib

from . import db, login_manager, wiki_pwd
from .wiki_util import unified_diff


@login_manager.user_loader
def load_user(user_id):
    return WikiUser.objects(id=user_id).first()


class Permission:
    """Permissions to access Project Wiki"""
    READ = 0x01
    WRITE = 0x02
    ADMIN = 0x40
    SUPER = 0x80


roles = OrderedDict([
    ('Super', 0xff),
    ('Admin', 0x7f),
    ('User', Permission.READ | Permission.WRITE),
    ('Guest', Permission.READ)
])


class AnonymousUser(AnonymousUserMixin):
    id = ''
    name = 'system'
    group = ''

    def can(self, group, permissions):
        return False

    def belong_to(self, group):
        return False

    def is_admin(self, group):
        return False

    def is_super_admin(self):
        return False


class WikiUser(UserMixin, db.Document):
    """Collection of Project Wiki users
    
    :param name: username
    :param email: user email
    :param password_hash: the hash of user's password
        The actual password is not stored, only its hash.
    :param permissions: user's permissions for each group
        Example: 
            {'group1': 0x03, 'group2': 0x40}
    """
    name = db.StringField(unique=True)
    email = db.StringField(required=True)
    password_hash = db.StringField()
    permissions = db.DictField(default=dict())

    meta = {'collection': 'wiki_user'}

    def __repr__(self):
        return '<User {}>'.format(self.name)

    def set_password(self, password):
        self.password_hash = wiki_pwd.hash(password)

    def verify_password(self, password):
        return wiki_pwd.verify(password, self.password_hash)

    def set_role(self, group, role):
        """Set the role of a user.
        
        :param group: group name (no whitespace)
        :param role: `Super`, `Admin`, `User`, or `Guest`,
            Super: Add/remove group, activate/deactiavte group, 
                   add/remove users, etc. 
            Admin: Add/remove users in the group, read/write pages.
            User: Read/write pages.
            Guest: Read pages. 
        """
        self.permissions[group] = roles[role]

    def get_role(self, group):
        idx = list(roles.values()).index(self.permissions[group])
        return list(roles)[idx]

    def can(self, group, permissions):
        """Check user's permission"""
        if self.is_super_admin():
            return True
        if group in self.permissions:
            return (self.permissions[group] & permissions) == permissions
        else:
            return False

    def belong_to(self, group):
        return group in self.permissions

    def is_admin(self, group):
        return self.can(group, Permission.ADMIN)

    def is_super_admin(self):
        return 'super' in self.permissions \
            and (self.permissions['super'] & Permission.SUPER) == Permission.SUPER


class WikiFile(db.Document):
    """Collection of uploaded files.
    
    :param id: file id
        The `id` is a sequencial integer share by all groups.
        For example, if a file is uploaded in `group1`, and its id is 100, 
        the id of next file, no matter which group it is uploaded in, will 
        be 101. 
    :param name: original file name
    :param secured_name: secured file name created from original file name
        Secured file names are created to ensure file names can't be used 
        to corrupt computer systems.
    :param mime_type: file type
        Example: image/png
    :param size: file size in bytes
    :param upload_on: the time when file is uploaded
    :param upload_by: username of the one uploads the file
    """
    id = db.SequenceField(primary_key=True)
    name = db.StringField(max_length=256, required=True)
    secured_name = db.StringField(max_length=256)
    mime_type = db.StringField()
    size = db.IntField()  # in bytes
    uploaded_on = db.DateTimeField(default=datetime.now)
    uploaded_by = db.StringField()

    meta = {
        'collection': 'wiki_file',
        'allow_inheritance': True,
    }

    def __repr__(self):
        return '<File - %s>' % self.name


class WikiPageVersion(db.Document):
    """Collection of page versions.
    
    :param diff: differences between two adjacent versions
    :param version: version number
    :param modified_on: the time when this version of page is modified
    :param modified_by: username of the one who modified the wiki page
    """
    diff = db.StringField()
    version = db.IntField()
    modified_on = db.DateTimeField()
    modified_by = db.StringField()

    def __repr__(self):
        return '<Version {}>'.format(self.version)

    meta = {
        'collection': 'wiki_page_version',
        'indexes': [{
            'fields': ['$diff'],
            'default_language': 'english'
        }]
    }


class WikiComment(db.EmbeddedDocument):
    """Comment, once submitted, can be deleted by author or admin, 
    but cannot be modified. 
    Comment accepts the same kind of markdown used to edit wiki pages.
    In addition, when one can enter `[@user1]`, Project Wiki will send 
    out a notification email to `user1`.
    
    :param id: comment id
    :param timestamp: the time comment is submitted
    :param author: username of comment author
    :param html: html rendered from entered markdown
    :param md: submitted markdown
    """
    # id = <epoch time>-<author id>
    id = db.StringField(required=True)
    timestamp = db.DateTimeField(default=datetime.now)
    author = db.StringField()
    html = db.StringField()
    md = db.StringField()


class WikiPage(db.Document):
    """Collection of Project Wiki pages.
    
    :param title: page title
    :param md: page markdown
    :param html: html rendered from `md`
    :param toc: table of contents generated based on headings in `md`
    :param current_version: current version number of the page
    :param versions: a list references to previous versions of the page
    :param modified_on: the most recent time when page is modified
    :param modified_by: username of the one who modified the page recently
    :param comments: comments
    :param refs: a list of references to the pages mentioned
    :param files: a list of references to the files mentioned
    """
    title = db.StringField(required=True, unique=True)
    md = db.StringField()
    html = db.StringField()
    toc = db.StringField()
    current_version = db.IntField(default=1)
    versions = db.ListField(db.ReferenceField(WikiPageVersion))
    modified_on = db.DateTimeField(default=datetime.now)
    modified_by = db.StringField()
    comments = db.ListField(db.EmbeddedDocumentField(WikiComment))

    refs = db.ListField(db.ReferenceField('self'))
    files = db.ListField(db.ReferenceField('WikiFile'))

    meta = {
        'collection': 'wiki_page',
        'indexes': [
            '#title', {
                'fields': ['$title', '$md', '$comments.md'],
                'default_language': 'english',
                'weights': {'title': 10, 'md': 2, 'comments.md': 1}
            }
        ]
    }

    def __repr__(self):
        return '<Wiki Page - {}>'.format(self.title)

    def update_content(self, group, md, html, toc):
        """Update page content and make other changes accordingly.
        
        :param group: group name (no whitespace)
        :param md: markdown
        :param html: html rendered from `md`
        :param toc: table of contents generated based on headings in `md`
        """
        self.html = html
        self.toc = toc
        diff = unified_diff.make_patch(self.md, md)
        if diff:
            pv = WikiPageVersion(diff, self.current_version, self.modified_on,
                                 self.modified_by).switch_db(group).save()
            self.versions.append(pv)
            self.md = md
            self.modified_on = datetime.now()
            self.modified_by = current_user.name
            self.current_version += 1
            
            with switch_db(WikiCache, group) as _WikiCache:
                _cache = _WikiCache.objects.only('changes_id_title').first()
                _cache.add_changed_page(self.id, self.title, self.modified_on)
        self.save()

    def rename(self, group, new_title):
        """Rename a wikipage, update all the pages which reference it, 
        as well as WikiPageVersion, WikiCache.
        
        :param group: group name (no whitespace)
        :param new_title: the new title of the page
        """
        old_md = '[[{}]]'.format(self.title)
        new_md = '[[{}]]'.format(new_title)
        
        old_html = render_wiki_link(group, self.id, self.title)
        new_html = render_wiki_link(group, self.id, new_title)
        
        # `switch_db(WikiPage, group)` has already been done in `main.wiki_rename_page`.
        for p in self.__class__.objects(refs__contains=self.id).exclude('comments').all():
            p.md = p.md.replace(old_md, new_md)
            p.html = p.html.replace(old_html, new_html)
            p.save()
            
        with switch_db(WikiPageVersion, group) as _WikiPageVersion:
            for pv in _WikiPageVersion.objects.search_text(old_md).all():
                pv.diff = pv.diff.replace(old_md, new_md)
                pv.save()
        with switch_db(WikiCache, group) as _WikiCache:
            _WikiCache.objects(changes_id_title=[self.id, self.title]).\
                update(set__changes_id_title__S=[self.id, new_title])
            _WikiCache.objects(keypages_id_title=[self.id, self.title]).\
                update(set__keypages_id_title__S=[self.id, new_title])

        self.title = new_title
        self.save()

    def get_version_content(self, group, old_ver_num):
        """Recover an old version of the page. 
        Because WikiPageVersion only stores the unified diff between two adjecent 
        versions, to get a really old version it needs to apply the difference 
        one by one. 
        For example, if there is a `page` whose current version is 10, and one 
        need to recover version 7, here is what would happen:
            page.content[version 10] + diff[version 9] -> page.content[version 9]
            page.content[version  9] + diff[version 8] -> page.content[version 8]
            page.content[version  8] + diff[version 7] -> page.content[version 7]
        So it took longer to calculate what the content of an old version is than 
        a newer version.
        
        :param group: group name (no whitespace)
        :param old_ver_num: the old version number
        """
        with switch_db(WikiPageVersion, group):
            old_to_current = self.versions[(old_ver_num - 1):]
            old_to_current_patches = [v.diff for v in old_to_current[::-1]]
            return unified_diff.apply_patches(self.md, old_to_current_patches, revert=True)

    def make_wikipage_diff(self, group, old_ver_num, new_ver_num):
        """Generate a table to compare differences between two different 
        versions of the page.
        
        :param group: group name (no whitespace)
        :param old_ver_num: old version number
        :param new_ver_num: new version number
        """
        old_content = self.get_version_content(group, old_ver_num)
        new_content = self.get_version_content(group, new_ver_num)
        d = difflib.HtmlDiff()
        diff_table = d.make_table(old_content.splitlines(), new_content.splitlines())
        diff_table = diff_table.replace('&nbsp;', ' ').replace(' nowrap="nowrap"', '')
        return diff_table


class WikiCache(db.Document):
    """Each group should only have one document in this collection.
    
    :param keypages_id_title: keypage ids and titles
    :param changes_id_title: recently changed page ids and titles
    """
    keypages_id_title = db.ListField()
    changes_id_title = db.ListField()
    latest_change_time = db.DateTimeField(default=datetime.now)

    meta = {'collection': 'wiki_cache'}

    def update_keypages(self, group, *titles):
        self.keypages_id_title = []
        with switch_db(WikiPage, group) as _WikiPage:
            for t in titles:
                p = _WikiPage.objects(title=t).only('id').first()
                if p is not None:
                    self.keypages_id_title.append((p.id, t))

            # Deduplicate keypages and keep the original order
            self.keypages_id_title = sorted(set(self.keypages_id_title),
                                            key=self.keypages_id_title.index)
        self.save()

    def add_changed_page(self, page_id, page_title, page_time):
        page_id_title = [page_id, page_title]
        if not self.changes_id_title:
            self.changes_id_title = []
        self.changes_id_title = list(filter(lambda x:x != page_id_title, 
                                            self.changes_id_title))
        self.changes_id_title.append(page_id_title)
        if len(self.changes_id_title) > 50:
            self.changes_id_title = self.changes_id_title[-50:]
        self.latest_change_time = page_time
        self.save()


class WikiGroup(db.Document):
    """Collection of Project Wiki groups.
    
    :param name_with_whitespace: group name with whitespace, for display
    :param name_no_whitespace: group name without whitespace, used as argument
    """
    name_with_whitespace = db.StringField()
    name_no_whitespace = db.StringField()
    active = db.BooleanField()

    meta = {'collection': 'wiki_group'}


class WikiLoginRecord(db.Document):
    username = db.StringField()
    timestamp = db.DateTimeField(default=datetime.now)
    browser = db.StringField()
    platform = db.StringField()
    details = db.StringField()
    ip = db.StringField()

    meta = {
        'collection': 'wiki_login_record',
        'ordering': ['-timestamp']
    }


def render_wiki_link(group, page_id, page_title, tostring=True):
    """Render html """
    el = etree.Element('a', attrib={
        'class': 'wiki-page',
        'href': '/{0}/{1!s}/page'.format(group, page_id)
    })
    el.text = page_title
    if tostring:
        return etree.tostring(el, encoding='unicode')
    else:
        return el


def render_wiki_file(group, file_id, filename, tostring=True):
    sub_el = etree.Element('img', attrib={
        'alt': 'file icon',
        'src': '/static/icons/file-icon.png',
        'width': '20',
        'height': '20'
    })
    sub_el.tail = filename
    el = etree.Element('a', attrib={'href': '/{}/file/{}?filename={}'.
                       format(group, file_id, filename),
                       'class': 'wiki-file'})
    el.append(sub_el)
    if tostring:
        return etree.tostring(el, encoding='unicode')
    else:
        return el


def render_wiki_image(group, file_id, filename, tostring=True):
    el = etree.Element('img', attrib={'src': '/{}/file/{}?filename={}'.
                       format(group, file_id, filename),
                       'class': 'wiki-file'})
    if tostring:
        return etree.tostring(el, encoding='unicode')
    else:
        return el
