#!/usr/bin/python
import sys
import os
from enum import Enum
from ftplib import FTP
from getpass import getpass

host = str()


class ArgumentKeys(Enum):
    HOST = 0
    PORT = 1
    USER = 2
    PASSWORD = 3
    TRANSFER_FILE = 4,
    CWD = 5


def print_usage() -> None:
    print('Usage ftp [options] host.')
    print('\t-port\t- Set port for connection')
    print('\t-u\t\t- Set user')
    print('\t-p\t\t- Set password')
    print('\t-t\t\t- Set path to file for transfer to ftp server')
    print('\t-cwd\t\t - Set base directory.')


def parse_arguments() -> dict:
    args = \
        {
            ArgumentKeys.TRANSFER_FILE: []
        }
    arg_key = ArgumentKeys.HOST

    if len(sys.argv) < 2:
        print_usage()
        sys.exit(1)

    for arg in sys.argv[1:]:
        if arg == '-port':
            arg_key = ArgumentKeys.PORT
        elif arg == '-u':
            arg_key = ArgumentKeys.USER
        elif arg == '-p':
            arg_key = ArgumentKeys.PASSWORD
        elif arg == '-t':
            arg_key = ArgumentKeys.TRANSFER_FILE
        elif arg == '-cwd':
            arg_key = ArgumentKeys.CWD
        else:
            if arg_key == ArgumentKeys.TRANSFER_FILE:
                args[arg_key].append(arg)
            else:
                args[arg_key] = arg
            arg_key = ArgumentKeys.HOST
    return args


def parse_host(host_name: str) -> (str, str, str):
    user = str()
    h = str()
    pwd = str()
    value = str()

    for c in host_name:
        if c == '@':
            user = value
            value = ''
        elif c == ':':
            h = value
            value = ''
        else:
            value += c

    if not h:
        h = value
    else:
        pwd = value

    return h, user, pwd


def try_connect(ftp: FTP, args: dict) -> bool:
    global host
    host = args.get(ArgumentKeys.HOST)
    if not host:
        host = input('Input host name: ')
        if not host or host.isspace():
            return False

    port = args.get(ArgumentKeys.PORT)
    if not port or not port.isdigit():
        port = '21'

    (h, u, p) = parse_host(host)

    host = h

    user = args.get(ArgumentKeys.USER)
    if not user or user.isspace():
        args[ArgumentKeys.USER] = u

    pwd = args.get(ArgumentKeys.CWD)
    if not pwd or pwd.isspace():
        args[ArgumentKeys.CWD] = p

    try:
        print(ftp.connect(host, int(port)))
        return True
    except BaseException as ex:
        print("Connect error: {}".format(ex))
        return False


def try_login(ftp: FTP, args: dict) -> bool:
    user = args.get(ArgumentKeys.USER);
    password = args.get(ArgumentKeys.PASSWORD)

    try_count = 0
    while True:
        try:
            status = ftp.login(user, password)
            print(status)
            return True
        except BaseException as ex:
            print("Login error: {}".format(ex))
            try_count += 1
            if try_count > 3:
                return False

            if not user or user.isspace():
                user = input('User ' + host + ': ')
            if not user or user.isspace():
                return False
            password = getpass("{} password: ".format(user))


def try_transfer_file(ftp: FTP, path: str) -> bool:
    try:
        if os.path.isfile(path):
            name =  os.path.basename(path)
            print("Sending file: {}...".format(name))
            file = open(path, 'rb')
            ftp.storbinary("STOR {}".format(name), file)
            file.close()
        elif os.path.isdir(path):
            name = os.path.basename(path)
            print("Make directory: {}".format(name))
            ftp.mkd(name)
            ftp.cwd(name)
            for f in os.listdir(path):
                local_path = os.path.join(path, f)
                if not try_transfer_file(ftp, local_path):
                    return False
            ftp.cwd('..')

        return True
    except BaseException as ex:
        print("Transfer file {} error: {}.".format(path, ex))
        return False


def try_transfer_files(ftp: FTP, args: dict) -> bool:
    files = args.get(ArgumentKeys.TRANSFER_FILE)
    if not files:
        return True

    for f in files:
        if not try_transfer_file(ftp, f):
            return False

    return True


def main():
    args = parse_arguments()
    ftp = FTP()

    if not try_connect(ftp, args):
        sys.exit(1)

    if not try_login(ftp, args):
        sys.exit(1)

    if not try_transfer_files(ftp, args):
        sys.exit(1)

    cwd = args.get(ArgumentKeys.CWD)
    if cwd and not cwd.isspace():
        ftp.cwd(cwd)

    ftp.quit()


if __name__ == '__main__':
    main()
