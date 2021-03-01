import React from 'react';
import ReactDOM from 'react-dom';
import { navigate } from '@reach/router';
import { Utils } from './utils/utils';
import { gettext, siteRoot, mediaUrl, logoPath, logoWidth, logoHeight, siteTitle } from './utils/constants';
import Loading from './components/loading';
import Paginator from './components/paginator';
import CommonToolbar from './components/toolbar/common-toolbar';
import NoticeItem from './components/common/notice-item';
import PDFViewer from './components/pdf-viewer';
import ExpandText from './components/expand-text';
import ShowMore from 'react-show-more';

import './css/bloxberg-certificate.css';
const {
  repoName, repoDesc, institute, authors, year, 
  doi_repos, archive_repos, bloxberg_certs, owner_contact_email
} = window.libraryDetails.pageOptions;


class LibraryDetailsPage extends React.Component {

  constructor(props) {
    super(props);
    this.archiveTheadData = [
      {width: '20%', text: gettext('Version')},
      {width: '50%', text: gettext('Date')},
      {width: '30%', text: gettext('Link to Archive')},
    ];

    this.doiTheadData = [
      {width: '50%', text: gettext('Date')},
      {width: '50%', text: gettext('DOI')},
    ]

    this.certTheadData = [
      {width: '20%', text: gettext('Name')},
      {width: '50%', text: gettext('Date')},
      {width: '30%', text: gettext('Link')},
    ]

    this.state = {
      showArchives: (JSON.parse(archive_repos).length > 0) ? true : false,
      showDoi: (JSON.parse(doi_repos).length > 0) ? true : false,
      showCerts: (JSON.parse(bloxberg_certs).length > 0) ? true : false,
    }
  }

  render() {
    return(
       <div className="h-100 d-flex flex-column">
          <div className="top-header d-flex justify-content-between">
            <a href={siteRoot}>
              <img src={mediaUrl + logoPath} height={logoHeight} width={logoWidth} title={siteTitle} alt="logo" />
            </a>
          </div>

          <div className="flex-auto container-fluid pt-4 pb-6 o-auto">
              <div className="row">
                <div className="col-md-6 offset-md-1">
                  <h1><ExpandText
                    maxLength={40}
                    className='cert_title'
                    text={repoName}
                  />
                  </h1>
                  <ShowMore
                      lines={3}
                      more='Show more'
                      less='Show less'
                      anchorClass=''
                  >
                      {repoDesc}
                  </ShowMore>
                  <br/>
                  <div className="table_row"><b>{gettext('Author(s)')}: </b>{authors}</div>
                  {institute && <div className="cert_table_row"><b>{gettext('Institute')}: </b>{institute}</div>}
                  {year && <div className="cert_table_row"><b>{gettext('Year')}: </b>{year}</div>}
                  <br/>
                  {this.state.showArchives && 
                    <div className="d-flex justify-content-between align-items-center op-bar">
                      <p className="m-0">{gettext('Archives')}</p>
                    </div>
                  }
                  {this.state.showArchives &&
                    <Content
                      theadData={this.archiveTheadData}
                      data={JSON.parse(archive_repos)}
                      type="archive"
                    />
                  }
                  {this.state.showArchives && <br/>}

                  {this.state.showDoi && 
                    <div className="d-flex justify-content-between align-items-center op-bar">
                      <p className="m-0">{gettext('Digital Object Identifier(DOI)')}</p>
                    </div>
                  }
                  {this.state.showDoi &&
                    <Content
                      theadData={this.doiTheadData}
                      data={JSON.parse(doi_repos)}
                      type="doi"
                    />
                  }
                  {this.state.showDoi && <br/>}
                  {this.state.showCerts && 
                    <div className="d-flex justify-content-between align-items-center op-bar">
                      <p className="m-0">{gettext('bloxberg Transactions')}</p>
                    </div>
                  }
                  {this.state.showCerts &&
                    <Content
                      theadData={this.certTheadData}
                      data={JSON.parse(bloxberg_certs)}
                      type="cert"
                    />
                  }
                  {this.state.showCerts && <br/>}

                  <div className="table_row"><b>{gettext('Contact')}: </b><a href={"mailto:" + owner_contact_email}>{owner_contact_email}</a></div>
                </div>
              </div>
          </div>
        </div>
    )
  }
}

class Content extends React.Component {

  constructor(props) {
    super(props);
  } 

  renderTbody = (data, type) => {
    switch(type) {
      case "archive":
        return data.map((item, index) =>
          (<tr key={index}>
            <td>{item.version} </td>
            <td>{item.created} </td>
            <td>
              <a href={`${siteRoot}archive/libs/${item.repo_id}/${item.version}/0/`} title={gettext('Link')}>{gettext('Link')}</a>
            </td>
          </tr>))
      case "doi":
        return data.map((item, index) =>
          (<tr key={index}>
            <td>{item.created} </td>
            <td>
              <a href={item.doi}>{item.doi}</a>
            </td>
          </tr>))
      case "cert":
        return data.map((item, index) =>
        (<tr key={index}>
          <td>{item.content_name} </td>
          <td>{item.created} </td>
          {item.path == '/' ? 
            <td>
              <a href={`${siteRoot}bloxberg-cert/transaction/${item.transaction_id}/`}>{gettext('Link to certificates')}</a>
            </td> : 
            <td>
              <a href={`${siteRoot}bloxberg-cert/transaction/${item.transaction_id}/${item.checksum}/`}>{gettext('Link to certificate')}</a>
            </td>
          }
        </tr>))
    }
  }

  render() {
    const { theadData, data, type } = this.props;
    return (
      <table className="table-hover">
        <thead>
          <tr>
            {theadData.map((item, index) => {
              return <th key={index} width={item.width}>{item.text}</th>;
            })}
          </tr>
        </thead>
        <tbody>
          {this.renderTbody(data, type)}
        </tbody>
      </table>
    );
  }
}


ReactDOM.render(
  <LibraryDetailsPage />,
  document.getElementById('wrapper')
);