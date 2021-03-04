import React from 'react';
import ReactDOM from 'react-dom';
import { navigate } from '@reach/router';
import { Utils } from './utils/utils';
import { gettext, siteRoot, mediaUrl, logoPath, logoWidth, logoHeight, siteTitle } from './utils/constants';
import { seafileAPI } from './utils/seafile-api';
import Loading from './components/loading';
import ModalPortal from './components/modal-portal';
import toaster from './components/toast';
import CommonToolbar from './components/toolbar/common-toolbar';

import './css/toolbar.css';
import './css/search.css';

import './css/repo-snapshot.css';

const { 
  repoID, repoName, checksums, transactionId,
  commitID, commitTime, commitDesc, commitRelativeTime,
  showAuthor, authorAvatarURL, authorName, authorNickName
} = window.app.pageOptions;

class BloxbergRepoSnapshot extends React.Component {

  constructor(props) {
    super(props);
    this.state = {
      isLoading: true,
      errorMsg: '',
      folderPath: '/',
      folderItems: [],
    };
  }

  componentDidMount() {
    this.renderFolder(this.state.folderPath);
  }

  onSearchedClick = (selectedItem) => {
    if (selectedItem.is_dir === true) {
      let url = siteRoot + 'library/' + selectedItem.repo_id + '/' + selectedItem.repo_name + selectedItem.path;
      navigate(url, {repalce: true});
    } else {
      let url = siteRoot + 'lib/' + selectedItem.repo_id + '/file' + Utils.encodePath(selectedItem.path);
      let newWindow = window.open('about:blank');
      newWindow.location.href = url;
    }
  }

  renderFolder = (folderPath) => {
    this.setState({
      folderPath: folderPath,
      folderItems: [],
      isLoading: true
    });

    seafileAPI.listCommitDir(repoID, commitID, folderPath).then((res) => {
      this.setState({
        isLoading: false,
        folderItems: res.data.dirent_list
      });
    }).catch((error) => {
      this.setState({
        isLoading: false,
        errorMsg: Utils.getErrorMsg(error, true) // true: show login tip if 403
      }); 
    });
  }

  clickFolderPath = (folderPath, e) => {
    e.preventDefault();
    this.renderFolder(folderPath);
  }

  renderPath = () => {
    const path = this.state.folderPath;
    const pathList = path.split('/');

    if (path == '/') {
      return repoName;
    }

    return (
      <React.Fragment>
        <a href="#" onClick={this.clickFolderPath.bind(this, '/')}>{repoName}</a>
        <span> / </span>
        {pathList.map((item, index) => {
          if (index > 0 && index != pathList.length - 1) {
            return (
              <React.Fragment key={index}>
                <a href="#" onClick={this.clickFolderPath.bind(this, pathList.slice(0, index+1).join('/'))}>{pathList[index]}</a>
                <span> / </span>
              </React.Fragment>
            );  
          }
        }
        )}  
        {pathList[pathList.length - 1]} 
      </React.Fragment>
    );
  }

  render() {
    const { isConfirmDialogOpen, folderPath } = this.state;

    return (
      <React.Fragment>
        <div className="h-100 d-flex flex-column">
          <div className="top-header d-flex justify-content-between">
            <a href={siteRoot}>
              <img src={mediaUrl + logoPath} height={logoHeight} width={logoWidth} title={siteTitle} alt="logo" />
            </a>
            <CommonToolbar onSearchedClick={this.onSearchedClick} />
          </div>
          <div className="flex-auto container-fluid pt-4 pb-6 o-auto">
            <div className="row">
              <div className="col-md-10 offset-md-1">
                <h2 dangerouslySetInnerHTML={{__html: Utils.generateDialogTitle(gettext('{placeholder} Snapshot'), repoName) + ` <span class="heading-commit-time">(${commitTime})</span>`}}></h2>
                {folderPath == '/' && (
                  <div className="d-flex mb-2 align-items-center">
                    <p className="m-0">{commitDesc}</p>
                    <div className="ml-4 border-left pl-4 d-flex align-items-center">
                      {showAuthor ? (
                        <React.Fragment>
                          <img src={authorAvatarURL} width="20" height="20" alt="" className="rounded mr-1" />
                          <a href={`${siteRoot}profile/${encodeURIComponent(authorName)}/`}>{authorNickName}</a>
                        </React.Fragment>
                      ) : <span>{gettext('Unknown')}</span>}
                      <p className="m-0 ml-2" dangerouslySetInnerHTML={{__html: commitRelativeTime}}></p>
                    </div>
                  </div>
                )}
                <div className="d-flex justify-content-between align-items-center op-bar">
                  <p className="m-0">{gettext('Current path: ')}{this.renderPath()}</p>
                </div>
                <Content 
                  data={this.state}
                  renderFolder={this.renderFolder}
                />
              </div>
            </div>
          </div>
        </div>
      </React.Fragment>
    );
  }
}

class Content extends React.Component {

  constructor(props) {
    super(props);
    this.theadData = [
      {width: '5%', text: ''},
      {width: '50%', text: gettext('Name')},
      {width: '15%', text: gettext('Size')},
      {width: '15%', text: ''},
      {width: '15%', text: ''}
    ];
  } 

  render() {
    const { isLoading, errorMsg, folderPath, folderItems } = this.props.data;

    if (isLoading) {
      return <Loading />;
    }

    if (errorMsg) {
      return <p className="error mt-6 text-center">{errorMsg}</p>;
    }

    return (
      <table className="table-hover">
        <thead>
          <tr>
            {this.theadData.map((item, index) => {
              return <th key={index} width={item.width}>{item.text}</th>;
            })}
          </tr>
        </thead>
        <tbody>
          {folderItems.map((item, index) => {
            return <FolderItem 
              key={index}
              item={item} 
              folderPath={folderPath}
              renderFolder={this.props.renderFolder}
            />;
          })
          }
        </tbody>
      </table>
    );
  }
}

class FolderItem extends React.Component {

  constructor(props) {
    super(props);
    this.state = {
      isIconShown: false
    };
  }

  handleMouseOver = () => {
    this.setState({isIconShown: true});
  }

  handleMouseOut = () => {
    this.setState({isIconShown: false});
  }

  renderFolder = (e) => {
    e.preventDefault();

    const item = this.props.item;
    const { folderPath } = this.props;
    this.props.renderFolder(Utils.joinPath(folderPath, item.name));
  }

  render() {
    const item = this.props.item;
    const { isIconShown } = this.state;
    const { folderPath } = this.props;
    return item.type == 'dir' ? (
      <tr onMouseOver={this.handleMouseOver} onMouseOut={this.handleMouseOut}>
        <td className="text-center"><img src={Utils.getFolderIconUrl()} alt={gettext('Directory')} width="24" /></td>
        <td><a href="#" onClick={this.renderFolder}>{item.name}</a></td>
        <td></td>
        <td></td>
      </tr>
    ) : (
      <tr onMouseOver={this.handleMouseOver} onMouseOut={this.handleMouseOut}>
        <td className="text-center"><img src={Utils.getFileIconUrl(item.name)} alt={gettext('File')} width="24" /></td>
        <td><a href={`${siteRoot}repo/${repoID}/snapshot/files/?obj_id=${item.obj_id}&commit_id=${commitID}&p=${encodeURIComponent(Utils.joinPath(folderPath, item.name))}`} target="_blank">{item.name}</a></td>
        <td>{Utils.bytesToSize(item.size)}</td>
        <td className="text-center">
          <a href={`${siteRoot}api2/bloxberg-pdf/${transactionId}/${JSON.parse(checksums)[Utils.joinPath(folderPath, item.name)]}/?p=${encodeURIComponent(Utils.joinPath(folderPath, item.name))}`} download className={`${isIconShown ? '': 'invisible'}`} title={gettext('Download Certificate')}>{gettext('Download Certificate')}</a>
        </td>
        <td className="text-center">
          <a href={`${siteRoot}repo/${repoID}/${item.obj_id}/download/?file_name=${encodeURIComponent(item.name)}&p=${encodeURIComponent(Utils.joinPath(folderPath, item.name))}`} className={`${isIconShown ? '': 'invisible'}`} title={gettext('Download File')}>{gettext('Download File')}</a>
        </td>
      </tr>
    );
  }
}

ReactDOM.render(
  <BloxbergRepoSnapshot />,
  document.getElementById('wrapper')
);
