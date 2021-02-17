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
        const {repoID} = this.props;
        keeperAPI.canCertify(repoID).then(() => {
            this.certifyLibrary()
        }).catch(error => {
            let errMessage = Utils.getErrorMsg(error);
            toaster.danger(errMessage);
        })
    }

    certifyLibrary = () => {
        const {repoID, repoName} = this.props;
        toaster.success("Certifying the library through bloxberg", {duration: 3});
        keeperAPI.certifyOnBloxberg(repoID, '/', 'dir', repoName).then(() => {
            toaster.success(`Your files with the library ${repoName} are currently being certified. We will inform you once the task has successfully finished. This may take a while.`, {duration: 3});
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
                    <span>Certify all files within the library via the bloxberg blockchain. A new entry under “Library Details” on the left sidebar will be created, where you can access the certified version and the file and a proof of certification. Certifying may take some time, depending on the size of the library. Adding metadata is optional, but recommended.</span>
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
