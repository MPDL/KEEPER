import React from 'react';
import { gettext } from '../../utils/constants';

// KEEPER: self-service Data Transfer section on the user settings / profile page
// (/profile/). Shown under the Social Login / SAML section. Links to the
// self-service data transfer page at /account/migrate/.
class DataTransfer extends React.Component {

  render() {
    return (
      <div id="data-transfer" className="setting-item">
        <h3 className="setting-item-heading">{gettext('Data Transfer')}</h3>
        <p className="mb-2">
          {gettext('Data transfer is needed sometimes after activating SAML (SSO). If you have activated SSO and lost access to your libraries and groups, login again using the local account credentials and proceed with data transfer.')}
        </p>
        <a href="/account/migrate/" className="btn btn-outline-primary">
          {gettext('Go to Data Transfer')}
        </a>
      </div>
    );
  }
}

export default DataTransfer;
