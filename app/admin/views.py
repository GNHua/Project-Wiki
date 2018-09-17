import os
import platform
import subprocess
import datetime
from flask import request, redirect, url_for, flash, render_template
from flask_login import current_user
from mongoengine.context_managers import switch_db
from mongoengine.connection import _connection_settings as db_connection_settings
from mongoengine.connection import disconnect

from . import admin
from ..main.views import wiki_render_template
from .. import config, basedir, db, wiki_pwd, wiki_md
from ..models import WikiGroup, WikiPage, WikiPageVersion, WikiUser, WikiCache, WikiFile, WikiLoginRecord
from ..decorators import super_required, admin_required, user_required, guest_required
from .forms import AddGroupForm, NewUserForm, ExistingUserForm, FileDeletionForm, PageDeletionForm, SearchForm
from ..wiki_util.pagination import calc_page_num


@admin.route('/super-admin', methods=['GET', 'POST'])
@super_required
def wiki_super_admin():
    form = AddGroupForm()

    # Create a new group with its own database and static file directory
    if form.validate_on_submit():
        new_group_name = form.groupname.data

        # Save the name of the new group in database `admin`
        # Remove whitespaces in the group name.
        # Then use it to name the database which is about to be initialized.
        new_group = WikiGroup(name_with_whitespace=new_group_name,
                              name_no_whitespace=new_group_name.replace(' ', ''),
                              active=True)

        # Initialize a new database for the just-created group
        # Make sure the new group name is not occupied.
        if new_group.name_no_whitespace in db.connection.database_names():
            flash('Group already exists.')
        else:
            try:
                os.mkdir(os.path.join(basedir, 'Project_Wiki_Data', 'uploads', new_group.name_no_whitespace))
                new_group.save()
                db.register_connection(alias=new_group.name_no_whitespace, 
                                       name=new_group.name_no_whitespace,
                                       host=config.MONGODB_SETTINGS['host'],
                                       port=config.MONGODB_SETTINGS['port'])
                user = WikiUser.objects(name=form.username.data).first()
                if user is None:
                    WikiUser(name=form.username.data,
                             email=form.email.data,
                             password_hash=wiki_pwd.hash(form.password.data),
                             permissions={new_group.name_no_whitespace: 0x7f}).save()
                else:
                    user.set_role(new_group.name_no_whitespace, 'Admin')
                    user.save()
                WikiPage(title='Home', md='', html='', toc='').\
                    switch_db(new_group.name_no_whitespace).save()
                WikiCache(keypages_id_title=[], changes_id_title=[]). \
                    switch_db(new_group.name_no_whitespace).save()
                flash('New group added')
                return redirect(url_for('.wiki_super_admin'))
            except FileExistsError:
                flash('Upload directory already exists.')

    return render_template('admin/wiki_super_admin.html',
                           form=form,
                           all_groups=WikiGroup.objects.all())


@admin.route('/server-reload')
@super_required
def wiki_server_reload():
    # TODO: use another way to reboot server
    # if platform.system() == 'Darwin' or platform.system() == 'Linux':
    #     with open(os.path.join(basedir, 'Project_Wiki_Data', 'gunicorn.pid'), 'r') as f:
    #         pid = f.read().strip()
    #     subprocess.run(['kill', '-HUP', pid])
    #     flash('Server reload completed')
    return redirect(url_for('.wiki_super_admin'))


@admin.route('/activate-group/<group>')
@super_required
def wiki_activate_group(group):
    wg = WikiGroup.objects(name_no_whitespace=group).first()
    if wg is not None:
        if wg.active:
            wg.active = False
            db_connection_settings.pop(group, None)
            disconnect(group)
        else:
            wg.active = True
            db.register_connection(alias=group, name=group,
                                   host=config.MONGODB_SETTINGS['host'],
                                   port=config.MONGODB_SETTINGS['port'])
        wg.save()
    return redirect(url_for('.wiki_super_admin'))


@admin.route('/delete-group/<group>')
@super_required
def wiki_delete_group(group):
    # TODO: delete uploaded files
    wg = WikiGroup.objects(name_no_whitespace=group).first()
    if wg is not None:
        if wg.active:
            db_connection_settings.pop(group, None)
            disconnect(group)
        db.connection.drop_database(group)
        wg.delete()
        users = WikiUser.objects.all()
        for u in users:
            if u.permissions:
                u.save()
            else:
                u.delete()
    return redirect(url_for('.wiki_super_admin'))


@admin.route('/login-record')
@super_required
def wiki_show_login_record():
    page_num = request.args.get('page', default=1, type=int)
    records = WikiLoginRecord.objects.paginate(page=page_num, per_page=100)
    start_page, end_page = calc_page_num(page_num, records.pages)
    return render_template('admin/wiki_login_record.html',
                           records=records,
                           start_page=start_page,
                           end_page=end_page,
                           total_pages=records.pages)


@admin.route('/recent-user-activities')
@super_required
def wiki_recent_user_activities():
    usernames = [u.name for u in WikiUser.objects.only('name').all()]
    records = []
    for username in usernames:
        rec = WikiLoginRecord.objects(username=username).order_by('-timestamp').first()
        records.append(rec)
    records = list(filter(None.__ne__, records))
    return render_template('admin/wiki_recent_user_activities.html', records=records)


@admin.route('/all-users')
@super_required
def wiki_all_users():
    all_users = WikiUser.objects.order_by('username').all()
    return render_template('admin/wiki_all_users.html', all_users=all_users)


@admin.route('/backup')
@super_required
def wiki_backup():
    backup_dir = os.path.join(basedir, config.DATA_FOLDER, 'backup', 
                              datetime.datetime.now().strftime('%Y.%m.%d.%H%M%S'))
    subprocess.run(['mongodump', '--out', backup_dir, 
                    '--username', config.MONGODB_SETTINGS['username'],
                    '--password', config.MONGODB_SETTINGS['password'],
                    '--host', config.MONGODB_SETTINGS['host'],
                    '--port', str(config.MONGODB_SETTINGS['port'])])
    flash('Backup completed')
    return redirect(url_for('.wiki_super_admin'))


@admin.route('/<group>/admin', methods=['GET', 'POST'])
@guest_required
def wiki_group_admin(group):
    if not current_user.is_admin(group):
        return redirect(url_for('auth.wiki_change_password', 
                                group=group, 
                                username=current_user.name))
    
    form = NewUserForm(access='User')

    if form.validate_on_submit():
        user = WikiUser.objects(name=form.username.data).first()
        # If user does not exist, add a new user.
        # If user exists but does not have access to the group, grant access.
        if user is None:
            new_user = WikiUser(name=form.username.data, email=form.email.data)
            new_user.set_password(form.password.data)
            new_user.set_role(group, form.access.data)
            new_user.save()
            flash('New user added')
            return redirect(url_for('.wiki_group_admin', group=group))
        elif not user.belong_to(group) and not user.is_super_admin():
            user.set_role(group, form.access.data)
            user.save()
            flash('New user added')
            return redirect(url_for('.wiki_group_admin', group=group))
        else:
            flash('User already exists.')

    all_users = [u for u in WikiUser.objects.order_by('username') if u.belong_to(group)]
    return wiki_render_template('admin/wiki_group_admin.html',
                                group=group,
                                form=form,
                                all_users=all_users)


@admin.route('/<group>/manage-user/<user_id>', methods=['GET', 'POST'])
@admin_required
def wiki_group_manage_user(group, user_id):
    user = WikiUser.objects.get_or_404(id=user_id)
    if not user.belong_to(group):
        return url_for('.wiki_group_admin', group=group)
    form = ExistingUserForm()
    
    if form.validate_on_submit():
        if form.remove.data:
            user.permissions.pop(group, None)
            if user.permissions:
                user.save()
            else:
                user.delete()
        else:
            if user.email != form.email.data:
                user.email = form.email.data
            if form.password.data != '':
                user.set_password(form.password.data)
            if user.get_role(group) != form.access.data:
                user.set_role(group, form.access.data)
            user.save()
        return redirect(url_for('.wiki_group_admin', group=group))

    form.email.data = user.email
    form.access.data = user.get_role(group)
    return wiki_render_template('admin/wiki_group_manage_user.html', 
                                group=group, form=form, user_id=user_id)


@admin.route('/<group>/all-wikipages', methods=['GET', 'POST'])
@admin_required
def wiki_show_all_wikipages(group):
    search_keyword = request.args.get('search')
    page_num = request.args.get('page', default=1, type=int)
    
    delete_form = PageDeletionForm()
    search_form = SearchForm(search=search_keyword)
    if search_keyword and not search_keyword.isspace():
        with switch_db(WikiPage, group) as _WikiPage:
            results = _WikiPage.objects(title__ne='Home').\
                search_text(search_keyword).order_by('id').\
                only('title', 'modified_on', 'modified_by', 'current_version').\
                order_by('$text_score').paginate(page=page_num, per_page=100)
        start_page, end_page = calc_page_num(page_num, results.pages)
    else:
        with switch_db(WikiPage, group) as _WikiPage:
            results = _WikiPage.objects(title__ne='Home').order_by('id').\
                only('title', 'modified_on', 'modified_by', 'current_version').\
                paginate(page=page_num, per_page=100)
        start_page, end_page = calc_page_num(page_num, results.pages)
    
    if search_form.validate_on_submit():
        return redirect(url_for('.wiki_show_all_wikipages', 
                                group=group, 
                                search=search_form.search.data))

    return wiki_render_template('admin/wiki_show_all_pages.html',
                                group=group,
                                delete_form=delete_form,
                                search_form=search_form,
                                results=results,
                                start_page=start_page,
                                end_page=end_page,
                                total_pages=results.pages)


@admin.route('/<group>/delete-wikipage', methods=['POST'])
@admin_required
def wiki_group_delete_wikipage(group):
    form = PageDeletionForm()
    with switch_db(WikiFile, group) as _WikiFile, \
            switch_db(WikiPage, group) as _WikiPage, \
            switch_db(WikiPageVersion, group) as _WikiPageVersion, \
            switch_db(WikiCache, group) as _WikiCache:
        page_to_delete = _WikiPage.objects(id=form.page_id.data).first()
        _WikiPageVersion.objects(id__in=[pv.id for pv in page_to_delete.versions]).delete()
        _WikiCache.objects.update_one(pull__changes_id_title=(page_to_delete.id, page_to_delete.title),
                                      pull__keypages_id_title=(page_to_delete.id, page_to_delete.title))
        if page_to_delete.title != 'Home':
            for wp in _WikiPage.objects(refs__contains=page_to_delete.id):
                wp_md = wp.md.replace('[[{}]]'.format(page_to_delete.title), '')
                wp_toc, wp_html = wiki_md(group, wp_md)
                _WikiPage.objects(id=wp.id).update_one(set__md=wp_md,
                                                       set__html=wp_html,
                                                       set__toc=wp_toc)
            page_to_delete.delete()
    return ''


@admin.route('/<group>/all-files')
@admin_required
def wiki_show_all_files(group):
    # TODO: server error when there is no uploaded files
    page_num = request.args.get('page', default=1, type=int)
    with switch_db(WikiFile, group) as _WikiFile:
        files = _WikiFile.objects.paginate(page=page_num, per_page=100)
    start_page, end_page = calc_page_num(page_num, files.pages)
    form = FileDeletionForm()
    return wiki_render_template('admin/wiki_show_all_files.html',
                                group=group,
                                form=form,
                                files=files,
                                start_page=start_page,
                                end_page=end_page,
                                total_pages=files.pages)


@admin.route('/<group>/delete-file', methods=['POST'])
@admin_required
def wiki_group_delete_file(group):
    form = FileDeletionForm()
    with switch_db(WikiFile, group) as _WikiFile, \
            switch_db(WikiPage, group) as _WikiPage:
        file_to_delete = _WikiFile.objects(id=form.file_id.data).first()
        _WikiPage.objects(files__contains=file_to_delete.id).\
            update(pull__files=file_to_delete)
        file_to_delete.delete()
    os.remove(os.path.join(config.UPLOAD_FOLDER, group, str(form.file_id.data)))
    return ''


@admin.route('/<group>/delete-comment/<page_id>/<comment_id>')
@user_required
def wiki_group_delete_comment(group, page_id, comment_id):
    with switch_db(WikiPage, group) as _WikiPage:
        page = _WikiPage.objects(id=page_id).only('comments').first()
        for c in page.comments:
            if c.id == comment_id:
                comment_to_del = c
        
        if current_user.is_admin(group) or \
                comment_to_del.author == current_user.name:
            _WikiPage.objects(id=page.id).update_one(pull__comments=comment_to_del)
            
        return redirect(request.referrer)
