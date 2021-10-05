import datetime
import subprocess
import tempfile
import lzma
import boto3
import shutil

from shlex import quote
from smart_open import open, register_compressor


class Archive(object):
    def __init__(self, source_host,
                 source_username,
                 source_password,
                 destination_bucket,
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

    def _handle_xz(self, file_obj, mode):
        return lzma.LZMAFile(filename=file_obj, mode=mode,
                             format=lzma.FORMAT_XZ)

    def _get_cmd_path(self, cmd):
        cmd_path = shutil.which(quote(cmd))
        if cmd_path is None:
            raise FileNotFoundError(f'{cmd} could not be found in system path')
        else:
            return cmd_path

    def _get_archive_name(self):
        timestamp = datetime.datetime.utcnow().replace(
            tzinfo=datetime.timezone.utc, microsecond=0, second=0).isoformat()
        return(timestamp)

    def get_command(self):
        """Override this method for each of the Backup types"""
        pass

    def call_backup(self):
        cmd = self.get_command()
        process = subprocess.Popen(cmd, shell=False, stdout=subprocess.PIPE)
        return process

    def do_archive(self, process):
        session = boto3.Session(
                    aws_access_key_id=self.access_key_id,
                    aws_secret_access_key=self.secret_access_key)
        s3_client = session.client('s3', endpoint_url=self.endpoint_url)

        register_compressor('.xz', self._handle_xz)
        key = f'{self._get_archive_name()}.sql.xz'
        s3_uri = f's3://{self.destination_bucket}/{key}'
        while True:
            output = process.stdout.readline()
            if process.poll() is not None:
                break
            if output:
                with tempfile.NamedTemporaryFile() as tmp:
                    tp = {'writebuffer': tmp, 'client': s3_client}
                    with open(s3_uri, 'wb', transport_params=tp) as fout:
                        print(output)
                        fout.write(output)
        return process.poll()
