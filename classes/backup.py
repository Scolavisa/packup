class Backup:
    def __init__(self, logger, config):
        self.logger = logger
        self.settings = config

    def do_backup(self):
        """
        read backup rules and execute them
        creates seperate files as tar.gz for every backup rule
        :return:
        """


    def send_to_backupserver(self) -> None:
        print("send to backupserver")

    def package_backup(self) -> None:
        print("Package backups into one file")

    def encrypt_file(self) -> None:
        print("encrypt backup file")
