(this["webpackJsonpseahub-frontend"]=this["webpackJsonpseahub-frontend"]||[]).push([[35],{1579:function(e,t,n){n(52),e.exports=n(1580)},1580:function(e,t,n){"use strict";n.r(t);var a=n(6),r=n(7),s=n(9),c=n(8),o=n(2),i=n.n(o),u=n(23),j=n.n(u),b=n(10),d=n(1),p=n(171),f=n(142),O=n(15),l=n(137),h=(n(240),n(0)),v=window.app.pageOptions,g=v.repoID,m=v.filePath,w=v.err,x=v.commitID,k=v.fileType,y=function(e){Object(s.a)(n,e);var t=Object(c.a)(n);function n(){return Object(a.a)(this,n),t.apply(this,arguments)}return Object(r.a)(n,[{key:"render",value:function(){return Object(h.jsx)(p.a,{content:Object(h.jsx)(L,{})})}}]),n}(i.a.Component),L=function(e){Object(s.a)(n,e);var t=Object(c.a)(n);function n(e){var r;return Object(a.a)(this,n),(r=t.call(this,e)).state={isLoading:!w,errorMsg:""},r}return Object(r.a)(n,[{key:"componentDidMount",value:function(){var e=this;if(!w){!function t(){b.b.queryOfficeFileConvertStatus(g,x,m,k.toLowerCase()).then((function(n){switch(n.data.status){case"PROCESSING":e.setState({isLoading:!0}),setTimeout(t,2e3);break;case"ERROR":e.setState({isLoading:!1,errorMsg:Object(d.jb)("Document convertion failed.")});break;case"DONE":e.setState({isLoading:!1,errorMsg:""});var a=document.createElement("script");a.type="text/javascript",a.src="".concat(d.Hb,"js/pdf/viewer.js"),document.body.append(a)}})).catch((function(t){t.response?e.setState({isLoading:!1,errorMsg:Object(d.jb)("Document convertion failed.")}):e.setState({isLoading:!1,errorMsg:Object(d.jb)("Please check the network.")})}))}()}}},{key:"render",value:function(){var e=this.state,t=e.isLoading,n=e.errorMsg;return w?Object(h.jsx)(f.a,{}):t?Object(h.jsx)(O.a,{}):n?Object(h.jsx)(f.a,{errorMsg:n}):Object(h.jsx)("div",{className:"file-view-content flex-1 pdf-file-view",children:Object(h.jsx)(l.a,{})})}}]),n}(i.a.Component);j.a.render(Object(h.jsx)(y,{}),document.getElementById("wrapper"))}},[[1579,1,0]]]);
//# sourceMappingURL=viewFileDocument.chunk.js.map