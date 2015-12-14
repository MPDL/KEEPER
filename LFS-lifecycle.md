# GitLab git LFS lifecycle 

hosted @ https://drg-srv1-ref (i.e. https://10.20.5.7) 

**NOTE**: `git clone git@drg-srv1-ref:vlad/gitlab-lfs-test.git` does not work due to special settigs for access to the git-lfs storage via https, thus lfs repo should be created and set up step by step.

``````
git init
git lfs install
git remote add origin git@drg-srv1-ref:vlad/gitlab-lfs-test.git
git config http.sslverify false (not check self-signed certificate of drg-srv1-ref, can be omitted in production)
``````

What should be fetched from LFS storage is configured via `lfs.fetchexclude` and `lfs.fetchinclude` [settings](https://github.com/github/git-lfs/blob/master/docs/man/git-lfs-fetch.1.ronn):

``````
git config lfs.fetchexclude "high_resolution/*.jpg"
git config lfs.fetchinclude "pictures/*.jpg,thumbnails/*.jpg"
``````
then 
``````
git fetch origin master
``````
downloads only pointers, not not real in .git/lfs!

## checkout real LFS files according to `lfs.fetchexclude` and `lfs.fetchinclude`
``````
git checkout master
``````

## checkout LFS BOLB file/directories
``````
change `lfs.fetchexclude` and/or `lfs.fetchinclude`
git lfs fetch origin
git lfs checkout 
``````


## checkout all BLOBs under LFS control
``````
git lfs fetch --all
git lfs checkout
``````

## add new BLOB file to LFS control
``````
cp path_to_file/file_name working_directory
git lfs track file_name
git add file_name
git commit -am 'added LFS file'
``````
**PROBLEM**: it is impossible to add to LFS a file which has been already committed to git!!!

## modify/commit a LFS file 
``````
change LFS file
git commit -am 'some LFS file has been changed'
``````
older version of the file is available, can be checked out with `git checkout [ref]` 


## check LFS environment:
``````
export GIT_CURL_VERBOSE=1 (for git REST tracing)
git lfs ls-files
git lfs track
git lfs env
git config -l
``````

