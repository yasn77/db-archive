from shlex import quote

from aurora_archive.archive import Archive


class MysqlArchive(Archive):
    def get_command(self):
        mysqldump = self._get_cmd_path('mysqldump')
        db = list()
        if self.all_db:
            db.append('--all-databases')
        else:
            db = list(self.db)

        return [mysqldump,
                '--single-transaction',
                '--host={}'.format(quote(self.source_host)),
                '--user={}'.format(quote(self.source_username)),
                '--password={}'.format(quote(self.source_password)),
                ] + db
