#!/usr/bin/env python3

# Created by MCNoviceElectronics
# March 2018
# Vist: https://mcnoviceelectronics.wordpress.com
# See post for more details:
# https://mcnoviceelectronics.wordpress.com/2018/03/22/raspberry-pi-creating-local-apt-repository/

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

def run_shell_cmd(shell_cmd, func_txt='run_shell_cmd'):
    p_status = -1
    try:
        logging.debug('%s shell command: %s', func_txt, shell_cmd)
        p = subprocess.Popen(shell_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        (output, err) = p.communicate()
        p_status = p.wait()
        logging.debug('Output: %s', output)
        if p_status != 0:
            logging.error('Shell cmd status: %d', p_status)
            logging.error('Error msg: %s', err)
    except:
        logging.exception('run_shell_cmd Exception running cmd %s', func_txt)
        raise SystemExit

    return p_status, output

def get_new_files(apt_archives, modify_ts=None):
    deb_files = []
    find_cmd = 'find ' + apt_archives + ' -name "*.deb"'
    try:
        if modify_ts is not None:
            find_cmd = find_cmd + ' -newermt @' + modify_ts

        p_status, output = run_shell_cmd(find_cmd, 'get_new_files')
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
            p_status, output = run_shell_cmd(scp_cmd, 'send_deb_files')
        else:
            #just for debugging do not send deb files return everything OK
            p_status = 0
    except:
        logging.exception('Exception in send_deb_files')

    return p_status

def get_dir_modify_time(dir_location):
    dir_modify_unix_ts = int(os.path.getmtime(dir_location))
    logging.info('Mod time: %s (%s)',
                 dir_modify_unix_ts,
                 datetime.datetime.fromtimestamp(int(dir_modify_unix_ts)).strftime('%Y-%m-%d %H:%M:%S'))
    return dir_modify_unix_ts

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

    apt_archives_unix = get_dir_modify_time(apt_archives)

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
