import React from 'react';
import ReactDOM from 'react-dom';
import {
  gettext,
  siteRoot,
  mediaUrl,
  logoPath,
  logoWidth,
  logoHeight,
  siteTitle,
} from './utils/constants';
import PDFViewer from './components/pdf-viewer';
import ExpandText from './components/expand-text';
import ReadMoreArea from '@foxeian/react-read-more';

import './css/bloxberg-certificate.css';
import './css/pdf-file-view.css';
const {
  repoName,
  repoDesc,
  institute,
  authors,
  year,
  transactionId,
  pdfUrl,
  metadataUrl,
  historyFileUrl,
} = window.bloxbergCertificate.pageOptions;

class BloxbergCertificatePage extends React.Component {
  constructor(props) {
    super(props);
  }

  render() {
    let transactionLink = "__BLOXBERG_EXPLORER__/tx/" + transactionId;
    return (
      <div className="h-100 d-flex flex-column">
        <div className="top-header d-flex justify-content-between">
          <a href={siteRoot}>
            <img
              src={mediaUrl + logoPath}
              height={logoHeight}
              width={logoWidth}
              title={siteTitle}
              alt="logo"
            />
          </a>
        </div>

        <div className="container-fluid pt-4 pb-6 o-auto">
          <div className="row">
            <div className="col-md-6 offset-md-1 shadow">
              <h1>
                <ExpandText
                  maxLength={40}
                  className="cert_title"
                  text={repoName}
                />
              </h1>
              <ReadMoreArea
                lettersLimit={500}
                expandLabel="Read more"
                collapseLabel="Read less"
              >
                {repoDesc}
              </ReadMoreArea>
              <div className="table_row">
                <b>{gettext('Author(s)')}: </b>
                {authors}
              </div>
              {institute && (
                <div className="cert_table_row">
                  <b>{gettext('Institute')}: </b>
                  {institute}
                </div>
              )}
              {year && (
                <div className="cert_table_row">
                  <b>{gettext('Year')}: </b>
                  {year}
                </div>
              )}
              <div className="cert_table_row">
                <b>{gettext('Transaction')}: </b>
                <a href={transactionLink} target="_blank" rel="noreferrer">
                  {transactionId}
                </a>
              </div>
              <div className="cert_table_row">
                <a href={historyFileUrl} download>
                  {gettext('Download File')}
                </a>
              </div>
              <div className="cert_table_row">
                <a href={pdfUrl} download>
                  {gettext('Download Certificate')}
                </a>
              </div>
            </div>
            <div className="col-md-4">
              <blockcerts-verifier
                display-mode="card"
                src={metadataUrl}
              ></blockcerts-verifier>
            </div>
          </div>
        </div>
        <div className="file-view-content flex-1 pdf-file-view">
          <PDFViewer />
        </div>
      </div>
    );
  }
}

ReactDOM.render(
  <BloxbergCertificatePage />,
  document.getElementById('wrapper')
);
