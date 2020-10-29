import React, {Fragment} from 'react';
import PropTypes from 'prop-types';
import {Modal, ModalBody, ModalFooter, ModalHeader} from 'reactstrap';
import {gettext} from '../../utils/constants';
import {keeperAPI} from '../../utils/seafile-api';
import {Utils} from '../../utils/utils';
import toaster from '../toast';
import KeeperArchiveMetadataForm from '../keeper-archive-metadata-form';

const propTypes = {
    repoID: PropTypes.string.isRequired,
    repoName: PropTypes.string.isRequired,
    toggleDialog: PropTypes.func.isRequired,
    hideDialog: PropTypes.func.isRequired
};

class KeeperEditMetadataDialog extends React.Component {
    constructor(props) {
        super(props);
    }

    onUpdateArchiveMetadata = (defaultMd, state) => {
        this.props.hideDialog();
        let newState = {};
        Object.keys(defaultMd).map(k => {
            newState[k] = state[k];
        });
        //return promise, not run!
        return keeperAPI
            .updateArchiveMetadata(this.props.repoID, newState)
            .then((res) => {
                newState = res.data;
                newState.validMd = state.validMd;
                //if publisher is empty, apply defaultPublisher
                if (!("publisher" in newState && newState.publisher && newState.publisher.trim())) {
                    newState.publisher = defaultMd.publisher;
                    newState.validMd.publisher = true;
                }
                return newState;
            })
            .catch((error) => {
                let errMessage = Utils.getErrorMsg(error);
                toaster.danger(errMessage);
            });
    }

    render() {
        return (
            <KeeperArchiveMetadataForm
                hideDialog={this.props.hideDialog}
                repoID={this.props.repoID}
                header={
                    <Fragment>
                        <span>{gettext("Edit Metadata for ")}</span>
                        <span style={{color: '#57a5b8'}}> {this.props.repoName}</span>
                        <span> {gettext("library")}</span>
                    </Fragment>
                }
                onButton1={this.onUpdateArchiveMetadata}
                button1Label={gettext("Save metadata")}
            />
        )
    }
}

KeeperEditMetadataDialog.propTypes = propTypes;

export default KeeperEditMetadataDialog;
