
# Created by MCNoviceElectronics
# March 2018
# Vist: https://mcnoviceelectronics.wordpress.com
# See post for more details:
# https://mcnoviceelectronics.wordpress.com/2018/03/22/raspberry-pi-creating-local-apt-repository/

import configparser
import logging
import os

class APT_Config:

    def __init__(self, log_level='INFO'):
        self.log_level = log_level
        self.scp_host = '192.168.1.100'
        self.scp_user = 'user'
        self.scp_loc = '/opt/apt-mirror/raspbian/stretch'
        self.apt_archives = '/var/cache/apt/archives'
        self.last_modified = None
        self.config_loc = None

    #
    # Creates or reads the configuration file
    #  depending if the directories exists
    #
    def setup_config(self, config_dir, config_file):
        try:
            config_dir_path = os.path.join(os.environ['HOME'], config_dir)
            config_loc = os.path.join(config_dir_path, config_file)
            self.config_loc = config_loc
            if not os.path.isdir(config_dir_path):
                os.mkdir(config_dir_path)

            if os.path.exists(config_loc):
                return self.read_config(config_loc)
            else:
                self.create_config(config_loc)
        except SystemExit:
            raise SystemExit
        except:
            logging.exception('Exception setting up configuration')

    #
    #  Reads the configuration file to get the database information
    #
    def read_config(self, config_loc):
        try:
            config = configparser.ConfigParser()
            config.read(config_loc)
            log_level = config['APT_SYNC']['LogLevel']
            if log_level is not None:
                self.log_level = log_level
                root = logging.getLogger()
                root.setLevel(os.environ.get('LOGLEVEL', self.log_level))
                logging.info('LogLevel set to %s', self.log_level)
            else:
                logging.warning('Log level is not set, setting to default: %s', self.log_level)

            scp_host = config['APT_SYNC']['SCPHost']
            if scp_host is not None:
                self.scp_host = scp_host
                logging.info('SCPHost set to %s', self.scp_host)
            else:
                logging.warning('SCPHost is not set, setting to default: %s', self.scp_host)

            scp_user = config['APT_SYNC']['SCPUser']
            if scp_user is not None:
                self.scp_user = scp_user
                logging.info('SCPUser set to %s', self.scp_user)
            else:
                logging.warning('SCPUser is not set, setting to default: %s', self.scp_user)

            scp_loc = config['APT_SYNC']['SCPLocation']
            if scp_loc is not None:
                self.scp_loc = scp_loc
                logging.info('SCPLocation set to %s', self.scp_loc)
            else:
                logging.warning('SCPLocation is not set, setting to default: %s', self.scp_loc)

            apt_archives = config['APT_SYNC']['APTArchives']
            if apt_archives is not None:
                self.apt_archives = apt_archives
                logging.info('APTArchives set to %s', self.apt_archives)
            else:
                logging.warning('APTArchives is not set, setting to default: %s', self.apt_archives)

            last_modified = config['APT_DATA']['LastModified']
            if last_modified is not None and last_modified != '':
                self.last_modified = int(last_modified)
                logging.info('LastModified is set to %s', self.last_modified)
            else:
                self.last_modified = None

            return self.scp_host, self.scp_user, self.scp_loc, \
                    self.apt_archives, self.last_modified

        except KeyError as k_err:
            logging.exception('Key exception read configuration values')
            raise SystemExit
        except ValueError as v_err:
            logging.exception('ValueError while setting variable')
            raise SystemExit
        except:
            logging.exception('Exception while reading config')
            raise SystemExit


    def update_last_modified(self, last_modified):
        self.create_config(self.config_loc, last_modified)

    #
    # Creates a sample configuration file
    #  User still needs to edit so quits program
    #
    def create_config(self, config_loc, last_modified=None):
        try:
            config = configparser.ConfigParser()
            config['APT_SYNC'] = { 'LogLevel' : self.log_level,
                                'SCPHost' : self.scp_host,
                                'SCPUser' : self.scp_user,
                                'SCPLocation' : self.scp_loc,
                                'APTArchives' : self.apt_archives }
            if last_modified is None:
                config['APT_DATA'] = { 'LastModified' : '' }
            else:
                config['APT_DATA'] = { 'LastModified' : last_modified }

            with open(config_loc, "w") as configFile:
                config.write(configFile)
                if last_modified is None:
                    logging.warning('Created new config file in %s, please edit file with correct settings',
                                        config_loc)
                else:
                    logging.info('Updated config file with new last_modified time: %s', last_modified)
        except:
            logging.exception('Exception while creating config')
        finally:
            if last_modified is None:
                raise SystemExit
