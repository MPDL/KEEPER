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
import '@bloxberg-org/blockcerts-verifier/dist/ie11.js'

import './css/bloxberg-certificate.css';
import './css/pdf-file-view.css';
const {
  repoName, repoDesc, institute, authors, year, 
  transactionId, pdfUrl, metadataUrl, historyFileUrl, datasetLink
} = window.bloxbergCertificate.pageOptions;


class BloxbergCertificatePage extends React.Component {

  constructor(props) {
    super(props);
    this.state = {
      modalIsOpen:false,
      metadataUrl:metadataUrl
    };
  }


  toggleModal = () => {
    this.setState({ 
      modalIsOpen: !this.state.modalIsOpen,
      metadataUrl: ''
    });
  }

  render() {

    let PDFViewerClassName = this.state.modalIsOpen ? "file-view-content-full flex-1 pdf-file-view col-md-8 offset-md-2" : "file-view-content flex-1 pdf-file-view col-md-8 offset-md-2"
    let transactionLink = "https://blockexplorer.bloxberg.org/tx/" + transactionId + "/internal_transactions"
    return(
       <div className="h-100 d-flex flex-column">
          <div className="top-header d-flex justify-content-between">
            <a href={siteRoot}>
              <img src={mediaUrl + logoPath} height={logoHeight} width={logoWidth} title={siteTitle} alt="logo" />
            </a>
          </div>

          {!this.state.modalIsOpen && <div className="pt-4 pb-6 o-auto">
              <div className="row">
                <div className="col-md-6 offset-md-1 shadow">
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
                  <div className="table_row"><b>Author(s): </b>{authors}</div>
                  {institute && <div className="cert_table_row"><b>Institute: </b>{institute}</div>}
                  {year && <div className="cert_table_row"><b>Year: </b>{year}</div>}
                  <div className="cert_table_row"><b>Transaction: </b><a href={transactionLink} target="_blank">{transactionId}</a></div>
                  <div className="cert_table_row"><a href={ historyFileUrl }>Link to dataset</a></div>
                  <div className="cert_table_row"><a href={ pdfUrl } download>download certificate</a></div>
                </div>
                <div className="col-md-4">
                  <blockcerts-verifier display-mode="card" src={this.state.metadataUrl}></blockcerts-verifier>
                </div>
              </div>
          </div>}
          <div className={ PDFViewerClassName } onClick={this.toggleModal}>
            <PDFViewer />
          </div>

          
        </div>
    )
  }

}


ReactDOM.render(
  <BloxbergCertificatePage />,
  document.getElementById('wrapper')
);