(this["webpackJsonpseahub-frontend"]=this["webpackJsonpseahub-frontend"]||[]).push([[8],{1561:function(e,t,n){n(49),e.exports=n(1694)},1694:function(e,t,n){"use strict";n.r(t);var i=n(6),s=n(7),a=n(9),o=n(8),r=n(2),c=n.n(r),l=n(20),d=n.n(l),h=n(57),u=n.n(h),p=n(1),m=n(5),j=n(47),b=n(48),f=n(86),O=n(14),g=n(12),v=n.n(g),I=n(4),k=n(91),C=n(0);v.a.locale(window.app.config.lang);var w=function(e){Object(a.a)(n,e);var t=Object(o.a)(n);function n(e){var s;return Object(i.a)(this,n),(s=t.call(this,e)).onMouseEnter=function(){s.props.isItemFreezed||s.setState({isShowOperationIcon:!0})},s.onMouseLeave=function(){s.props.isItemFreezed||s.setState({isShowOperationIcon:!1})},s.onToggleClick=function(e){s.setState({isMenuShow:!s.state.isMenuShow}),s.props.onFreezedItemToggle()},s.onItemClick=function(){if(s.setState({isShowOperationIcon:!1}),s.props.item.commit_id!==s.props.currentItem.commit_id){var e=s.props.index;s.props.onItemClick(s.props.item,e)}},s.onItemRestore=function(){s.props.onItemRestore(s.props.currentItem)},s.onItemDownload=function(){},s.state={isShowOperationIcon:!1,isMenuShow:!1},s}return Object(s.a)(n,[{key:"render",value:function(){if(!this.props.currentItem)return"";var e=this.props.item,t=v()(e.ctime).format("YYYY-MM-DD HH:mm"),n=!1;this.props.item&&this.props.currentItem&&(n=this.props.item.commit_id===this.props.currentItem.commit_id);var i=this.props.currentItem.rev_file_id,s=k.a.getUrl({type:"download_historic_file",filePath:p.jb,objID:i});return Object(C.jsxs)("li",{className:"history-list-item ".concat(n?"item-active":""),onMouseEnter:this.onMouseEnter,onMouseLeave:this.onMouseLeave,onClick:this.onItemClick,children:[Object(C.jsxs)("div",{className:"history-info",children:[Object(C.jsx)("div",{className:"time",children:t}),Object(C.jsxs)("div",{className:"owner",children:[Object(C.jsx)("span",{className:"squire-icon"}),Object(C.jsx)("span",{children:e.creator_name})]})]}),Object(C.jsx)("div",{className:"history-operation",children:Object(C.jsxs)(I.i,{isOpen:this.state.isMenuShow,toggle:this.onToggleClick,children:[Object(C.jsx)(I.l,{tag:"a",className:"fas fa-ellipsis-v ".concat(this.state.isShowOperationIcon||n?"":"invisible"),"data-toggle":"dropdown","aria-expanded":this.state.isMenuShow,alt:Object(p.nb)("More Operations")}),Object(C.jsxs)(I.k,{children:[0!==this.props.index&&Object(C.jsx)(I.j,{onClick:this.onItemRestore,children:Object(p.nb)("Restore")}),Object(C.jsx)(I.j,{tag:"a",href:s,onClick:this.onItemDownLoad,children:Object(p.nb)("Download")})]})]})})]})}}]),n}(c.a.Component),x=function(e){Object(a.a)(n,e);var t=Object(o.a)(n);function n(e){var s;return Object(i.a)(this,n),(s=t.call(this,e)).componentDidMount=function(){var e=s.props.historyList;e.length>0&&(s.setState({currentItem:e[0]}),1===e?s.props.onItemClick(e[0]):s.props.onItemClick(e[0],e[1]))},s.onFreezedItemToggle=function(){s.setState({isItemFreezed:!s.state.isItemFreezed})},s.onScrollHandler=function(e){var t=e.target.clientHeight,n=e.target.scrollHeight,i=t+e.target.scrollTop+1>=n,a=s.props.hasMore;i&&a&&s.props.reloadMore()},s.onItemClick=function(e,t){if(s.setState({currentItem:e}),t!==s.props.historyList.length){var n=s.props.historyList[t+1];s.props.onItemClick(e,n)}else s.props.onItemClick(e)},s.state={isItemFreezed:!1,currentItem:null},s}return Object(s.a)(n,[{key:"render",value:function(){var e=this;return Object(C.jsxs)("ul",{className:"history-list-container",onScroll:this.onScrollHandler,children:[this.props.historyList.map((function(t,n){return Object(C.jsx)(w,{item:t,index:n,currentItem:e.state.currentItem,isItemFreezed:e.state.isItemFreezed,onItemClick:e.onItemClick,onItemRestore:e.props.onItemRestore,onFreezedItemToggle:e.onFreezedItemToggle},n)})),this.props.isReloadingData&&Object(C.jsx)("li",{children:Object(C.jsx)(O.a,{})})]})}}]),n}(c.a.Component),y=n(11),S=function(e){Object(a.a)(n,e);var t=Object(o.a)(n);function n(e){var s;return Object(i.a)(this,n),(s=t.call(this,e)).reloadMore=function(){if(!s.state.isReloadingData){var e=s.state.currentPage+1;s.setState({currentPage:e,isReloadingData:!0}),f.a.listFileHistoryRecords(p.jb,e,p.a).then((function(e){s.updateResultState(e.data),s.setState({isReloadingData:!1})}))}},s.onItemRestore=function(e){var t=e.commit_id;f.a.revertFile(p.jb,t).then((function(e){e.data.success&&(s.setState({isLoading:!0}),s.refershFileList());var t=Object(p.nb)("Successfully restored.");y.a.success(t)}))},s.onItemClick=function(e,t){s.props.onItemClick(e,t)},s.state={historyInfo:"",currentPage:1,hasMore:!1,isLoading:!0,isError:!1,fileOwner:"",isReloadingData:!1},s}return Object(s.a)(n,[{key:"componentDidMount",value:function(){var e=this;f.a.listFileHistoryRecords(p.jb,1,p.a).then((function(t){if(0===t.data.length)throw e.setState({isLoading:!1}),Error("there has an error in server");e.initResultState(t.data)}))}},{key:"refershFileList",value:function(){var e=this;f.a.listFileHistoryRecords(p.jb,1,p.a).then((function(t){e.initResultState(t.data)}))}},{key:"initResultState",value:function(e){e.data.length&&this.setState({historyInfo:e.data,currentPage:e.page,hasMore:e.total_count>p.a*this.state.currentPage,isLoading:!1,isError:!1,fileOwner:e.data[0].creator_email})}},{key:"updateResultState",value:function(e){e.data.length&&this.setState({historyInfo:[].concat(Object(b.a)(this.state.historyInfo),Object(b.a)(e.data)),currentPage:e.page,hasMore:e.total_count>p.a*this.state.currentPage,isLoading:!1,isError:!1,fileOwner:e.data[0].creator_email})}},{key:"render",value:function(){return Object(C.jsx)("div",{className:"side-panel history-side-panel",children:Object(C.jsxs)("div",{className:"side-panel-center",children:[Object(C.jsx)("div",{className:"history-side-panel-title",children:Object(p.nb)("History Versions")}),Object(C.jsxs)("div",{className:"history-body",children:[this.state.isLoading&&Object(C.jsx)(O.a,{}),this.state.historyInfo&&Object(C.jsx)(x,{hasMore:this.state.hasMore,isReloadingData:this.state.isReloadingData,historyList:this.state.historyInfo,reloadMore:this.reloadMore,onItemClick:this.onItemClick,onItemRestore:this.onItemRestore})]})]})})}}]),n}(c.a.Component),M=n(180),R=n.n(M),F=n(34),N=function(e){Object(a.a)(n,e);var t=Object(o.a)(n);function n(){var e;Object(i.a)(this,n);for(var s=arguments.length,a=new Array(s),o=0;o<s;o++)a[o]=arguments[o];return(e=t.call.apply(t,[this].concat(a))).onSearchedClick=function(){},e}return Object(s.a)(n,[{key:"componentDidMount",value:function(){R.a.highlightAll()}},{key:"render",value:function(){return Object(C.jsx)("div",{className:"main-panel",children:Object(C.jsx)("div",{className:"main-panel-center content-viewer",children:Object(C.jsx)("div",{className:"markdown-viewer-render-content",children:this.props.renderingContent?Object(C.jsx)(O.a,{}):Object(C.jsx)("div",{className:"diff-view article",children:Object(C.jsx)(F.a,{scriptSource:p.Lb+"js/mathjax/tex-svg.js",newMarkdownContent:this.props.newMarkdownContent,oldMarkdownContent:this.props.oldMarkdownContent})})})})})}}]),n}(c.a.Component),D=n(10),L=(n(178),n(478),n(98),n(108),function(e){Object(a.a)(n,e);var t=Object(o.a)(n);function n(e){var s;return Object(i.a)(this,n),(s=t.call(this,e)).onSearchedClick=function(e){m.a.handleSearchedItemClick(e)},s.setDiffContent=function(e,t){s.setState({renderingContent:!1,newMarkdownContent:e,oldMarkdownContent:t})},s.onHistoryItemClick=function(e,t){s.setState({renderingContent:!0}),t?u.a.all([D.b.getFileRevision(p.rb,e.commit_id,e.path),D.b.getFileRevision(p.rb,t.commit_id,t.path)]).then(u.a.spread((function(e,t){u.a.all([D.b.getFileContent(e.data),D.b.getFileContent(t.data)]).then(u.a.spread((function(e,t){s.setDiffContent(e.data,t.data)})))}))):D.b.getFileRevision(p.rb,e.commit_id,e.path).then((function(e){u.a.all([D.b.getFileContent(e.data)]).then(u.a.spread((function(e){s.setDiffContent(e.data,"")})))}))},s.state={renderingContent:!0,newMarkdownContent:"",oldMarkdownContent:""},s}return Object(s.a)(n,[{key:"render",value:function(){return Object(C.jsxs)(r.Fragment,{children:[Object(C.jsxs)("div",{id:"header",className:"history-header",children:[Object(C.jsxs)("div",{className:"title",children:[Object(C.jsx)("a",{href:"javascript:window.history.back()",className:"go-back",title:"Back",children:Object(C.jsx)("span",{className:"fas fa-chevron-left"})}),Object(C.jsx)("span",{className:"name",children:p.ib})]}),Object(C.jsx)("div",{className:"toolbar",children:Object(C.jsx)(j.a,{onSearchedClick:this.onSearchedClick})})]}),Object(C.jsxs)("div",{id:"main",className:"history-content",children:[Object(C.jsx)(N,{newMarkdownContent:this.state.newMarkdownContent,oldMarkdownContent:this.state.oldMarkdownContent,renderingContent:this.state.renderingContent}),Object(C.jsx)(S,{onItemClick:this.onHistoryItemClick})]})]})}}]),n}(c.a.Component));d.a.render(Object(C.jsx)(L,{}),document.getElementById("wrapper"))},478:function(e,t,n){}},[[1561,1,0]]]);
//# sourceMappingURL=fileHistory.chunk.js.map