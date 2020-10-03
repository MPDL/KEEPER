import React from 'react';
import PropTypes from 'prop-types';
import {Alert, Button, Form, FormGroup, Input, Label, Modal, ModalBody, ModalFooter, ModalHeader} from 'reactstrap';
import {gettext} from '../../utils/constants';
import {Utils} from '../../utils/utils';


const propTypes = {
  toggleDialog: PropTypes.func.isRequired,
  values: PropTypes.object.isRequired,
};

let term_count, term_entries = {};

class KeeperCatalogFacetDialog extends React.Component {

  constructor(props) {
    super(props);
    const facet = {...this.props.values};
    this.state = {
      errorMsg: '',
      searchTerm: '',
      isSubmitBtnActive: false,
      order: facet["order"] || 'asc',
      terms: [],
      termsChecked: facet["termsChecked"] || [],
    };

  }

  componentDidMount() {
    this.props.values.keeperApiFunc().then((res) => {
      const {ts, tc, tes} = this.props.values.extractTermsFunc(res.data);
      term_count = tc;
      term_entries = tes;
      this.setState({
        terms: ts.filter(t => this.state.termsChecked.indexOf(t) == -1),
      });
    }).catch((error) => {
      this.setState({
        errorMsg: Utils.getErrorMsg(error, true) // true: show login tip if 403
      });
    });

  }

  toggle = () => {
    this.props.toggleDialog();
  }

  setOrder = (e) => {
    this.setState({
      order: e.target.value,
      isSubmitBtnActive: true
    });
  }

  inputSearchTerm = (e) => {
    this.setState({searchTerm: e.target.value});
  }

  addToTermsChecked(name) {
    this.state.termsChecked.unshift(name);
    this.setState({
      terms: this.state.terms.filter(t => t !== name),
      termsChecked: this.state.termsChecked,
    });
    //remove from parent terms
    //this.props.setTerms.call(this, this.state.termsChecked, terms);
  }

  addToTerms(name) {
    this.state.terms.push(name);
    this.setState({
      terms: this.state.terms,
      termsChecked: this.state.termsChecked.filter(t => t !== name),
    });
  }

  isChecked(name) {
    return this.state.termsChecked.indexOf(name) != -1;
  }

  handleCheckboxChange = (e) => {
    const name = e.target.name;
    if (this.state.termsChecked.indexOf(name) == -1) {
      this.addToTermsChecked(name);
    } else {
      this.addToTerms(name);
    }
    this.setState({isSubmitBtnActive: true, searchTerm: ""});
  }

  calculateScope = () => {
    let scope = [];
    for (let term of this.state.termsChecked) {
      scope = scope.concat(term_entries[term]);
    }
    return [...new Set(scope)];
  }

  handleApply = () => {
    const scope = this.calculateScope();
    this.props.applyFacet(this.state.termsChecked, this.state.terms, term_count, this.state.order, scope);
    this.toggle();
  }

  handleCleanAll = () => {
    this.props.applyFacet([], [], {}, 'asc', []);
    this.toggle();
  }


  getTermFragment = (inputField, index) => {
      let showFragment = !this.state.searchTerm ||
          (this.state.searchTerm && inputField && inputField.toLowerCase().indexOf(this.state.searchTerm.toLowerCase()) != -1);
      if (showFragment)
        return (
              <React.Fragment key={`${inputField}~${index}`}>
                <FormGroup className="ml-5 mb-0">
                  <Label>
                    <Input type="checkbox" name={inputField} checked={this.isChecked(inputField)}
                           onChange={this.handleCheckboxChange}/>
                    {inputField + " (" + term_count[inputField] + ")"}
                  </Label>
                </FormGroup>
              </React.Fragment>
        )
  }

  getOrderFragment = (o, label) => {
    return (
        <FormGroup check className="ml-4">
          <Label check>
            <Input type="radio" name="order" value={o} checked={this.state.order == o} onChange={this.setOrder} className="mr-1"/>
            {gettext(label)}
          </Label>
        </FormGroup>
    )
  }

  render() {
    const { dialogTitle } = this.props;
    const { 
      errorMsg,
      searchTerm,
    } = this.state;
    return (
      <Modal isOpen={true} toggle={this.toggle}>
        <ModalHeader toggle={this.toggle}>{dialogTitle}</ModalHeader>
        <ModalBody>
          <Form>
            {this.getOrderFragment("asc", "Ascending")}
            {this.getOrderFragment("desc", "Descending")}
            <FormGroup>
              <Label>{gettext('Search')}</Label>
              <Input style={{width: "50%"}} value={searchTerm} onChange={this.inputSearchTerm}/>
            </FormGroup>
            {this.state.termsChecked.map((inputField, index) => (
                this.getTermFragment(inputField, index)
            ))}
            {this.state.terms.map((inputField, index2) => (
                this.getTermFragment(inputField, index2)
            ))}
          </Form>
          {errorMsg && <Alert color="danger">{errorMsg}</Alert>}
        </ModalBody>
        <ModalFooter>
          <Button color="primary" className="w-9" onClick={this.handleApply} disabled={!this.state.isSubmitBtnActive}>{gettext('Apply')}</Button>
          <Button className="ml-4"  color="primary" onClick={this.handleCleanAll}>{gettext('Disable all')}</Button>
          <Button className="ml-7" color="secondary" onClick={this.toggle}>{gettext('Cancel')}</Button>
        </ModalFooter>
      </Modal>
    );
  }
}

KeeperCatalogFacetDialog.propTypes = propTypes;

export default KeeperCatalogFacetDialog;
