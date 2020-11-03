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
    this.state = {
      errorMsg: '',
      searchTerm: '',
      isSubmitBtnActive: false,
      order: facet.order || 'asc',
      termsChecked: [...facet.termsChecked] || [],
    };
    this.state.terms = this.getTerms();
  }


  getTerms = () => {
    const { termsChecked } = this.state;
    const { termEntries } = this.props.values;
    // sort terms by amount of entries, desc, and than name, asc
    let termsSorted = Object.keys(termEntries)
      .sort((a, b) => {
        let aLen = termEntries[a].length;
        let bLen = termEntries[b].length;
        if (aLen == bLen) {
          return a.localeCompare(b);
        }
        return bLen - aLen;
      });
    if (termsSorted.length > 0 && termsChecked.length > 0) {
      termsSorted = termsSorted.filter(t => !termsChecked.includes(t));
    }
    return termsSorted;
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
      termsChecked: this.state.termsChecked,
    }, () => {
      this.setState({terms: this.getTerms()});
    });
  }

  addToTerms(name) {
    let {termsChecked} = this.state;
    termsChecked = termsChecked.filter(t => t !== name);
    this.setState({
      termsChecked: termsChecked,
    }, () => {
      this.setState({terms: this.getTerms()});
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
    this.props.applyFacet(this.props.name, this.state.termsChecked, this.state.order);
    this.toggle();
  }

  handleCleanAll = () => {
    this.props.applyFacet(this.props.name, [], "asc");
    this.toggle();
  }

  isTermInScope = (term) => {
    const cscope = this.props.catalogScope || [];
    if (cscope.length == 0)
      return true;
    const tscope = this.props.values.termEntries[term];
    return tscope.some(e => cscope.includes(e));
  }

  getTermFragment = (inputField, idx) => {
    let { termEntries } = this.props.values;
    // if (!this.isTermInScope(inputField))
    //   return
    return (
      <Fragment key={`${inputField}~${idx}`}>
        <FormGroup className="ml-5 mb-0">
          <Label>
            <Input type="checkbox" name={inputField} checked={this.isChecked(inputField)}
              onChange={this.handleCheckboxChange}/>
            {inputField + " (" + termEntries[inputField].length + ")"}
          </Label>
        </FormGroup>
      </Fragment>
    );
  }

  getOrderFragment = (o, label) => {
    return (
      <FormGroup check>
        <Label check>
          <Input type="radio" name="order" value={o} checked={this.state.order == o} onChange={this.setOrder} className="mr-1"/>
          {gettext(label)}
        </Label>
      </FormGroup>
    );
  }

  render() {
    const { dialogTitle, name, hasCatalogSearchTerm } = this.props;
    const { errorMsg, searchTerm, termsChecked, terms, isSubmitBtnActive } = this.state;
    
    let termsCatalogSearchTermFiltered = hasCatalogSearchTerm ? terms.filter((term) => this.isTermInScope(term)) : terms;

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
            {termsChecked
              .map((term, idx) => (
                this.getTermFragment(term, idx)
              ))}
            {termsCatalogSearchTermFiltered
              .filter((term) =>
                (typeof searchTerm === "undefined" || searchTerm === null) ||
                  (term && term.toLowerCase().includes(searchTerm.toLowerCase()))
              )
              .map((term, idx) => (
                idx + termsChecked.length < maxTerms && this.getTermFragment(term, idx)
              ))}
            {termsCatalogSearchTermFiltered.length + termsChecked.length >= maxTerms &&
              <div className="ml-1">...</div>
            }
          </Form>
          {errorMsg && <Alert color="danger">{errorMsg}</Alert>}
        </ModalBody>
        <ModalFooter>
          <Button color="primary" className="w-9" onClick={this.handleApply} disabled={!isSubmitBtnActive}>{gettext('Apply')}</Button>
          <Button className="ml-4"  color="primary" onClick={this.handleCleanAll}>{gettext('Reset')}</Button>
          <Button className="ml-4" color="secondary" onClick={this.toggle}>{gettext('Cancel')}</Button>
        </ModalFooter>
      </Modal>
    );
  }
}

KeeperCatalogFacetDialog.propTypes = propTypes;

export default KeeperCatalogFacetDialog;
