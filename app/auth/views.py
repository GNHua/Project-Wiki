from flask_login import login_user, logout_user, current_user
from flask import request, redirect, url_for, flash, render_template, session

from . import auth
from ..main.views import wiki_render_template
from .. import wiki_pwd
from ..decorators import super_required, guest_required
from ..models import WikiUser, WikiGroup, WikiLoginRecord
from .forms import LoginForm, ChangePwdForm


@auth.route('/super-login', methods=['GET', 'POST'])
def wiki_super_login():
    if current_user.is_super_admin():
        return redirect(url_for('admin.wiki_super_admin'))

    form = LoginForm()
    if form.validate_on_submit():
        user = WikiUser.objects(name=form.username.data).first()
        if user is not None and user.verify_password(form.password.data) \
                and user.is_super_admin():
            login_user(user, form.remember_me.data)
            WikiLoginRecord(
                username=form.username.data,
                browser=request.user_agent.browser, 
                platform=request.user_agent.platform, 
                details=request.user_agent.string, 
                ip=request.remote_addr, 
            ).save()
            return redirect(url_for('admin.wiki_super_admin'))
        flash('Invalid username or password.')
    return render_template('auth/wiki_login.html', form=form)


@auth.route('/super-logout')
@super_required
def wiki_super_logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('.wiki_super_login'))


@auth.route('/<group>/login', methods=['GET', 'POST'])
def wiki_group_login(group):
    all_groups = [g.name_no_whitespace for g in WikiGroup.objects.all()]
    if group not in all_groups:
        return redirect(url_for('main.index'))

    if current_user.belong_to(group) or current_user.is_super_admin():
        return redirect(url_for('main.wiki_group_home', group=group))

    form = LoginForm()
    if form.validate_on_submit():
        user = WikiUser.objects(name=form.username.data).first()

        if user is not None and user.belong_to(group) \
                and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            session.permanent = True
            WikiLoginRecord(
                username=form.username.data,
                browser=request.user_agent.browser, 
                platform=request.user_agent.platform, 
                details=request.user_agent.string, 
                ip=request.remote_addr, 
            ).save()
            return redirect(
                request.args.get('next')
                or url_for('main.wiki_group_home', group=group)
            )
        flash('Invalid username or password.')
    return render_template('auth/wiki_login.html', group=group, form=form)


@auth.route('/<group>/logout')
@guest_required
def wiki_group_logout(group):
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('.wiki_group_login', group=group))


@auth.route('/<group>/change-password/<username>', methods=['GET', 'POST'])
@guest_required
def wiki_change_password(group, username):
    if username != current_user.name:
        return redirect(url_for('.wiki_change_password', group=group, username=username))
    
    form = ChangePwdForm()
    if form.validate_on_submit():
        if not current_user.verify_password(form.old_password.data):
            flash('Password Verification Failed.')
        elif form.new_password.data != form.confirm_password.data:
            flash('Please confirm new password again.')
        else:
            WikiUser.objects(name=current_user.name).\
                update_one(set__password_hash=wiki_pwd.hash(form.new_password.data))
            flash('Password changed.')
    
    all_users = [u for u in WikiUser.objects.order_by('username') if u.belong_to(group)]
    return wiki_render_template('auth/wiki_change_password.html',
                                group=group,
                                form=form,
                                all_users=all_users)
