#!/usr/bin/env python

import os
import sys
import glob
import subprocess
import StringIO

import ConfigParser

########################
## Helper functions
########################

class InvalidAnswer(Exception):
    def __init__(self, msg):
        Exception.__init__(self)
        self.msg = msg
    def __str__(self):
        return self.msg

class Utils(object):
    '''Groups all helper functions here'''
    @staticmethod
    def highlight(content):
        '''Add ANSI color to content to get it highlighted on terminal'''
        return '\x1b[33m%s\x1b[m' % content

    @staticmethod
    def info(msg, newline=True):
        sys.stdout.write(msg)
        if newline:
            sys.stdout.write('\n')

    @staticmethod
    def error(msg):
        '''Print error and exit'''
        print
        print 'Error: ' + msg
        sys.exit(1)

    @staticmethod
    def run_argv(argv, cwd=None, env=None, suppress_stdout=False, suppress_stderr=False):
        '''Run a program and wait it to finish, and return its exit code. The
        standard output of this program is supressed.

        '''
        with open(os.devnull, 'w') as devnull:
            if suppress_stdout:
                stdout = devnull
            else:
                stdout = sys.stdout

            if suppress_stderr:
                stderr = devnull
            else:
                stderr = sys.stderr

            proc = subprocess.Popen(argv,
                                    cwd=cwd,
                                    stdout=stdout,
                                    stderr=stderr,
                                    env=env)
            return proc.wait()

    @staticmethod
    def run(cmdline, cwd=None, env=None, suppress_stdout=False, suppress_stderr=False):
        '''Like run_argv but specify a command line string instead of argv'''
        with open(os.devnull, 'w') as devnull:
            if suppress_stdout:
                stdout = devnull
            else:
                stdout = sys.stdout

            if suppress_stderr:
                stderr = devnull
            else:
                stderr = sys.stderr

            proc = subprocess.Popen(cmdline,
                                    cwd=cwd,
                                    stdout=stdout,
                                    stderr=stderr,
                                    env=env,
                                    shell=True)
            return proc.wait()

    @staticmethod
    def prepend_env_value(name, value, env=None, seperator=':'):
        '''prepend a new value to a list'''
        if env is None:
            env = os.environ

        try:
            current_value = env[name]
        except KeyError:
            current_value = ''

        new_value = value
        if current_value:
            new_value += seperator + current_value

        env[name] = new_value

    @staticmethod
    def must_mkdir(path):
        '''Create a directory, exit on failure'''
        try:
            os.mkdir(path)
        except OSError, e:
            Utils.error('failed to create directory %s:%s' % (path, e))

    @staticmethod
    def find_in_path(prog):
        if 'win32' in sys.platform:
            sep = ';'
        else:
            sep = ':'

        dirs = os.environ['PATH'].split(sep)
        for d in dirs:
            d = d.strip()
            if d == '':
                continue
            path = os.path.join(d, prog)
            if os.path.exists(path):
                return path

        return None

    @staticmethod
    def read_config(fn=None):
        '''Return a case sensitive ConfigParser by reading the file "fn"'''
        cp = ConfigParser.ConfigParser()
        cp.optionxform = str
        if fn:
            cp.read(fn)

        return cp

    @staticmethod
    def write_config(cp, fn):
        '''Return a case sensitive ConfigParser by reading the file "fn"'''
        with open(fn, 'w') as fp:
            cp.write(fp)

    @staticmethod
    def ask_question(desc,
                     key=None,
                     note=None,
                     default=None,
                     validate=None,
                     yes_or_no=False,
                     password=False):
        '''Ask a question, return the answer.
        @desc description, e.g. "What is the port of ccnet?"

        @key a name to represent the target of the question, e.g. "port for
        ccnet server"

        @note additional information for the question, e.g. "Must be a valid
        port number"

        @default the default value of the question. If the default value is
        not None, when the user enter nothing and press [ENTER], the default
        value would be returned

        @validate a function that takes the user input as the only parameter
        and validate it. It should return a validated value, or throws an
        "InvalidAnswer" exception if the input is not valid.

        @yes_or_no If true, the user must answer "yes" or "no", and a boolean
        value would be returned

        @password If true, the user input would not be echoed to the
        console

        '''
        assert key or yes_or_no
        # Format description
        print
        if note:
            desc += '\n' + note

        desc += '\n'
        if yes_or_no:
            desc += '[ yes or no ]'
        else:
            if default:
                desc += '[ default "%s" ]' % default
            else:
                desc += '[ %s ]' % key

        desc += ' '
        while True:
            # prompt for user input
            if password:
                answer = getpass.getpass(desc).strip()
            else:
                answer = raw_input(desc).strip()

            # No user input: use default
            if not answer:
                if default:
                    answer = default
                else:
                    continue

            # Have user input: validate answer
            if yes_or_no:
                if answer not in ['yes', 'no']:
                    print Utils.highlight('\nPlease answer yes or no\n')
                    continue
                else:
                    return answer == 'yes'
            else:
                if validate:
                    try:
                        return validate(answer)
                    except InvalidAnswer, e:
                        print Utils.highlight('\n%s\n' % e)
                        continue
                else:
                    return answer

    @staticmethod
    def validate_port(port):
        try:
            port = int(port)
        except ValueError:
            raise InvalidAnswer('%s is not a valid port' % Utils.highlight(port))

        if port <= 0 or port > 65535:
            raise InvalidAnswer('%s is not a valid port' % Utils.highlight(port))

        return port

    @staticmethod
    def get_python_executable():
        '''Find a suitable python executable'''
        try_list = [
            'python2.7',
            'python27',
            'python2.6',
            'python26',
        ]


        for prog in try_list:
            path = Utils.find_in_path(prog)
            if path is not None:
                return path

        path = os.environ.get('PYTHON', 'python')

        if not path:
            Utils.error('Can not find python executable')

        return path

    @staticmethod
    def pkill(process):
        '''Kill the program with the given name'''
        argv = [
            'pkill', '-f', process
        ]

        Utils.run_argv(argv)


    @staticmethod
    def check_file(path):
        if not os.path.isfile(path):
            Utils.error("Cannot find file %s" % path)


class EnvManager(object):
    '''System environment and directory layout'''
    def __init__(self):
        self.install_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.install_path = os.path.realpath(os.path.join(self.install_path, 'seafile-server-latest'))

        self.top_dir = os.path.dirname(self.install_path)
        self.bin_dir = os.path.join(self.install_path, 'seafile', 'bin')
        self.central_config_dir = os.path.join(self.top_dir, 'conf')

        self.pro_data_dir = os.path.join(self.top_dir, 'pro-data')
        self.pro_program_dir = os.path.join(self.install_path, 'pro')
        self.pro_pylibs_dir = os.path.join(self.pro_program_dir, 'python')
        self.pro_misc_dir = os.path.join(self.pro_program_dir, 'misc')

        self.seafes_dir = os.path.join(self.pro_pylibs_dir, 'seafes')
        self.seahub_dir = os.path.join(self.install_path, 'seahub')

        self.ccnet_dir = os.path.join(self.top_dir, 'ccnet')
        self.seafile_dir = ''
        self.central_config_dir = os.path.join(self.top_dir, 'conf')

    def read_seafile_conf_dir(self):
        '''Read seafile conf dir from ccnet/seafile.ini'''
        seafile_ini = os.path.join(self.ccnet_dir, 'seafile.ini')
        with open(seafile_ini, 'r') as fp:
            path = fp.read()

        self.seafile_dir = path.strip()

    def get_seahub_env(self):
        '''Prepare for seahub syncdb'''
        env = dict(os.environ)
        env['CCNET_CONF_DIR'] = self.ccnet_dir
        env['SEAFILE_CONF_DIR'] = self.seafile_dir
        env['SEAFILE_CENTRAL_CONF_DIR'] = self.central_config_dir
        env['SEAFES_DIR'] = self.seafes_dir
        env['SEAHUB_DIR'] = self.seahub_dir
        self.setup_python_path(env)
        return env

    def read_keeper_conf(self):
        '''Read keeper config file'''
        '''
FILES=( $(find ${SEAFILE_DIR} -maxdepth 1 -type f -name "keeper*.properties") )
( [[ $? -ne 0 ]] || [[ ${#FILES[@]} -eq 0 ]] ) && err_and_exit "Cannot find instance properties file in ${SEAFILE_DIR}"
[[ ${#FILES[@]} -ne 1 ]] && err_and_exit "Too many instance properties files in ${SEAFILE_DIR}:\n ${FILES[*]}"
PROPERTIES_FILE="${FILES[0]}"
source "${PROPERTIES_FILE}"
if [ $? -ne 0  ]; then
	err_and_exit "Cannot intitialize variables"
fi
        '''
        conf_files = glob.glob(self.top_dir + '/keeper*.ini')
        if not conf_files:
            Utils.error('Cannot find KEEPER config files')

        self.keeper_config = ConfigParser.ConfigParser()
        self.keeper_config.optionxform = str
        self.keeper_config.readfp(open(conf_files[0]))
        print(self.keeper_config.items('seafile'))


        # find file properties file
        # keeper_ini =
        # get Config


    def setup_python_path(self, env):
        '''And PYTHONPATH and CCNET_CONF_DIR/SEAFILE_CONF_DIR to env, which is
        needed by seahub

        '''
        extra_python_path = [
            self.pro_pylibs_dir,

            os.path.join(self.top_dir, 'conf'), # LDAP sync has to access seahub_settings.py
            os.path.join(self.install_path, 'seahub', 'thirdpart'),
            os.path.join(self.install_path, 'seahub-extra'),
            os.path.join(self.install_path, 'seahub-extra', 'thirdparts'),

            os.path.join(self.install_path, 'seafile/lib/python2.6/site-packages'),
            os.path.join(self.install_path, 'seafile/lib64/python2.6/site-packages'),
            os.path.join(self.install_path, 'seafile/lib/python2.7/site-packages'),
            os.path.join(self.install_path, 'seafile/lib64/python2.7/site-packages'),
        ]

        for path in extra_python_path:
            Utils.prepend_env_value('PYTHONPATH', path, env=env)

########################
## END helper functions
########################

def do_deploy(args):
    '''
    Deploy conf/ directory
    function deploy_conf () {
        check_file "$PROPERTIES_FILE" "Cannot find properties file $PROPERTIES_FILE for the instance"
        for i in seahub_settings.py ccnet.conf seafile.conf seafevents.conf seafdav.conf; do
            deploy_file "conf/$i" "-p" "$PROPERTIES_FILE"
        done
    }
    '''
    if args.all:
        Utils.info('do deploy --all')
    elif args.conf:
        # Utils.check_file($PROPERTIES_FILE)
        pass
    else:
        env_mgr.read_keeper_conf()
        Utils.info('do deploy smth.')

def do_restore(args):
    if args.seafile_src_to_ext:
        Utils.info('do seafile-src-to-ext')
    else:
        Utils.info('smth. else')

def do_generate(args):
    if args.i18n:
        Utils.info('Generate i18n...')
        Utils.run("./i18n.sh compile-all", cwd=env_mgr.seahub_dir)
        Utils.info('Done.')
    if args.min_css:
        Utils.info('Generate seahub.min.css...')
        Utils.run("yui-compressor -v seahub.css -o seahub.min.css", cwd=os.path.join(env_mgr.seahub_dir, 'media', 'css'))
        Utils.info('Done.')


# def handle_virus_scan_commands(args):
    # env_mgr.read_seafile_conf_dir()
    # argv = [
        # Utils.get_python_executable(),
        # '-m', 'seafevents.virus_scanner.run_virus_scan',
        # '-c', os.path.join(env_mgr.central_config_dir, 'seafevents.conf'),
    # ]

    # Utils.run_argv(argv, env=env_mgr.get_seahub_env())


env_mgr = EnvManager()

def main():
    try:
        import argparse
    except ImportError:
        sys.path.insert(0, glob.glob(os.path.join(env_mgr.pro_pylibs_dir, 'argparse*.egg'))[0])
        import argparse

    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(title='subcommands', description='')

    # deploy
    parser_deploy = subparsers.add_parser('deploy', help='Deploy KEEPER components')
    parser_deploy = parser_deploy.add_mutually_exclusive_group()
    parser_deploy.set_defaults(func=do_deploy)
    parser_deploy.add_argument('--all', help='deploy all KEEPER components', action='store_true')
    parser_deploy.add_argument('--conf', help='deploy KEEPER configurations', action='store_true')
    parser_deploy.add_argument('--http-conf', help='deploy http-conf', action='store_true')
    parser_deploy.add_argument('-f', '--file', help='deploy file(s)', nargs='+')
    parser_deploy.add_argument('-d', '--directory', help='deploy directory', nargs=1)

    # restore
    parser_restore = subparsers.add_parser('restore', help='Restore files')
    parser_restore.set_defaults(func=do_restore)
    parser_restore.add_argument('--seafile-src-to-ext', help='Restore all KEEPER files from overriden seafile src files', action='store_true')

    # generate
    parser_generate = subparsers.add_parser('generate', help='Generate components')
    parser_generate.set_defaults(func=do_generate)
    parser_generate.add_argument('--i18n', help='Compile i18n files', action='store_true')
    parser_generate.add_argument('--min-css', help='Generate min.css file for seahub.css', action='store_true')




    if len(sys.argv) == 1:
        print parser.format_help()
        return

    args = parser.parse_args()

    print(args)

    args.func(args)


# case "$1" in
    # deploy-all)
        # create_and_deploy_directories "scripts" "seahub-data"
        # create_custom_link
        # deploy_directories "seafile-server-latest"
        # deploy_conf
		# #TODO: create_server_script_links
		# $0 compile-i18n
		# deploy_http_conf
        # migrate_avatars
    # ;;

    # deploy-conf)
        # deploy_conf
	# ;;

    # deploy-http-conf)
        # deploy_http_conf
	# ;;

    # deploy)
        # [ -z "$2" ] && ($0 || exit 1 )
        # deploy_file $2 $3 $4
    # ;;

    # deploy-dir)
        # [ -z "$2" ] && ($0 || exit 1 )
        # deploy_directories "${@:2}"
    # ;;

    # restore)
        # restore_directories "seafile-server-latest"
        # remove_custom_link
    # ;;

    # clean-all)
        # $0 restore
        # rm -rfv $SEAFILE_DIR/seahub-data
    # ;;

    # compile-i18n)
        # pushd $SEAFILE_LATEST_DIR/seahub
        # ./i18n.sh compile-all
        # popd
    # ;;

    # copy-seafile-sources-in-ext)
         # copy_seaf_src_to_ext
    # ;;

    # min.css)
        # pushd $SEAFILE_LATEST_DIR/seahub/media/css
        # yui-compressor -v seahub.css -o seahub.min.css
        # popd
    # ;;


    # *)
        # echo "Usage: $0 {deploy-all|deploy-conf|deploy-http-conf|deploy <file> [-p <properties-file>]|deploy-dir <dir>|restore|clean-all|compile-i18n|copy-seafile-sources-in-ext|min.css}"
        # exit 1
     # ;;
# esac



    # parser = argparse.ArgumentParser()
    # subparsers = parser.add_subparsers(title='subcommands', description='')

    # # setup
    # parser_setup = subparsers.add_parser('setup', help='Setup extra components of seafile pro')
    # parser_setup.set_defaults(func=do_setup)
    # parser_setup.add_argument('--migrate', help='migrate from community version', action='store_true')

    # # for non-migreate setup
    # parser_setup.add_argument('--mysql', help='use mysql', action='store_true')
    # parser_setup.add_argument('--mysql_host')
    # parser_setup.add_argument('--mysql_port')
    # parser_setup.add_argument('--mysql_user')
    # parser_setup.add_argument('--mysql_password')
    # parser_setup.add_argument('--mysql_db')

    # # search
    # parser_search = subparsers.add_parser('search', help='search related utility commands')
    # parser_search.add_argument('--update', help='update seafile search index', action='store_true')
    # parser_search.add_argument('--clear', help='delete seafile search index', action='store_true')
    # parser_search.set_defaults(func=handle_search_commands)

    # # ldapsync
    # parser_ldap_sync = subparsers.add_parser('ldapsync', help='ldap sync commands')
    # parser_ldap_sync.add_argument('-t', '--test', help='test ldap sync', action='store_true')
    # parser_ldap_sync.set_defaults(func=handle_ldap_sync_commands)

    # # virus scan
    # parser_virus_scan = subparsers.add_parser('virus_scan', help='virus scan commands')
    # parser_virus_scan.set_defaults(func=handle_virus_scan_commands)

    # if len(sys.argv) == 1:
        # print parser.format_help()
        # return

    # args = parser.parse_args()
    # args.func(args)

if __name__ == '__main__':
    main()
    print "test"
