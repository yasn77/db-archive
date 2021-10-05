#!/usr/bin/env python

import click
import aurora_archive.mysql_archive as mysql

AURORA_DB_TYPES = ['MYSQL', 'PGSQL']


@click.command()
@click.option('-a', '--aurora-db-type',
              type=click.Choice(AURORA_DB_TYPES, case_sensitive=False),
              help=f'Aurora DB Type to use, valid values are \
                    {AURORA_DB_TYPES} (case insensitive)')
@click.option('-s', '--source-host', help='Source host')
@click.option('-u', '--source-username', help='Source username')
@click.option('-p', '--source-password', help='Source password')
@click.option('-b', '--destination-bucket', help='Destination S3 Bucket')
@click.option('--access-key-id', prompt=True, prompt_required=False,
              default=None, help='AWS Access Key ID')
@click.option('--secret-access-key', prompt=True, prompt_required=False,
              default=None, help='AWS Secret Access Key')
@click.option('--s3-endpoint-url', prompt=True, prompt_required=False,
              default=None,
              help='S3 Endpoint to use (if you aren\'t using AWS')
def main(aurora_db_type,
         source_host,
         source_username,
         source_password,
         destination_bucket,
         access_key_id,
         secret_access_key,
         s3_endpoint_url):
    assert aurora_db_type is not None

    if aurora_db_type.lower() == 'mysql':
        archiver = mysql.MysqlArchive(source_host,
                                      source_username,
                                      source_password,
                                      destination_bucket,
                                      access_key_id=access_key_id,
                                      secret_access_key=secret_access_key,
                                      s3_endpoint_url=s3_endpoint_url)
    else:
        print("No Aurora type selected")

    print(archiver.get_command())
    process = archiver.call_backup()
    archiver.do_archive(process)


if __name__ == '__main__':
    main()
