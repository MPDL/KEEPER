#!/usr/bin/env python

import os
import sys
import glob
import subprocess
import StringIO
import shutil

import ConfigParser


BACKUP_POSTFIX = '_orig'

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
        '''Create a directory recursively, exit on failure'''
        try:
            os.mkdirs(path)
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

    @staticmethod
    def check_dir(path):
        if not os.path.isdir(path):
            Utils.error("Cannot find dir %s" % path)

class EnvManager(object):
    '''System environment and directory layout'''
    def __init__(self):
        self.install_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.install_path = os.path.join(self.install_path, 'seafile-server-latest')

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
        '''Read keeper config file and set keeper related properties '''
        conf_files = glob.glob(self.top_dir + '/keeper*.ini')
        if not conf_files:
            Utils.error('Cannot find KEEPER config files')

        self.keeper_config = ConfigParser.ConfigParser()
        self.keeper_config.optionxform = str
        self.keeper_config.readfp(open(conf_files[0]))

        self.custom_link = os.path.join(self.install_path, 'seahub', 'media', 'custom')
        self.custom_dir = os.path.join(self.seafile_dir, 'seahub-data', 'custom')

        self.keeper_ext_dir = os.path.join(self.top_dir, 'KEEPER', 'seafile_keeper_ext')

        self.SEAF_EXT_DIR_MAPPING = {
            'conf': os.path.join(self.top_dir, 'conf'),
            'seafile-server-latest': self.install_path,
            'seahub-data': os.path.join(self.top_dir, 'seahub-data'),
            'scripts': os.path.join(self.top_dir, 'scripts'),
            'http': os.path.join(self.keeper_config.get('http', '__HTTP_CONF_ROOT_DIR__'), 'sites-available'),
        }

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

def create_custom_link():
    """
    Create link to custom directory for seafile customization,
    see http://manual.seafile.com/config/seahub_customization.html
    TO BE TESTED!!!!
    """
    if os.path.islink(env_mgr.custom_link):
        Utils.info("Link {} already exists, skipping!".format(env_mgr.custom_link))
    else:
        if not os.path.isdir(env_mgr.custom_dir):
            Utils.info("{} does not exist, creating".format(env.custom_dir))
            Utils.must_mkdir(env_mgr.custom_dir)
        os.symlink(env_mgr.custom_dir, env_mgr.custom_link)



def expand_properties(content):
    for section in env_mgr.keeper_config.sections():
        for key, value in env_mgr.keeper_config.items(section):
            content = content.replace(key, value)
    return content

def backup_file(path):
    back_path = path + BACKUP_POSTFIX
    if os.path.exists(back_path):
        Utils.info("Backup already exists: {}, skipping!".format(path + BACKUP_POSTFIX))
    else:
        try:
            Utils.info("Backup {} to {}".format(path, back_path))
            os.rename(path, path + BACKUP_POSTFIX)
        except Exception as e:
            Utils.error("Cannot backup {}, error: {}".format(path, repr(e)))



def deploy_file(path, dest_dir=None):

    Utils.check_file(path)

    p = path.strip('/').split('/')

    if not dest_dir:
        if not p[0] in env_mgr.SEAF_EXT_DIR_MAPPING:
            Utils.error("Cannot find dest directory mapping for " + path )
        dest_dir = env_mgr.SEAF_EXT_DIR_MAPPING[p[0]]

    dest_path = dest_dir + '/' + '/'.join(p[1:])

    if not os.path.isdir(dest_dir):
        Utils.info("Create dir <{}>".format(dest_dir))
        Utils.must_mkdir(dest_dir)
    if os.path.exists(dest_path):
        backup_file(dest_path)
    else:
        if not Utils.ask_question("Deploy file {} into {}?".format(path, dest_path),
                                default="yes",
                                yes_or_no=True):
            return

    fin = open(path, 'r')
    content = expand_properties(fin.read())
    fin.close()

    fout = open(dest_path, 'w')
    fout.write(content)
    fout.close()
    Utils.info(Utils.highlight("{} has been deployed into {}".format(path, dest_path)))

    # Utils.info(dest_path)

def deploy_dir(path):
    Utils.check_dir(path)
    for file in os.listdir(path):
        deploy_file(path + '/' + file)

def deploy_http_conf():
    path = 'http'
    Utils.check_dir(path)
    opts = dict(env_mgr.keeper_config.items('http'))

    for file in [opts['__MAINTENANCE_HTTP_CONF__'], opts['__HTTP_CONF__']]:
        deploy_file('http/' + file)

    deploy_file('http/' + opts['__MAINTENANCE_HTML__'], dest_dir=opts['__HTML_DEFAULT_DIR__'])

def do_deploy(args):

    if args.all:
        # TODO
        # Utils.info('do deploy --all')
        # for path in ['scripts', 'seahub-data', 'conf']:
           # deploy_dir(path)
        # create_custom_link()
        # deploy_dir('seafile-server-latest')
        # do_generate(type('',(object,),{"i18n": True, "min_css": False})())
        # deploy_http_conf()
        pass
    elif args.conf:
        deploy_dir('conf')
    elif args.http_conf:
        deploy_http_conf()
    else:
        if args.directory:
            for path in args.directory:
                deploy_dir(path)
        if args.file:
            for path in args.file:
                deploy_file(path)

        # check file

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
        cmd = "yui-compressor -v seahub.css -o seahub.min.css"
        RC = Utils.run(cmd, cwd=os.path.join(env_mgr.seahub_dir, 'media', 'css'))
        if RC != 0:
            Utils.error("Cannot run {}, RC={}".format(cmd, RC))

def do_upgrade(args):
    print('Upgrade')

    print env_mgr.keeper_ext_dir
    # for root, dirs, files in os.walk(os.path.join(env_mgr.keeper_ext_dir, 'seafile-server-latest')):
    for root, dirs, files in os.walk('seafile-server-latest'):
        if  files and \
            not ('/keeper' in root
                or '/.rope' in root or '/.cache' in root or '/__pycache__' in root
                or '/.git' in root or '/tags' in root
            ):
            for file in files:
                if not (file.endswith('.pyc') or file.endswith('.png')):
                    dest_path = os.path.join(root, file)
                    src_path = os.path.join(env_mgr.top_dir, dest_path)
                    print("Copy from {} to {}".format(src_path, dest_path))
                    shutil.copy(src_path, dest_path)


env_mgr = EnvManager()

def main():
    try:
        import argparse
    except ImportError:
        sys.path.insert(0, glob.glob(os.path.join(env_mgr.pro_pylibs_dir, 'argparse*.egg'))[0])
        import argparse

    env_mgr.read_keeper_conf()

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
    parser_deploy.add_argument('-d', '--directory', help='deploy directory(s)', nargs='+')

    # restore
    # parser_restore = subparsers.add_parser('restore', help='Restore files')
    # parser_restore.set_defaults(func=do_restore)
    # parser_restore.add_argument('--seafile-src-to-ext', help='Restore all KEEPER files from overriden seafile src files', action='store_true')

    # upgrade
    parser_upgrade = subparsers.add_parser('upgrade', help='Upgrade KEEPER')
    parser_upgrade.set_defaults(func=do_upgrade)
    parser_upgrade.add_argument('--seafile-src-to-ext', help='''Upgrade KEEPER ext files to current Seafile sources.
                                Upgrade should be done BEFORE deploy-all command, on fresh untarred seafile-server files.
                                Upgraded files should be merged with the current KEEPER code!
                                Check https://keeper.mpdl.mpg.de/lib/a0b4567a-8f72-4680-8a76-6100b6ebbc3e/file/Keeper%%20System%%20Administration/Upgrade2Current-Seafie.md
                                ''', action='store_true')

    # generate
    parser_generate = subparsers.add_parser('generate', help='Generate components')
    parser_generate.set_defaults(func=do_generate)
    parser_generate.add_argument('--i18n', help='Compile i18n files', action='store_true')
    parser_generate.add_argument('--min-css', help='''Generate min.css file for seahub.css.
                                 Please install yui-compressor: http://yui.github.io/yuicompressor in your system!
                                 ''', action='store_true')


    if len(sys.argv) == 1:
        print parser.format_help()
        return

    args = parser.parse_args()
    print(args)
    args.func(args)


if __name__ == '__main__':
    main()
