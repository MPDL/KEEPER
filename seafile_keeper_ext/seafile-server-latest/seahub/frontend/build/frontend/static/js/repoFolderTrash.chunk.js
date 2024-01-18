(this["webpackJsonpseahub-frontend"]=this["webpackJsonpseahub-frontend"]||[]).push([[18],{1739:function(e,t,r){r(71),e.exports=r(1774)},1740:function(e,t,r){},1774:function(e,t,r){"use strict";r.r(t);var n=r(3),s=r(5),a=r(29),c=r(7),o=r(6),i=r(2),l=r.n(i),d=r(28),h=r.n(d),b=r(21),j=r(12),u=r.n(j),O=r(4),p=r(1),m=r(8),f=r(19),g=r(23),x=r(10),v=r(67),D=r(123),M=r(108),k=r(109),F=r(147),I=r(293),S=r(0),w=function(e){Object(c.a)(r,e);var t=Object(o.a)(r);function r(e){var s;return Object(n.a)(this,r),(s=t.call(this,e)).handleInputChange=function(e){s.setState({inputValue:e})},s.formSubmit=function(){var e=s.state.inputValue,t=s.props.repoID;s.setState({submitBtnDisabled:!0}),m.b.deleteRepoTrash(t,e.value).then((function(e){x.a.success(Object(p.pb)("Clean succeeded.")),s.props.refreshTrash(),s.props.toggleDialog()})).catch((function(e){var t=O.a.getErrorMsg(e);s.setState({formErrorMsg:t,submitBtnDisabled:!1})}))},s.options=[{label:Object(p.pb)("3 days ago"),value:3},{label:Object(p.pb)("1 week ago"),value:7},{label:Object(p.pb)("1 month ago"),value:30},{label:Object(p.pb)("all"),value:0}],s.state={inputValue:s.options[0],submitBtnDisabled:!1},s}return Object(s.a)(r,[{key:"render",value:function(){var e=this.state.formErrorMsg;return Object(S.jsxs)(D.a,{isOpen:!0,centered:!0,toggle:this.props.toggleDialog,children:[Object(S.jsx)(M.a,{toggle:this.props.toggleDialog,children:Object(p.pb)("Clean")}),Object(S.jsx)(k.a,{children:Object(S.jsxs)(l.a.Fragment,{children:[Object(S.jsx)("p",{children:Object(p.pb)("Clear files in trash and history\uff1a")}),Object(S.jsx)(I.a,{defaultValue:this.options[0],options:this.options,autoFocus:!1,onChange:this.handleInputChange,placeholder:""}),e&&Object(S.jsx)("p",{className:"error m-0 mt-2",children:e})]})}),Object(S.jsx)(F.a,{children:Object(S.jsx)("button",{className:"btn btn-primary",disabled:this.state.submitBtnDisabled,onClick:this.formSubmit,children:Object(p.pb)("Submit")})})]})}}]),r}(l.a.Component),C=(r(130),r(143),r(1740),window.app.pageOptions),_=C.repoID,N=C.repoFolderName,y=C.path,T=C.enableClean,L=function(e){Object(c.a)(r,e);var t=Object(o.a)(r);function r(e){var s;return Object(n.a)(this,r),(s=t.call(this,e)).getItems=function(e){m.b.getRepoFolderTrash(_,y,e).then((function(e){var t=e.data,r=t.data,n=t.more,a=t.scan_stat;!r.length&&n?s.getItems(a):s.setState({isLoading:!1,items:s.state.items.concat(r),more:n,scanStat:a})})).catch((function(e){s.setState({isLoading:!1,errorMsg:O.a.getErrorMsg(e,!0)})}))},s.getMore=function(){s.setState({isLoading:!0}),s.getItems(s.state.scanStat)},s.onSearchedClick=function(e){if(!0===e.is_dir){var t=p.qc+"library/"+e.repo_id+"/"+e.repo_name+e.path;Object(b.c)(t,{repalce:!0})}else{var r=p.qc+"lib/"+e.repo_id+"/file"+O.a.encodePath(e.path);window.open("about:blank").location.href=r}},s.goBack=function(e){e.preventDefault(),window.history.back()},s.cleanTrash=function(){s.toggleCleanTrashDialog()},s.toggleCleanTrashDialog=function(){s.setState({isCleanTrashDialogOpen:!s.state.isCleanTrashDialogOpen})},s.refreshTrash=function(){s.setState({isLoading:!0,errorMsg:"",items:[],scanStat:null,more:!1,showFolder:!1}),s.getItems()},s.renderFolder=function(e,t,r){s.setState({showFolder:!0,commitID:e,baseDir:t,folderPath:r,folderItems:[],isLoading:!0}),m.b.listCommitDir(_,e,"".concat(t.substr(0,t.length-1)).concat(r)).then((function(e){s.setState({isLoading:!1,folderItems:e.data.dirent_list})})).catch((function(e){e.response?403==e.response.status?s.setState({isLoading:!1,errorMsg:Object(p.pb)("Permission denied")}):s.setState({isLoading:!1,errorMsg:Object(p.pb)("Error")}):s.setState({isLoading:!1,errorMsg:Object(p.pb)("Please check the network.")})}))},s.clickRoot=function(e){e.preventDefault(),s.refreshTrash()},s.clickFolderPath=function(e,t){t.preventDefault();var r=s.state,n=r.commitID,a=r.baseDir;s.renderFolder(n,a,e)},s.renderFolderPath=function(){var e=s.state.folderPath.split("/");return Object(S.jsxs)(l.a.Fragment,{children:[Object(S.jsx)("a",{href:"#",onClick:s.clickRoot,children:N}),Object(S.jsx)("span",{children:" / "}),e.map((function(t,r){if(r>0&&r!=e.length-1)return Object(S.jsxs)(l.a.Fragment,{children:[Object(S.jsx)("a",{href:"#",onClick:s.clickFolderPath.bind(Object(a.a)(s),e.slice(0,r+1).join("/")),children:e[r]}),Object(S.jsx)("span",{children:" / "})]},r)})),e[e.length-1]]})},s.state={isLoading:!0,errorMsg:"",items:[],scanStat:null,more:!1,isCleanTrashDialogOpen:!1},s}return Object(s.a)(r,[{key:"componentDidMount",value:function(){this.getItems()}},{key:"render",value:function(){var e=this.state,t=e.isCleanTrashDialogOpen,r=e.showFolder;return Object(S.jsxs)(l.a.Fragment,{children:[Object(S.jsxs)("div",{className:"h-100 d-flex flex-column",children:[Object(S.jsxs)("div",{className:"top-header d-flex justify-content-between",children:[Object(S.jsx)("a",{href:p.qc,children:Object(S.jsx)("img",{src:p.Nb+p.Ib,height:p.Hb,width:p.Jb,title:p.rc,alt:"logo"})}),Object(S.jsx)(v.a,{onSearchedClick:this.onSearchedClick})]}),Object(S.jsx)("div",{className:"flex-auto container-fluid pt-4 pb-6 o-auto",children:Object(S.jsx)("div",{className:"row",children:Object(S.jsxs)("div",{className:"col-md-10 offset-md-1",children:[Object(S.jsx)("h2",{children:O.a.generateDialogTitle(Object(p.pb)("{placeholder} Trash"),N)}),Object(S.jsx)("a",{href:"#",className:"go-back",title:Object(p.pb)("Back"),onClick:this.goBack,role:Object(p.pb)("Back"),children:Object(S.jsx)("span",{className:"fas fa-chevron-left"})}),Object(S.jsxs)("div",{className:"d-flex justify-content-between align-items-center op-bar",children:[Object(S.jsxs)("p",{className:"m-0",children:[Object(p.pb)("Current path: "),r?this.renderFolderPath():N]}),"/"==y&&T&&!r&&Object(S.jsx)("button",{className:"btn btn-secondary clean",onClick:this.cleanTrash,children:Object(p.pb)("Clean")})]}),Object(S.jsx)(P,{data:this.state,getMore:this.getMore,renderFolder:this.renderFolder})]})})})]}),t&&Object(S.jsx)(g.a,{children:Object(S.jsx)(w,{repoID:_,refreshTrash:this.refreshTrash,toggleDialog:this.toggleCleanTrashDialog})})]})}}]),r}(l.a.Component),P=function(e){Object(c.a)(r,e);var t=Object(o.a)(r);function r(e){var s;return Object(n.a)(this,r),(s=t.call(this,e)).theadData=[{width:"5%",text:""},{width:"45%",text:Object(p.pb)("Name")},{width:"20%",text:Object(p.pb)("Delete Time")},{width:"15%",text:Object(p.pb)("Size")},{width:"15%",text:""}],s}return Object(s.a)(r,[{key:"render",value:function(){var e=this,t=this.props.data,r=t.isLoading,n=t.errorMsg,s=t.items,a=t.more,c=t.showFolder,o=t.commitID,i=t.baseDir,d=t.folderPath,h=t.folderItems;return Object(S.jsxs)(l.a.Fragment,{children:[Object(S.jsxs)("table",{className:"table-hover",children:[Object(S.jsx)("thead",{children:Object(S.jsx)("tr",{children:this.theadData.map((function(e,t){return Object(S.jsx)("th",{width:e.width,children:e.text},t)}))})}),Object(S.jsx)("tbody",{children:c?h.map((function(t,r){return Object(S.jsx)(B,{item:t,commitID:o,baseDir:i,folderPath:d,renderFolder:e.props.renderFolder},r)})):s.map((function(t,r){return Object(S.jsx)(R,{item:t,renderFolder:e.props.renderFolder},r)}))})]}),r&&Object(S.jsx)(f.a,{}),n&&Object(S.jsx)("p",{className:"error mt-6 text-center",children:n}),a&&!r&&!c&&Object(S.jsx)("button",{className:"btn btn-block more mt-6",onClick:this.props.getMore,children:Object(p.pb)("More")})]})}}]),r}(l.a.Component),R=function(e){Object(c.a)(r,e);var t=Object(o.a)(r);function r(e){var s;return Object(n.a)(this,r),(s=t.call(this,e)).handleMouseOver=function(){s.setState({isIconShown:!0})},s.handleMouseOut=function(){s.setState({isIconShown:!1})},s.restoreItem=function(e){e.preventDefault();var t=s.props.item,r=t.commit_id,n=t.parent_dir+t.obj_name;(t.is_dir?m.b.restoreFolder(_,r,n):m.b.restoreFile(_,r,n)).then((function(e){s.setState({restored:!0}),x.a.success(Object(p.pb)("Successfully restored 1 item."))})).catch((function(e){var t="";t=e.response?e.response.data.error_msg||Object(p.pb)("Error"):Object(p.pb)("Please check the network."),x.a.danger(t)}))},s.renderFolder=function(e){e.preventDefault();var t=s.props.item;s.props.renderFolder(t.commit_id,t.parent_dir,O.a.joinPath("/",t.obj_name))},s.state={restored:!1,isIconShown:!1},s}return Object(s.a)(r,[{key:"render",value:function(){var e=this.props.item,t=this.state,r=t.restored,n=t.isIconShown;return r?null:e.is_dir?Object(S.jsxs)("tr",{onMouseOver:this.handleMouseOver,onMouseOut:this.handleMouseOut,onFocus:this.handleMouseOver,children:[Object(S.jsx)("td",{className:"text-center",children:Object(S.jsx)("img",{src:O.a.getFolderIconUrl(),alt:Object(p.pb)("Directory"),width:"24"})}),Object(S.jsx)("td",{children:Object(S.jsx)("a",{href:"#",onClick:this.renderFolder,children:e.obj_name})}),Object(S.jsx)("td",{title:u()(e.deleted_time).format("LLLL"),children:u()(e.deleted_time).format("YYYY-MM-DD")}),Object(S.jsx)("td",{}),Object(S.jsx)("td",{children:Object(S.jsx)("a",{href:"#",className:n?"":"invisible",onClick:this.restoreItem,role:"button",children:Object(p.pb)("Restore")})})]}):Object(S.jsxs)("tr",{onMouseOver:this.handleMouseOver,onMouseOut:this.handleMouseOut,onFocus:this.handleMouseOver,children:[Object(S.jsx)("td",{className:"text-center",children:Object(S.jsx)("img",{src:O.a.getFileIconUrl(e.obj_name),alt:Object(p.pb)("File"),width:"24"})}),Object(S.jsx)("td",{children:Object(S.jsx)("a",{href:"".concat(p.qc,"repo/").concat(_,"/trash/files/?obj_id=").concat(e.obj_id,"&commit_id=").concat(e.commit_id,"&base=").concat(encodeURIComponent(e.parent_dir),"&p=").concat(encodeURIComponent("/"+e.obj_name)),target:"_blank",children:e.obj_name})}),Object(S.jsx)("td",{title:u()(e.deleted_time).format("LLLL"),children:u()(e.deleted_time).format("YYYY-MM-DD")}),Object(S.jsx)("td",{children:O.a.bytesToSize(e.size)}),Object(S.jsx)("td",{children:Object(S.jsx)("a",{href:"#",className:n?"":"invisible",onClick:this.restoreItem,role:"button",children:Object(p.pb)("Restore")})})]})}}]),r}(l.a.Component),B=function(e){Object(c.a)(r,e);var t=Object(o.a)(r);function r(e){var s;return Object(n.a)(this,r),(s=t.call(this,e)).handleMouseOver=function(){s.setState({isIconShown:!0})},s.handleMouseOut=function(){s.setState({isIconShown:!1})},s.renderFolder=function(e){e.preventDefault();var t=s.props.item,r=s.props,n=r.commitID,a=r.baseDir,c=r.folderPath;s.props.renderFolder(n,a,O.a.joinPath(c,t.name))},s.state={isIconShown:!1},s}return Object(s.a)(r,[{key:"render",value:function(){var e=this.props.item,t=(this.state.isIconShown,this.props),r=t.commitID,n=t.baseDir,s=t.folderPath;return"dir"==e.type?Object(S.jsxs)("tr",{onMouseOver:this.handleMouseOver,onMouseOut:this.handleMouseOut,children:[Object(S.jsx)("td",{className:"text-center",children:Object(S.jsx)("img",{src:O.a.getFolderIconUrl(),alt:Object(p.pb)("Directory"),width:"24"})}),Object(S.jsx)("td",{children:Object(S.jsx)("a",{href:"#",onClick:this.renderFolder,children:e.name})}),Object(S.jsx)("td",{}),Object(S.jsx)("td",{}),Object(S.jsx)("td",{})]}):Object(S.jsxs)("tr",{onMouseOver:this.handleMouseOver,onMouseOut:this.handleMouseOut,children:[Object(S.jsx)("td",{className:"text-center",children:Object(S.jsx)("img",{src:O.a.getFileIconUrl(e.name),alt:Object(p.pb)("File"),width:"24"})}),Object(S.jsx)("td",{children:Object(S.jsx)("a",{href:"".concat(p.qc,"repo/").concat(_,"/trash/files/?obj_id=").concat(e.obj_id,"&commit_id=").concat(r,"&base=").concat(encodeURIComponent(n),"&p=").concat(encodeURIComponent(O.a.joinPath(s,e.name))),target:"_blank",children:e.name})}),Object(S.jsx)("td",{}),Object(S.jsx)("td",{children:O.a.bytesToSize(e.size)}),Object(S.jsx)("td",{})]})}}]),r}(l.a.Component);h.a.render(Object(S.jsx)(L,{}),document.getElementById("wrapper"))}},[[1739,1,0]]]);
//# sourceMappingURL=repoFolderTrash.chunk.js.map