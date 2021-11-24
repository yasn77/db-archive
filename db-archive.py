#!/usr/bin/env python

import click
import datetime
import db_archive.mysql_archive as mysql
import db_archive.pgsql_archive as pgsql

from db_archive import get_version

DB_TYPES = ['MYSQL', 'PGSQL']
ENV_PREFIX = 'DA_'


@click.command()
@click.option('-a', '--db-type', envvar=f'{ENV_PREFIX}DB_TYPE',
              type=click.Choice(DB_TYPES, case_sensitive=False),
              help=f'DB Type to use, valid values are \
                    {DB_TYPES} (case insensitive)')
@click.option('-s', '--source-host', envvar=f'{ENV_PREFIX}SOURCE_HOST',
              help='Source host')
@click.option('--source-port', prompt=True, prompt_required=False,
              envvar=f'{ENV_PREFIX}SOURCE_PORT', default=None,
              help='Source Port')
@click.option('-u', '--source-username', envvar=f'{ENV_PREFIX}SOURCE_USERNAME',
              help='Source username')
@click.option('-p', '--source-password', envvar=f'{ENV_PREFIX}SOURCE_PASSWORD',
              help='Source password')
@click.option('-b', '--destination-bucket',
              envvar=f'{ENV_PREFIX}DESTINATION_BUCKET',
              help='Destination S3 Bucket')
@click.option('--access-key-id', prompt=True, prompt_required=False,
              default=None, help='AWS Access Key ID')
@click.option('--secret-access-key', prompt=True, prompt_required=False,
              default=None, help='AWS Secret Access Key')
@click.option('--s3-endpoint-url', prompt=True, prompt_required=False,
              default=None,
              envvar=f'{ENV_PREFIX}ENDPOINT_URL',
              help='S3 Endpoint to use (if you aren\'t using AWS')
@click.version_option(version=get_version(),
                      message='{"version": "%(version)s"}')
@click.argument('db', nargs=-1, required=False)
def main(db_type,
         source_host,
         source_port,
         source_username,
         source_password,
         destination_bucket,
         access_key_id,
         secret_access_key,
         s3_endpoint_url,
         db):
    """
    Stream backup from database backup command to S3

    This provides an effecient way of backup up a database without
    storing to disk first. This can be useful for large database dumps.

    To archive, you should set a lifecycle policy on S3 to move files
    to Glacier.

    Each option can be set using environment variables, by
    replacing '-' with '_' and prefixing the environment variable
    with 'DA_'. For example '--db-type' would be 'DA_DB_TYPE'
    """
    assert db_type is not None

    if db_type.lower() == 'mysql':
        archiver = mysql.MysqlArchive(source_host,
                                      source_port,
                                      source_username,
                                      source_password,
                                      destination_bucket,
                                      db,
                                      access_key_id=access_key_id,
                                      secret_access_key=secret_access_key,
                                      s3_endpoint_url=s3_endpoint_url)
    if db_type.lower() == 'pgsql':
        archiver = pgsql.PgsqlArchive(source_host,
                                      source_port,
                                      source_username,
                                      source_password,
                                      destination_bucket,
                                      db,
                                      access_key_id=access_key_id,
                                      secret_access_key=secret_access_key,
                                      s3_endpoint_url=s3_endpoint_url)
    else:
        print("No DB type selected")

    starttime = datetime.datetime.now()
    click.echo(click.style(f"Starting Archive at {starttime}", fg='green'))
    process = archiver.call_backup()
    archiver.do_archive(process)
    endtime = datetime.datetime.now()
    click.echo(click.style(
        f"Completed at {endtime}. Duration {endtime - starttime}", fg='green'))


if __name__ == '__main__':
    main()
