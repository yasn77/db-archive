from os import chmod
from shlex import quote
from db_archive.archive import Archive
from pathlib import Path


class PgsqlArchive(Archive):
    def _get_default_port(self):
        return '5432'

    def _create_pgpass(self):
        home = str(Path.home())
        pgpass_file = f'{home}/.pgpass'
        with open(pgpass_file, 'a+') as f:
            f.write(f'{self.source_host}'
                    ':*:*:'
                    f'{self.source_username}:{self.source_password}\n')
        chmod(pgpass_file, 0o600)

    def _get_db_type(self):
        return 'pgsql'

    def get_command(self):
        self._create_pgpass()
        cmd = [self._get_cmd_path('pg_dumpall'),
               '--host={}'.format(quote(self.source_host)),
               '--port={}'.format(quote(self._get_port())),
               '--username={}'.format(quote(self.source_username)),
               '-w']
        print(len(self.db))
        if self.all_db is False and len(self.db) == 1:
            print('in condition')
            cmd[0] = self._get_cmd_path('pg_dump')
            cmd.append(quote(self.db[0]))
        elif self.all_db is False and len(self.db) > 1:
            print('WARN: pgsql archive supports only dumping all '
                  'or a single DB')
            print('WARN: Using pg_dumpall')
        return cmd
