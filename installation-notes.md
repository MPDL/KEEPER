# [git-annex](https://git-annex.branchable.com/)
> git-annex is designed for git users who love the command line.

## installation 
* [Ubuntu](https://git-annex.branchable.com/install/Ubuntu/) 
  * `sudo apt-get install git-annex`: out of box 
  * `annex assiatant`: works, but emerges OpenSSH password issue
    * **problems**
      * installation is tricky
      * deep git knowledges is needed

* [Windows 7](https://git-annex.branchable.com/install/Windows/) 
  * **NOTES**: 
    * only works with 32 bit version of git
    * run `git annex test` for git-annex installation info

## Conclusion
* fallback in `direct mode` (e.g. always for windows) does not guarantee versioning! 

> With direct mode, you're operating without large swathes of git-annex's carefully constructed safety net, which ensures that past versions of files are preserved and can be accessed. With direct mode, any file can be edited directly, or deleted at any time, and there's no guarantee that the old version is backed up somewhere else.

**NOTE**: [mpdl-techwatch](https://techwatch.mpdl.mpg.de/git-annex/)

# [ownCloud](https://owncloud.org/)

* DRG server: http://10.20.5.7:81/owncloud/

* installed version: 8.1.3

## problems
* ubuntu clients 1.5 & 1.7 from apt-get cannot authenticate!!! (see (https://forum.owncloud.org/viewtopic.php?t=29187&p=91290) and (https://doc.owncloud.org/server/8.1/admin_manual/release_notes.html#changes-in-8-1)
  * solution: install the client directly from ownCloud suggested software repository, e.g. for Ubuntu, from here: https://software.opensuse.org/download/package?project=isv:ownCloud:desktop&package=owncloud-client

> apt-get install owncloud-client

* **TODO**: email settings for sharing per email 


# [GitLab](https://gitlab.com)

* DRG server: https://10.20.5.7

* installed version: CE 8.2.1

## installation
* out-of-box for Ubuntu server, e.g. https://about.gitlab.com/downloads-ee/ 
* [git-annex support](https://about.gitlab.com/2015/02/17/gitlab-annex-solves-the-problem-of-versioning-large-binaries-with-git/) should be switched on manually in `gitlab.rb`:

> ## If enabled, git-annex needs to be installed on the server where gitlab is setup
> # For Debian and Ubuntu systems this can be done with: sudo apt-get install git-annex
> # For CentOS: sudo yum install epel-release && sudo yum install git-annex
> gitlab_shell['git_annex_enabled'] = true

* downgrade from EE to CE from 8.2 due to git-lfs support in CE, see [here](https://about.gitlab.com/2015/11/23/announcing-git-lfs-support-in-gitlab/)
```
  # gitlab-ctl uninstall
    for omnibus installation (see http://doc.gitlab.com/ee/downgrade_ee_to_ce/README.html):
  # gitlab-rails runner "Service.where(type: 'JenkinsService').delete_all" ) 
    or for source installation:
  $ bundle exec rails runner "Service.where(type: 'JenkinsService').delete_all" production
    check /etc/gitlab/gitlab.rb (e.g. remove git-annex support)
  # gitlab-ctl reconfigure
  # gitlab-ctl start
```

# [git-lfs](https://git-lfs.github.com/)
support of the feature is promised for GitHub enterprise 2.4 and current GitHub.com, see e.g. https://help.github.com/articles/collaboration-with-git-large-file-storage/ and announced for GitLab from version 8.2,  see https://about.gitlab.com/2015/11/23/announcing-git-lfs-support-in-gitlab/
>TODO: test CE 8.2 with git-lfs feature!

## git-lfs@github directly
* does not work for ubuntu 15.04 from [bash srcipt](https://packagecloud.io/github/git-lfs/install), should be installed directly from [.deb](https://packagecloud.io/github/git-lfs/packages/debian/jessie/git-lfs_1.0.0_amd64.deb) 
* problems:
  * no clear documentation for git-lfs workflow
  * not clear how to work with version of BLOBs 
>after pull/checkout/commit of LFS repository the pointers are overriden with real files, it not clear how to generate new pointers for v2
  * remote server should be server with Git Large File Storage support, otherwise the feature is not supported
  * Git Large File Storage on GitHub Enterprise is part of an early access technical preview. It is not currently supported for production use [See](https://help.github.com/enterprise/2.2/user/articles/configuring-git-large-file-storage/) . **NOTE**: useless feature
?gitswarm## git-lifs@[lfs-test-server](https://github.com/github/lfs-test-server)
  * to be installed from source from latest release https://github.com/github/lfs-test-server/releases (0.3.0 at the moment)
  * latest golang (1.5.1 at the moment) to be installed to compile the code: https://github.com/ethereum/go-ethereum/wiki/Installing-Go 
  * installation instructions:  
    * set `export GOPATH=/opt/git-lfs-server-test/lfs-test-server`
    * `go build`, `go get` all packages which are not found, then `go build` again. the ./lfs-test-server file should be created
    * set environment variables via script&run, see https://github.com/github/lfs-test-server#running
    * set [lfs]  url = "http://lsf_server_host:port/"  in local repo
  * problems:
    * only `git lfs push` on already created local lfs repo is possible, no way to clone/pull from remote repo has been found!!! 
    * very slow 

 
# [Git on the Server](https://git-scm.com/book/en/v2/Git-on-the-Server-The-Protocols)
## [Smart-HTTP](https://git-scm.com/book/en/v2/Git-on-the-Server-Smart-HTTP)
### unauthenticated clients
* to be very careful with apache settings like `a2enmod cgi alias env rewrite` etc.
* `mv hooks/post-update.sample hooks/post-update && git update-server-info` !!!!!
*  leave out `GIT_HTTP_EXPORT_ALL` for unauthenticated clients
### authenticated clients
* use apache mod dav_fs, see ftp://www.kernel.org/pub/software/scm/git/docs/v2.4.0/howto/setup-git-server-over-http.html
## [git://](https://git-scm.com/book/en/v2/Git-on-the-Server-The-Protocols#The-Git-Protocol)
### [installation](https://git-scm.com/book/en/v2/Git-on-the-Server-Git-Daemon) 


# [GitSwarm](https://www.perforce.com/downloads/helix-gitswarm)

* DRG server: http://10.20.5.8

* installed version: 2015.4/a2b7761

## installation
* install [server](https://www.perforce.com/perforce/r15.4/manuals/gitswarm/install/README.html) 
  * **NOTE**: control server with `p4dctl` 
* to install client you need to
 * install packages `helix-cli` and `helix-p4d`: https://www.perforce.com/perforce-packages/helix-versioning-engine
* helix visual client (`p4v`) can be downloaded from https://www.perforce.com/downloads/helix `P4V: VISUAL CLIENT` and used as described in https://www.perforce.com/documentation/tenminute-test-drive-linuxunix
* acces server via env variables, see `P4PORT` and `P4CHARSET` [variable settings](http://www.perforce.com/perforce/doc.current/manuals/cmdref/P4CHARSET.html) 

## installation from [OVA](https://www.perforce.com/node/9065), preferable?

# [Helix Swarm](https://www.perforce.com/perforce/doc.current/manuals/swarm/setup.packages.html#setup.packages.install)

* DRG server: http://10.20.5.8:81

* installed version: SWARM/2015.3/1257057 (2015/10/30)

* install packages `helix-swarm, helix-swarm-triggers, helix-swarm-optional`
* run script `$sudo /opt/perforce/swarm/sbin/configure-swarm.sh -i`
* **NOTE**: Web error 500, see here http://answers.perforce.com/articles/KB/3696, solution:
 * create group `p4 group never-expired`
 * set `Timeout: unlimited`
 * set `Users: root`
 * `p4 login root`
 * `p4 tickets`, copy ticket for root  
 * edit `/opt/perforce/swarm/data/config.php`:
```
...
'p4' => array(
        'port' => 'ssl:localhost:1666',
        'user' => 'root',
        'password' => '!!!paste_ticket!!!',
    ),
...
```
 * restart apache2