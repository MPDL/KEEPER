const axios = require('axios');

class KeeperAPI {
  init({ server, username, password, token }) {
    this.server = server;
    this.username = username;
    this.password = password;
    this.token = token; //none
    if (this.token && this.server) {
      this.req = axios.create({
        baseURL: this.server,
        headers: { Authorization: 'Token ' + this.token },
      });
    }
    return this;
  }

  initForSeahubUsage({ siteRoot, xcsrfHeaders }) {
    if (siteRoot && siteRoot.charAt(siteRoot.length - 1) === '/') {
      var server = siteRoot.substring(0, siteRoot.length - 1);
      this.server = server;
    } else {
      this.server = siteRoot;
    }

    this.req = axios.create({
      headers: {
        'X-CSRFToken': xcsrfHeaders,
      },
    });
    return this;
  }

  _sendPostRequest(url, form) {
    if (form.getHeaders) {
      return this.req.post(url, form, {
        headers: form.getHeaders(),
      });
    } else {
      return this.req.post(url, form);
    }
  }

  getToken() {
    const url = this.server + '/api2/auth-token/';
    axios
      .post(url, {
        username: this.username,
        password: this.password,
      })
      .then((response) => {
        this.token = response.data;
        return this.token;
      });
  }

  canCertify(repoID) {
    const url = this.server + '/api2/can-certify/';
    const params = {
      repo_id: repoID,
    };
    return this.req.post(url, params);
  }

  certifyOnBloxberg(repoID, path, type, name) {
    const url = this.server + '/api2/certify/';
    const params = {
      repo_id: repoID,
      path: path,
      type: type,
      name: name
    };
    return this.req.post(url, params);
  }

  addDoi(repoID) {
    const url = this.server + '/api2/doi/';
    const params = {
      repo_id: repoID,
    };
    return this.req.post(url, params);
  }

  canArchive(repoID) {
    const url = this.server + '/api2/can-archive/';
    const params = {
      repo_id: repoID,
    };
    return this.req.post(url, params);
  }

  archiveLibrary(repoID) {
    const url = this.server + '/api2/archive/';
    const params = {
      repo_id: repoID,
    };
    return this.req.post(url, params);
  }


  listLibraryDetails() {
    const url = this.server + '/api2/library-details/';
    return this.req.get(url);
  }

  getArchiveMetadata(repoID) {
    const url = this.server + '/api2/archive-metadata/?repo_id=' + repoID;
    return this.req.get(url);
  }

  updateArchiveMetadata(repoID, md) {
    const url = this.server + '/api2/archive-metadata/';
    md.repo_id = repoID;
    md.validate = true
    return this.req.post(url, md);
  }

  getMpgInstitutes() {
    const url = this.server + '/api2/mpg-institutes/';
    return this.req.get(url);
  }

  getProjectCatalog(page, perPage, authorFacet, yearFacet, instituteFacet, directorFacet, scope, searchTerm) {
    const url = this.server + '/api2/project-catalog/';

    let params = {
      page: page || 1,
      per_page: perPage || 25,
      search_term: searchTerm || '',
      author_facet: authorFacet || {},
      year_facet: yearFacet || {},
      institute_facet: instituteFacet || {},
      director_facet: directorFacet || {},
    };
    if (scope != null) {
      params.scope = scope;
    }
    // console.log("params:" + JSON.stringify(params));
    return this.req.post(url, params);
  }


}

export { KeeperAPI };
