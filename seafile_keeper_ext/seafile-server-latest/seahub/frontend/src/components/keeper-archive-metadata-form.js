import React from 'react';
import Select from 'react-select';
import AsyncCreatableSelect from 'react-select/lib/AsyncCreatable';
import {Utils} from '../utils/utils';
import {gettext,} from '../utils/constants';
import {keeperAPI} from '../utils/seafile-api';
import toaster from './toast';
import {Col, FormGroup, Input, Label, Row, Tooltip} from 'reactstrap';
import PropTypes from 'prop-types';

import '../css/toolbar.css';
import '../css/search.css';

import '../css/user-settings.css';
import '../css/keeper-archive-metadata-form.css';

let mpgInstituteOptions = [];

const defaultResourceType = "Library";
const resourceTypes = ["Library", "Project"];

const defaultAuthors = [{ firstName: "", lastName: "", affs: [""] }];
const defaultDirectors = [{ firstName: "", lastName: "" }];
const defaultPublisher = gettext("MPDL Keeper Service, Max-Planck-Gesellschaft zur Förderung der Wissenschaften e. V.");

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
  errors: "",
};

const defaultValidMd = {
  title: true,
  authors:  [true],
  publisher: true,
  description: true,
  year: true,
  institute: true,
  department: true,
  directors: [true],
  resourceType: true,
};

const infoAreaPropTypes = {
  id: PropTypes.string.isRequired,
};

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

    // console.log(this.props.id);
    return (
        <React.Fragment>
          <div className="input-tip pt-0">
            {this.props.id != "license" &&
              <span style={{color: "red", fontWeight: "900"}}>*&nbsp;&nbsp;</span>
            }
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
    this.state = {
      ...defaultMd,
      validMd: defaultValidMd,
    };
  }

  componentDidMount() {
    keeperAPI
      .getArchiveMetadata(this.props.repoID)
      .then((res) => {
        let state = {};
        if ('data' in res) {
          Object.keys(defaultMd).map((k) => {
            state[k] = k in res.data ? res.data[k] : "";
          });
          if (!("authors" in state && state.authors.length > 0)) {
            state.authors = defaultAuthors;
          }
          if (!("directors" in state && state.directors.length > 0)) {
            state.directors = defaultDirectors;
          }
          if (!("publisher" in state && state.publisher && state.publisher.trim())) {
            state.publisher = defaultPublisher;
          }
          if (
            !("resourceType" in state && state.resourceType && state.resourceType.trim())
          ) {
            state.resourceType = defaultResourceType;
          }
        } else {
          state = defaultMd;
        }

        this.pupulateValidMd(state);

        state.validMd = this.state.validMd;
        this.setState(state);

        this.props.canArchive(this.state.validMd, true);

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

  pupulateValidMd = (md) => {
    Object.keys(defaultValidMd).map(k => {
      if (k == "authors" || k == "directors") {
        for (let idx in md[k]) {
          this.state.validMd[k][idx] = this.isValidMd(k.slice(0, -1), md[k][idx])
        }
      } else {
        this.state.validMd[k] = this.isValidMd(k, md[k]);
      }
    })
  }

  updateArchiveMetadata = (e) => {
    e.preventDefault();
    let state = {};
    Object.keys(defaultMd).map((k) => {
      state[k] = this.state[k];
    });
    keeperAPI
      .updateArchiveMetadata(this.props.repoID, state)
      .then((res) => {
        state = res.data;

        //if empty publisher, apply defaultPublisher
        if (!("publisher" in state && state.publisher && state.publisher.trim())) {
          state.publisher = defaultPublisher;
          this.state.validMd.publisher = true;
        }

        state.validMd = this.state.validMd;
        this.setState(state);
        this.props.canArchive(this.state.validMd, true);

        toaster.success(gettext("Success"), {duration: 3});

      })
      .catch((error) => {
        let errMessage = Utils.getErrorMsg(error);
        toaster.danger(errMessage);
      });
  };

  isValidMd = (key, value) => {
    if (!key || !value)
      return false;
    let isValid = true;
    if (key == "title" || key == "description" || key == "publisher" || key == "department"  || key == "institute") {
      isValid = value.trim() != "";
    } else if (key == "year") {
      const parsed = parseInt(value, 10);
      isValid = !isNaN(parsed) && parsed > 0;
    } else if (key == "author" || key == "director") {
      isValid = (value.firstName && value.firstName.trim() != "") || (value.lastName && value.lastName.trim() != "");
    }
    return isValid;
  }

  handleInputChange(e, key) {
    this.state.validMd[key] = this.isValidMd(key, e.target.value);
    this.setState({
          [key]: e.target.value,
          validMd: this.state.validMd
        },
        () => {
         this.props.canArchive(this.state.validMd, false);
       }
    );
  }

  setAuthorInputFields(values) {
    for (let idx in values) {
      this.state.validMd.authors[idx] = this.isValidMd("author", values[idx]);
    }
    this.setState({
          authors: values,
          validMd: this.state.validMd
        },
        () => {
           this.props.canArchive(this.state.validMd, false);
       }
    );
  }

  handleAuthorAddFields = idx => {
    const values = [...this.state.authors];
    values.splice(idx + 1, 0, { firstName: "", lastName: "", affs: [""] });
    this.setAuthorInputFields(values);
  };

  handleAuthorRemoveFields = idx => {
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
    for (let idx in values) {
      this.state.validMd.directors[idx] = this.isValidMd("director", values[idx]);
    }
    this.setState({
          directors: values,
          validMd: this.state.validMd},
          () => {
            this.props.canArchive(this.state.validMd, false);
          }
    );
  }

  handleDirectorAddFields = idx => {
    const values = [...this.state.directors];
    values.splice(idx + 1, 0, { firstName: "", lastName: "" });
    this.setDirectorInputFields(values);
  };

  handleDirectorRemoveFields = idx => {
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

  onResourceSelectChange = selectedItem => {
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

  filterInstitutes = input => {
    return mpgInstituteOptions.filter((i) =>
      i.label.toLowerCase().includes(input.toLowerCase())
    );
  };

  promiseOptions = input =>
    new Promise((resolve) => {
      resolve(this.filterInstitutes(input));
    });

  handleInstituteChange = option => {
    let insName =
      option == null
        ? ""
        : !("value" in option) || option.value.trim() === ""
          ? ""
          : option.value;
    this.state.validMd.institute = this.isValidMd("institute", insName);
    this.setState({
      institute: insName,
      validMd: this.state.validMd
      },
        () => {
            this.props.canArchive(this.state.validMd, false);
    });
  };

  validationProps = key => {
    return (this.state.validMd[key] ? {valid: true} : {invalid: true})
  }

  validationInSelects = key => {
    return (this.state.validMd[key] ? "is-valid" : "is-invalid")
  }

  validationInAuthors = idx => {
    return (this.state.validMd.authors[idx] ? {valid: true} : {invalid: true})
  }

  validationInDirectors = idx => {
    return (this.state.validMd.directors[idx] ? {valid: true} : {invalid: true})
  }

  render() {

    return (
      <React.Fragment>
        <div className="h-100 d-flex flex-column">
          <div className="flex-auto d-flex o-hidden">
            <div className="main-panel d-flex flex-column">
              <h2 style={{fontWeight: "900"}} className="heading">{gettext("Archive Metadata")}</h2>
              <div
                className="content position-relative" style={{paddingBottom: "2rem"}}
              >
                <form method="post">

                  {/*Title*/}
                  <FormGroup row className="md-item">
                    <Col sm={12}>
                      <Label
                          id="lbl-title"
                          sm={1}
                      >
                        {gettext("Title")}:
                      </Label>
                      <Row>
                        <Col sm={11}>
                          <Input
                              type="textarea"
                              className="form-control"
                              placeholder={gettext("Title of your research project") + "..."}
                              value={this.state.title}
                              onChange={(e) => {
                                this.handleInputChange(e, "title");
                              }}
                              {...this.validationProps("title")}
                          />
                        </Col>
                        <Col sm={1}>
                          <InfoArea id="title"
                              helpText="Please enter the title of your research project."
                          />
                        </Col>
                      </Row>
                    </Col>
                  </FormGroup>

                  {/*Authors*/}
                  <FormGroup row className="md-item">
                    {this.state.authors.map((inputField, index) => (
                        <React.Fragment key={`${inputField}~${index}`}>
                          <Label
                              id="lbl-authors"
                              sm={1}
                              className="pt-3"
                              for="lbl-authors"
                          >
                            {gettext("Author") +
                            (this.state.authors.length > 1
                                ? " #" + (index + 1)
                                : "")}
                            :
                          </Label>
                          <Col sm={4} className="form-group md-item">
                            <Label for="firstName">
                              {gettext('First Name')}:
                            </Label>
                            <Input
                                name="firstName"
                                value={inputField.firstName}
                                onChange={(e) =>
                                    this.handleAuthorInputChange(index, e)
                                }
                                {...this.validationInAuthors(index)}
                            />
                          </Col>
                          <div className="form-group col-sm-5 md-item">
                            <label htmlFor="lastName">
                              {gettext('Last Name')}:
                            </label>
                            <Input
                                name="lastName"
                                value={inputField.lastName}
                                onChange={(e) =>
                                    this.handleAuthorInputChange(index, e)
                                }
                                {...this.validationInAuthors(index)}
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
                              <span className="info-area-names">
                                <InfoArea
                                  id="author"
                                  className="info-area-names"
                                  helpText="Please enter the authors and affiliation of your research project"
                                />
                              </span>
                          }

                          {inputField.affs.map((_, aidx) => (
                              <React.Fragment
                                  key={`${inputField}~${index}~${aidx}`}
                              >
                                <div className="form-group col-sm-11 ml-2">
                                  <label
                                      className="offset-sm-1"
                                      htmlFor="lbl-affiliation"
                                  >
                                    {gettext('Affiliation') +
                                    (inputField.affs.length > 1
                                        ? ' #' + (aidx + 1)
                                        : "")}
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
                  </FormGroup>

                  {/*Publisher*/}
                  <FormGroup row className="md-item">
                    <Col sm={12}>
                      <Label
                          id="lbl-publisher"
                          sm={1}
                          htmlFor="publisher"
                      >
                        {gettext('Publisher')}:
                      </Label>
                      <Row>
                        <Col sm={11}>
                          <Input
                              id="publisher"
                              type="textarea"
                              style={{height: "4em"}}
                              placeholder={gettext("Please enter the name of entity that holds, archives, publishes prints, distributes, releases, issues, or produces the resource") + "..."}
                              className="form-control"
                              value={this.state.publisher}
                              onChange={(e) => {
                                this.handleInputChange(e, "publisher");
                              }}
                              {...this.validationProps("publisher")}
                          />
                        </Col>
                        <Col sm={1}>
                          <InfoArea
                              id="publisher"
                              helpText="Please enter the name of entity that holds, archives, publishes prints, distributes, releases, issues, or produces the resource."
                          />
                        </Col>
                      </Row>
                    </Col>
                  </FormGroup>
                  
                  {/*Description*/}
                  <FormGroup row className="md-item">
                    <Col sm={12}>
                      <Label
                          id="lbl-description"
                          sm={1}
                          htmlFor="description"
                      >
                        {gettext("Description")}:
                      </Label>
                      <Row>
                        <Col sm={11}>
                          <Input
                            id="description"
                            type="textarea"
                            style={{height: "6em"}}
                            placeholder={gettext("Please enter the description of your research project") + "..."}
                            className="form-control"
                            value={this.state.description}
                            onChange={(e) => {
                              this.handleInputChange(e, "description");
                            }}
                            {...this.validationProps("description")}
                        />
                        </Col>
                        <Col sm={1}>
                          <InfoArea
                            id="description"
                            helpText="Please enter the description of your research project."
                          />
                        </Col>
                      </Row>
                    </Col>

                  </FormGroup>

                  {/*Year*/}
                  <FormGroup row className="md-item">
                    <Label
                        id="lbl-year"
                        sm={1}
                        className="pt-0"
                        for="lbl-year"
                    >
                      {gettext("Year")}:
                    </Label>
                    <Col sm={4}>
                      <Input
                          className="form-control"
                          placeholder={gettext("Year of project start...")}
                          value={this.state.year}
                          onChange={(e) => {
                            this.handleInputChange(e, "year");
                          }}
                          {...this.validationProps("year")}
                      />
                    </Col>
                      <InfoArea
                          id="year"
                          helpText="Please enter year of project start."
                      />
                  </FormGroup>

                  {/*Institute*/}
                  <FormGroup row className="md-item">
                    <Label
                        id="lbl-institute"
                        className="pt-3"
                        sm={1}
                        for="institute"
                    >
                      {gettext('Institute')}:
                    </Label>
                    <Col sm={5} className="form-group md-item">
                      <Label>{gettext('Institute name')}:</Label>
                      <AsyncCreatableSelect
                          id="institute"
                          className={this.state.validMd.institute ? "is-valid" : "is-invalid"}
                          isClearable
                          cacheOptions
                          value={{
                            value: this.state.institute,
                            label: this.state.institute,
                          }}
                          onChange={this.handleInstituteChange}
                          loadOptions={this.promiseOptions}
                          {...this.validationProps("institute")}
                      />
                    </Col>
                    <Col sm={5} className="form-group md-item">
                      <Label for="department">
                        {gettext('Department')}:
                      </Label>
                      <Input
                        value={this.state.department}
                        onChange={(e) =>
                            this.handleInputChange(e, "department")
                        }
                        {...this.validationProps("department")}
                      />
                    </Col>
                    <span className="info-area-names">
                      <InfoArea
                          id="institute"
                          helpText="Please enter the related Max Planck Institute for this research project."
                      />
                    </span>
                    {this.state.directors.map((inputField, index) => (
                        <React.Fragment key={`${inputField}~${index}`}>
                          <Label
                              id="lbl-directors"
                              sm={2}
                              className="form-group offset-sm-1 pt-3"
                              for="directors"
                          >
                            {gettext('Director or PI') +
                            (this.state.directors.length > 1
                                ? ' #' + (index + 1)
                                : "")}
                            :
                          </Label>
                          <FormGroup className="col-sm-4 md-item">
                            <Label form="firstName">
                              {gettext('First Name')}:
                            </Label>
                            <Input
                                name="firstName"
                                value={inputField.firstName}
                                onChange={(e) =>
                                    this.handleDirectorInputChange(index, e)
                                }
                                {...this.validationInDirectors(index)}

                            />
                          </FormGroup>
                          <FormGroup className="col-sm-4 md-item">
                            <Label for="lastName">
                              {gettext('Last Name')}:
                            </Label>
                            <Input
                                name="lastName"
                                value={inputField.lastName}
                                onChange={(e) =>
                                    this.handleDirectorInputChange(index, e)
                                }
                                {...this.validationInDirectors(index)}
                            />
                          </FormGroup>
                          <FormGroup>
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
                          </FormGroup>
                        </React.Fragment>
                    ))}
                  </FormGroup>

                  {/*Resource Type*/}
                  <Row className="form-group md-item">
                    <Label
                        id="lbl-resource-type"
                        sm={2}
                        className="pt-0"
                        for="resource-type"
                    >
                      {gettext('Resource Type')}:
                    </Label>
                    <Col sm={3}>
                      <Select
                          id="resource-type"
                          value={{
                            value: this.state.resourceType,
                            label: this.state.resourceType
                          }}
                          options={this.resourceOptions}
                          onChange={this.onResourceSelectChange}
                      />
                    </Col>
                    <InfoArea
                        id="resource-type"
                        helpText="Please enter the resource type of the entity. Allowed values for this field: Library (default), Project."
                    />
                  </Row>

                  {/*License*/}
                  <Row className="form-group md-item">
                    <Label
                        id="lbl-license"
                        className="pt-0"
                        sm={1}
                        for="license"
                    >
                      {gettext("License")}:
                    </Label>
                    <Col sm={7}>
                      <Input
                          id="license"
                          placeholder={gettext("Please enter the license") + "..."}
                          className="form-control"
                          value={this.state.license}
                          onChange={(e) => {
                            this.handleInputChange(e, "license");
                          }}
                      />
                    </Col>
                    <InfoArea
                        id="license" helpText="Please enter the license."
                    />
                  </Row>
                  <button
                      type="submit"
                      className="btn btn-outline-primary offset-sm-9 col-sm-3"
                      onClick={this.updateArchiveMetadata}
                  >
                    {" "}
                    {gettext("Save metadata")}
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