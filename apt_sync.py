#!/usr/bin/env python3

# Created by MCNoviceElectronics
# March 2018
# Vist: https://mcnoviceelectronics.wordpress.com

from apt_config import APT_Config

import datetime
import logging
import os
import signal
import subprocess

_config_dir = '.apt_sync'
_config_file = 'apt_sync.ini'
#
# Custom logging formatter for exceptions
#   makes them all one line
#
class OneLineExceptionFormatter(logging.Formatter):
    def formatException(self, exc_info):
        result = super().formatException(exc_info)
        result = result.replace('\n', ' ')
        return repr(result)

    def format(self, record):
        result = super().format(record)
        if record.exc_text:
            result = result.replace('\n', '')
        return result

#
# Handles signals and cleans up everything
#
def sig_handler(signum, frame):
    logging.shutdown()
    quit()

#
#  Setup the custom logger
#
def setup_logging(log_level):
    handler = logging.StreamHandler()
    formatter = OneLineExceptionFormatter('%(asctime)s|%(filename)s|%(name)s|%(levelname)s|%(lineno)d|%(message)s')
    handler.setFormatter(formatter)
    root = logging.getLogger('APT_SYNC')
    root.setLevel(os.environ.get('LOGLEVEL', log_level))
    root.addHandler(handler)
    return root

def get_new_files(apt_archives, modify_ts=None):
    deb_files = []
    find_cmd = ['find', apt_archives, '-name', '*.deb']
    try:
        if modify_ts is not None:
            find_cmd.append('-newermt')
            find_cmd.append('@' + modify_ts)

        logging.debug('Find cmd: %s', find_cmd)
        p = subprocess.Popen(find_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        (output, err) = p.communicate()
        p_status = p.wait()
        logging.debug('Output: %s', output)
        logging.debug('RC: %s', p_status)
        if p_status != 0:
            logging.error('Shell cmd status: %d', p_status)
            logging.error('Error msg: %s', err)
        deb_files = output.decode('utf-8').split('\n')
        logging.info('Num debs: %s', len(deb_files))
    except:
        logging.exception('Exception in get_new_files')

    return deb_files

def send_deb_files(deb_files, scp_remote_cmd, debug=False):
    p_status = -1
    try:
        scp_local_cmd = 'scp'
        for f in deb_files:
            scp_local_cmd = scp_local_cmd + ' ' + f

        scp_cmd = scp_local_cmd + ' ' + scp_remote_cmd
        logging.debug('SCP_CMD: %s', scp_cmd)
        if not debug:
            p = subprocess.Popen(scp_cmd, stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
            (output, err) = p.communicate()
            p_status = p.wait()
            logging.debug('Output: %s', output)
            logging.debug('RC: %s', p_status)
            if p_status != 0:
                logging.error('Shell cmd status: %d', p_status)
                logging.error('Error msg: %s', err)
        else:
            p_status = 0
    except:
        logging.exception('Exception in send_deb_files')

    return p_status

def main():
    #INIT everything
    try:
        setup_logging('INFO')
        apt_config = APT_Config(log_level='INFO')
        scp_host, scp_user, scp_loc, apt_archives, last_modified \
            = apt_config.setup_config(_config_dir, _config_file)
    except SystemExit:
        logging.warn('Config needs to be setup, exiting')
        logging.shutdown()
        quit()

    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)

    apt_archives_unix = int(os.path.getmtime(apt_archives))
    logging.info('Mod time: %s (%s)',
                 apt_archives_unix,
                 datetime.datetime.fromtimestamp(int(apt_archives_unix)).strftime('%Y-%m-%d %H:%M:%S'))

    deb_files = []
    if last_modified is None:
        deb_files = get_new_files(apt_archives)
    else:
        if apt_archives_unix > last_modified:
            deb_files = get_new_files(apt_archives, str(last_modified))
        else:
            logging.info('No new files')

    scp_remote_cmd = scp_user + '@' + scp_host + ':' + scp_loc
    if deb_files is not None and len(deb_files) > 0:
        ret_code = send_deb_files(deb_files, scp_remote_cmd)
        if ret_code == 0:
            apt_config.update_last_modified(apt_archives_unix)
            logging.info('All Good')

    logging.shutdown()

if __name__ == "__main__":
    main()
