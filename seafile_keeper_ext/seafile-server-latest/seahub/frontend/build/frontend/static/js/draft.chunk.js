(this["webpackJsonpseahub-frontend"]=this["webpackJsonpseahub-frontend"]||[]).push([[9],{1737:function(e,t,n){n(71),e.exports=n(1815)},1738:function(e,t,n){"use strict";var i=n(797),a=n(798),s=n(799),o=n(801),r=n(802),c=n(803);e.exports=function e(){var t=[],n=o(),v={},g=!1,O=-1;return w.data=function(e,t){if(r(e))return 2===arguments.length?(b("data",g),v[e]=t,w):d.call(v,e)&&v[e]||null;if(e)return b("data",g),v=e,w;return v},w.freeze=x,w.attachers=t,w.use=function(e){var n;if(b("use",g),null===e||void 0===e);else if("function"===typeof e)r.apply(null,arguments);else{if("object"!==typeof e)throw new Error("Expected usable value, not `"+e+"`");"length"in e?o(e):a(e)}n&&(v.settings=i(v.settings||{},n));return w;function a(e){o(e.plugins),e.settings&&(n=i(n||{},e.settings))}function s(e){if("function"===typeof e)r(e);else{if("object"!==typeof e)throw new Error("Expected usable value, not `"+e+"`");"length"in e?r.apply(null,e):a(e)}}function o(e){var t,n;if(null===e||void 0===e);else{if("object"!==typeof e||!("length"in e))throw new Error("Expected a list of plugins, not `"+e+"`");for(t=e.length,n=-1;++n<t;)s(e[n])}}function r(e,n){var a=C(e);a?(c(a[1])&&c(n)&&(n=i(a[1],n)),a[1]=n):t.push(l.call(arguments))}},w.parse=function(e){var t,n=s(e);if(x(),f("parse",t=w.Parser),h(t))return new t(String(n),n).parse();return t(String(n),n)},w.stringify=function(e,t){var n,i=s(t);if(x(),u("stringify",n=w.Compiler),j(e),h(n))return new n(e,i).compile();return n(e,i)},w.run=N,w.runSync=function(e,t){var n,i=!1;return N(e,t,s),p("runSync","run",i),n;function s(e,t){i=!0,a(e),n=t}},w.process=y,w.processSync=function(e){var t,n=!1;return x(),f("processSync",w.Parser),u("processSync",w.Compiler),y(t=s(e),i),p("processSync","process",n),t;function i(e){n=!0,a(e)}},w;function w(){for(var n=e(),a=t.length,s=-1;++s<a;)n.use.apply(null,t[s]);return n.data(i(!0,{},v)),n}function x(){var e,i,a,s;if(g)return w;for(;++O<t.length;)i=(e=t[O])[0],null,!1!==(a=e[1])&&(!0===a&&(e[1]=void 0),"function"===typeof(s=i.apply(w,e.slice(1)))&&n.use(s));return g=!0,O=1/0,w}function C(e){for(var n,i=t.length,a=-1;++a<i;)if((n=t[a])[0]===e)return n}function N(e,t,i){if(j(e),x(),i||"function"!==typeof t||(i=t,t=null),!i)return new Promise(a);function a(a,o){n.run(e,s(t),(function(t,n,s){n=n||e,t?o(t):a?a(n):i(null,n,s)}))}a(null,i)}function y(e,t){if(x(),f("process",w.Parser),u("process",w.Compiler),!t)return new Promise(n);function n(n,i){var a=s(e);m.run(w,{file:a},(function(e){e?i(e):n?n(a):t(null,a)}))}n(null,t)}}().freeze();var l=[].slice,d={}.hasOwnProperty,m=o().use((function(e,t){t.tree=e.parse(t.file)})).use((function(e,t,n){e.run(t.tree,t.file,(function(e,i,a){e?n(e):(t.tree=i,t.file=a,n())}))})).use((function(e,t){t.file.contents=e.stringify(t.tree,t.file)}));function h(e){return"function"===typeof e&&function(e){var t;for(t in e)return!0;return!1}(e.prototype)}function f(e,t){if("function"!==typeof t)throw new Error("Cannot `"+e+"` without `Parser`")}function u(e,t){if("function"!==typeof t)throw new Error("Cannot `"+e+"` without `Compiler`")}function b(e,t){if(t)throw new Error("Cannot invoke `"+e+"` on a frozen processor.\nCreate a new processor first, by invoking it: use `processor()` instead of `processor`.")}function j(e){if(!e||!r(e.type))throw new Error("Expected node, got `"+e+"`")}function p(e,t,n){if(!n)throw new Error("`"+e+"` finished async. Use `"+t+"` instead")}},1739:function(e,t,n){},1740:function(e,t,n){},1741:function(e,t,n){},1815:function(e,t,n){"use strict";n.r(t);var i=n(3),a=n(5),s=n(29),o=n(7),r=n(6),c=n(2),l=n.n(c),d=n(28),m=n.n(d),h=n(83),f=(n(226),n(54)),u=n(1),b=n(8),j=n(133),p=n(19),v=n(1738),g=n(507),O=n(827),w=n(828),x=n(829),C=n(835),N=n(839),y=n(129),S=n(849),D=n(857),I=n(519),k=n(858).default;var R=v().use(g,{commonmark:!0}).use(w).use(O).use(x,{allowDangerousHTML:!0}).use(N).use(C).use((function(e){var t=y(e,this.data("settings")),n=k(I,{attributes:{input:["type"],li:["className"],code:["className"]},tagNames:["input","code"]});this.Compiler=function(e){var i=D(e,n);return S(i,t)}})),L=(v().use(g,{commonmark:!0}).use(O),n(317)),T=n(320),E=n(319),_=n(191),M=n(4),q=n(10),P=(n(551),n(0)),F=function(e){Object(o.a)(n,e);var t=Object(r.a)(n);function n(e){var a;return Object(i.a)(this,n),(a=t.call(this,e)).handleCommentChange=function(e){a.setState({comment:e.target.value})},a.submitComment=function(){var e=a.state.comment.trim();e.length>0&&(b.b.postComment(u.K,u.G,e).then((function(){a.props.listComments()})).catch((function(e){var t=M.a.getErrorMsg(e);q.a.danger(t)})),a.setState({comment:""}))},a.resolveComment=function(e){b.b.updateComment(u.K,e.target.id,"true").then((function(e){a.props.listComments()})).catch((function(e){var t=M.a.getErrorMsg(e);q.a.danger(t)}))},a.editComment=function(e,t){b.b.updateComment(u.K,e,null,null,t).then((function(e){a.props.listComments()})).catch((function(e){var t=M.a.getErrorMsg(e);q.a.danger(t)}))},a.deleteComment=function(e){b.b.deleteComment(u.K,e.target.id).then((function(e){a.props.listComments()})).catch((function(e){var t=M.a.getErrorMsg(e);q.a.danger(t)}))},a.scrollToQuote=function(e,t,n){a.props.scrollToQuote(e,t,n),a.setState({comment:""})},a.state={showResolvedComment:!0,comment:""},a}return Object(a.a)(n,[{key:"componentWillReceiveProps",value:function(e){if(this.props.commentsList.length<e.commentsList.length){var t=this;setTimeout((function(){t.refs.commentsList.scrollTo(0,1e4)}),100)}}},{key:"render",value:function(){var e=this,t=this.props.commentsList;return Object(P.jsxs)("div",{className:"seafile-comment h-100",children:[Object(P.jsx)("div",{className:"flex-fill o-auto",children:t.length>0?Object(P.jsx)("ul",{className:"seafile-comment-list",ref:"commentsList",children:t.map((function(t,n){return Object(P.jsx)(H,{item:t,showResolvedComment:e.state.showResolvedComment,resolveComment:e.resolveComment,editComment:e.editComment,scrollToQuote:e.scrollToQuote,deleteComment:e.deleteComment},n)}))}):Object(P.jsx)("p",{className:"text-center my-4",children:Object(u.pb)("No comment yet.")})}),Object(P.jsxs)("div",{className:"seafile-comment-footer flex-shrink-0",children:[Object(P.jsx)("textarea",{className:"add-comment-input",value:this.state.comment,placeholder:Object(u.pb)("Add a comment..."),onChange:this.handleCommentChange,clos:"100",rows:"3",warp:"virtual"}),Object(P.jsx)("div",{className:"comment-submit-container",children:Object(P.jsx)(h.a,{className:"submit-comment",color:"primary",size:"sm",onClick:this.submitComment,children:Object(u.pb)("Submit")})})]})]})}}]),n}(l.a.Component),H=function(e){Object(o.a)(n,e);var t=Object(r.a)(n);function n(e){var a;return Object(i.a)(this,n),(a=t.call(this,e)).toggleDropDownMenu=function(){a.setState({dropdownOpen:!a.state.dropdownOpen})},a.convertComment=function(e){R.process(e.comment).then((function(e){var t=String(e);a.setState({comment:t})})),R.process(e.quote).then((function(e){var t=String(e);a.setState({quote:t})}))},a.scrollToQuote=function(){var e=a.props.item;a.props.scrollToQuote(e.newIndex,e.oldIndex,e.quote)},a.toggleEditComment=function(){a.setState({editable:!a.state.editable})},a.updateComment=function(e){var t=a.state.newComment;a.props.item.comment!==t&&a.props.editComment(e.target.id,t),a.toggleEditComment()},a.handleCommentChange=function(e){a.setState({newComment:e.target.value})},a.state={dropdownOpen:!1,comment:"",quote:"",newComment:a.props.item.comment,editable:!1},a}return Object(a.a)(n,[{key:"componentWillMount",value:function(){this.convertComment(this.props.item)}},{key:"componentWillReceiveProps",value:function(e){this.convertComment(e.item)}},{key:"render",value:function(){var e=this.props.item;return e.resolved&&!this.props.showResolvedComment?null:this.state.editable?Object(P.jsxs)("li",{className:"seafile-comment-item",id:e.id,children:[Object(P.jsxs)("div",{className:"seafile-comment-info",children:[Object(P.jsx)("img",{className:"avatar",src:e.avatarUrl,alt:""}),Object(P.jsxs)("div",{className:"reviewer-info",children:[Object(P.jsx)("div",{className:"reviewer-name ellipsis",children:e.name}),Object(P.jsx)("div",{className:"review-time",children:e.time})]})]}),Object(P.jsxs)("div",{className:"seafile-edit-comment",children:[Object(P.jsx)("textarea",{className:"edit-comment-input",value:this.state.newComment,onChange:this.handleCommentChange,clos:"100",rows:"3",warp:"virtual"}),Object(P.jsx)(h.a,{className:"comment-btn",color:"primary",size:"sm",onClick:this.updateComment,id:e.id,children:Object(u.pb)("Update")})," ",Object(P.jsx)(h.a,{className:"comment-btn",color:"secondary",size:"sm",onClick:this.toggleEditComment,children:Object(u.pb)("Cancel")})]})]}):Object(P.jsxs)("li",{className:e.resolved?"seafile-comment-item seafile-comment-item-resolved":"seafile-comment-item",id:e.id,children:[Object(P.jsxs)("div",{className:"seafile-comment-info",children:[Object(P.jsx)("img",{className:"avatar",src:e.avatarUrl,alt:""}),Object(P.jsxs)("div",{className:"reviewer-info",children:[Object(P.jsx)("div",{className:"reviewer-name ellipsis",children:e.name}),Object(P.jsx)("div",{className:"review-time",children:e.time})]}),!e.resolved&&Object(P.jsxs)(L.a,{isOpen:this.state.dropdownOpen,size:"sm",className:"seafile-comment-dropdown",toggle:this.toggleDropDownMenu,children:[Object(P.jsx)(T.a,{className:"seafile-comment-dropdown-btn",children:Object(P.jsx)("i",{className:"fas fa-ellipsis-v"})}),Object(P.jsxs)(E.a,{children:[e.userEmail===u.Cc&&Object(P.jsx)(_.a,{onClick:this.props.deleteComment,className:"delete-comment",id:e.id,children:Object(u.pb)("Delete")}),e.userEmail===u.Cc&&Object(P.jsx)(_.a,{onClick:this.toggleEditComment,className:"edit-comment",id:e.id,children:Object(u.pb)("Edit")}),Object(P.jsx)(_.a,{onClick:this.props.resolveComment,className:"seafile-comment-resolved",id:e.id,children:Object(u.pb)("Mark as resolved")})]})]})]}),e.newIndex>=-1&&e.oldIndex>=-1&&Object(P.jsx)("blockquote",{className:"seafile-comment-content",children:Object(P.jsx)("div",{onClick:this.scrollToQuote,dangerouslySetInnerHTML:{__html:this.state.quote}})}),Object(P.jsx)("div",{className:"seafile-comment-content",dangerouslySetInnerHTML:{__html:this.state.comment}})]})}}]),n}(l.a.Component),K=F,A=(n(1739),function(e){Object(o.a)(n,e);var t=Object(r.a)(n);function n(e){var a;return Object(i.a)(this,n),(a=t.call(this,e)).handleCommentChange=function(e){var t=e.target.value;a.setState({comment:t})},a.submitComment=function(){var e=a.props,t=e.quote,n=e.newIndex,i=e.oldIndex,s=a.state.comment.trim();if(0!==s.length){if(t.length>0){var o={quote:t,newIndex:n,oldIndex:i};b.b.postComment(u.K,u.G,s,JSON.stringify(o)).then((function(){a.props.onCommentAdded()})).catch((function(e){var t=M.a.getErrorMsg(e);q.a.danger(t)}))}else b.b.postComment(u.K,u.G,s).then((function(){a.props.onCommentAdded()})).catch((function(e){var t=M.a.getErrorMsg(e);q.a.danger(t)}));a.setState({comment:""})}},a.setQuoteText=function(e){R.process(e).then((function(e){var t=String(e);a.setState({quote:t})}))},a.state={comment:"",quote:""},a}return Object(a.a)(n,[{key:"componentDidMount",value:function(){this.setQuoteText(this.props.quote)}},{key:"componentWillReceiveProps",value:function(e){this.props.quote!==e.quote&&this.setQuoteText(e.quote)}},{key:"render",value:function(){return Object(P.jsxs)("div",{className:"review-comment-dialog",children:[Object(P.jsx)("div",{children:u.Qb}),Object(P.jsx)("blockquote",{className:"review-comment-dialog-quote",children:Object(P.jsx)("div",{dangerouslySetInnerHTML:{__html:this.state.quote}})}),Object(P.jsx)("textarea",{value:this.state.comment,onChange:this.handleCommentChange}),Object(P.jsxs)("div",{className:"button-group",children:[Object(P.jsx)(h.a,{size:"sm",color:"primary",onClick:this.submitComment,children:Object(u.pb)("Submit")}),Object(P.jsx)(h.a,{size:"sm",color:"secondary",onClick:this.props.toggleCommentDialog,children:Object(u.pb)("Cancel")})]}),Object(P.jsx)("span",{className:"review-comment-dialog-triangle"})]})}}]),n}(l.a.Component)),Q=n(308),G=n(123),Y=n(108),V=n(109),B=n(147),U=n(75),z=(n(1740),function(e){Object(o.a)(n,e);var t=Object(r.a)(n);function n(e){var a;return Object(i.a)(this,n),(a=t.call(this,e)).listReviewers=function(){b.b.listDraftReviewers(a.props.draftID).then((function(e){a.setState({reviewers:e.data.reviewers})}))},a.handleSelectChange=function(e){a.setState({selectedOption:e}),a.Options=[]},a.addReviewers=function(){if(a.state.selectedOption.length>0){a.refs.reviewSelect.clearSelect();for(var e=[],t=0;t<a.state.selectedOption.length;t++)e[t]=a.state.selectedOption[t].email;a.setState({loading:!0,errorMsg:[]}),b.b.addDraftReviewers(a.props.draftID,e).then((function(e){if(e.data.failed.length>0){for(var t=[],n=0;n<e.data.failed.length;n++)t[n]=e.data.failed[n];a.setState({errorMsg:t})}a.setState({selectedOption:null,loading:!1}),e.data.success.length>0&&a.listReviewers()})).catch((function(e){var t=M.a.getErrorMsg(e);q.a.danger(t)}))}},a.deleteReviewer=function(e){var t=e.target.getAttribute("name");b.b.deleteDraftReviewer(a.props.draftID,t).then((function(e){if(200===e.data){for(var n=[],i=0;i<a.state.reviewers.length;i++)a.state.reviewers[i].user_email!==t&&n.push(a.state.reviewers[i]);a.setState({reviewers:n})}})).catch((function(e){var t=M.a.getErrorMsg(e);q.a.danger(t)}))},a.state={reviewers:a.props.reviewers,selectedOption:null,errorMsg:[],loading:!1},a.Options=[],a}return Object(a.a)(n,[{key:"render",value:function(){var e=this,t=this.props.toggleAddReviewerDialog,n=this.state,i=n.reviewers,a=n.errorMsg;return Object(P.jsxs)(G.a,{isOpen:!0,toggle:t,children:[Object(P.jsx)(Y.a,{toggle:t,children:Object(u.pb)("Request a review")}),Object(P.jsxs)(V.a,{children:[Object(P.jsx)("p",{children:Object(u.pb)("Add new reviewer")}),Object(P.jsxs)("div",{className:"add-reviewer",children:[Object(P.jsx)(U.a,{placeholder:Object(u.pb)("Search users..."),onSelectChange:this.handleSelectChange,ref:"reviewSelect",isMulti:!0,className:"reviewer-select"}),this.state.selectedOption&&!this.state.loading?Object(P.jsx)(h.a,{color:"secondary",onClick:this.addReviewers,children:Object(u.pb)("Submit")}):Object(P.jsx)(h.a,{color:"secondary",disabled:!0,children:Object(u.pb)("Submit")})]}),a.length>0&&a.map((function(e){var t=arguments.length>1&&void 0!==arguments[1]?arguments[1]:0;return Object(P.jsxs)("p",{className:"reviewer-select-error error",children:[a[t].email,": ",a[t].error_msg]},t)})),i.length>0&&i.map((function(t){var n=arguments.length>1&&void 0!==arguments[1]?arguments[1]:0;return Object(P.jsxs)("div",{className:"reviewer-select-info",children:[Object(P.jsxs)("div",{className:"d-flex",children:[Object(P.jsx)("img",{className:"avatar reviewer-select-avatar",src:t.avatar_url,alt:""}),Object(P.jsx)("span",{className:"reviewer-select-name ellipsis",children:t.user_name})]}),Object(P.jsx)("i",{className:"fa fa-times",name:t.user_email,onClick:e.deleteReviewer})]},n)}))]}),Object(P.jsx)(B.a,{children:Object(P.jsx)(h.a,{color:"secondary",onClick:t,children:Object(u.pb)("Close")})})]})}}]),n}(l.a.Component)),X=z,J=n(90),W=n(1837),Z=n(1838),$=n(1836),ee=n(1839),te=n(1840),ne=n(33),ie=n.n(ne),ae=n(46),se=n(12),oe=n.n(se);n(549);oe.a.locale(window.app.config.lang);var re=function(e){Object(o.a)(n,e);var t=Object(r.a)(n);function n(e){var a;return Object(i.a)(this,n),(a=t.call(this,e)).onClick=function(e,t,n,i){if(t===a.state.activeItem)return!1;a.props.onHistoryItemClick(i,n,t)},a.onScroll=function(e){var t=e.target.clientHeight,n=e.target.scrollHeight;if(t+e.target.scrollTop+1>=n&&a.props.totalReversionCount>a.perPage*a.state.currentPage){var i=a.state.currentPage+1;a.setState({currentPage:i,loading:!0}),b.b.listFileHistoryRecords(u.K,u.G,i,a.perPage).then((function(e){var t=Object.assign([],a.props.historyList);a.props.onHistoryListChange([].concat(Object(ae.a)(t),Object(ae.a)(e.data.data))),a.setState({loading:!1})})).catch((function(e){var t=M.a.getErrorMsg(e);q.a.danger(t)}))}},a.perPage=25,a.state={currentPage:1,loading:!1},a}return Object(a.a)(n,[{key:"render",value:function(){var e=this;return Object(P.jsx)("div",{className:"history-body",children:Object(P.jsxs)("ul",{onScroll:this.onScroll,className:"history-list-container",children:[this.props.historyList?this.props.historyList.map((function(t){var n=arguments.length>1&&void 0!==arguments[1]?arguments[1]:0,i=arguments.length>2?arguments[2]:void 0,a=n+1;return a===i.length&&(a=n),Object(P.jsx)(ce,{onClick:e.onClick,ctime:t.ctime,className:e.props.activeItem===n?"item-active":"",name:t.creator_name,index:n,preItem:i[a],currentItem:t},n)})):Object(P.jsx)(p.a,{}),this.state.loading&&Object(P.jsx)("li",{className:"reloading-reversion",children:Object(P.jsx)(p.a,{})})]})})}}]),n}(l.a.Component),ce=function(e){Object(o.a)(n,e);var t=Object(r.a)(n);function n(){return Object(i.a)(this,n),t.apply(this,arguments)}return Object(a.a)(n,[{key:"render",value:function(){var e=this,t=oe.a.parseZone(this.props.ctime).format("YYYY-MM-DD HH:mm");return Object(P.jsx)("li",{onClick:function(t){return e.props.onClick(t,e.props.index,e.props.preItem,e.props.currentItem)},className:"history-list-item "+this.props.className,children:Object(P.jsxs)("div",{className:"history-info",children:[Object(P.jsx)("div",{className:"time",children:t}),Object(P.jsxs)("div",{className:"owner",children:[Object(P.jsx)("i",{className:"squire-icon"}),Object(P.jsx)("span",{children:this.props.name})]})]})})}}]),n}(l.a.Component),le=re,de=n(14),me=n(23),he=function e(t){Object(i.a)(this,e);var n=new Date(t.created_at).getTime();if(this.time=oe()(n).format("YYYY-MM-DD HH:mm"),this.id=t.id,this.avatarUrl=t.avatar_url,this.comment=t.comment,this.name=t.user_name,this.userEmail=t.user_email,this.resolved=t.resolved,t.detail){var a=JSON.parse(t.detail);this.newIndex=a.newIndex,this.oldIndex=a.oldIndex,this.quote=a.quote}},fe=(n(221),n(130),n(355),n(1741),n(526)),ue=n(12),be=J.b.toSlateRange,je=J.b.toDOMNode,pe=function(e){Object(o.a)(n,e);var t=Object(r.a)(n);function n(e){var a;return Object(i.a)(this,n),(a=t.call(this,e)).initialContent=function(){switch(u.L){case"open":if(!u.E)return void a.setState({isLoading:!1,isShowDiff:!1});if(!u.Xb)return void b.b.getFileDownloadLink(u.K,u.G).then((function(e){b.b.getFileContent(e.data).then((function(e){a.setState({draftContent:e.data,draftOriginContent:e.data,isLoading:!1,isShowDiff:!1})}))}));var e=window.location.hash;if(0===e.indexOf("#history-")){var t,n,i=e.slice(9,49),o=e.slice(50,90);a.setState({isLoading:!1,activeTab:"history"}),b.b.listFileHistoryRecords(u.K,u.G,1,25).then((function(e){var s=e.data.data;a.setState({historyList:s,totalReversionCount:e.data.total_count});for(var r=0,c=s.length;r<c&&(o===s[r].commit_id&&(a.setState({activeItem:r}),t=s[r].path),i===s[r].commit_id&&(n=s[r].path),!t||!n);r++);j.a.all([b.b.getFileRevision(u.K,i,n),b.b.getFileRevision(u.K,o,t)]).then(j.a.spread((function(e,t){j.a.all([b.b.getFileContent(e.data),b.b.getFileContent(t.data)]).then(j.a.spread((function(e,t){a.setDiffViewerContent(t.data,e.data)})))})))}))}else j.a.all([b.b.getFileDownloadLink(u.K,u.G),b.b.getFileDownloadLink(u.K,u.I)]).then(j.a.spread((function(e,t){j.a.all([b.b.getFileContent(e.data),b.b.getFileContent(t.data)]).then(j.a.spread((function(e,t){a.setState({draftContent:e.data,draftOriginContent:t.data,isLoading:!1});var n=Object(s.a)(a);setTimeout((function(){n.getChangedNodes()}),100)})))})));break;case"published":if(!u.Xb)return void a.setState({isLoading:!1,isShowDiff:!1});var r=u.qc+"repo/"+u.K+"/"+u.J+"/download?p="+u.I,c=u.qc+"repo/"+u.K+"/"+u.Yb+"/download?p="+u.I;j.a.all([b.b.getFileContent(r),b.b.getFileContent(c)]).then(j.a.spread((function(e,t){a.setState({draftContent:e.data,draftOriginContent:t.data,isLoading:!1})})))}},a.onHistoryItemClick=function(e,t,n){var i=t.commit_id,s=e.commit_id,o="history-"+i+"-"+s;a.setURL(o),a.setState({activeItem:n,isLoading:!0}),j.a.all([b.b.getFileRevision(u.K,s,e.path),b.b.getFileRevision(u.K,i,t.path)]).then(j.a.spread((function(e,t){j.a.all([b.b.getFileContent(e.data),b.b.getFileContent(t.data)]).then(j.a.spread((function(e,t){a.setDiffViewerContent(e.data,t.data)})))})))},a.onHistoryListChange=function(e){a.setState({historyList:e})},a.listComments=function(){b.b.listComments(u.K,u.G).then((function(e){var t=[];e.data.comments.forEach((function(e){t.push(new he(e))})),a.setState({commentsList:t})}))},a.addComment=function(e){e.stopPropagation(),a.getQuote(),a.quote&&a.setState({isShowCommentDialog:!0})},a.onCommentAdded=function(){a.listComments(),a.toggleCommentDialog()},a.toggleCommentDialog=function(){a.setState({isShowCommentDialog:!a.state.isShowCommentDialog})},a.getOriginRepoInfo=function(){b.b.getRepoInfo(u.K).then((function(e){a.setState({originRepoName:e.data.repo_name})}))},a.getDraftInfo=function(){"open"===u.L&&b.b.getFileInfo(u.K,u.G).then((function(e){a.setState({draftInfo:e.data})}))},a.getChangedNodes=function(){var e=a.refs.diffViewer.value,t=[],n="";e.map((function(e,i){var a=e.data.diff_state;("diff-added"===a&&"diff-added"!==n||"diff-removed"===a&&"diff-removed"!==n||"diff-replaced"===a&&"diff-replaced"!==n)&&t.push(i),n=e.data.diff_state})),a.setState({changedNodes:t})},a.scrollToChangedNode=function(e){if(0!=a.state.changedNodes.length){"up"===e?a.changeIndex++:a.changeIndex--,a.changeIndex>a.state.changedNodes.length-1&&(a.changeIndex=0),a.changeIndex<0&&(a.changeIndex=a.state.changedNodes.length-1);for(var t=window,n=a.state.changedNodes[a.changeIndex],i=window.viewer.children[n],s=je(window.viewer,i);-1===s.className.indexOf("diff-")&&"BODY"!==s.tagName;)s=s.parentNode;var o=a.findScrollContainer(s,t);o==t.document.body||o==t.document.documentElement?t.scrollTo(0,s.offsetTop):o.scrollTop=s.offsetTop}},a.findScrollContainer=function(e,t){for(var n,i=e.parentNode,a=["auto","overlay","scroll"];!n&&i.parentNode;){var s=t.getComputedStyle(i).overflowY;if(a.includes(s)){n=i;break}i=i.parentNode}return n||t.document.body},a.scrollToQuote=function(e,t,n){var i=a.refs.diffViewer.value.find((function(n){if(n.data.old_index==t&&n.data.new_index==e)return n}));if(i){var s=je(window.viewer,i);if(!s)return;var o=window,r=a.findScrollContainer(s,o);r==o.document.body||r==o.document.documentElement?o.scrollTo(0,s.offsetTop):r.scrollTop=s.offsetTop}},a.showDiffViewer=function(){return Object(P.jsxs)("div",{children:[a.state.isShowDiff?Object(P.jsx)(f.a,{scriptSource:u.Nb+"js/mathjax/tex-svg.js",newMarkdownContent:a.state.draftContent,oldMarkdownContent:a.state.draftOriginContent,ref:"diffViewer"}):Object(P.jsx)(f.a,{scriptSource:u.Nb+"js/mathjax/tex-svg.js",newMarkdownContent:a.state.draftContent,oldMarkdownContent:a.state.draftContent,ref:"diffViewer"}),Object(P.jsx)("i",{className:"fa fa-plus-square review-comment-btn",ref:"commentbtn",onMouseDown:a.addComment})]})},a.listReviewers=function(){b.b.listDraftReviewers(u.H).then((function(e){a.setState({reviewers:e.data.reviewers})}))},a.onSwitchShowDiff=function(){if(!a.state.isShowDiff){var e=Object(s.a)(a);setTimeout((function(){e.getChangedNodes()}),100)}a.setState({isShowDiff:!a.state.isShowDiff})},a.toggleDiffTip=function(){a.setState({showDiffTip:!a.state.showDiffTip})},a.toggleAddReviewerDialog=function(){a.state.showReviewerDialog&&a.listReviewers(),a.setState({showReviewerDialog:!a.state.showReviewerDialog})},a.showDiffButton=function(){return Object(P.jsxs)("div",{className:"seafile-toggle-diff",children:[Object(P.jsxs)("label",{className:"custom-switch",id:"toggle-diff",children:[Object(P.jsx)("input",{type:"checkbox",checked:a.state.isShowDiff&&"checked",name:"option",className:"custom-switch-input",onChange:a.onSwitchShowDiff}),Object(P.jsx)("span",{className:"custom-switch-indicator"})]}),Object(P.jsx)(Q.a,{placement:"bottom",isOpen:a.state.showDiffTip,target:"toggle-diff",toggle:a.toggleDiffTip,children:Object(u.pb)("View diff")})]})},a.onPublishDraft=function(){b.b.publishDraft(u.H).then((function(e){a.setState({draftStatus:e.data.draft_status})}))},a.initialDiffViewerContent=function(){b.b.listFileHistoryRecords(u.K,u.G,1,25).then((function(e){a.setState({historyList:e.data.data,totalReversionCount:e.data.total_count}),e.data.data.length>1?j.a.all([b.b.getFileRevision(u.K,e.data.data[0].commit_id,u.G),b.b.getFileRevision(u.K,e.data.data[1].commit_id,u.G)]).then(j.a.spread((function(e,t){j.a.all([b.b.getFileContent(e.data),b.b.getFileContent(t.data)]).then(j.a.spread((function(e,t){a.setState({draftContent:e.data,draftOriginContent:t.data})})))}))):b.b.getFileRevision(u.K,e.data.data[0].commit_id,u.G).then((function(e){b.b.getFileContent(e.data).then((function(e){a.setState({draftContent:e.data,draftOriginContent:""})}))}))}))},a.setDiffViewerContent=function(e,t){a.setState({draftContent:e,draftOriginContent:t,isLoading:!1})},a.setURL=function(e){var t=new fe(window.location.href);t.set("hash",e),window.location.href=t.toString()},a.tabItemClick=function(e){a.state.activeTab!==e&&("history"!==e&&window.location.hash&&a.setURL("#"),"reviewInfo"==e?a.initialContent():"history"==e&&a.initialDiffViewerContent(),a.setState({activeTab:e}))},a.showNavItem=function(e){var t=a.state.commentsList.length;switch(e){case"info":return Object(P.jsx)(W.a,{className:"nav-item",children:Object(P.jsx)(Z.a,{className:ie()({active:"reviewInfo"===a.state.activeTab}),onClick:function(){a.tabItemClick("reviewInfo")},children:Object(P.jsx)("i",{className:"fas fa-info-circle"})})});case"comments":return Object(P.jsx)(W.a,{className:"nav-item",children:Object(P.jsxs)(Z.a,{className:ie()({active:"comments"===a.state.activeTab}),onClick:function(){a.tabItemClick("comments")},children:[Object(P.jsx)("i",{className:"fa fa-comments"}),t>0&&Object(P.jsx)("div",{className:"comments-number",children:t})]})});case"history":return Object(P.jsx)(W.a,{className:"nav-item",children:Object(P.jsx)(Z.a,{className:ie()({active:"history"===a.state.activeTab}),onClick:function(){a.tabItemClick("history")},children:Object(P.jsx)("i",{className:"fas fa-history"})})})}},a.getDomNodeByPath=function(e){for(var t,n=document.querySelector(".viewer-component");"number"===typeof e[0]&&n;)(t=n.children[e[0]]).getAttribute("data-slate-node")||(t=t.children[0]),e.shift(),n=t;return t},a.setBtnPosition=function(){var e=window.getSelection();if(e.rangeCount){var t=e.getRangeAt(0),n=null,i=a.refs.commentbtn.style;try{n=be(window.viewer,t)}catch(r){return void(i.top="-1000px")}if(n&&!de.h.isCollapsed(n)){a.range=n;var s=n.anchor.path.slice();s.pop();var o=a.getDomNodeByPath(s);i.right="0px",i.top=o?"".concat(o.offsetTop,"px"):"-1000px"}else i.top="-1000px"}},a.getQuote=function(){if(a.range){a.quote=Object(f.l)(de.b.fragment(window.viewer,a.range));var e=window.viewer.children[a.range.anchor.path[0]];a.newIndex=e.data.new_index,a.oldIndex=e.data.old_index}},a.renderDiffButton=function(){switch(u.L){case"open":if(!u.E||!u.Xb)return;return a.showDiffButton();case"published":if(!u.Xb)return;return a.showDiffButton()}},a.renderNavItems=function(){switch(u.L){case"open":return u.E?Object(P.jsxs)($.a,{tabs:!0,className:"review-side-panel-nav",children:[a.showNavItem("info"),a.showNavItem("comments"),a.showNavItem("history")]}):Object(P.jsx)($.a,{tabs:!0,className:"review-side-panel-nav",children:a.showNavItem("info")});case"published":return u.Xb?Object(P.jsxs)($.a,{tabs:!0,className:"review-side-panel-nav",children:[a.showNavItem("info"),a.showNavItem("comments")]}):Object(P.jsx)($.a,{tabs:!0,className:"review-side-panel-nav",children:a.showNavItem("info")})}},a.renderContent=function(){switch(u.L){case"open":return u.E?a.showDiffViewer():Object(P.jsx)("p",{className:"error",children:Object(u.pb)("Draft has been deleted.")});case"published":return u.Xb?a.showDiffViewer():Object(P.jsx)("p",{className:"error",children:Object(u.pb)("Original file has been deleted.")})}},a.state={draftContent:"",draftOriginContent:"",draftInfo:{},isLoading:!0,isShowDiff:!0,showDiffTip:!1,activeTab:"reviewInfo",commentsList:[],changedNodes:[],originRepoName:"",isShowCommentDialog:!1,activeItem:null,historyList:[],showReviewerDialog:!1,reviewers:[],draftStatus:u.L},a.quote="",a.newIndex=null,a.oldIndex=null,a.changeIndex=-1,a.range=null,a}return Object(a.a)(n,[{key:"componentDidMount",value:function(){this.getOriginRepoInfo(),this.getDraftInfo(),this.listReviewers(),this.listComments(),this.initialContent(),document.addEventListener("selectionchange",this.setBtnPosition)}},{key:"componentWillUnmount",value:function(){document.removeEventListener("selectionchange",this.setBtnPosition)}},{key:"render",value:function(){var e=this.state,t=e.draftInfo,n=e.reviewers,i=e.originRepoName,a=e.draftStatus,s=u.qc+"lib/"+u.K+"/file"+u.G+"?mode=edit",o="published"==this.state.draftStatus,r="open"==this.state.draftStatus&&"rw"==u.mb,c="open"==this.state.draftStatus&&"rw"==u.mb,l=ue(1e3*t.mtime).format("YYYY-MM-DD HH:mm"),d="".concat(u.qc,"profile/").concat(encodeURIComponent(t.last_modifier_email),"/");return Object(P.jsxs)("div",{className:"wrapper",children:[Object(P.jsxs)("div",{id:"header",className:"header review",children:[Object(P.jsxs)("div",{className:"cur-file-info",children:[Object(P.jsx)("div",{className:"info-item file-feature",children:Object(P.jsx)("span",{className:"sf2-icon-review"})}),Object(P.jsxs)("div",{children:[Object(P.jsxs)("div",{className:"info-item file-info",children:[Object(P.jsx)("span",{className:"file-name",children:u.F}),Object(P.jsx)("span",{className:"mx-2 file-review",children:Object(u.pb)("Review")})]}),!o&&t.mtime&&Object(P.jsxs)("div",{className:"last-modification",children:[Object(P.jsx)("a",{href:d,children:t.last_modifier_name}),Object(P.jsx)("span",{className:"mx-1",children:l})]})]})]}),Object(P.jsxs)("div",{className:"button-group",children:[this.renderDiffButton(),c&&Object(P.jsx)("a",{href:s,className:"mx-1",children:Object(P.jsx)(h.a,{className:"file-operation-btn",color:"secondary",children:Object(u.pb)("Edit Draft")})}),r&&Object(P.jsx)("button",{className:"btn btn-success file-operation-btn",title:Object(u.pb)("Publish draft"),onClick:this.onPublishDraft,children:Object(u.pb)("Publish")}),o&&Object(P.jsx)("button",{className:"btn btn-success file-operation-btn",title:Object(u.pb)("Published"),disabled:!0,children:Object(u.pb)("Published")})]})]}),Object(P.jsx)("div",{id:"main",className:"main",ref:"main",children:Object(P.jsxs)("div",{className:"cur-view-container",children:[Object(P.jsx)("div",{className:"cur-view-content",ref:"viewContent",children:this.state.isLoading?Object(P.jsx)("div",{className:"markdown-viewer-render-content article",children:Object(P.jsx)(p.a,{})}):Object(P.jsx)("div",{className:"markdown-viewer-render-content article",children:this.renderContent()})}),Object(P.jsx)("div",{className:"cur-view-right-part",children:Object(P.jsxs)("div",{className:"review-side-panel",children:[this.renderNavItems(),Object(P.jsxs)(ee.a,{activeTab:this.state.activeTab,children:[Object(P.jsx)(te.a,{tabId:"reviewInfo",children:Object(P.jsxs)("div",{className:"review-side-panel-body",children:[Object(P.jsx)(ve,{reviewers:n,toggleAddReviewerDialog:this.toggleAddReviewerDialog}),Object(P.jsx)(ge,{}),u.E&&Object(P.jsx)(we,{commentsList:this.state.commentsList}),!0===this.state.isShowDiff&&this.state.changedNodes.length>0&&Object(P.jsx)(xe,{changedNumber:this.state.changedNodes.length,scrollToChangedNode:this.scrollToChangedNode}),Object(P.jsx)(Oe,{originRepoName:i,draftInfo:t,draftStatus:a})]})}),Object(P.jsx)(te.a,{tabId:"comments",className:"comments",children:Object(P.jsx)(K,{scrollToQuote:this.scrollToQuote,listComments:this.listComments,commentsList:this.state.commentsList,inResizing:!1})}),Object(P.jsx)(te.a,{tabId:"history",className:"history",children:Object(P.jsx)(le,{activeItem:this.state.activeItem,historyList:this.state.historyList,totalReversionCount:this.state.totalReversionCount,onHistoryItemClick:this.onHistoryItemClick,onHistoryListChange:this.onHistoryListChange})})]})]})})]})}),this.state.showReviewerDialog&&Object(P.jsx)(me.a,{children:Object(P.jsx)(X,{showReviewerDialog:this.state.showReviewerDialog,toggleAddReviewerDialog:this.toggleAddReviewerDialog,draftID:u.H,reviewers:n})}),this.state.isShowCommentDialog&&Object(P.jsx)(me.a,{children:Object(P.jsx)(A,{toggleCommentDialog:this.toggleCommentDialog,onCommentAdded:this.onCommentAdded,quote:this.quote,newIndex:this.newIndex,oldIndex:this.oldIndex})})]})}}]),n}(l.a.Component),ve=function(e){Object(o.a)(n,e);var t=Object(r.a)(n);function n(e){return Object(i.a)(this,n),t.call(this,e)}return Object(a.a)(n,[{key:"render",value:function(){var e=this.props.reviewers;return Object(P.jsxs)("div",{className:"review-side-panel-item",children:[Object(P.jsxs)("div",{className:"review-side-panel-header",children:[Object(u.pb)("Reviewers"),Object(P.jsx)("i",{className:"fa fa-cog",onClick:this.props.toggleAddReviewerDialog})]}),e.length>0?e.map((function(e){var t=arguments.length>1&&void 0!==arguments[1]?arguments[1]:0;return Object(P.jsxs)("div",{className:"reviewer-info",children:[Object(P.jsx)("img",{className:"avatar review-side-panel-avatar",src:e.avatar_url,alt:""}),Object(P.jsx)("span",{className:"reviewer-name ellipsis",children:e.user_name})]},t)})):Object(P.jsx)("span",{children:Object(u.pb)("No reviewer yet.")})]})}}]),n}(l.a.Component),ge=function(e){Object(o.a)(n,e);var t=Object(r.a)(n);function n(){return Object(i.a)(this,n),t.apply(this,arguments)}return Object(a.a)(n,[{key:"render",value:function(){return Object(P.jsxs)("div",{className:"review-side-panel-item",children:[Object(P.jsx)("div",{className:"review-side-panel-header",children:Object(u.pb)("Author")}),Object(P.jsxs)("div",{className:"author-info",children:[Object(P.jsx)("img",{className:"avatar review-side-panel-avatar",src:u.e,alt:""}),Object(P.jsx)("span",{className:"author-name ellipsis",children:u.d})]})]})}}]),n}(l.a.Component),Oe=function(e){Object(o.a)(n,e);var t=Object(r.a)(n);function n(e){return Object(i.a)(this,n),t.call(this,e)}return Object(a.a)(n,[{key:"render",value:function(){var e=this.props,t=e.draftStatus,n=e.originRepoName,i=u.gc+"/lib/"+u.K+"/file"+u.I;return Object(P.jsx)("div",{className:"dirent-table-container",children:Object(P.jsxs)("table",{className:"table-thead-hidden",children:[Object(P.jsx)("thead",{children:Object(P.jsxs)("tr",{children:[Object(P.jsx)("th",{width:"25%"}),Object(P.jsx)("th",{width:"75%"})]})}),Object(P.jsx)("tbody",{children:Object(P.jsxs)("tr",{children:[Object(P.jsx)("th",{className:"align-text-top",children:Object(u.pb)("Location")}),Object(P.jsx)("td",{children:"open"===t?Object(P.jsxs)("span",{children:[n,u.G]}):Object(P.jsx)("a",{href:i,className:"text-dark",children:i})})]})})]})})}}]),n}(l.a.Component),we=function(e){Object(o.a)(n,e);var t=Object(r.a)(n);function n(e){return Object(i.a)(this,n),t.call(this,e)}return Object(a.a)(n,[{key:"render",value:function(){var e=this.props.commentsList,t=0;if(e)for(var n=0,i=e.length;n<i;n++)!1===e[n].resolved&&t++;return Object(P.jsxs)("div",{className:"review-side-panel-item",children:[Object(P.jsx)("div",{className:"review-side-panel-header",children:Object(u.pb)("Comments")}),Object(P.jsx)("div",{className:"changes-info",children:Object(P.jsxs)("span",{children:[Object(u.pb)("Unresolved comments:")," ",t]})})]})}}]),n}(l.a.Component),xe=function(e){Object(o.a)(n,e);var t=Object(r.a)(n);function n(e){return Object(i.a)(this,n),t.call(this,e)}return Object(a.a)(n,[{key:"render",value:function(){var e=this;return Object(P.jsxs)("div",{className:"review-side-panel-item",children:[Object(P.jsx)("div",{className:"review-side-panel-header",children:Object(u.pb)("Changes")}),Object(P.jsxs)("div",{className:"changes-info",children:[Object(P.jsxs)("span",{children:[Object(u.pb)("Number of changes:")," ",this.props.changedNumber]}),this.props.changedNumber>0&&Object(P.jsxs)("div",{children:[Object(P.jsx)("i",{className:"fa fa-arrow-circle-up",onClick:function(){e.props.scrollToChangedNode("down")}}),Object(P.jsx)("i",{className:"fa fa-arrow-circle-down",onClick:function(){e.props.scrollToChangedNode("up")}})]})]})]})}}]),n}(l.a.Component);m.a.render(Object(P.jsx)(pe,{}),document.getElementById("wrapper"))},549:function(e,t,n){}},[[1737,1,0]]]);
//# sourceMappingURL=draft.chunk.js.map