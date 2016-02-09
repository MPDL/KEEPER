# Performance testing

## ownCloud 

### **Server**: ownCloud Server 8.1.3 @ Ubuntu server 14.04 @ lenovo T430 laptop, 4CPU@2900 MHz 16GB RAM, Disk 500 GB;    

### **Data bundle** imeji Foto_images repo (3,3GB): 6164 JPGs in 3 folders

* **Client**: ownCloud Client 2.0.1 @ Ubuntu desktop 15.04 @ lenovo T530 laptop, 8CPUS@2300 MHz 16GB RAM, Disk 500 GB
* **Task**: sync/download 6164 jpegs/4,3GB locally
* **Result**: 6m15s

* **Client**: ownCloud Client 2.0.1 @ Ubuntu desktop 14.04 @ lenovo T430 laptop, 4CPUS@2600 MHz 8GB RAM, Disk 500 GB
* **Task**: sync/download 6164 jpegs/4,3GB loca
* **Result**: 6m16s

* **Client**: ownCloud Client 2.0.1 @ Windows 7 SP1 Prof @ lenovo T430 laptop, 4CPUS@2600 MHz 8GB RAM, Disk 500 GB
* **Task**: sync/download 6164 jpegs/4,3GB locally
* **Result**: 24m19s!!!! / 20m16s / 20m41s

* **Client**: ownCloud Client 2.0.1 @ Windows 7 SP1 Prof @ lenovo T430 laptop, 4CPUS@2600 MHz 8GB RAM, Disk 500 GB
* **Task**: sync/upload 6164 jpegs/4,3GB locally
* **Result**: 1h23m55s !!!!!!!!!!!!!!!!!!!!1

## GitLab

### **Server**: GitLab Server 8.0.4-ee @ Ubuntu server 14.04 @ lenovo T430 laptop, 4CPU@2900 MHz 16GB RAM, Disk 500 GB    

### **Data bundle** imeji Foto_images repo (3,3GB): 6164 JPGs in 3 folders

### Client PC: Schulung06 (Ununtu 14.04)
* **Task**: `git clone ...` 
* **Time**: 5m52s

* **Task**: `git add *` 
* **Time**: 20s

* **Task**: `git push origin master` 
* **Time**: 6m32s

* **Task**: `git push origin master` with `.gitattributes`:
```
*.jpg binary -delta
```
* **Time**: 5m13s


## git-annex, standalone 

### **Server**: remote central repository @ Ubuntu server 14.04 @ lenovo T430 laptop, 4CPU@2900 MHz 16GB RAM, Disk 500 GB;    

### **Data bundle** imeji Foto_images repo (3,3GB): 6164 JPGs in 3 folders

### Client PC: N117 (Ununtu 15.04)
* **Task**: `git annex add .` 
* **Time**: s52.62

* **Task**: push to server: `git annex sync --content`
* **Time**: 10m19.63

### Client PC: Schulung06 (Ununtu 14.04)
* **Task**: `git annex add .` 
* **Time**: s59.87

* **Task**: `git annex sync --content` (pull)
* **Time**: 7m15s

* **Task**: `git annex sync --content` (push)
* **Time**: 6m53s


## GitLab + git-annex support!!!

### **Server**: GitLab Server 8.0.4-ee @ Ubuntu server 14.04 @ lenovo T430 laptop, 4CPU@2900 MHz 16GB RAM, Disk 500 GB    

### Client PC: N117 (Ununtu 15.04)
* **Task**: `git annex add .` 
* **Time**: s38.72

* **Task**: `git annex sync --content` (push)
* **Time**: 22m31.99s

### Client PC: Schulung06 (Ununtu 14.04)
* **Task**: `git annex sync --content` (push)
* **Time**: 31m18s

* **Task**: `git annex sync --content` (pull)
* **Time**: 13m8s


## [git-lfs](https://git-lfs.github.com/)

### **Data bundle** imeji Foto_images repo (3,3GB): 6164 JPGs in 3 folders

### Client PC: N117 (Ununtu 15.04)
* **Task**: `git add *` 
* **Time**: s38.72


## [plain git](git-plain@drg-srv1-ref:/opt/git-plain/faces-images.git)

### **Data bundle** imeji Foto_images repo (3,3GB): 6164 JPGs in 3 folders
### Client PC: Schulung06 (Ununtu 14.04)

#### ssh://

* **Task**: `git add .` 
* **Time**: 3m4s

* **Task**: `git commit -am ''` 
* **Time**: 3s

* **Task**: `git push origin master`: *.jpg binary -delta 
* **Time**: 5m30s

* **Task**: `git push origin master`
* **Time**: 5m12s / 5m5s

* **Task**: `git clone git-plain@drg-srv1-ref:/opt/git-plain/faces-images.git` 
* **Time**: 5m13s

#### smart http:// (https://git-scm.com/book/en/v2/Git-on-the-Server-The-Protocols#The-HTTP-Protocols)

* **Task**: `git clone http://drg-srv1-ref:82/faces-images.git` 
* **Time**: 6m13s / 6m18s

* **Task**: `git push origin master` on WebDAV mod via http with basic authentication, see ftp://www.kernel.org/pub/software/scm/git/docs/v2.4.0/howto/setup-git-server-over-http.html
* **Time**: 5m40s / 5m48s

##### git://, see [1](https://git-scm.com/book/en/v2/Git-on-the-Server-The-Protocols#The-Git-Protocol), [2](https://git-scm.com/book/en/v2/Git-on-the-Server-Git-Daemon)

* **Task**: `git clone git://drg-srv1-ref/faces-images.git`
* **Time**: 7m7s / 7m3s 
> `git daemon --reuseaddr --base-path=/opt/git-plain/ /opt/git-plain/`

* **Task**: `git clone git://drg-srv1-ref/faces-images.git`
* **Time**: 5m49s / 5m59s
> `git daemon --reuseaddr --export-all --verbose --enable=receive-pack --base-path=/opt/git-plain/ /opt/git-plain/`

* **Task**: `git push origin master`, see http://stackoverflow.com/questions/792611/receive-pack-service-not-enabled-for-git for push!!!
* **Time**: 5m10s / 5m14s / 5m15

##### file:// and local (https://git-scm.com/book/en/v2/Git-on-the-Server-The-Protocols#Local-Protocol)

* **Task**: `git clone file:///home/user1/faces-images-plain/faces-images/` (local but over network!!!)
* **Time**: 2m32s / 2m17s

* **Task**: `git clone /home/user1/faces-images-plain/faces-images/`
* **Time**: 1m14s / 35s!!! / 29s !!!

* **Task**: `git push bare master` to the remote file:///home/user1/faces-images-plain/bare/
* **Time**: 1m10s / 52s

* **Task**: `git push bare2 master` to the remote /home/user1/faces-images-plain/bare/
* **Time**: 58s / 55s

### Client PC: schulung-res (Windows 7 SP1)
#### ssh://

* **Task**: `git clone git-plain@drg-srv1-ref:/opt/git-plain/faces-images.git` 
* **Time**: 8m12s / 7m33s

* **Task**: `git push origin master` on remote repo git-plain@drg-srv1-ref:/opt/git-plain/faces-images.git 
* **Time**: 8m36s / 8m24s

#### smart http://

* **Task**: `git pull origin master` on remote repo http://git-plai:git@drg-srv1-ref:82/faces-images.git
* **Time**: 8m2s

* **Task**: `git clone http://git-plai:git@drg-srv1-ref:82/faces-images.git` 
* **Time**: 8m2s / 14m48s  i.e. clone==pull!

* **Task**: `git push origin master` on WebDAV mod via http with basic authentication, see ftp://www.kernel.org/pub/software/scm/git/docs/v2.4.0/howto/setup-git-server-over-http.html
* **Time**: ---
>***Problems***: [Thu Nov 19 13:32:01.992839 2015] [dav:error] [pid 29894] (104)Connection reset by peer: [client 10.20.5.17:55234] An error occurred while reading the request body (URI: /faces-images.git/objects/40/9386d317208a19c761152442bfae0fae6d24c9_586abb42311671c15726921177860e32561fdb3a)  [500, #0]

##### git://, see [1](https://git-scm.com/book/en/v2/Git-on-the-Server-The-Protocols#The-Git-Protocol), [2](https://git-scm.com/book/en/v2/Git-on-the-Server-Git-Daemon)

* **Task**: `git clone git://drg-srv1-ref/faces-images.git`
* **Time**: 7m46s / 7m36s
> `git daemon --reuseaddr --export-all --verbose --enable=receive-pack --base-path=/opt/git-plain/ /opt/git-plain/`

* **Task**: `git push origin master`, see http://stackoverflow.com/questions/792611/receive-pack-service-not-enabled-for-git for push!!!
* **Time**: ---
> cannot be pushed via git:// from windows, the ssh should be used as workaround !!!, see http://stackoverflow.com/questions/9732703/git-cant-push-from-windows

##### file:// and local (https://git-scm.com/book/en/v2/Git-on-the-Server-The-Protocols#Local-Protocol)

* **Task**: `git clone file://~/git-plain/faces-images/` (local but over network!!!)
* **Time**: 7m16s / 11m6s

* **Task**: `git clone ~/git-plain/faces-images/`
* **Time**: 4m3s / 2m5s / 3m38s

* **Task**: `git push bare master` to the remote file://~/git-plain/faces-images/bare/
* **Time**: 1m50s / 1m20s

* **Task**: `git push bare2 master` to the remote ~/git-plain/faces-images/bare2/
* **Time**: 58s / 1m11s

## big-project repo 26G
tif/*.tif (25G) and pdf/*.pdf (497M) under git-lfs, xml/**/*.xml(33M) and doc/*(36M) is under plain git

* **Task**: `time git add .` 
* **Time**: 204,07s user 55,24s system 37% cpu 11:33,21 total
 
* **Task**: `time git commit -am 'initial commit git and git-lfs files'` 
* **Time**: 227,70s user 71,20s system 78% cpu 6:20,41 total

* **Task**: `git lfs push origin master` 
* **Time**: 496,18s!!!!!! user 56,33s system 22% cpu 40:30,94 total

## Direct comparison of file-sharing sevices @ DRG

### tested file: 2G incompressible random file
> dd if=/dev/urandom of=huge2GB.img bs=1048576 count=2000

* **Task**: upload by synchronisation
* **Time**: 
 * seafile http://10.20.5.7:8000/: 3m17s  
 * pydio http://10.20.5.7:81/pydio: 3m35s
 * ownCloud http://10.20.5.7:81/owncloud: 5m10s

