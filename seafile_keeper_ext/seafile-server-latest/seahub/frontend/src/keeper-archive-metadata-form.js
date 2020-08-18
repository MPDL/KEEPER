import React from 'react';
import Select from 'react-select';
import AsyncCreatableSelect from 'react-select/lib/AsyncCreatable';
import ReactDOM from "react-dom";
import { navigate } from "@reach/router";
import { Utils } from "./utils/utils";
import {
  gettext,
  siteRoot,
  mediaUrl,
  logoPath,
  logoWidth,
  logoHeight,
  siteTitle,
} from "./utils/constants";
import { keeperAPI } from "./utils/seafile-api";
import toaster from "./components/toast";
import CommonToolbar from "./components/toolbar/common-toolbar";
import SideNav from "./components/user-settings/side-nav";
import { Tooltip  } from 'reactstrap';
import PropTypes from 'prop-types';

import "./css/toolbar.css";
import "./css/search.css";

import "./css/user-settings.css";
import "./css/keeper-archive-metadata-form.css";

const { repoId, csrfToken } = window.app.pageOptions;
let val_errors = {};
let mpgInstituteOptions = [];

const defaultResourceType = 'Library';
const resourceTypes = ['Library', 'Project'];

const defaultAuthors = [{ firstName: '', lastName: '', affs: [''] }];
const defaultDirectors = [{ firstName: '', lastName: '' }];
const defaultPublisher = 'MPDL Keeper Service, Max-Planck-Gesellschaft zur Förderung der Wissenschaften e. V.';

const defaultMd = {
  title: "",
  authors: defaultAuthors,
  publisher: defaultPublisher,
  description: "",
  year: "",
  institute: "",
  department: "",
  directors: defaultDirectors,
  resourceType: defaultResourceType,
  license: "",
};

const propTypes = {
  id: PropTypes.string.isRequired, 
  text: PropTypes.string.isRequired, 
};

class HelpIcon extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      tooltipOpen: false,
    };
  }

  toggle = () => {
    this.setState({
      tooltipOpen: !this.state.tooltipOpen,
    });
  };

  render() {
    return (
      <React.Fragment>
        <span className="fas fa-question-circle" id={this.props.id} />
        <Tooltip
          toggle={this.toggle}
          delay={{ show: 0, hide: 0 }}
          target={this.props.id}
          placement="right"
          isOpen={this.state.tooltipOpen}
        >
          {this.props.text}
        </Tooltip>
      </React.Fragment>
    );
  }
}
HelpIcon.propTypes = propTypes;

class KeeperArchiveMetadataForm extends React.Component {
  constructor(props) {
    super(props);
    this.sideNavItems = [
      { show: true, href: "#lbl-title", text: gettext("Title") },
      { show: true, href: "#lbl-authors", text: gettext("Authors") },
      { show: true, href: "#lbl-publisher", text: gettext("Publisher") },
      { show: true, href: "#lbl-description", text: gettext("Description") },
      { show: true, href: "#lbl-year", text: gettext("Year") },
      { show: true, href: "#lbl-institute", text: gettext("Institute") },
      {
        show: true,
        href: "#lbl-resource-type",
        text: gettext("Resource Type"),
      },
      { show: true, href: "#lbl-license", text: gettext("License") },
    ];
    this.state = defaultMd;
    this.state.curItemID = this.sideNavItems[0].href.substr(1);
  }

  componentDidMount() {
    keeperAPI
      .getArchiveMetadata(repoId)
      .then((res) => {
        let md = {};
        if ("data" in res) {
          Object.keys(defaultMd).map((k) => {
            md[k] = k in res.data ? res.data[k] : "";
          });
          if (!("authors" in md && md.authors.length > 0)) {
            md.authors = defaultAuthors;
          }
          if (!("directors" in md && md.directors.length > 0)) {
            md.directors = defaultDirectors;
          }
          if (!("publisher" in md && md.publisher && md.publisher.trim())) {
            md.publisher = defaultPublisher;
          }
          if (
            !("resourceType" in md && md.resourceType && md.resourceType.trim())
          ) {
            md.resourceType = defaultResourceType;
          }
        } else {
          md = defaultMd;
        }

        md.curItemID = this.sideNavItems[0].href.substr(1);
        this.setState(md);

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
    //alert('here' + JSON.stringify(md));
    keeperAPI
      .updateArchiveMetadata(repoId, md)
      .then((res) => {
        md = res.data;
        //populate validation errors
        if ('errors' in md && md.errors) {
          val_errors = {};
          //alert(JSON.stringify(md.errors));
          let err_keys = Object.keys(md.errors);
          if (err_keys && err_keys.length >= 1) {
            err_keys.map((k) => {
              val_errors[k] = md.errors[k];
            });
          }

          //if empty publisher, det defaultPublisher
          if (!("publisher" in md && md.publisher && md.publisher.trim())) {
            md.publisher = defaultPublisher;
          }
          this.setState(md);
        } else {
          //redirect!!!
          window.location.href =
            "redirect_to" in md ? md.redirect_to : siteRoot;
        } 
        //toaster.success(gettext("Success"), {duration: 3});
      })
      .catch((error) => {
        let errMessage = Utils.getErrorMsg(error);
        toaster.danger(errMessage);
      });
  };

  onSearchedClick = (selectedItem) => {
    if (selectedItem.is_dir === true) {
      let url =
        siteRoot +
        "library/" +
        selectedItem.repo_id +
        "/" +
        selectedItem.repo_name +
        selectedItem.path;
      navigate(url, { repalce: true });
    } else {
      let url =
        siteRoot +
        "lib/" +
        selectedItem.repo_id +
        "/file" +
        Utils.encodePath(selectedItem.path);
      let newWindow = window.open("about:blank");
      newWindow.location.href = url;
    }
  };

  handleContentScroll = (e) => {
    const scrollTop = e.target.scrollTop;
    const scrolled = this.sideNavItems.filter((item) => {
      return (
        item.show &&
        document.getElementById(item.href.substr(1)).offsetTop - 45 < scrollTop
      );
    });
    if (scrolled.length) {
      this.setState({
        curItemID: scrolled[scrolled.length - 1].href.substr(1),
      });
    }
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
    values.splice(idx + 1, 0, { firstName: "", lastName: "", affs: [""] });
    this.setAuthorInputFields(values);
  };

  handleAuthorRemoveFields = (idx) => {
    const values = [...this.state.authors];
    values.splice(idx, 1);
    this.setAuthorInputFields(values);
  };

  handleAuthorInputChange = (idx, e) => {
    const values = [...this.state.authors];
    if (e.target.name === "firstName") {
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
    values[idx].affs.splice(aidx + 1, 0, "");
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
    values.splice(idx + 1, 0, { firstName: "", lastName: "" });
    this.setDirectorInputFields(values);
  };

  handleDirectorRemoveFields = (idx) => {
    const values = [...this.state.directors];
    values.splice(idx, 1);
    this.setDirectorInputFields(values);
  };

  handleDirectorInputChange = (idx, e) => {
    const values = [...this.state.directors];
    if (e.target.name === "firstName") {
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
        ? ""
        : !("value" in option) || option.value.trim() === ""
          ? ""
          : option.value;
    this.setState({ institute: insName });
  };


  render() {
    return (
      <React.Fragment>
        <div className="h-100 d-flex flex-column">
          <div className="top-header d-flex justify-content-between">
            <a href={siteRoot}>
              <img
                src={mediaUrl + logoPath}
                height={logoHeight}
                width={logoWidth}
                title={siteTitle}
                alt="logo"
              />
            </a>
            <CommonToolbar onSearchedClick={this.onSearchedClick} />
          </div>
          <div className="flex-auto d-flex o-hidden">
            {
              <div className="side-panel o-auto">
                <SideNav
                  data={this.sideNavItems}
                  curItemID={this.state.curItemID}
                />
              </div>
            }

            <div className="main-panel d-flex flex-column">
              <h2 className="heading">{gettext("Archive Metadata")}</h2>
              <div
                className="content position-relative"
                onScroll={this.handleContentScroll}
              >
                <form
                  action=""
                  method="post"
                  onSubmit={this.updateArchiveMetadata}
                >
                  <input
                    type="hidden"
                    name="csrfmiddlewaretoken"
                    value={csrfToken}
                  />

                  {/*Title*/}
                  <div className="form-group row">
                    <label
                      id="lbl-title"
                      className="col-sm-1 col-form-label"
                      htmlFor="lbl-title"
                    >
                      {gettext("Title")}:
                    </label>
                    <div className="col-sm-7 setting-item">
                      <textarea
                        className="form-control"
                        value={this.state.title}
                        onChange={(e) => {
                          this.handleInputChange(e, "title");
                        }}
                      />
                      {val_errors.title && (
                        <div>
                          <label className="val-error m-0">
                            {val_errors.title}
                          </label>
                        </div>
                      )}
                    </div>
                    <div className="col-sm-4 m-0 input-tip">
                      <HelpIcon
                        id="title-help"
                        text={gettext(
                          "MANDATORY: Please enter the title of your research project."
                        )}
                      />
                    </div>
                  </div>

                  {/*Authors*/}
                  <div className="form-group row">
                    {this.state.authors.map((inputField, index) => (
                      <React.Fragment key={`${inputField}~${index}`}>
                        <label
                          id="lbl-authors"
                          className="col-sm-1 col-form-label"
                          htmlFor="lbl-authors"
                        >
                          {gettext("Author") +
                            (this.state.authors.length > 1
                              ? " #" + (index + 1)
                              : "")}
                          :
                        </label>
                        <div className="form-group col-sm-3 setting-item">
                          <label htmlFor="firstName">
                            {gettext("First Name")}:
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
                        <div className="form-group col-sm-4 setting-item">
                          <label htmlFor="lastName">
                            {gettext("Last Name")}:
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
                        <div className="form-group col-sm-4">
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
                        {inputField.affs.map((_, aidx) => (
                          <React.Fragment
                            key={`${inputField}~${index}~${aidx}`}
                          >
                            <label
                              className="form-group offset-sm-1 col-sm-1"
                              htmlFor="lbl-affiliation"
                            >
                              {gettext("Affiliation") +
                                (inputField.affs.length > 1
                                  ? " #" + (aidx + 1)
                                  : "")}
                              :
                            </label>
                            <div className="form-group col-sm-6 setting-item">
                              <input
                                type="text"
                                className="form-control"
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
                            <div className="form-group col-sm-4">
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
                    {val_errors.authors && (
                      <label className="offset-sm-1 col-sm-7 col-form-label val-error">
                        {val_errors.authors}
                      </label>
                    )}
                  </div>

                  {/*Publisher*/}
                  <div className="form-group row">
                    <label
                      id="lbl-publisher"
                      className="col-sm-1 col-form-label"
                      htmlFor="publisher"
                    >
                      {gettext("Publisher")}:
                    </label>
                    <div className="col-sm-7 setting-item">
                      <input
                        id="publisher"
                        className="form-control"
                        value={this.state.publisher}
                        onChange={(e) => {
                          this.handleInputChange(e, "publisher");
                        }}
                      />
                      {val_errors.publisher && (
                        <div>
                          <label className="val-error m-0">
                            {val_errors.publisher}
                          </label>
                        </div>
                      )}
                    </div>
                    <p className="col-sm-4 m-0 input-tip">
                      <HelpIcon
                        id="publisher-help"
                        text={gettext(
                          "MANDATORY: Please enter the name of entity that holds, archives, publishes prints, distributes, releases, issues, or produces the resource."
                        )}
                      />
                    </p>
                  </div>

                  {/*Description*/}
                  <div className="form-group row">
                    <label
                      id="lbl-description"
                      className="col-sm-1 col-form-label"
                      htmlFor="description"
                    >
                      {gettext("Description")}:
                    </label>
                    <div className="col-sm-7 setting-item">
                      <textarea
                        id="description"
                        className="form-control"
                        value={this.state.description}
                        onChange={(e) => {
                          this.handleInputChange(e, "description");
                        }}
                      />
                      {val_errors.description && (
                        <div>
                          <label className="val-error m-0">
                            {val_errors.description}
                          </label>
                        </div>
                      )}
                    </div>
                    <p className="col-sm-4 m-0 input-tip">
                      <HelpIcon
                        id="description-help"
                        text={gettext(
                          "MANDATORY: Please enter the description of your research project."
                        )}
                      />
                    </p>
                  </div>

                  {/*Year*/}
                  <div className="form-group row">
                    <label
                      id="lbl-year"
                      className="col-sm-1 col-form-label"
                      htmlFor="lbl-year"
                    >
                      {gettext("Year")}:
                    </label>
                    <div className="col-sm-1 setting-item">
                      <input
                        className="form-control"
                        value={this.state.year}
                        onChange={(e) => {
                          this.handleInputChange(e, "year");
                        }}
                      />
                      {val_errors.year && (
                        <div>
                          <label className="val-error m-0">
                            {val_errors.year}
                          </label>
                        </div>
                      )}
                    </div>
                    <p className="col-sm-4 m-0 input-tip">
                      <HelpIcon
                        id="year-help"
                        text={gettext(
                          "MANDATORY: Please enter year of project start."
                        )}
                      />
                    </p>
                  </div>

                  {/*Institute*/}
                  <div className="form-group row">
                    <label
                      id="lbl-institute"
                      className="col-sm-1 col-form-label"
                      htmlFor="institute"
                    >
                      {gettext("Institute")}:
                    </label>
                    <div className="form-group col-sm-4 setting-item">
                      <label>{gettext("Institute name")}:</label>
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
                    <div className="form-group col-sm-3 setting-item">
                      <label htmlFor="department">
                        {gettext("Department")}:
                      </label>
                      <input
                        type="text"
                        className="form-control"
                        value={this.state.department}
                        onChange={(e) =>
                          this.handleInputChange(e, "department")
                        }
                      />
                    </div>
                    <p className="col-sm-4 m-0 input-tip">
                      <HelpIcon
                        id="institute-help"
                        text={gettext(
                          "MANDATORY: Please enter the related Max Planck Institute for this research project."
                        )}
                      />
                    </p>
                    {val_errors.institute && (
                      <label className="offset-sm-1 col-sm-4 col-form-label val-error">
                        {val_errors.institute}
                      </label>
                    )}
                    {val_errors.department && (
                      <label
                        className={
                          (val_errors.institute ? "" : "offset-sm-5 ") +
                          "col-sm-4 col-form-label val-error"
                        }
                      >
                        {val_errors.department}
                      </label>
                    )}
                  </div>
                  <div className="form-group row">
                    {this.state.directors.map((inputField, index) => (
                      <React.Fragment key={`${inputField}~${index}`}>
                        <label
                          id="lbl-directors"
                          className="offset-sm-1 col-sm-1 col-form-label"
                          htmlFor="directors"
                        >
                          {gettext("Director or PI") +
                            (this.state.directors.length > 1
                              ? " #" + (index + 1)
                              : "")}
                          :
                        </label>
                        <div className="form-group col-sm-3 setting-item">
                          <label htmlFor="firstName">
                            {gettext("First Name")}:
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
                        <div className="form-group col-sm-3 setting-item">
                          <label htmlFor="lastName">
                            {gettext("Last Name")}:
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
                        <div className="form-group col-sm-4">
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
                    {val_errors.directors && (
                      <label className="offset-sm-1 col-sm-7 col-form-label val-error">
                        {val_errors.directors}
                      </label>
                    )}
                  </div>

                  {/*Resource Type*/}
                  <div className="form-group row">
                    <label
                      id="lbl-resource-type"
                      className="col-sm-1 col-form-label"
                      htmlFor="resource-type"
                    >
                      {gettext("Resource Type")}:
                    </label>
                    <div className="col-sm-2 setting-item">
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
                    <p className="col-sm-1 m-0 input-tip">
                      <HelpIcon
                        id="resource-type-help"
                        text={gettext(
                          "MANDATORY: Please enter the resource type of the entity. Allowed values for this field: Library (default), Project."
                        )}
                      />
                    </p>
                  </div>

                  {/*License*/}
                  <div className="form-group row">
                    <label
                      id="lbl-license"
                      className="col-sm-1 col-form-label"
                      htmlFor="license"
                    >
                      {gettext("License")}:
                    </label>
                    <div className="col-sm-7 setting-item">
                      <input
                        id="license"
                        className="form-control"
                        value={this.state.license}
                        onChange={(e) => {
                          this.handleInputChange(e, "license");
                        }}
                      />
                    </div>
                    <p className="col-sm-4 m-0 input-tip">
                      <HelpIcon
                        id="license-help"
                        text={gettext("OPTIONAL: Please enter the license.")}
                      />
                    </p>
                  </div>

                  <button
                    type="submit"
                    className="btn btn-outline-primary offset-sm-6 col-sm-2"
                  >
                    {" "}
                    {gettext("Submit")}
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

ReactDOM.render(<KeeperArchiveMetadataForm />, document.getElementById("wrapper"));
