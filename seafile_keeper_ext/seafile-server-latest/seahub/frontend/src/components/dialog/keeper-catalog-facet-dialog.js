import React, {Fragment} from 'react';
import PropTypes from 'prop-types';
import {Alert, Button, Form, FormGroup, Input, Label, Modal, ModalBody, ModalFooter, ModalHeader} from 'reactstrap';
import {gettext} from '../../utils/constants';

const propTypes = {
  toggleDialog: PropTypes.func.isRequired,
  name: PropTypes.string.isRequired,
  values: PropTypes.object.isRequired,
  catalogScope: PropTypes.arrayOf(PropTypes.number).isRequired,
};

const maxTerms = 30;

class KeeperCatalogFacetDialog extends React.Component {

  constructor(props) {
    super(props);
    const facet = this.props.values;
    let tes = facet.termEntries;
    //console.log(facet);
    let tc = [...facet.termsChecked] || [];

    // sort terms by amount of entries, desc
    let termsSorted = Object.keys(tes)
        .sort((a, b) => (tes[b].length-tes[a].length));
    let ts = termsSorted || [];
    //terms are not checked terms
    if (ts.length > 0 && tc.length > 0) {
      ts = ts.filter(t => !tc.includes(t))
    }

    this.state = {
      errorMsg: '',
      searchTerm: '',
      isSubmitBtnActive: false,
      order: facet.order || 'asc',
      terms: ts,
      termsChecked: tc,
    };
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


  handleApply = () => {
    this.props.applyFacet(
        this.props.name,
        this.state.termsChecked, this.state.order);
    this.toggle();
  }

  handleCleanAll = () => {
    this.props.applyFacet(this.props.name,
        [], [], {}, 'asc', []);
    this.toggle();
  }

  isTermInScope = (term) => {
    const cscope = this.props.catalogScope || [];
    if (cscope.length == 0)
      return true
    const tscope = this.props.values.termEntries[term];
    return tscope.some(e => cscope.indexOf(e) != -1)
  }

  getTermFragment = (inputField, index) => {
    let {termEntries} = this.props.values;
    let {catalogScope} = this.props;
    if (this.state.searchTerm && inputField && inputField.toLowerCase().indexOf(this.state.searchTerm.toLowerCase()) == -1)
      return
    if (!(inputField && inputField in termEntries))
      return
    if (!this.isTermInScope(inputField))
      return
    return (
        <Fragment key={`${inputField}~${index}`}>
          <FormGroup className="ml-5 mb-0">
            <Label>
              <Input type="checkbox" name={inputField} checked={this.isChecked(inputField)}
                     onChange={this.handleCheckboxChange}/>
              {inputField + " (" + termEntries[inputField].length + ")"}
            </Label>
          </FormGroup>
        </Fragment>
    )
  }

  getOrderFragment = (o, label) => {
    return (
        <FormGroup check>
          <Label check>
            <Input type="radio" name="order" value={o} checked={this.state.order == o} onChange={this.setOrder} className="mr-1"/>
            {gettext(label)}
          </Label>
        </FormGroup>
    )
  }

  render() {
    const { dialogTitle, name } = this.props;
    const { 
      errorMsg,
      searchTerm,
    } = this.state;
    return (
      <Modal isOpen={true} toggle={this.toggle}>
        <ModalHeader toggle={this.toggle}>{gettext("Select " + name.charAt(0).toUpperCase() + name.slice(1) + "(s)")}</ModalHeader>
        <ModalBody>
          <Form>
            {this.getOrderFragment("asc", "Ascending")}
            {this.getOrderFragment("desc", "Descending")}
            <FormGroup className="mt-3">
              <Input style={{width: "60%", height: "60%"}} placeholder={gettext('Search')} value={searchTerm} onChange={this.inputSearchTerm}/>
            </FormGroup>
            {this.state.termsChecked
                .map((inputField, index) => (
                  this.getTermFragment(inputField, index)
            ))}
            {this.state.terms
                .map((inputField, index2) => (index2 < maxTerms && this.getTermFragment(inputField, index2)
              ))}
            {this.state.terms.length >= maxTerms &&
              <div className="ml-1">...</div>
            }
          </Form>
          {errorMsg && <Alert color="danger">{errorMsg}</Alert>}
        </ModalBody>
        <ModalFooter>
          <Button color="primary" className="w-9" onClick={this.handleApply} disabled={!this.state.isSubmitBtnActive}>{gettext('Apply')}</Button>
          <Button className="ml-4"  color="primary" onClick={this.handleCleanAll}>{gettext('Reset')}</Button>
          <Button className="ml-4" color="secondary" onClick={this.toggle}>{gettext('Cancel')}</Button>
        </ModalFooter>
      </Modal>
    );
  }
}

KeeperCatalogFacetDialog.propTypes = propTypes;

export default KeeperCatalogFacetDialog;
