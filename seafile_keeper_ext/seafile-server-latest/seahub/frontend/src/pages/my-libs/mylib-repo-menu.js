import React from 'react';
import PropTypes from 'prop-types';
import { Dropdown, DropdownMenu, DropdownToggle, DropdownItem } from 'reactstrap';
import { gettext, isPro, folderPermEnabled, enableRepoSnapshotLabel, enableResetEncryptedRepoPassword, isEmailConfigured } from '../../utils/constants';
import { Utils } from '../../utils/utils';

const propTypes = {
  isPC: PropTypes.bool,
  repo: PropTypes.object.isRequired,
  isStarred: PropTypes.bool,
  onFreezedItem: PropTypes.func.isRequired,
  onUnfreezedItem: PropTypes.func.isRequired,
  onMenuItemClick: PropTypes.func.isRequired,
};

class MylibRepoMenu extends React.Component {

  constructor(props) {
    super(props);
    this.state = {
      isItemMenuShow: false,
    };
  }

  onMenuItemClick = (e) => {
    let operation = Utils.getEventData(e, 'toggle');
    this.props.onMenuItemClick(operation);
  }

  onDropdownToggleClick = (e) => {
    this.toggleOperationMenu(e);
  }

  toggleOperationMenu = (e) => {
    let dataset = e.target ? e.target.dataset : null;
    if (dataset && dataset.toggle && dataset.toggle === 'Rename') {
      this.setState({isItemMenuShow: !this.state.isItemMenuShow});
      return;
    }
    
    this.setState(
      {isItemMenuShow: !this.state.isItemMenuShow},
      () => {
        if (this.state.isItemMenuShow) {
          this.props.onFreezedItem();
        } else {
          this.props.onUnfreezedItem();
        }
      }
    );
  }

  generatorOperations = () => {
    let repo = this.props.repo;
    let showResetPasswordMenuItem = isPro && repo.encrypted && enableResetEncryptedRepoPassword && isEmailConfigured;
    let showAssignDoiMenuItem = repo.doi && !repo.encrypted;
    let showArchiveLibraryMenuItem = !repo.encrypted;
    let operations = ['Rename', 'Transfer']; 
    if (folderPermEnabled) {
      operations.push('Folder Permission');
    }
    operations.push('Share Links Admin', 'Divider');
    if (repo.encrypted) {
      operations.push('Change Password');
    }
    if (showResetPasswordMenuItem) {
      operations.push('Reset Password');
    }
    operations.push('History Setting', 'API Token');
    if (this.props.isPC && enableRepoSnapshotLabel) {
      operations.push('Label Current State');
    }
    if (showAssignDoiMenuItem) {
      operations.push('Assign DOI to current state');
    }
    if (showArchiveLibraryMenuItem) {
      operations.push('Archive Library');
    }
     return operations;
  }

  translateOperations = (item) => {
    let translateResult = '';
    switch(item) {
      case 'Star':
        translateResult = gettext('Star');
        break;
      case 'Unstar':
        translateResult = gettext('Unstar');
        break;
      case 'Share':
        translateResult = gettext('Share');
        break;
      case 'Delete':
        translateResult = gettext('Delete');
        break;
      case 'Rename':
        translateResult = gettext('Rename');
        break;
      case 'Transfer':
        translateResult = gettext('Transfer');
        break;
      case 'History Setting':
        translateResult = gettext('History Setting');
        break;
      case 'Change Password':
        translateResult = gettext('Change Password');
        break;
      case 'Reset Password':
        translateResult = gettext('Reset Password');
        break;
      case 'Folder Permission':
        translateResult = gettext('Folder Permission');
        break;
      case 'Label Current State':
        translateResult = gettext('Label Current State');
        break;
      case 'API Token':
        translateResult = 'API Token'; // translation is not needed here
        break;
      case 'Share Links Admin':
        translateResult = gettext('Share Links Admin');
        break;
      case 'Assign DOI to current state':
        translateResult = gettext('Assign DOI to current state');
        break;
      case 'Archive Library':
        translateResult = gettext('Archive Library');
        break;
       default:
        break;
    }

    return translateResult;
  }

  render() {
    let operations = this.generatorOperations();

    // pc menu
    if (this.props.isPC) {
      return (
        <Dropdown isOpen={this.state.isItemMenuShow} toggle={this.toggleOperationMenu}>
          <DropdownToggle 
            tag="i"
            className="sf-dropdown-toggle sf2-icon-caret-down"
            title={gettext('More Operations')}
            // onClick={this.clickOperationMenuToggle}
            data-toggle="dropdown" 
            aria-expanded={this.state.isItemMenuShow}
          />
          <DropdownMenu>
            {operations.map((item, index)=> {
              if (item == 'Divider') {
                return <DropdownItem key={index} divider />; 
              } else {
                return (<DropdownItem key={index} data-toggle={item} onClick={this.onMenuItemClick}>{this.translateOperations(item)}</DropdownItem>);
              }
            })}
          </DropdownMenu>
        </Dropdown>
      );
    }

    // mobile menu
    operations.unshift('Delete');
    operations.unshift('Share');
    this.props.isStarred ? operations.unshift('Unstar') : operations.unshift('Star');

    return (
      <Dropdown isOpen={this.state.isItemMenuShow} toggle={this.toggleOperationMenu}>
        <DropdownToggle 
          tag="i"
          className="sf-dropdown-toggle fa fa-ellipsis-v ml-0"
          title={gettext('More Operations')}
          // onClick={this.clickOperationMenuToggle}
          data-toggle="dropdown" 
          aria-expanded={this.state.isItemMenuShow}
        />
        <div className={`${this.state.isItemMenuShow ? '' : 'd-none'}`} onClick={this.toggleOperationMenu}>
          <div className="mobile-operation-menu-bg-layer"></div>
          <div className="mobile-operation-menu">
            {operations.map((item, index) => {
              if (item != 'Divider') {
                return (<DropdownItem key={index} className="mobile-menu-item" data-toggle={item} onClick={this.onMenuItemClick}>{this.translateOperations(item)}</DropdownItem>);
              }
            })}
          </div>
        </div>
      </Dropdown>
    );
  }
}

MylibRepoMenu.propTypes = propTypes;

export default MylibRepoMenu;
