(this["webpackJsonpseahub-frontend"]=this["webpackJsonpseahub-frontend"]||[]).push([[18],{1586:function(e,t,n){n(52),e.exports=n(1716)},1716:function(e,t,n){"use strict";n.r(t);var c=n(6),r=n(7),a=n(27),o=n(9),s=n(8),i=n(2),l=n.n(i),d=n(23),j=n.n(d),h=n(17),b=n(5),O=n(1),m=n(10),u=n(15),p=n(20),f=n(11),x=n(50),g=n(4),v=n(0),k=function(e){Object(o.a)(n,e);var t=Object(s.a)(n);function n(e){var r;return Object(c.a)(this,n),(r=t.call(this,e)).action=function(){r.setState({btnDisabled:!0}),r.props.restoreRepo()},r.state={btnDisabled:!1},r}return Object(r.a)(n,[{key:"render",value:function(){var e=this.props,t=(e.formActionURL,e.csrfToken,e.toggle);return Object(v.jsxs)(g.x,{centered:!0,isOpen:!0,toggle:t,children:[Object(v.jsx)(g.A,{toggle:t,children:Object(O.jb)("Restore Library")}),Object(v.jsx)(g.y,{children:Object(v.jsx)("p",{children:Object(O.jb)("Are you sure you want to restore this library?")})}),Object(v.jsxs)(g.z,{children:[Object(v.jsx)(g.c,{color:"secondary",onClick:t,children:Object(O.jb)("Cancel")}),Object(v.jsx)(g.c,{color:"primary",onClick:this.action,disabled:this.state.btnDisabled,children:Object(O.jb)("Restore")})]})]})}}]),n}(i.Component),w=(n(107),n(116),n(530),window.app.pageOptions),y=w.repoID,C=w.repoName,D=w.canRestoreRepo,N=w.commitID,F=w.commitTime,I=w.commitDesc,S=w.commitRelativeTime,P=w.showAuthor,M=w.authorAvatarURL,R=w.authorName,_=w.authorNickName,L=function(e){Object(o.a)(n,e);var t=Object(s.a)(n);function n(e){var r;return Object(c.a)(this,n),(r=t.call(this,e)).toggleDialog=function(){r.setState({isConfirmDialogOpen:!r.state.isConfirmDialogOpen})},r.onSearchedClick=function(e){if(!0===e.is_dir){var t=O.hc+"library/"+e.repo_id+"/"+e.repo_name+e.path;Object(h.c)(t,{repalce:!0})}else{var n=O.hc+"lib/"+e.repo_id+"/file"+b.a.encodePath(e.path);window.open("about:blank").location.href=n}},r.goBack=function(e){e.preventDefault(),window.history.back()},r.renderFolder=function(e){r.setState({folderPath:e,folderItems:[],isLoading:!0}),m.b.listCommitDir(y,N,e).then((function(e){r.setState({isLoading:!1,folderItems:e.data.dirent_list})})).catch((function(e){r.setState({isLoading:!1,errorMsg:b.a.getErrorMsg(e,!0)})}))},r.clickFolderPath=function(e,t){t.preventDefault(),r.renderFolder(e)},r.renderPath=function(){var e=r.state.folderPath,t=e.split("/");return"/"==e?C:Object(v.jsxs)(l.a.Fragment,{children:[Object(v.jsx)("a",{href:"#",onClick:r.clickFolderPath.bind(Object(a.a)(r),"/"),children:C}),Object(v.jsx)("span",{children:" / "}),t.map((function(e,n){if(n>0&&n!=t.length-1)return Object(v.jsxs)(l.a.Fragment,{children:[Object(v.jsx)("a",{href:"#",onClick:r.clickFolderPath.bind(Object(a.a)(r),t.slice(0,n+1).join("/")),children:t[n]}),Object(v.jsx)("span",{children:" / "})]},n)})),t[t.length-1]]})},r.restoreRepo=function(){m.b.revertRepo(y,N).then((function(e){r.toggleDialog(),f.a.success(Object(O.jb)("Successfully restored the library."))})).catch((function(e){var t=b.a.getErrorMsg(e);r.toggleDialog(),f.a.danger(t)}))},r.state={isLoading:!0,errorMsg:"",folderPath:"/",folderItems:[],isConfirmDialogOpen:!1},r}return Object(r.a)(n,[{key:"componentDidMount",value:function(){this.renderFolder(this.state.folderPath)}},{key:"render",value:function(){var e=this.state,t=e.isConfirmDialogOpen,n=e.folderPath;return Object(v.jsxs)(l.a.Fragment,{children:[Object(v.jsxs)("div",{className:"h-100 d-flex flex-column",children:[Object(v.jsxs)("div",{className:"top-header d-flex justify-content-between",children:[Object(v.jsx)("a",{href:O.hc,children:Object(v.jsx)("img",{src:O.Hb+O.Cb,height:O.Bb,width:O.Db,title:O.ic,alt:"logo"})}),Object(v.jsx)(x.a,{onSearchedClick:this.onSearchedClick})]}),Object(v.jsx)("div",{className:"flex-auto container-fluid pt-4 pb-6 o-auto",children:Object(v.jsx)("div",{className:"row",children:Object(v.jsxs)("div",{className:"col-md-10 offset-md-1",children:[Object(v.jsx)("h2",{dangerouslySetInnerHTML:{__html:b.a.generateDialogTitle(Object(O.jb)("{placeholder} Snapshot"),C)+' <span class="heading-commit-time">('.concat(F,")</span>")}}),Object(v.jsx)("a",{href:"#",className:"go-back",title:Object(O.jb)("Back"),onClick:this.goBack,children:Object(v.jsx)("span",{className:"fas fa-chevron-left"})}),"/"==n&&Object(v.jsxs)("div",{className:"d-flex mb-2 align-items-center",children:[Object(v.jsx)("p",{className:"m-0",children:I}),Object(v.jsxs)("div",{className:"ml-4 border-left pl-4 d-flex align-items-center",children:[P?Object(v.jsxs)(l.a.Fragment,{children:[Object(v.jsx)("img",{src:M,width:"20",height:"20",alt:"",className:"rounded mr-1"}),Object(v.jsx)("a",{href:"".concat(O.hc,"profile/").concat(encodeURIComponent(R),"/"),children:_})]}):Object(v.jsx)("span",{children:Object(O.jb)("Unknown")}),Object(v.jsx)("p",{className:"m-0 ml-2",dangerouslySetInnerHTML:{__html:S}})]})]}),Object(v.jsxs)("div",{className:"d-flex justify-content-between align-items-center op-bar",children:[Object(v.jsxs)("p",{className:"m-0",children:[Object(O.jb)("Current path: "),this.renderPath()]}),"/"==n&&D&&Object(v.jsx)("button",{className:"btn btn-secondary op-bar-btn",onClick:this.toggleDialog,children:Object(O.jb)("Restore")})]}),Object(v.jsx)(U,{data:this.state,renderFolder:this.renderFolder})]})})})]}),t&&Object(v.jsx)(p.a,{children:Object(v.jsx)(k,{restoreRepo:this.restoreRepo,toggle:this.toggleDialog})})]})}}]),n}(l.a.Component),U=function(e){Object(o.a)(n,e);var t=Object(s.a)(n);function n(e){var r;return Object(c.a)(this,n),(r=t.call(this,e)).theadData=[{width:"5%",text:""},{width:"55%",text:Object(O.jb)("Name")},{width:"20%",text:Object(O.jb)("Size")},{width:"20%",text:""}],r}return Object(r.a)(n,[{key:"render",value:function(){var e=this,t=this.props.data,n=t.isLoading,c=t.errorMsg,r=t.folderPath,a=t.folderItems;return n?Object(v.jsx)(u.a,{}):c?Object(v.jsx)("p",{className:"error mt-6 text-center",children:c}):Object(v.jsxs)("table",{className:"table-hover",children:[Object(v.jsx)("thead",{children:Object(v.jsx)("tr",{children:this.theadData.map((function(e,t){return Object(v.jsx)("th",{width:e.width,children:e.text},t)}))})}),Object(v.jsx)("tbody",{children:a.map((function(t,n){return Object(v.jsx)(T,{item:t,folderPath:r,renderFolder:e.props.renderFolder},n)}))})]})}}]),n}(l.a.Component),T=function(e){Object(o.a)(n,e);var t=Object(s.a)(n);function n(e){var r;return Object(c.a)(this,n),(r=t.call(this,e)).handleMouseOver=function(){r.setState({isIconShown:!0})},r.handleMouseOut=function(){r.setState({isIconShown:!1})},r.restoreItem=function(e){e.preventDefault();var t=r.props.item,n=b.a.joinPath(r.props.folderPath,t.name);("dir"==t.type?m.b.revertFolder(y,n,N):m.b.revertFile(y,n,N)).then((function(e){f.a.success(Object(O.jb)("Successfully restored 1 item."))})).catch((function(e){var t=b.a.getErrorMsg(e);f.a.danger(t)}))},r.renderFolder=function(e){e.preventDefault();var t=r.props.item,n=r.props.folderPath;r.props.renderFolder(b.a.joinPath(n,t.name))},r.state={isIconShown:!1},r}return Object(r.a)(n,[{key:"render",value:function(){var e=this.props.item,t=this.state.isIconShown,n=this.props.folderPath;return"dir"==e.type?Object(v.jsxs)("tr",{onMouseOver:this.handleMouseOver,onMouseOut:this.handleMouseOut,children:[Object(v.jsx)("td",{className:"text-center",children:Object(v.jsx)("img",{src:b.a.getFolderIconUrl(),alt:Object(O.jb)("Directory"),width:"24"})}),Object(v.jsx)("td",{children:Object(v.jsx)("a",{href:"#",onClick:this.renderFolder,children:e.name})}),Object(v.jsx)("td",{}),Object(v.jsx)("td",{children:Object(v.jsx)("a",{href:"#",className:"action-icon sf2-icon-reply ".concat(t?"":"invisible"),onClick:this.restoreItem,title:Object(O.jb)("Restore")})})]}):Object(v.jsxs)("tr",{onMouseOver:this.handleMouseOver,onMouseOut:this.handleMouseOut,children:[Object(v.jsx)("td",{className:"text-center",children:Object(v.jsx)("img",{src:b.a.getFileIconUrl(e.name),alt:Object(O.jb)("File"),width:"24"})}),Object(v.jsx)("td",{children:Object(v.jsx)("a",{href:"".concat(O.hc,"repo/").concat(y,"/snapshot/files/?obj_id=").concat(e.obj_id,"&commit_id=").concat(N,"&p=").concat(encodeURIComponent(b.a.joinPath(n,e.name))),target:"_blank",children:e.name})}),Object(v.jsx)("td",{children:b.a.bytesToSize(e.size)}),Object(v.jsxs)("td",{children:[Object(v.jsx)("a",{href:"#",className:"action-icon sf2-icon-reply ".concat(t?"":"invisible"),onClick:this.restoreItem,title:Object(O.jb)("Restore")}),Object(v.jsx)("a",{href:"".concat(O.hc,"repo/").concat(y,"/").concat(e.obj_id,"/download/?file_name=").concat(encodeURIComponent(e.name),"&p=").concat(encodeURIComponent(b.a.joinPath(n,e.name))),className:"action-icon sf2-icon-download ".concat(t?"":"invisible"),title:Object(O.jb)("Download")})]})]})}}]),n}(l.a.Component);j.a.render(Object(v.jsx)(L,{}),document.getElementById("wrapper"))},530:function(e,t,n){}},[[1586,1,0]]]);
//# sourceMappingURL=repoSnapshot.chunk.js.map