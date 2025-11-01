import React, { useState } from 'react';
import PropTypes from 'prop-types';
import { gettext } from '../../../utils/constants';
import { Utils } from '../../../utils/utils';
import TreeSection from '../../tree-section';
import TrashDialog from '../../dialog/trash-dialog';
import LibSettingsDialog from '../../dialog/lib-settings';
import RepoHistoryDialog from '../../dialog/repo-history';

import './index.css';

// KEEPER
import ArchiveLibraryDialog from '../../dialog/archive-library-dialog';
import KeeperEditMetadataDialog from '../../dialog/keeper-edit-metadata-dialog';
import CertifyLibraryDialog from '../../dialog/certify-library-dialog';


const DirOthers = ({ userPerm, repoID, currentRepoInfo }) => {

  // console.log(currentRepoInfo)

  const showSettings = currentRepoInfo.is_admin; // repo owner, department admin, shared with 'Admin' permission
  let [isSettingsDialogOpen, setSettingsDialogOpen] = useState(false);
  const toggleSettingsDialog = () => {
    setSettingsDialogOpen(!isSettingsDialogOpen);
  };

  const [showTrashDialog, setShowTrashDialog] = useState(false);
  const toggleTrashDialog = () => {
    setShowTrashDialog(!showTrashDialog);
  };

  let [isRepoHistoryDialogOpen, setRepoHistoryDialogOpen] = useState(false);
  const toggleRepoHistoryDialog = () => {
    setRepoHistoryDialogOpen(!isRepoHistoryDialogOpen);
  };

  // KEEPER
  // Archiving is switched off, switch on next line if KEEPER_ARCHIVING_ENABLED is set to true
  // const showArchive = !currentRepoInfo.encrypted && currentRepoInfo.is_admin; // repo owner, department admin, shared with 'Admin' permission
  const showArchive = false
  let [isArchiveDialogOpen, setArchiveDialogOpen] = useState(false);
  const toggleArchiveDialog = () => {
    setArchiveDialogOpen(!isArchiveDialogOpen);
  };
  const hideArchiveDialog = () => {
    setArchiveDialogOpen(false);
  };

  const showKeeperMetadata = !currentRepoInfo.encrypted && currentRepoInfo.is_admin; // repo owner, department admin, shared with 'Admin' permission
  let [isKeeperMetadataDialogOpen, setKeeperMetadataDialogOpen] = useState(false);
  const toggleKeeperMetadataDialog = () => {
    setKeeperMetadataDialogOpen(!isKeeperMetadataDialogOpen);
  };
  const hideKeeperMetadataDialog = () => {
    setKeeperMetadataDialogOpen(false);
  };

  const showCertify = !currentRepoInfo.encrypted && currentRepoInfo.is_admin; // repo owner, department admin, shared with 'Admin' permission
  let [isCertifyDialogOpen, setCertifyDialogOpen] = useState(false);
  const toggleCertifyDialog = () => {
    setCertifyDialogOpen(!isCertifyDialogOpen);
  };
  const hideCertifyDialog = () => {
    setCertifyDialogOpen(false);
  };

  // END KEEPER

  return (
    <TreeSection title={gettext('Others')} className="dir-others">
      {showSettings && (
        <div className='dir-others-item text-nowrap' title={gettext('Settings')} onClick={toggleSettingsDialog}>
          <span className="sf3-font-set-up sf3-font"></span>
          <span className="dir-others-item-text">{gettext('Settings')}</span>
        </div>
      )}
      {userPerm == 'rw' && (
        <div className='dir-others-item text-nowrap' title={gettext('Trash')} onClick={toggleTrashDialog}>
          <span className="sf3-font-trash sf3-font"></span>
          <span className="dir-others-item-text">{gettext('Trash')}</span>
        </div>
      )}
      {Utils.isDesktop() && (
        <div className='dir-others-item text-nowrap' title={gettext('History')} onClick={toggleRepoHistoryDialog}>
          <span className="sf3-font-history sf3-font"></span>
          <span className="dir-others-item-text">{gettext('History')}</span>
        </div>
      )}
      {showArchive && (
        <div className='dir-others-item text-nowrap' title={gettext('Archive Library')} onClick={toggleArchiveDialog}>
          <span className="sf3-font-upload sf3-font"></span>
          <span className="dir-others-item-text">{gettext('Archive')}</span>
        </div>
      )}
      {showKeeperMetadata && (
        <div className='dir-others-item text-nowrap' title={gettext('Edit Library Metadata')} onClick={toggleKeeperMetadataDialog}>
          <span className="sf3-font-files2 sf3-font"></span>
          <span className="dir-others-item-text">{gettext('Library Metadata')}</span>
        </div>
      )}
      {showCertify && (
        <div className='dir-others-item text-nowrap' title={gettext('Certify Library')} onClick={toggleCertifyDialog}>
          <span className="sf3-font-magic sf3-font"></span>
          <span className="dir-others-item-text">{gettext('Certify Library')}</span>
        </div>
      )}

      {showTrashDialog && (
        <TrashDialog
          repoID={repoID}
          currentRepoInfo={currentRepoInfo}
          showTrashDialog={showTrashDialog}
          toggleTrashDialog={toggleTrashDialog}
        />
      )}
      {isSettingsDialogOpen && (
        <LibSettingsDialog
          repoID={repoID}
          currentRepoInfo={currentRepoInfo}
          toggleDialog={toggleSettingsDialog}
        />
      )}
      {isRepoHistoryDialogOpen && (
        <RepoHistoryDialog
          repoID={repoID}
          userPerm={userPerm}
          currentRepoInfo={currentRepoInfo}
          toggleDialog={toggleRepoHistoryDialog}
        />
      )}
      {isArchiveDialogOpen && (
        <ArchiveLibraryDialog
          repoID={repoID}
          repoName={currentRepoInfo.repo_name}
          toggleDialog={toggleArchiveDialog}
          hideDialog={hideArchiveDialog}
        />
      )}
      {isKeeperMetadataDialogOpen && (
        <KeeperEditMetadataDialog
          repoID={repoID}
          repoName={currentRepoInfo.repo_name}
          toggleDialog={toggleKeeperMetadataDialog}
          hideDialog={hideKeeperMetadataDialog}
        />
      )}
      {isCertifyDialogOpen && (
        <CertifyLibraryDialog
          repoID={repoID}
          repoName={currentRepoInfo.repo_name}
          toggleDialog={toggleCertifyDialog}
          hideDialog={hideCertifyDialog}
        />
      )}
    </TreeSection>
  );
};

DirOthers.propTypes = {
  userPerm: PropTypes.string,
  repoID: PropTypes.string,
  currentRepoInfo: PropTypes.object.isRequired,
};

export default DirOthers;
