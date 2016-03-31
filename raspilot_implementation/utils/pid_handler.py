import os

import sys


class PidHandler:
    def __init__(self, pids_dir_path, pid_name):
        self.__pids_dir_path = pids_dir_path
        self.__pid_name = pid_name
        self.__pid_file = None

    def create_pid_file(self):
        """
        Creates PID file
        @return: returns path to pid_file
        """
        pid = str(os.getpid())
        if not os.path.exists(self.__pids_dir_path):
            os.makedirs(self.__pids_dir_path)
        pid_file = os.path.join(self.__pids_dir_path, self.__pid_name)
        if os.path.isfile(pid_file):
            print("{} already exists, exiting".format(pid_file))
            sys.exit()
        f = open(pid_file, 'w')
        f.write(pid)
        f.close()
        self.__pid_file = pid_file

    def remove_pid_file(self):
        """
        Removes PID file.
        @param pid_file path to the pidfile
        @type pid_file str
        @return: return nothing
        """
        if self.__pid_file:
            os.unlink(self.__pid_file)
