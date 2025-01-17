from __future__ import absolute_import

import os
import logging
import click

from datacube.utils import gen_password
from datacube.config import LocalConfig
from datacube.index._api import Index
from datacube.ui import click as ui
from datacube.ui.click import cli


_LOG = logging.getLogger('datacube-user')
USER_ROLES = ('user', 'ingest', 'manage', 'admin')


@cli.group(name='user', help='User management commands')
def user_cmd():
    pass


@user_cmd.command('list')
@ui.pass_index()
def list_users(index):
    """
    List users
    """
    for role, user, description in index.users.list_users():
        click.echo('{0:6}\t{1:15}\t{2}'.format(role, user, description if description else ''))


@user_cmd.command('grant')
@click.argument('role',
                type=click.Choice(USER_ROLES),
                nargs=1)
@click.argument('users', nargs=-1)
@ui.pass_index()
def grant(index, role, users):
    """
    Grant a role to users
    """
    index.users.grant_role(role, *users)


@user_cmd.command('create')
@click.argument('role',
                type=click.Choice(USER_ROLES), nargs=1)
@click.argument('user', nargs=1)
@click.option('--description')
@ui.pass_index()
@ui.pass_config
def create_user(config, index, role, user, description):
    # type: (LocalConfig, Index, str, str, str) -> None
    """
    Create a User
    """
    password = gen_password(12)
    index.users.create_user(user, password, role, description=description)

    click.echo('{host}:{port}:*:{username}:{password}'.format(
        host=config.db_hostname or 'localhost',
        port=config.db_port,
        username=user,
        password=password
    ))


@user_cmd.command('delete')
@click.argument('users', nargs=-1)
@ui.pass_index()
@ui.pass_config
def delete_user(config, index, users):
    """
    Delete a User
    """
    index.users.delete_user(*users)
