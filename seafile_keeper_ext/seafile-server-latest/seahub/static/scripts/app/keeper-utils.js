define([
  'jquery',
  'underscore',
  'common',
  'js.cookie'
], function ($, _, Common, Cookie) {
  'use strict';

  var keeperUtils = {}


  keeperUtils.start_archive = function (repo_name, repo_id) {
    $.ajax({
      url: "/api2/ajax/can-archive/",
      data: {
        repo_id: repo_id,
      },
      cache: false,
      dataType: 'json',
      beforeSend: Common.prepareCSRFToken,
      success: function (data) {
        if (data.status === "success") {
          keeperUtils.archive(repo_name, repo_id, data.quota);
        } else if (data.status === "in_processing") {
          Common.feedback(data.msg, 'error', 8000);
        } else if (data.status === "quota_expired") {
          keeperUtils.archive_failed(repo_name, data.status, "");
        } else if (data.status === "snapshot_archived") {
          keeperUtils.archive_failed(repo_name, data.status, "");
        } else if (data.status === "is_too_big") {
          keeperUtils.archive_failed(repo_name, data.status, "");
        } else if (data.status === "metadata_error") {
          keeperUtils.archive_failed(repo_name, data.status, data.msg);
        } else if (data.status === "system_error") {
          keeperUtils.archive_failed(repo_name, data.status, data.msg);
        }
      },
      error: function (error) {
        keeperUtils.archive_failed(repo_name, "unknown", "");
      }
    })
    return false;
  }


  keeperUtils.archive = function (repo_name, repo_id, quota) {
    var info_archiving_link = "<a href=https://mpdl.zendesk.com/hc/en-us/articles/360011432700-Archiving target=\"_blank\">" + gettext("Information on Archiving") + "</a>."
    var archive_info = gettext("By archiving this library, the current state of everything contained within it will be archived on a dedicated archiving system. For more information, please follow the link: {archive_info_link} This library can be archived {quota} more times.").replace("{archive_info_link}", info_archiving_link).replace("{quota}", quota);
    var $form = $('<form action="" method=""><h3 id="dialogTitle">' + gettext("Archive {library_name}").replace("{library_name}", '<span style="color:#57a5b8;">' + repo_name + '</span></h3><p>') + archive_info + '</p><button type="submit" class="submit">' + gettext("Archive") + '</button></form>');

    var $el = $('<div><span class="loading-icon loading-tip"></span></div>');
    $el.modal({ focus: false, minWidth: 400 });
    $('#simplemodal-container').css({ 'height': 'auto' });
    $('#simplemodal-data').html($form);

    $form.on('submit', function () {
      var $submit = $('[type="submit"]', $form);

      Common.disableButton($submit);
      $.ajax({
        url: "/api2/ajax/archive/",
        data: {
          repo_id: repo_id,
        },
        dataType: "json",
        beforeSend: Common.prepareCSRFToken,
        success: function (data) {
          if (data.status) {
            Common.feedback(data.msg, data.status, 8000);
          } else {
            Common.feedback('Archive Library Failed', 'error');
          }
        }
      });
      $.modal.close();
      return false;
    });
  }


  keeperUtils.archive_failed = function (repo_name, error_type, error_msg) {
    var archive_info;
    switch (error_type) {
      case "quota_expired":
        archive_info = gettext("Cannot archive, since the maximum number of archives for this library has been reached. Please contact Keeper support.");
        break;
      case "snapshot_archived":
        archive_info = gettext("Cannot archive, since the library snapshot has already been archived.");
        break;
      case "is_too_big":
        archive_info = gettext("Cannot archive, since the library is too large.");
        break;
      case "metadata_error":
        archive_info = error_msg;
        break;
      case "system_error":
        archive_info = error_msg;
        break;
      default:
        archive_info = "Can not archive due to unknown reason, please contact support.";
        break;
    }

    Common.feedback(archive_info, 'error');
  }

  return keeperUtils;
});
