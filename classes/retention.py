from datetime import date

class Retention:
    def __init__(self, ftp_connection, logger, config):
        self.ftpconn = ftp_connection
        self.logger = logger
        self.settings = config

    def read_file_list(self):
        self.logger.info("Read file list")
        self.ftpconn.cwd(self.settings["USEDIR"])
        return self.ftpconn.listdir()

    def remove_older_than(self, file_list, days, dryrun=True):
        self.logger.info("Read file list")
        for file_name in file_list:
            # check if file should be deleted
            # extract datepart
            file_date = file_name[7:17]
            if len(file_date) == 10:
                self.logger.debug("Examening {}".format(file_date))
                year = int(file_date[0:4])
                month = int(file_date[5:7])
                day = int(file_date[8:])
                diff = date.today() - date(year, month, day)
                if diff.days >= days:
                    # delete this file
                    self.logger.info("File will be deleted: {}".format(file_name))
                    if not dryrun:
                        self.ftpconn.remove(file_name)
            else:
                self.logger.info("Can't render date of file: {}".format(file_name))

