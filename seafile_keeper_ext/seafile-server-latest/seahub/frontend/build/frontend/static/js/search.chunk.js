(this["webpackJsonpseahub-frontend"]=this["webpackJsonpseahub-frontend"]||[]).push([[19],{1766:function(e,t,s){s(48),e.exports=s(1789)},1789:function(e,t,s){"use strict";s.r(t);var a=s(6),n=s(7),r=s(9),i=s(8),l=s(2),c=s.n(l),o=s(20),h=s.n(o),p=s(46),d=s(90),j=s(1),u=s(10),b=s(12),m=s.n(b),f=s(5),O=s(0),g=function(e){Object(r.a)(s,e);var t=Object(i.a)(s);function s(e){var n;return Object(a.a)(this,s),(n=t.call(this,e)).handlerFileURL=function(e){return e.is_dir?j.mc+"library/"+e.repo_id+"/"+e.repo_name+e.fullpath:j.mc+"lib/"+e.repo_id+"/file"+f.a.encodePath(e.fullpath)},n.handlerParentDirPath=function(e){var t=e.is_dir?e.fullpath.length-e.name.length-1:e.fullpath.length-e.name.length;return e.fullpath.substring(0,t)},n.handlerParentDirURL=function(e){return j.mc+"library/"+e.repo_id+"/"+e.repo_name+n.handlerParentDirPath(e)},n}return Object(n.a)(s,[{key:"render",value:function(){var e=this.props.item,t=decodeURI(e.fullpath).substring(1),s=t?f.a.getFolderIconUrl(!1,192):f.a.getDefaultLibIconUrl(!0),a=e.is_dir?s:f.a.getFileIconUrl(e.name,192);return""!==e.thumbnail_url&&(a=e.thumbnail_url),Object(O.jsxs)("li",{className:"search-result-item",children:[Object(O.jsx)("img",{className:t?"item-img":"lib-item-img",src:a,alt:""}),Object(O.jsxs)("div",{className:"item-content",children:[Object(O.jsx)("div",{className:"item-name ellipsis",children:Object(O.jsx)("a",{href:this.handlerFileURL(e),target:"_blank",title:e.name,rel:"noreferrer",children:e.name})}),Object(O.jsx)("div",{className:"item-link ellipsis",children:Object(O.jsxs)("a",{href:this.handlerParentDirURL(e),target:"_blank",rel:"noreferrer",children:[e.repo_name,this.handlerParentDirPath(e)]})}),Object(O.jsx)("div",{className:"item-link ellipsis",children:f.a.bytesToSize(e.size)+" "+m()(1e3*e.last_modified).format("YYYY-MM-DD")}),Object(O.jsx)("div",{className:"item-text ellipsis",dangerouslySetInnerHTML:{__html:e.content_highlight}})]})]})}}]),s}(c.a.Component),x=function(e){Object(r.a)(s,e);var t=Object(i.a)(s);function s(e){return Object(a.a)(this,s),t.call(this,e)}return Object(n.a)(s,[{key:"render",value:function(){var e=this.props,t=e.resultItems,s=e.total;return Object(O.jsxs)("div",{className:"search-result-container position-static",children:[Object(O.jsx)("p",{className:"tip",children:s>0?s+" "+(1===s?Object(j.nb)("result"):Object(j.nb)("results")):Object(j.nb)("No result")}),Object(O.jsx)("ul",{className:"search-result-list",children:t.map((function(e,t){return Object(O.jsx)(g,{item:e},t)}))})]})}}]),s}(c.a.Component),y=s(65),S=s.n(y),_=s(4),v=s(363),T=window.search.pageOptions,k=T.repo_name,C=T.search_repo,I=function(e){Object(r.a)(s,e);var t=Object(i.a)(s);function s(e){var n;return Object(a.a)(this,s),(n=t.call(this,e)).getFileTypesList=function(e){for(var t=[Object(j.nb)("Text"),Object(j.nb)("Document"),Object(j.nb)("Image"),Object(j.nb)("Video"),Object(j.nb)("Audio"),"PDF","Markdown"],s=[],a=0,n=e.length;a<n;a++)e[a]&&s.push(t[a]);return s},n.disabledStartDate=function(e){if(!e)return!1;var t=e.isAfter(m()(),"day"),s=n.props.stateAndValues.time_to;return s&&e.isAfter(s)||t},n.disabledEndDate=function(e){if(!e)return!1;var t=e.isAfter(m()(),"day"),s=n.props.stateAndValues.time_from;return s&&e.isBefore(s)||t},n}return Object(n.a)(s,[{key:"render",value:function(){var e=this,t=this.props.stateAndValues,s=t.errorDateMsg,a=t.errorSizeMsg;if(t.isShowSearchFilter){var n=t.size_from,r=t.size_to,i=t.time_from,c=t.time_to,o=t.search_repo,h=t.fileTypeItemsStatus,p=this.getFileTypesList(h),d=p.length;return Object(O.jsxs)("div",{className:"search-filters",children:[o&&Object(O.jsxs)("span",{className:"mr-4",children:[Object(j.nb)("Libraries"),": ","all"==o?Object(j.nb)("All"):k]}),d>0&&Object(O.jsxs)("span",{className:"mr-4",children:[Object(j.nb)("File Types"),": ",p.map((function(e,t){return Object(O.jsxs)("span",{children:[e,t!==d-1&&","," "]},t)}))]}),i&&c&&Object(O.jsxs)("span",{className:"mr-4",children:[Object(j.nb)("Last Update"),": ",i.format("YYYY-MM-DD")," ",Object(j.nb)("to")," ",c.format("YYYY-MM-DD")]}),n&&r&&Object(O.jsxs)("span",{className:"mr-4",children:[Object(j.nb)("Size"),": ",n,"MB - ",r,"MB"]})]})}return Object(O.jsx)("div",{className:"advanced-search",children:Object(O.jsxs)(_.g,{isOpen:t.isCollapseOpen,children:["all"!==C&&Object(O.jsx)("div",{className:"search-repo search-catalog",children:Object(O.jsxs)(_.D,{children:[Object(O.jsxs)(_.f,{md:"2",lg:"2",children:[Object(j.nb)("Libraries"),": "]}),Object(O.jsx)(_.f,{md:"4",lg:"4",children:Object(O.jsx)(_.n,{check:!0,children:Object(O.jsxs)(_.t,{check:!0,children:[Object(O.jsx)(_.p,{type:"radio",name:"repo",checked:t.isAllRepoCheck,onChange:function(){return e.props.handlerRepo(!0)}}),Object(j.nb)("In all libraries")]})})}),Object(O.jsx)(_.f,{md:"4",lg:"4",children:Object(O.jsx)(_.n,{check:!0,children:Object(O.jsxs)(_.t,{check:!0,children:[Object(O.jsx)(_.p,{type:"radio",name:"repo",checked:!t.isAllRepoCheck,onChange:function(){return e.props.handlerRepo(!1)}}),k]})})})]})}),Object(O.jsxs)("div",{className:"search-file-types search-catalog",children:[Object(O.jsxs)(_.D,{children:[Object(O.jsxs)(_.f,{md:"2",lg:"2",children:[Object(j.nb)("File Types"),": "]}),Object(O.jsx)(_.f,{md:"4",lg:"4",children:Object(O.jsx)(_.n,{check:!0,children:Object(O.jsxs)(_.t,{check:!0,children:[Object(O.jsx)(_.p,{type:"radio",name:"types",checked:!t.isFileTypeCollapseOpen,onChange:this.props.closeFileTypeCollapse}),Object(j.nb)("All file types")]})})}),Object(O.jsx)(_.f,{md:"4",lg:"4",children:Object(O.jsx)(_.n,{check:!0,children:Object(O.jsxs)(_.t,{check:!0,children:[Object(O.jsx)(_.p,{type:"radio",name:"types",checked:t.isFileTypeCollapseOpen,onChange:this.props.openFileTypeCollapse}),Object(j.nb)("Custom file types")]})})})]}),Object(O.jsxs)(_.D,{children:[Object(O.jsx)(_.f,{md:"2",lg:"2"}),Object(O.jsx)(_.f,{md:"10",lg:"10",children:Object(O.jsxs)(_.g,{isOpen:t.isFileTypeCollapseOpen,children:[Object(O.jsx)(_.n,{className:"search-file-types-form",children:Object(O.jsxs)(l.Fragment,{children:[Object(O.jsx)(_.h,{type:"checkbox",id:"checkTextFiles",label:Object(j.nb)("Text files"),inline:!0,onChange:function(){return e.props.handlerFileTypes(0)},checked:t.fileTypeItemsStatus[0]}),Object(O.jsx)(_.h,{type:"checkbox",id:"checkDocuments",label:Object(j.nb)("Documents"),inline:!0,onChange:function(){return e.props.handlerFileTypes(1)},checked:t.fileTypeItemsStatus[1]}),Object(O.jsx)(_.h,{type:"checkbox",id:"checkImages",label:Object(j.nb)("Images"),inline:!0,onChange:function(){return e.props.handlerFileTypes(2)},checked:t.fileTypeItemsStatus[2]}),Object(O.jsx)(_.h,{type:"checkbox",id:"checkVideo",label:Object(j.nb)("Video"),inline:!0,onChange:function(){return e.props.handlerFileTypes(3)},checked:t.fileTypeItemsStatus[3]}),Object(O.jsx)(_.h,{type:"checkbox",id:"checkAudio",label:Object(j.nb)("Audio"),inline:!0,onChange:function(){return e.props.handlerFileTypes(4)},checked:t.fileTypeItemsStatus[4]}),Object(O.jsx)(_.h,{type:"checkbox",id:"checkPdf",label:"PDF",inline:!0,onChange:function(){return e.props.handlerFileTypes(5)},checked:t.fileTypeItemsStatus[5]}),Object(O.jsx)(_.h,{type:"checkbox",id:"checkMarkdown",label:"Markdown",inline:!0,onChange:function(){return e.props.handlerFileTypes(6)},checked:t.fileTypeItemsStatus[6]})]})}),Object(O.jsx)("input",{type:"text",className:"form-control search-input",name:"query",autoComplete:"off",placeholder:Object(j.nb)("Input file extensions here, separate with ','"),onChange:this.props.handlerFileTypesInput,value:t.input_fexts,onKeyDown:this.props.handleKeyDown})]})})]})]}),Object(O.jsxs)("div",{className:"search-date search-catalog",children:[Object(O.jsxs)(_.D,{children:[Object(O.jsxs)(_.f,{md:"2",lg:"2",className:"mt-2",children:[Object(j.nb)("Last Update"),": "]}),Object(O.jsxs)(_.f,{md:"4",lg:"4",sm:"4",xs:"5",className:"position-relative",children:[Object(O.jsx)(v.a,{inputWidth:"100%",disabledDate:this.disabledStartDate,value:t.time_from,onChange:this.props.handleTimeFromInput,showHourAndMinute:!1}),Object(O.jsx)("span",{className:"select-data-icon",children:Object(O.jsx)("i",{className:"fa fa-calendar-alt"})})]}),Object(O.jsx)("div",{className:"mt-2",children:"-"}),Object(O.jsxs)(_.f,{md:"4",lg:"4",sm:"4",xs:"5",className:"position-relative",children:[Object(O.jsx)(v.a,{inputWidth:"100%",disabledDate:this.disabledEndDate,value:t.time_to,onChange:this.props.handleTimeToInput,showHourAndMinute:!1}),Object(O.jsx)("span",{className:"select-data-icon",children:Object(O.jsx)("i",{className:"fa fa-calendar-alt"})})]})]}),s&&Object(O.jsxs)(_.D,{children:[Object(O.jsx)(_.f,{md:"2",lg:"2"}),Object(O.jsx)(_.f,{md:"8",className:"error mt-2",children:s})]})]}),Object(O.jsx)("div",{className:"search-size search-catalog",children:Object(O.jsxs)(_.D,{children:[Object(O.jsxs)(_.f,{md:"2",lg:"2",className:"mt-2",children:[Object(j.nb)("Size"),": "]}),Object(O.jsxs)(_.f,{md:"4",lg:"4",sm:"4",xs:"5",children:[Object(O.jsx)(_.n,{children:Object(O.jsxs)(_.q,{children:[Object(O.jsx)(_.p,{type:"tel",name:"size_from",onKeyDown:this.props.handleKeyDown,onChange:this.props.handleSizeFromInput,value:t.size_from}),Object(O.jsx)(_.r,{addonType:"append",children:"MB"})]})}),Object(O.jsxs)(S.a,{query:"(min-width: 768px)",children:[a&&Object(O.jsx)("div",{className:"error mb-4",children:a}),Object(O.jsx)(_.c,{color:"primary",onClick:this.props.handleSubmit,children:Object(j.nb)("Submit")}),Object(O.jsx)(_.c,{className:"ml-2",onClick:this.props.handleReset,children:Object(j.nb)("Reset")})]})]}),Object(O.jsx)("div",{className:"mt-2",children:"-"}),Object(O.jsx)(_.f,{md:"4",lg:"4",sm:"4",xs:"5",children:Object(O.jsx)(_.n,{children:Object(O.jsxs)(_.q,{children:[Object(O.jsx)(_.p,{type:"tel",name:"size_to",onKeyDown:this.props.handleKeyDown,onChange:this.props.handleSizeToInput,value:t.size_to}),Object(O.jsx)(_.r,{addonType:"append",children:"MB"})]})})})]})}),Object(O.jsxs)(S.a,{query:"(max-width: 767.8px)",children:[a&&Object(O.jsx)("div",{className:"error mb-4",children:a}),Object(O.jsx)(_.c,{color:"primary",onClick:this.props.handleSubmit,children:Object(j.nb)("Submit")}),Object(O.jsx)(_.c,{className:"ml-2",onClick:this.props.handleReset,children:Object(j.nb)("Reset")})]})]})})}}]),s}(c.a.Component),F=s(11),D=s(14),N=(s(112),s(155)),M=window.search.pageOptions,z=M.q,w=M.search_repo,R=M.search_ftypes,L=function(e){Object(r.a)(s,e);var t=Object(i.a)(s);function s(e){var n;return Object(a.a)(this,s),(n=t.call(this,e)).handleSearchParams=function(e){var t={q:n.state.q.trim(),page:e},s=n.getFileTypesList();n.state.search_repo&&(t.search_repo=n.state.search_repo),n.state.search_ftypes&&(t.search_ftypes=n.state.search_ftypes),n.state.per_page&&(t.per_page=n.state.per_page),n.state.input_fexts&&(t.input_fexts=n.state.input_fexts);var a=n.state,r=a.time_from,i=a.time_to;return r&&(t.time_from=parseInt(r.valueOf()/1e3)),i&&(t.time_to=parseInt(i.valueOf()/1e3)),n.state.size_from&&(t.size_from=1e3*n.state.size_from*1e3),n.state.size_to&&(t.size_to=1e3*n.state.size_to*1e3),0!==s.length&&(t.ftype=s),t},n.handleSubmit=function(){if(n.compareNumber(n.state.size_from,n.state.size_to))n.setState({errorSizeMsg:Object(j.nb)("Invalid file size range.")});else{if(n.getValueLength(n.state.q.trim())<3)0===n.state.q.trim().length?n.setState({errorMsg:Object(j.nb)("It is required.")}):n.setState({errorMsg:Object(j.nb)("Required at least three letters.")}),n.state.isLoading&&n.setState({isLoading:!1});else{var e=n.handleSearchParams(1);n.getSearchResults(e)}n.state.isCollapseOpen&&n.setState({isCollapseOpen:!1})}},n.compareNumber=function(e,t){return!(!e||!t)&&parseInt(e.replace(/\-/g,""))>=parseInt(t.replace(/\-/g,""))},n.showSearchFilter=function(){n.setState({isShowSearchFilter:!0})},n.hideSearchFilter=function(){n.setState({isShowSearchFilter:!1})},n.handleReset=function(){n.setState({q:z.trim(),search_repo:w,search_ftypes:R,fileTypeItemsStatus:[!1,!1,!1,!1,!1,!1,!1],input_fexts:"",time_from:null,time_to:null,size_from:"",size_to:"",errorMsg:"",errorDateMsg:"",errorSizeMsg:""})},n.handlePrevious=function(e){e.preventDefault(),n.stateHistory&&n.state.page>1?n.setState(n.stateHistory,(function(){var e=n.handleSearchParams(n.state.page-1);n.getSearchResults(e)})):F.a.danger(Object(j.nb)("Error"),{duration:3})},n.handleNext=function(e){e.preventDefault(),n.stateHistory&&n.state.hasMore?n.setState(n.stateHistory,(function(){var e=n.handleSearchParams(n.state.page+1);n.getSearchResults(e)})):F.a.danger(Object(j.nb)("Error"),{duration:3})},n.toggleCollapse=function(){n.setState({isCollapseOpen:!n.state.isCollapseOpen}),n.hideSearchFilter()},n.openFileTypeCollapse=function(){n.setState({isFileTypeCollapseOpen:!0,search_ftypes:"custom"})},n.closeFileTypeCollapse=function(){n.setState({isFileTypeCollapseOpen:!1,fileTypeItemsStatus:Array(7).fill(!1),search_ftypes:"all",input_fexts:""})},n.handleSearchInput=function(e){n.setState({q:e.target.value}),n.state.errorMsg&&n.setState({errorMsg:""}),n.state.errorSizeMsg&&n.setState({errorSizeMsg:""}),n.state.errorDateMsg&&n.setState({errorDateMsg:""})},n.handleKeyDown=function(e){13===e.keyCode&&(e.preventDefault(),n.handleSubmit())},n.handlerRepo=function(e){e?n.setState({isAllRepoCheck:!0,search_repo:"all"}):n.setState({isAllRepoCheck:!1,search_repo:"all"!==w?w:""})},n.handlerFileTypes=function(e){var t=n.state.fileTypeItemsStatus;t[e]=!n.state.fileTypeItemsStatus[e],n.setState({fileTypeItemsStatus:t})},n.getFileTypesList=function(){for(var e=["Text","Document","Image","Video","Audio","PDF","Markdown"],t=[],s=0,a=n.state.fileTypeItemsStatus.length;s<a;s++)n.state.fileTypeItemsStatus[s]&&t.push(e[s]);return t},n.handlerFileTypesInput=function(e){n.setState({input_fexts:e.target.value.trim()})},n.handleTimeFromInput=function(e){n.setState({time_from:e?e.hours(0).minutes(0).seconds(0):e}),n.state.errorDateMsg&&n.setState({errorDateMsg:""})},n.handleTimeToInput=function(e){n.setState({time_to:e?e.hours(23).minutes(59).seconds(59):e}),n.state.errorDateMsg&&n.setState({errorDateMsg:""})},n.handleSizeFromInput=function(e){n.setState({size_from:e.target.value>=0?e.target.value:0}),n.state.errorSizeMsg&&n.setState({errorSizeMsg:""})},n.handleSizeToInput=function(e){n.setState({size_to:e.target.value>=0?e.target.value:0}),n.state.errorSizeMsg&&n.setState({errorSizeMsg:""})},n.stateHistory=null,n.state={isCollapseOpen:"all"!==w,isFileTypeCollapseOpen:!1,isResultGot:!1,isLoading:!0,isAllRepoCheck:"all"===w,isShowSearchFilter:!1,q:z.trim(),search_repo:w,search_ftypes:R,fileTypeItemsStatus:[!1,!1,!1,!1,!1,!1,!1],input_fexts:"",time_from:null,time_to:null,size_from:"",size_to:"",hasMore:!1,resultItems:[],page:1,per_page:20,errorMsg:"",errorDateMsg:"",errorSizeMsg:""},n}return Object(n.a)(s,[{key:"getSearchResults",value:function(e){var t=this;this.setState({isLoading:!0,isResultGot:!1});var s=N.cloneDeep(this.state);u.b.searchFiles(e,null).then((function(a){var n=a.data,r=n.results,i=n.has_more,l=n.total;t.setState({isLoading:!1,isResultGot:!0,resultItems:r,hasMore:i,total:l,page:e.page,isShowSearchFilter:!0}),t.stateHistory=s,t.stateHistory.resultItems=r,t.stateHistory.hasMore=i,t.stateHistory.page=e.page})).catch((function(e){t.setState({isLoading:!1}),e.response?F.a.danger(e.response.data.detail||e.response.data.error_msg||Object(j.nb)("Error"),{duration:3}):F.a.danger(Object(j.nb)("Please check the network."),{duration:3})}))}},{key:"getValueLength",value:function(e){for(var t,s=0,a=0,n=e.length;a<n;a++)10===(t=e.charCodeAt(a))?s+=2:t<127?s+=1:t>=128&&t<=2047?s+=2:t>=2048&&t<=65535&&(s+=3);return s}},{key:"componentDidMount",value:function(){this.state.q?this.handleSubmit():this.setState({isLoading:!1})}},{key:"render",value:function(){var e=this.state.isCollapseOpen;return Object(O.jsxs)("div",{className:"search-page",children:[Object(O.jsxs)("div",{className:"search-page-container",children:[Object(O.jsxs)("div",{className:"input-icon align-items-center d-flex",children:[Object(O.jsx)("input",{type:"text",className:"form-control search-input",name:"query",autoComplete:"off",value:this.state.q,placeholder:Object(j.nb)("Search Files"),onChange:this.handleSearchInput,onKeyDown:this.handleKeyDown}),Object(O.jsx)("i",{className:"search-icon-right input-icon-addon fas fa-search",onClick:this.handleSubmit}),Object(O.jsx)("i",{className:"fas action-icon fa-angle-double-".concat(e?"up":"down"),onClick:this.toggleCollapse})]}),this.state.errorMsg&&Object(O.jsx)("div",{className:"error",children:this.state.errorMsg}),Object(O.jsx)(I,{openFileTypeCollapse:this.openFileTypeCollapse,closeFileTypeCollapse:this.closeFileTypeCollapse,handlerFileTypes:this.handlerFileTypes,handlerFileTypesInput:this.handlerFileTypesInput,handleSubmit:this.handleSubmit,handleReset:this.handleReset,handlerRepo:this.handlerRepo,handleKeyDown:this.handleKeyDown,handleTimeFromInput:this.handleTimeFromInput,handleTimeToInput:this.handleTimeToInput,handleSizeFromInput:this.handleSizeFromInput,handleSizeToInput:this.handleSizeToInput,stateAndValues:this.state})]}),this.state.isLoading&&Object(O.jsx)(D.a,{}),!this.state.isLoading&&this.state.isResultGot&&Object(O.jsx)(x,{resultItems:this.state.resultItems,total:this.state.total}),!this.state.isLoading&&this.state.isResultGot&&Object(O.jsxs)("div",{className:"paginator",children:[1!==this.state.page&&Object(O.jsx)("a",{href:"#",onClick:this.handlePrevious,children:Object(j.nb)("Previous")}),1!==this.state.page&&this.state.hasMore&&Object(O.jsx)("span",{children:" | "}),this.state.hasMore&&Object(O.jsx)("a",{href:"#",onClick:this.handleNext,children:Object(j.nb)("Next")})]})]})}}]),s}(c.a.Component),A=(s(197),s(99),function(e){Object(r.a)(s,e);var t=Object(i.a)(s);function s(e){var n;return Object(a.a)(this,s),(n=t.call(this,e)).onSearchedClick=function(e){var t=e.is_dir?j.mc+"library/"+e.repo_id+"/"+e.repo_name+e.path:j.mc+"lib/"+e.repo_id+"/file"+f.a.encodePath(e.path);window.open("about:blank").location.href=t},n}return Object(n.a)(s,[{key:"render",value:function(){return Object(O.jsxs)("div",{className:"w-100 h-100",children:[Object(O.jsxs)("div",{className:"main-panel-north border-left-show",children:[Object(O.jsx)(d.a,{}),Object(O.jsx)(p.a,{onSearchedClick:this.onSearchedClick})]}),Object(O.jsx)("div",{className:"main-panel-south",children:Object(O.jsx)(L,{})})]})}}]),s}(c.a.Component));h.a.render(Object(O.jsx)(A,{}),document.getElementById("wrapper"))}},[[1766,1,0]]]);
//# sourceMappingURL=search.chunk.js.map