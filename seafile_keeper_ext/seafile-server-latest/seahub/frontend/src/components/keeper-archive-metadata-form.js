import React from 'react';
import Select from 'react-select';
import AsyncCreatableSelect from 'react-select/lib/AsyncCreatable';
import ReactDOM from 'react-dom';
import { navigate } from '@reach/router';
import { Utils } from '../utils/utils';
import {
  gettext,
  siteRoot,
  mediaUrl,
  logoPath,
  logoWidth,
  logoHeight,
  siteTitle,
} from '../utils/constants';
import { keeperAPI } from '../utils/seafile-api';
import toaster from './toast';
import CommonToolbar from './toolbar/common-toolbar';
import SideNav from './user-settings/side-nav';
import { Tooltip  } from 'reactstrap';
import PropTypes from 'prop-types';

import '../css/toolbar.css';
import '../css/search.css';

import '../css/user-settings.css';
import '../css/keeper-archive-metadata-form.css';

//const { repoId, csrfToken } = window.app.pageOptions;
let val_errors = {};
let mpgInstituteOptions = [];

const defaultResourceType = 'Library';
const resourceTypes = ['Library', 'Project'];

const defaultAuthors = [{ firstName: '', lastName: '', affs: [''] }];
const defaultDirectors = [{ firstName: '', lastName: '' }];
const defaultPublisher = 'MPDL Keeper Service, Max-Planck-Gesellschaft zur Förderung der Wissenschaften e. V.';

const defaultMd = {
  title: '',
  authors: defaultAuthors,
  publisher: defaultPublisher,
  description: '',
  year: '',
  institute: '',
  department: '',
  directors: defaultDirectors,
  resourceType: defaultResourceType,
  license: '',
  errors: '',
};


const infoAreaPropTypes = {
  id: PropTypes.string.isRequired,
  /*helpText: PropTypes.string.isRequired,
  errorText: PropTypes.string.isRequired,*/
};

function populate_val_errors(md) {
  val_errors = {};
  if ('errors' in md && md.errors) {
    let err_keys = Object.keys(md.errors);
    if (err_keys && err_keys.length > 0) {
      err_keys.map((k) => {
        val_errors[k] = md.errors[k];
      });
    }
  }
}

class InfoArea extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      helpTooltipOpen: false,
      errorTooltipOpen: false,
    };
  }

  toggleHelp = () => {
    this.setState({
      helpTooltipOpen: !this.state.helpTooltipOpen,
    });
  };

  toggleError = () => {
    this.setState({
      errorTooltipOpen: !this.state.errorTooltipOpen,
    });
  };

  render() {

    return (
        <React.Fragment>
          <div className="col-sm-1 m-0 input-tip">
            {!this.props.errorText
                ? <i className="fas fa-check-circle" style={{color: "green"}}/>
                : <span>
                <i className="fas fa-exclamation-circle" style={{color: "red"}} id={this.props.id + "-validation"}/>
                <Tooltip
                    toggle={this.toggleError}
                    delay={{show: 0, hide: 0}}
                    target={this.props.id + "-validation"}
                    placement="right"
                    isOpen={this.state.errorTooltipOpen}
                >
                  {this.props.errorText}
                </Tooltip>
            </span>
            }
            &nbsp;
            <i className="fas fa-question-circle" id={this.props.id + "-help"}/>
            <Tooltip
                toggle={this.toggleHelp}
                delay={{show: 0, hide: 0}}
                target={this.props.id + "-help"}
                placement="right"
                isOpen={this.state.helpTooltipOpen}
            >
              {gettext(this.props.helpText)}
            </Tooltip>
          </div>
        </React.Fragment>
    );
  }
}
InfoArea.propTypes = infoAreaPropTypes;



const keeperArchiveMetadataFormPropTypes = {
  repoID: PropTypes.string.isRequired,
};



class KeeperArchiveMetadataForm extends React.Component {
  constructor(props) {
    super(props);
    this.state = defaultMd;
  }

  componentDidMount() {
    keeperAPI
      .getArchiveMetadata(this.props.repoID)
      .then((res) => {
        let md = {};
        if ('data' in res) {
          Object.keys(defaultMd).map((k) => {
            md[k] = k in res.data ? res.data[k] : '';
          });
          if (!('authors' in md && md.authors.length > 0)) {
            md.authors = defaultAuthors;
          }
          if (!('directors' in md && md.directors.length > 0)) {
            md.directors = defaultDirectors;
          }
          if (!('publisher' in md && md.publisher && md.publisher.trim())) {
            md.publisher = defaultPublisher;
          }
          if (
            !('resourceType' in md && md.resourceType && md.resourceType.trim())
          ) {
            md.resourceType = defaultResourceType;
          }
        } else {
          md = defaultMd;
        }

        //alert(JSON.stringify(md));

        //populate validation errors
        populate_val_errors(md);

        this.setState(md);
        this.props.canArchive(val_errors);

        keeperAPI.getMpgInstitutes().then((res2) => {
          res2.data.map((v) => {
            mpgInstituteOptions.push({ value: v, label: v });
          });
        });
      })
      .catch((error) => {
        let errMessage = Utils.getErrorMsg(error);
        toaster.danger(errMessage);
      });
  }

  updateArchiveMetadata = (e) => {
    e.preventDefault();
    let md = {};
    Object.keys(defaultMd).map((k) => {
      md[k] = this.state[k];
    });
    keeperAPI
      .updateArchiveMetadata(this.props.repoID, md)
      .then((res) => {
        md = res.data;
        //alert('here' + JSON.stringify(md));

        populate_val_errors(md);

        //if empty publisher, det defaultPublisher
        if (!('publisher' in md && md.publisher && md.publisher.trim())) {
          md.publisher = defaultPublisher;
        }

        this.setState(md);
        this.props.canArchive(val_errors);

        /*if ('errors' in md && md.errors) {
          //populate validation errors
          populate_val_errors(md);

          //if empty publisher, det defaultPublisher
          if (!('publisher' in md && md.publisher && md.publisher.trim())) {
            md.publisher = defaultPublisher;
          }

          this.setState(md);
          this.props.canArchive(val_errors);
        } else {
          //redirect!!!
          window.location.href =
            'redirect_to' in md ? md.redirect_to : siteRoot;
        }*/

        if (!('errors' in md)) {
          toaster.success(gettext("Success"), {duration: 3});
        }

        //toaster.success(gettext("Success"), {duration: 3});
      })
      .catch((error) => {
        let errMessage = Utils.getErrorMsg(error);
        toaster.danger(errMessage);
      });
  };


  handleInputChange(e, key) {
    this.setState({
      [key]: e.target.value,
    });
  }

  setAuthorInputFields(values) {
    this.setState({ authors: values });
  }

  handleAuthorAddFields = (idx) => {
    const values = [...this.state.authors];
    values.splice(idx + 1, 0, { firstName: '', lastName: '', affs: [''] });
    this.setAuthorInputFields(values);
  };

  handleAuthorRemoveFields = (idx) => {
    const values = [...this.state.authors];
    values.splice(idx, 1);
    this.setAuthorInputFields(values);
  };

  handleAuthorInputChange = (idx, e) => {
    const values = [...this.state.authors];
    if (e.target.name === 'firstName') {
      values[idx].firstName = e.target.value;
    } else {
      values[idx].lastName = e.target.value;
    }
    this.setAuthorInputFields(values);
  };

  handleAuthorAffInputChange = (idx, aidx, e) => {
    const values = [...this.state.authors];
    values[idx].affs[aidx] = e.target.value;
    this.setAuthorInputFields(values);
  };

  handleAuthorAffAddFields = (idx, aidx) => {
    const values = [...this.state.authors];
    values[idx].affs.splice(aidx + 1, 0, '');
    this.setAuthorInputFields(values);
  };

  handleAuthorAffRemoveFields = (index, aidx) => {
    const values = [...this.state.authors];
    values[index].affs.splice(aidx, 1);
    this.setAuthorInputFields(values);
  };

  setDirectorInputFields(values) {
    this.setState({ directors: values });
  }

  handleDirectorAddFields = (idx) => {
    const values = [...this.state.directors];
    values.splice(idx + 1, 0, { firstName: '', lastName: '' });
    this.setDirectorInputFields(values);
  };

  handleDirectorRemoveFields = (idx) => {
    const values = [...this.state.directors];
    values.splice(idx, 1);
    this.setDirectorInputFields(values);
  };

  handleDirectorInputChange = (idx, e) => {
    const values = [...this.state.directors];
    if (e.target.name === 'firstName') {
      values[idx].firstName = e.target.value;
    } else {
      values[idx].lastName = e.target.value;
    }
    this.setDirectorInputFields(values);
  };

  onResourceSelectChange = (selectedItem) => {
    this.setState({
      resourceType: selectedItem.value,
    });
  };

  resourceOptions = resourceTypes.map((item) => {
    return {
      value: item,
      label: item,
    };
  });

  filterInstitutes = (inputValue) => {
    return mpgInstituteOptions.filter((i) =>
      i.label.toLowerCase().includes(inputValue.toLowerCase())
    );
  };

  promiseOptions = (inputValue) =>
    new Promise((resolve) => {
      resolve(this.filterInstitutes(inputValue));
    });

  handleInstituteChange = (option) => {
    let insName =
      option == null
        ? ''
        : !('value' in option) || option.value.trim() === ''
          ? ''
          : option.value;
    this.setState({ institute: insName });
  };


  render() {

    return (
      <React.Fragment>
        <div className="h-100 d-flex flex-column">
          <div className="flex-auto d-flex o-hidden">
            <div className="main-panel d-flex flex-column">
              <h2 className="heading">{gettext('Archive Metadata')}</h2>
              <div
                className="content position-relative"
              >
                <form
                    method="post"
                >

                  {/*Title*/}
                  <div className="form-group row md-item">
                    <div className="col-sm-11">
                      <label
                          id="lbl-title"
                          className="col-sm-1 col-form-label"
                          htmlFor="lbl-title"
                      >
                        {gettext('Title')}:
                      </label>
                      <textarea
                          className="form-control"
                          value={this.state.title}
                          onChange={(e) => {
                            this.handleInputChange(e, 'title');
                          }}
                      />
                    </div>
                    <InfoArea id="title"
                              helpText="MANDATORY: Please enter the title of your research project."
                              errorText={val_errors.title}/>
                  </div>

                  {/*Authors*/}
                  <div className="form-group row md-item">
                    {this.state.authors.map((inputField, index) => (
                        <React.Fragment key={`${inputField}~${index}`}>
                          <label
                              id="lbl-authors"
                              className="col-sm-1 col-form-label"
                              htmlFor="lbl-authors"
                          >
                            {gettext('Author') +
                            (this.state.authors.length > 1
                                ? ' #' + (index + 1)
                                : '')}
                            :
                          </label>
                          <div className="form-group col-sm-4 md-item">
                            <label htmlFor="firstName">
                              {gettext('First Name')}:
                            </label>
                            <input
                                type="text"
                                className="form-control"
                                name="firstName"
                                value={inputField.firstName}
                                onChange={(e) =>
                                    this.handleAuthorInputChange(index, e)
                                }
                            />
                          </div>
                          <div className="form-group col-sm-5 md-item">
                            <label htmlFor="lastName">
                              {gettext('Last Name')}:
                            </label>
                            <input
                                type="text"
                                className="form-control"
                                name="lastName"
                                value={inputField.lastName}
                                onChange={(e) =>
                                    this.handleAuthorInputChange(index, e)
                                }
                            />
                          </div>
                          <div className="form-group col-sm-1">
                            {this.state.authors.length > 1 && (
                                <button
                                    className="author-control btn btn-link"
                                    type="button"
                                    onClick={() =>
                                        this.handleAuthorRemoveFields(index)
                                    }
                                >
                                  -
                                </button>
                            )}
                            <button
                                className="author-control btn btn-link"
                                type="button"
                                onClick={() => this.handleAuthorAddFields(index)}
                            >
                              +
                            </button>
                          </div>
                          { index == 0 &&
                              <InfoArea
                                id="author"
                                helpText="MANDATORY: Please enter the authors and affiliation of your research project"
                                errorText={val_errors.authors}/>
                          }

                          {inputField.affs.map((_, aidx) => (
                              <React.Fragment
                                  key={`${inputField}~${index}~${aidx}`}
                              >
                                <div className="form-group col-sm-11">
                                  <label
                                      className="offset-sm-1"
                                      htmlFor="lbl-affiliation"
                                  >
                                    {gettext('Affiliation') +
                                    (inputField.affs.length > 1
                                        ? ' #' + (aidx + 1)
                                        : '')}
                                    :
                                  </label>
                                  <input
                                      type="text"
                                      className="form-control  offset-sm-1 col-sm-11"
                                      value={inputField.affs[aidx]}
                                      onChange={(e) =>
                                          this.handleAuthorAffInputChange(
                                              index,
                                              aidx,
                                              e
                                          )
                                      }
                                  />
                                </div>
                                <div className="form-group">
                                  {inputField.affs.length > 1 && (
                                      <button
                                          className="affiliation-control btn btn-link"
                                          type="button"
                                          onClick={() =>
                                              this.handleAuthorAffRemoveFields(
                                                  index,
                                                  aidx
                                              )
                                          }
                                      >
                                        -
                                      </button>
                                  )}
                                  <button
                                      className="affiliation-control btn btn-link"
                                      type="button"
                                      onClick={() =>
                                          this.handleAuthorAffAddFields(index, aidx)
                                      }
                                  >
                                    +
                                  </button>
                                </div>
                              </React.Fragment>
                          ))}
                        </React.Fragment>
                    ))}
                  </div>

                  {/*Publisher*/}
                  <div className="form-group row md-item">
                    <div className="col-sm-11">
                      <label
                          id="lbl-publisher"
                          className="col-sm-2 col-form-label"
                          htmlFor="publisher"
                      >
                        {gettext('Publisher')}:
                      </label>
                      <input
                          id="publisher"
                          className="form-control"
                          value={this.state.publisher}
                          onChange={(e) => {
                            this.handleInputChange(e, 'publisher');
                          }}
                      />
                    </div>
                    <InfoArea
                        id="publisher" helpText="MANDATORY: Please enter the name of entity that holds, archives, publishes prints, distributes, releases, issues, or produces the resource."
                              errorText={val_errors.publisher}/>

                  </div>

                  {/*Description*/}
                  <div className="form-group row md-item">
                    <div className="col-sm-11">
                      <label
                          id="lbl-description"
                          className="col-sm-1 col-form-label"
                          htmlFor="description"
                      >
                        {gettext('Description')}:
                      </label>
                      <textarea
                          id="description"
                          className="form-control"
                          value={this.state.description}
                          onChange={(e) => {
                            this.handleInputChange(e, 'description');
                          }}
                      />
                    </div>
                    <InfoArea
                        id="description" helpText="MANDATORY: Please enter the description of your research project."
                              errorText={val_errors.description}/>
                  </div>

                  {/*Year*/}
                  <div className="form-group row md-item">
                    <label
                        id="lbl-year"
                        className="col-sm-1 col-form-label"
                        htmlFor="lbl-year"
                    >
                      {gettext('Year')}:
                    </label>
                    <div className="col-sm-3">
                      <input
                          className="form-control"
                          value={this.state.year}
                          onChange={(e) => {
                            this.handleInputChange(e, 'year');
                          }}
                      />
                    </div>
                      <InfoArea
                          id="year"
                          helpText="MANDATORY: Please enter year of project start."
                          errorText={val_errors.year}
                      />
                  </div>

                  {/*Institute*/}
                  <div className="form-group row md-item">
                    <label
                        id="lbl-institute"
                        className="col-sm-1 col-form-label"
                        htmlFor="institute"
                    >
                      {gettext('Institute')}:
                    </label>
                    <div className="form-group col-sm-5 md-item">
                      <label>{gettext('Institute name')}:</label>
                      <AsyncCreatableSelect
                          id="institute"
                          isClearable
                          cacheOptions
                          value={{
                            value: this.state.institute,
                            label: this.state.institute,
                          }}
                          onChange={this.handleInstituteChange}
                          loadOptions={this.promiseOptions}
                      />
                    </div>
                    <div className="form-group col-sm-5 md-item">
                      <label htmlFor="department">
                        {gettext('Department')}:
                      </label>
                      <input
                          type="text"
                          className="form-control"
                          value={this.state.department}
                          onChange={(e) =>
                              this.handleInputChange(e, 'department')
                          }
                      />
                    </div>
                    {/*TODO: errors for department and directors*/}
                    <InfoArea
                        id="institute" helpText="MANDATORY: Please enter the related Max Planck Institute for this research project."
                              errorText={
                                (val_errors.institute ? ("Institute name: " + val_errors.institute + "\n") : "") +
                                (val_errors.department ? ("Department: " + val_errors.department) : "") +
                                (val_errors.directors ? ("Directors: " + val_errors.directors) : "")
                              }/>

                    {this.state.directors.map((inputField, index) => (
                        <React.Fragment key={`${inputField}~${index}`}>
                          <label
                              id="lbl-directors"
                              className="form-group offset-sm-1 col-sm-2 col-form-label"
                              htmlFor="directors"
                          >
                            {gettext('Director or PI') +
                            (this.state.directors.length > 1
                                ? ' #' + (index + 1)
                                : '')}
                            :
                          </label>
                          <div className="form-group col-sm-4 md-item">
                            <label htmlFor="firstName">
                              {gettext('First Name')}:
                            </label>
                            <input
                                type="text"
                                className="form-control"
                                name="firstName"
                                value={inputField.firstName}
                                onChange={(e) =>
                                    this.handleDirectorInputChange(index, e)
                                }
                            />
                          </div>
                          <div className="form-group col-sm-4 md-item">
                            <label htmlFor="lastName">
                              {gettext('Last Name')}:
                            </label>
                            <input
                                type="text"
                                className="form-control"
                                name="lastName"
                                value={inputField.lastName}
                                onChange={(e) =>
                                    this.handleDirectorInputChange(index, e)
                                }
                            />
                          </div>
                          <div className="form-group col-sm-1">
                            {this.state.directors.length > 1 && (
                                <button
                                    className="director-control btn btn-link"
                                    type="button"
                                    onClick={() =>
                                        this.handleDirectorRemoveFields(index)
                                    }
                                >
                                  -
                                </button>
                            )}
                            <button
                                className="director-control btn btn-link"
                                type="button"
                                onClick={() => this.handleDirectorAddFields(index)}
                            >
                              +
                            </button>
                          </div>
                        </React.Fragment>
                    ))}


                  </div>
                  {/*Resource Type*/}
                  <div className="form-group row md-item">
                    <label
                        id="lbl-resource-type"
                        className="col-sm-2 col-form-label"
                        htmlFor="resource-type"
                    >
                      {gettext('Resource Type')}:
                    </label>
                    <div className="col-sm-3">
                      <Select
                          id="resource-type"
                          value={{
                            value: this.state.resourceType,
                            label: this.state.resourceType
                          }}
                          options={this.resourceOptions}
                          onChange={this.onResourceSelectChange}
                      />
                    </div>
                    <InfoArea
                        id="resource-type" helpText="MANDATORY: Please enter the resource type of the entity. Allowed values for this field: Library (default), Project."
                              errorText=""/>
                  </div>

                  {/*License*/}
                  <div className="form-group row md-item">
                    <label
                        id="lbl-license"
                        className="col-sm-1 col-form-label"
                        htmlFor="license"
                    >
                      {gettext('License')}:
                    </label>
                    <div className="col-sm-7">
                      <input
                          id="license"
                          className="form-control"
                          value={this.state.license}
                          onChange={(e) => {
                            this.handleInputChange(e, 'license');
                          }}
                      />
                    </div>
                    <InfoArea
                        id="license" helpText="OPTIONAL: Please enter the license."
                              errorText=""/>

                  </div>

                  <button
                      type="submit"
                      className="btn btn-outline-primary offset-sm-9 col-sm-3"
                      onClick={this.updateArchiveMetadata}
                  >
                    {' '}
                    {gettext('Save metadata')}
                  </button>
                </form>

                {/*<br />*/}
                {/*<pre>{JSON.stringify(this.state, null, 2)}</pre>*/}
              </div>
            </div>
          </div>
        </div>
      </React.Fragment>
    );
  }
}

KeeperArchiveMetadataForm.propTypes = keeperArchiveMetadataFormPropTypes;

export default KeeperArchiveMetadataForm;
