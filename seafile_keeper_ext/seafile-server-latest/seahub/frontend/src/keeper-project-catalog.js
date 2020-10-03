import React, {Fragment} from 'react';
import ReactDOM from 'react-dom';
import {navigate} from '@reach/router';
import {Utils} from './utils/utils';
import {gettext, logoHeight, logoPath, logoWidth, mediaUrl, siteRoot, siteTitle} from './utils/constants';
import {keeperAPI} from './utils/seafile-api';
import Loading from './components/loading';
import Paginator from './components/paginator';
import CommonToolbar from './components/toolbar/common-toolbar';
import KeeperCatalogFacetDialog from './components/dialog/keeper-catalog-facet-dialog';

import './css/toolbar.css';
import './css/search.css';

import './css/keeper-project-catalog.css';

const { 
  repoID,
  repoName,
  userPerm
} = window.app.pageOptions;

const maxDescLength = 500;

const defaultFacet = {
      order: 'asc',
      terms: [],
      term_count: {},
      extractTermsFunc: (data) => {
        let terms = [], term_count = {}, term_entries = {};
        data.map(r => {
          terms.push(r[0]);
          term_entries[r[0]] = r[1];
          term_count[r[0]] = r[1].length;
        });
        return {ts: terms, tc: term_count, tes: term_entries};
      },
  }

class KeeperProjectCatalog extends React.Component {

  constructor(props) {
    super(props);
    this.state = {
      isLoading: true,
      errorMsg: '',
      currentPage: 1,
      perPage: 25,
      hasNextPage: false,
      items: [],
      scope: [],
      authorsOrder: 'asc',
      isAuthorFacetDialogOpen: false,
      isYearFacetDialogOpen: false,
      isInstituteFacetDialogOpen: false,
      isDirectorFacetDialogOpen: false,
    };
    this.state.authorFacet = {
      ...defaultFacet,
      name: "Author",
      termsChecked: [],
      keeperApiFunc: function() {return keeperAPI.getCatalogAuthors()},
    };

    this.state.yearFacet = {
      ...defaultFacet,
      name: "Year",
      termsChecked: [],
      keeperApiFunc: function() {return keeperAPI.getCatalogYears()},
    };

    this.state.instituteFacet = {
      ...defaultFacet,
      name: "Institute",
      termsChecked: [],
      keeperApiFunc: function() {return keeperAPI.getCatalogInstitutes()},
    };

    this.state.directorFacet = {
      ...defaultFacet,
      name: "Director",
      termsChecked: [],
      keeperApiFunc: function() {return keeperAPI.getCatalogDirectors()},
    };

  }

  componentDidMount() {
    let urlParams = (new URL(window.location)).searchParams;
    const {
      currentPage, perPage
    } = this.state;
    this.setState({
      perPage: parseInt(urlParams.get('per_page') || perPage),
      currentPage: parseInt(urlParams.get('page') || currentPage)
    }, () => {
      this.getItems(this.state.currentPage);
    });
    const script = document.createElement('script');
    script.src =
      'https://static.zdassets.com/ekr/snippet.js?key=32977f9b-455d-428b-8dd5-f4c65aad0daa';
    script.id = 'ze-snippet';
    script.async = true;
    document.body.appendChild(script);
  }

  getItems = (page) => {
    keeperAPI.getProjectCatalog(page, this.state.perPage,
        this.state.authorFacet, this.state.yearFacet, this.state.instituteFacet, this.state.directorFacet,
        this.state.scope).then((res) => {
      // console.log(JSON.stringify(res.data));
      this.setState({
        isLoading: false,
        currentPage: page,
        items: res.data.items,
        hasNextPage: res.data.more,
        isAccessDenied: "is_access_denied" in res.data && res.data.is_access_denied,
      });
    }).catch((error) => {
      this.setState({
        isLoading: false,
        errorMsg: Utils.getErrorMsg(error, true) // true: show login tip if 403
      }); 
    });
  }

  resetPerPage = (perPage) => {
    this.setState({
      perPage: perPage
    }, () => {
      this.getItems(1);
    }); 
  }

  applyAuthorFacet = (tc, ts, tcount, o, s) => {
    this.setState({
      scope: s,
      authorFacet: {
        ...this.state.authorFacet,
        termsChecked: tc,
        terms: ts,
        term_count: tcount,
        order: o,
      },
    }, () => this.getItems(1)
    );
    //console.log(this.state.authorFacet);
  }

  applyYearFacet = (tc, ts, tcount, o, s) => {
    this.setState({
      scope: s,
      yearFacet: {
        ...this.state.yearFacet,
        termsChecked: tc,
        terms: ts,
        term_count: tcount,
        order: o,
      },
    }, () => this.getItems(1)
    );
  }

  applyInstituteFacet = (tc, ts, tcount, o, s) => {
    this.setState({
      scope: s,
      instituteFacet: {
        ...this.state.instituteFacet,
        termsChecked: tc,
        terms: ts,
        term_count: tcount,
        order: o,
      },
    }, () => this.getItems(1)
    );
  }

  applyDirectorFacet = (tc, ts, tcount, o, s) => {
    this.setState({
      scope: s,
      directorFacet: {
        ...this.state.directorFacet,
        termsChecked: tc,
        terms: ts,
        term_count: tcount,
        order: o,
      },
    }, () => this.getItems(1)
    );
  }

  onSearchedClick = (selectedItem) => {
    if (selectedItem.is_dir === true) {
      let url = siteRoot + 'library/' + selectedItem.repo_id + '/' + selectedItem.repo_name + selectedItem.path;
      navigate(url, {repalce: true});
    } else {
      let url = siteRoot + 'lib/' + selectedItem.repo_id + '/file' + Utils.encodePath(selectedItem.path);
      let newWindow = window.open('about:blank');
      newWindow.location.href = url;
    }
  }

  toggleAuthorFacetDialog = () => {
      this.setState({isAuthorFacetDialogOpen: !this.state.isAuthorFacetDialogOpen});
    }

  toggleYearFacetDialog = () => {
      this.setState({isYearFacetDialogOpen: !this.state.isYearFacetDialogOpen});
    }

  toggleInstituteFacetDialog = () => {
      this.setState({isInstituteFacetDialogOpen: !this.state.isInstituteFacetDialogOpen});
    }

  toggleDirectorFacetDialog = () => {
      this.setState({isDirectorFacetDialogOpen: !this.state.isDirectorFacetDialogOpen});
    }

  getFacetFragment = (facet) => {
    return (
        <Fragment>
              <span style={{fontWeight: 600}}>{gettext(facet.name)}</span>
              {facet.termsChecked.length > 0 &&
                <i className={"ml-1 fa fa-arrow-" + (facet.order == "desc" ? "up" : "down")}/>
              }
              <ul>
                {facet.termsChecked.map((t, idx) =>  (
                  <React.Fragment key={`${t}~${idx}`}>
                    <li className="ml-5 mb-0">{t + " (" + facet.term_count[t] + ")"}</li>
                  </React.Fragment>
                ))}
              </ul>
        </Fragment>
    )
  }

  render() {
    const {isAuthorFacetDialogOpen, isYearFacetDialogOpen, isInstituteFacetDialogOpen, isDirectorFacetDialogOpen,
      authorFacet, yearFacet, instituteFacet, directorFacet} = this.state;
    return (
      <React.Fragment>
        <div className="h-100 d-flex flex-column">
          <div className="top-header d-flex justify-content-between">
            <a href={siteRoot}>
              <img src={mediaUrl + logoPath} height={logoHeight} width={logoWidth} title={siteTitle} alt="logo" />
            </a>
            <CommonToolbar onSearchedClick={this.onSearchedClick} />
          </div>
          <div className="flex-auto container-fluid pt-4 pb-6 o-auto">
            <div className="row">
              {this.state.isAccessDenied
                ? <h3 className="offset-md-2 col-md-8 mt-9 text-center error">
                    {gettext('Sie sind leider nicht berechtigt den Projektkatalog zu öffnen. Bitte wenden Sie sich an den Keeper Support.')}
                  </h3>
                : <div className="col-md-8 offset-md-2">
                    <h3 className="d-flex offset-md-3"
                        id="header">{(gettext('The KEEPER Project Catalog of the Max Planck Society'))}</h3>
                    <div className="row">

                      <div id="facet" className="col-md-3">
                        <h3 style={{color: "#57a5b8", fontSize: "1.75em", fontWeight: 500}}>{gettext('Show Projects')}</h3>

                        <div onClick={this.toggleAuthorFacetDialog}>
                          {this.getFacetFragment(this.state.authorFacet)}
                        </div>
                        <div onClick={this.toggleYearFacetDialog}>
                          {this.getFacetFragment(this.state.yearFacet)}
                        </div>
                        <div onClick={this.toggleInstituteFacetDialog}>
                          {this.getFacetFragment(this.state.instituteFacet)}
                        </div>
                        <div onClick={this.toggleDirectorFacetDialog}>
                          {this.getFacetFragment(this.state.directorFacet)}
                        </div>
                      </div>
                      <div className="col-md-9">
                        <Content
                            isLoading={this.state.isLoading}
                            errorMsg={this.state.errorMsg}
                            items={this.state.items}
                        />
                      </div>
                    </div>
                    <div className="row justify-content-center">
                      <Paginator
                          gotoPreviousPage={() => {
                            this.getItems(this.state.currentPage - 1)
                          }}
                          gotoNextPage={() => {
                            this.getItems(this.state.currentPage + 1)
                          }}
                          currentPage={this.state.currentPage}
                          hasNextPage={this.state.hasNextPage}
                          curPerPage={this.state.perPage}
                          resetPerPage={this.resetPerPage}
                      />
                    </div>
                    <Footer/>
                  </div>
              }
            </div>
          </div>
        </div>
        {isAuthorFacetDialogOpen &&
            <KeeperCatalogFacetDialog
              dialogTitle={gettext('Select Authors')}
              values={authorFacet}
              toggleDialog={this.toggleAuthorFacetDialog}
              applyFacet={this.applyAuthorFacet}
            />
        }
        {isYearFacetDialogOpen &&
            <KeeperCatalogFacetDialog
              dialogTitle={gettext('Select Years')}
              values={yearFacet}
              toggleDialog={this.toggleYearFacetDialog}
              applyFacet={this.applyYearFacet}
            />
        }
        {isInstituteFacetDialogOpen &&
            <KeeperCatalogFacetDialog
              dialogTitle={gettext('Select Institutes')}
              values={instituteFacet}
              toggleDialog={this.toggleInstituteFacetDialog}
              applyFacet={this.applyInstituteFacet}
            />
        }
        {isDirectorFacetDialogOpen &&
            <KeeperCatalogFacetDialog
              dialogTitle={gettext('Select Directors')}
              values={directorFacet}
              toggleDialog={this.toggleDirectorFacetDialog}
              applyFacet={this.applyDirectorFacet}
            />
        }
      </React.Fragment>
    );
  }
}

class Content extends React.Component {

  render() {
    const {
      isLoading, errorMsg, items,
    } = this.props;

    if (isLoading) {
      return <Loading />;
    }

    if (errorMsg) {
      return <p className="error mt-6 text-center">{errorMsg}</p>;
    }

    return (
      <React.Fragment>
          {items.map((item, index) => {
            return <Item key={index} item={item} />;
          })}
      </React.Fragment>
    );
  }
}

class Item extends React.Component {

  constructor(props) {
    super(props);
    this.state = {
      descExpanded: false,
    };
  }

   toggleDescription = () => {
    this.setState({descExpanded: !this.state.descExpanded});
  }

  toTitleCase = (txt) => {
    let str = txt.replace(/([^\W_]+[^\s-]*) */g, (t) => {
      return t.charAt(0).toUpperCase() + t.substr(1).toLowerCase();
    });
    return str;
  }

  getAuthors = (item) => {
    let author = [];
    if ("authors" in item && item.authors.length > 0) {
      let authors = item.authors
      for (let j = 0; j < authors.length ; j++) {
        let tauthor = "";
        let tauthors = this.toTitleCase(authors[j].name).split(", ");
        for (let i = 0; i < tauthors.length; i++) {
          if (i == 0 && tauthors[i].trim().length) {
            tauthor += tauthors[i] + ", ";
          } else if (tauthors[i].trim().length > 1)
            tauthor += tauthors[i].trim().charAt(0) + "., ";
        }
        tauthor = tauthor.trim().slice(0, -1);
        if (j >= 5)
          tauthor = "et al."
        author.push(tauthor);
        if (j >= 5)
          break;
        if ("affs" in authors[j])
          author.push(this.toTitleCase(authors[j].affs.join(", ")));
      }
    }
    return author.join("; ");
  }


  render() {
    const item = this.props.item;

    let showExpandDesc = item.description && item.description.length > maxDescLength;

    return (
      <React.Fragment>
        <div className="item-block" id={item.repo_id}>
          <div className="row">
            <div className="col-md-1">
              {
                item.is_certified && <img src="/catalog/static/certified.png"/>
              }
            </div>
            <div className="col-md-11">
              <h3>{
                item.landing_page_url
                  ? <a href={"/landing-page/libs/" + item.repo_id + "/"}>{item.title}</a>
                  : item.title || gettext("Project archive no.") + ": " + item.catalog_id
              }
              </h3>
              {
                item.description && <p>{
                  showExpandDesc
                      ? !this.state.descExpanded
                        ? item.description.substring(0, maxDescLength - 4) + "..."
                        : item.description
                      : item.description
                }
                {
                  showExpandDesc &&
                  <i onClick={this.toggleDescription}
                    className={"keeper-icon-triangle-" + (this.state.descExpanded ? "up" : "down")}
                  />
                }
                </p>
              }
              {
                item.authors && <p>{this.getAuthors(item)}</p>
              }
              {
                item.year && <p>{gettext("Year") + ": " + item.year}</p>
              }
              {
                item.owner && <p>{gettext("Contact") + ": " + item.owner.toLowerCase()}</p>
              }
              {
                item.landing_page_url &&
                  <p>
                      <a href={"/landing-page/libs/" + item.repo_id + "/"}>{gettext("Landing Page")}</a>
                  </p>
              }
              {/*{JSON.stringify(item)}*/}
            </div>
          </div>

        </div>


      </React.Fragment>
    );
  }
}

class Footer extends React.Component {
  render() {
    return (
        <React.Fragment>
          <div id="lg_footer">
            <div className="container">
              <div id="keeper-links" className="row">
                <div className="col-md-3">
                  <h4>Be informed</h4>
                  <a href="https://keeper.mpdl.mpg.de/f/d17ecbb967/" target="_blank">About Keeper</a><br/>
                  <a href="https://keeper.mpdl.mpg.de/f/1b0bfceac2/" target="_blank">Cared Data Commitment</a><br/>
                  <a href="/catalog" target="_blank">Project Catalog</a><br/>
                </div>
                <div className="col-md-3">
                  <h4>Get the desktop sync client</h4>
                  <a href="/download_client_program/" target="_blank">Download the Keeper client for Windows, Linux and
                    Mac</a>
                </div>
                <div className="col-md-3">
                  <h4>Find help</h4>
                  <a href="mailto:keeper@mpdl.mpg.de">Contact Keeper Support</a> <br/>
                  <a href="https://mpdl.zendesk.com/hc/en-us/categories/360001234340-Keeper" target="_blank">Help /
                    Knowledge
                    Base</a>
                </div>
                <div className="col-md-3">
                  <h4>Check terms</h4>
                  <a href="https://keeper.mpdl.mpg.de/f/f62758e53c/" target="_blank">Terms of Services</a> <br/>
                  <a href="https://keeper.mpdl.mpg.de/f/17e4e9d648/" target="_blank">Disclaimer</a><br/>
                  <a href="https://keeper.mpdl.mpg.de/f/bf2c8a977f70428587eb/" target="_blank">Privacy Policy</a>
                </div>
              </div>
              <div id="seafile-credits" className="row">
                <div className="col-md-12 text-center">
                  <div>
                    <a href="https://www.seafile.com/en/home/" target="_blank">The software behind Keeper <img
                        id="seafile-logo"
                        src="/media/custom/seafile_logo_footer.png"
                        height="35"/>© 2020 Seafile</a>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </React.Fragment>
    );
  }
}

  ReactDOM.render(
  <KeeperProjectCatalog />,
  document.getElementById('wrapper')
  );
