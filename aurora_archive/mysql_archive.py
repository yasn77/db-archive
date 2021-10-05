from shlex import quote

from aurora_archive.archive import Archive


class MysqlArchive(Archive):
    def get_command(self):
        mysqldump = self._get_cmd_path('mysqldump')
        return [mysqldump,
                '--all-databases',
                '--single-transaction',
                '--host={}'.format(quote(self.source_host)),
                '--user={}'.format(quote(self.source_username)),
                '--password={}'.format(quote(self.source_password))]
