# Perforce Helix P4 lifecycle, local server 

hosted @ http://drgtest11-ubuntu (i.e. https://10.20.5.8) 

see [tutorial](https://www.perforce.com/resources/tutorials/distributed-versioning-tutorial)

## Prerequisits
* install `helix-cli` and `helix-p4d`, see https://www.perforce.com/perforce-packages/helix-versioning-engine

## create local repo
``````
cd test_repo
p4 init -C0 

``````

## check env
``````
p4 set
p4 server
p4 info

``````

## issue changes
``````
p4 changes (shows submissions)
p4 status (shows status)
p4 rec (i.e. reconcile prompted action)
``````

## submit changes
``````
p4 submit -d "initial add my files"
``````

## submit new changes 
``````
p4 status (shows new reconcile actions, e.g edit)
p4 rec (reconcile, e.g. edit)
p4 submit -d "edit some files"

``````

## create a branch
``````
p4 switch -c dev
p4 switch -l (show a list of branches + current one marked with *)
p4 rec
p4 submit -d "dev fix"
p4 files (shows changes number)
``````

## switch to other branch
``````
p4 switch <name of branch> (e.g. main)
``````

## merge branch
``````
p4 merge --from <name of branch> (e.g. dev)
p4 resolve (resolves conflicts)
p4 submit -d "edit some files"
p4 changes

``````

# Working on shared repos
**NOTE**: following params should be set up central server, see https://www.perforce.com/blog/151111/helix-dvcs-administer-pro
``````
p4 configure set server.allowpush=3
p4 configure set server.allowfetch=3
``````
## clone on local PC from shared server

``````
 p4 clone -p ssl:gitswarm:1666 -f //gitswarm/projects/vlad/p5vlad/master/...
``````
**NOTES**: 
* scope of cloned files can be precisely defined with `-f`
* `-m depth` allows [shallow cloning](https://www.perforce.com/blog/150812/helix-dvcs-%E2%80%93-clone-pro-part-2): 
>> This option will ensure that at most depth revisions are cloned and transferred, typically making the cloning process faster and your resulting personal server smaller

## check servers
``````
p4 servers (shows local)
p4 remotes (shows remote servers)
``````
than make changes, reconcile to edit, submit changes and 

## push on remote
``````
p4 push
``````
### resolve resolve conflicts with shared server if any exist:
``````
p4 fetch -u
p4 resubmit -m (merge, resolve conflicts and submit)
p4 push (if any conflict are resolved)
``````

## work with p4v with local server
see [Personal server](https://www.perforce.com/blog/151111/helix-dvcs-administer-pro)
* start local server with 
````
p4d -r `p4 set -q P4INITROOT | sed 's/P4INITROOT=//'`/.p4root -p 1666 -d
````
* connect to it with p4v to `localhost:1666`
* create new workspace, stream field must be chosen!!!
* set `p4 set P4PORT=localhost:1666` and `p4 set P4CLIENT=<name of newly created WS, e.g. vlad_N117_3825>`
* check `p4 client`
now all changes can be submitted from WS to local server (rec/submit), and from cloned directory can be pushed to shared repo. 

## workflow with big files (suggested)
Exclude BLOBs from git control, they will be controlled p4. Git Fusion repo created by GitSwarm should be updated following way:
* change `.git-fusion/repos/<name-of-repo>/p4gf_config` from p4v

````
	....
[master]
view = //gitswarm/projects/vlad/p5vlad/master/... ... (auto generated)
        -//gitswarm/projects/vlad/p5vlad/master/BLOB3/... BLOB3/... (<-add here directory 1 to be excluded from git control, etc. from new line prfixed with -)
	....

````