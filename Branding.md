## GitLab
Good guide is here: http://axilleas.me/en/blog/2014/custom-gitlab-login-page/

**Note**: Problems by installation ob `ruby` ENV on Ubuntu 14.04, thus the code has been changed directly in `/opt/gitlab/embedded/service`. use `gitlab-rake assets:precompile && gitlab-ctl restart` to apply and deploy changes 

## Seafile
See http://manual.seafile.com/config/seahub_customization.html

## Pydio
Web GUI can be changed via `PYDIO_URL/pydio/settings/config/plugins/gui` interface by `admin` user 
