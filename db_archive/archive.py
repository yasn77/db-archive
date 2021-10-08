import datetime
import subprocess
import tempfile
import boto3
import shutil
import smart_open
import sys

from shlex import quote

from smart_open.compression import tweak_close

import logging

logging.getLogger('smart_open.s3').addHandler(
    logging.StreamHandler(stream=sys.stdout))
logging.getLogger('smart_open.s3').setLevel(logging.INFO)


class Archive(object):
    def __init__(self,
                 source_host,
                 source_username,
                 source_password,
                 destination_bucket,
                 db,
                 access_key_id=None,
                 secret_access_key=None,
                 s3_endpoint_url=None):
        self.source_host = source_host
        self.source_username = source_username
        self.source_password = source_password
        self.destination_bucket = destination_bucket
        self.access_key_id = access_key_id
        self.secret_access_key = secret_access_key
        self.endpoint_url = s3_endpoint_url
        self.db_type = self._get_db_type()
        if len(db) > 0:
            self.all_db = False
            self.db = db
        else:
            self.all_db = True

    def _get_cmd_path(self, cmd):
        cmd_path = shutil.which(quote(cmd))
        if cmd_path is None:
            raise FileNotFoundError(f'{cmd} could not be found in system path')
        else:
            return cmd_path

    def _get_archive_name(self):
        timestamp = datetime.datetime.utcnow().replace(
            tzinfo=datetime.timezone.utc, microsecond=0, second=0).isoformat()
        db_names = 'all' if self.all_db else '+'.join(self.db)
        return f'{db_names}-{timestamp}'

    def _get_db_type(self):
        """Override this method for each of the Backup types"""
        pass

    def _handle_gz(self, file_obj, mode):
        import gzip
        result = gzip.GzipFile(fileobj=file_obj, mode=mode, compresslevel=6)
        tweak_close(result, file_obj)
        return result

    def get_command(self):
        """Override this method for each of the Backup types"""
        pass

    def call_backup(self):
        cmd = self.get_command()
        try:
            process = subprocess.run(cmd,
                                     shell=False,
                                     check=True,
                                     stdout=subprocess.PIPE)
        except subprocess.CalledProcessError as e:
            print(f'ERR Backup Failed: Command failed to run - {e}')
            exit(e.returncode)
        else:
            return process

    def do_archive(self, process):
        session = boto3.Session(
                    aws_access_key_id=self.access_key_id,
                    aws_secret_access_key=self.secret_access_key)
        s3_client = session.client('s3', endpoint_url=self.endpoint_url)
        smart_open.register_compressor('.gz', self._handle_gz)
        key = f'{self._get_archive_name()}.sql.gz'
        s3_uri = f's3://{self.destination_bucket}/'\
                 f'{self.db_type}/{self.source_host}/{key}'
        with tempfile.NamedTemporaryFile() as tmp:
            tp = {'writebuffer': tmp,
                  'client': s3_client,
                  'buffer_size': '4096'}
            with smart_open.open(s3_uri, 'wb', transport_params=tp) as fout:
                fout.write(process.stdout.read())

