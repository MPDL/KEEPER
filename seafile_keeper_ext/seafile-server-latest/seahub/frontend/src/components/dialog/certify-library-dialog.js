import React from 'react';
import PropTypes from 'prop-types';
import {Modal, ModalHeader, ModalBody, ModalFooter} from 'reactstrap';
import {gettext} from '../../utils/constants';
import {keeperAPI} from '../../utils/seafile-api';
import {Utils} from '../../utils/utils';
import toaster from '../toast';

const propTypes = {
    repoID: PropTypes.string.isRequired,
    repoName: PropTypes.string.isRequired,
    toggleDialog: PropTypes.func.isRequired,
    hideDialog: PropTypes.func.isRequired
};

class CertifyLibraryDialog extends React.Component {
    constructor(props) {
        super(props);
    }


    formSubmit = () => {
        this.props.hideDialog();
        const {repoID, repoName} = this.props;
        toaster.success("Certify the Library through Bloxberg...", {duration: 4});
        keeperAPI.certifyOnBloxberg(repoID, '/', 'dir', repoName).then(() => {
          toaster.success("Transaction succeeded");
        }).catch(error => {
          let errMessage = Utils.getErrorMsg(error);
          toaster.danger(errMessage);
        });
    }

    render() {
        return (
            <Modal isOpen={true} toggle={this.props.hideDialog}>
                <ModalHeader toggle={this.props.hideDialog}>
                    <span>{gettext('Certify {library_name}').replace('{library_name}', '')}</span> <span
                    style={{color: '#57a5b8'}}>{this.props.repoName}</span> </ModalHeader>
                <ModalBody>
                    <span>Neque porro quisquam est qui dolorem ipsum quia dolor sit amet</span>
                </ModalBody>
                <ModalFooter>
                    <button className="btn btn-primary" onClick={this.formSubmit}>Certify</button>
                </ModalFooter>
            </Modal>
        )
    }
}

CertifyLibraryDialog.propTypes = propTypes;

export default CertifyLibraryDialog;
