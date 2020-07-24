import React from 'react';
import PropTypes from 'prop-types';
import { Modal, ModalHeader, ModalBody, ModalFooter } from 'reactstrap'; 
import { gettext } from '../../utils/constants';
import { keeperAPI } from '../../utils/seafile-api';
import { Utils } from '../../utils/utils';
import toaster from '../toast';

const propTypes = {
  repoID: PropTypes.string.isRequired,
  repoName: PropTypes.string.isRequired,
  toggleDialog: PropTypes.func.isRequired
};

class AssignDoiDialog extends React.Component {
  constructor(props) {
    super(props);
  }

  formSubmit = () => {
    const {repoID, repoName} = this.props;
    this.props.toggleDialog();
    keeperAPI.addDoi(repoID).then((res) => {
      if (res.data && res.data['msg']) {
        toaster.success(res.data['msg'], {duration: 3});
      }
    }).catch((error) => {
      let errorMsg = Utils.getErrorMsg(error);
      toaster.danger(errorMsg, {duration: 3});
    });
  }

  render() {
    return (
      <Modal isOpen={true} toggle={this.props.toggleDialog}>
        <ModalHeader toggle={this.props.toggleDialog}> <span>{gettext('Assign DOI to {library_name}').replace('{library_name}','')}</span> <span style={{color: '#57a5b8'}}>{this.props.repoName}</span> </ModalHeader>
        <ModalBody>
          {gettext("Please note: a DOI identifier will be assigned to the current state of the selected library (snapshot). The DOI will persistently reference to the snapshot and not the latest state of the library. A DOI can only be created once per library.")}
        </ModalBody>
        <ModalFooter>
          <button className="btn btn-primary" onClick={this.formSubmit}>{gettext('Assign DOI')}</button>
        </ModalFooter>
      </Modal>
    );
  }
}

AssignDoiDialog.propTypes = propTypes;

export default AssignDoiDialog;
