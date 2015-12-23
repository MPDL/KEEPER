# Server drg-srv1-ref
IP: 10.20.5.7

user: saquet+sudo


## OwnCloud: http://10.20.5.7:81/owncloud
user: admin

password: dRgOwnCl

user: vlad

password: D_4tXWzb

start-stop: service apache2 start/stop

## GitLabCE 8.2: https://10.20.5.7 or https://drg-srv1-ref
user: root

password: oviN-TMDubRzz6PC

user: vlad

password: -PRHop5X

start-stop: gitlab-ctl start/stop

## plain git-annex central bare repository
URL: ssh://share@10.20.5.7/data/annex.git

user: share

password: share 


# clients

## Linux schulung06, i.e. drgtest06-ubuntu, 
IP: 10.20.5.11 

user: user1

password: dRgTeSt_0

## installed:
* ownCloud client
* git-annex 
* git-annex repo, clone of ssh://share@10.20.5.7/data/annex.git: ~/annex
* gitlab git-anex repo, clone of git@drg-srv1-ref:vlad/annex-faces-images.git: ~/annex-faces-images

## windows 7 @ shulung-res, i.e. drg-test08
IP: 10.20.5.17

no password

## installed:
* ownCloud client
* git bash
* git-annex 
* gitlab git-anex repo, clone of http://vlad@drg-srv1-ref/vlad/annex-faces-images.git: (in git-bash) /c/Users/drg-test08/gitlab-annex/annex-faces-images


# shares with content
//filesvr01.mucam.mpg.de/share/mpdl/all/Inno/BLOB