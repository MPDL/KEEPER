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

class ArchiveLibraryDialog extends React.Component {
    constructor(props) {
        super(props);
    }

    onUpdateArchiveMetadata = (defaultMd, state) => {
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

    onArchiveClick = (a, b) => {
        this.props.hideDialog();
        //return promise, not run!
        return keeperAPI.archiveLibrary(this.props.repoID)
            .then((resp) => {
                return resp.data.msg;
        });
    }

    render() {
        const archive_info = gettext("By archiving this library, the current state of everything contained within " +
            "it will be archived on a dedicated archiving system. For more information, please follow the link: " +
            "{archive_info_link} This library can be archived {quota} more times. Please, fill out the following archive metadata form.").replace("{quota}",
            this.props.quota);
        const split = archive_info.split('{archive_info_link}')
        return (
                <KeeperArchiveMetadataForm
                    hideDialog={this.props.hideDialog}
                    repoID={this.props.repoID}
                    header={
                        <Fragment>
                            <span>{gettext('Archive {library_name}').replace('{library_name}', '')}</span>
                            <span style={{color: '#57a5b8'}}>{this.props.repoName}</span>
                            <span> {gettext('library')}</span>
                        </Fragment>
                    }
                    body={
                        <Fragment>
                            {split[0]}
                            <a href="https://mpdl.zendesk.com/hc/en-us/articles/360011432700-Archiving"
                                target="_blank">{gettext("Information on Archiving")}</a>.
                            {split[1]}
                        </Fragment>
                    }
                    onButton1={this.onUpdateArchiveMetadata}
                    button1Label={gettext("Save metadata")}
                    onButton2={this.onArchiveClick}
                    button2Label={gettext("Archive")}
                />
        )
    }
}

ArchiveLibraryDialog.propTypes = propTypes;

export default ArchiveLibraryDialog;
