(this["webpackJsonpseahub-frontend"]=this["webpackJsonpseahub-frontend"]||[]).push([[27],{1736:function(e,t,n){n(71),e.exports=n(1737)},1737:function(e,t,n){"use strict";n.r(t);var a=n(3),r=n(5),o=n(7),i=n(6),c=n(2),s=n.n(c),d=n(28),u=n.n(d),l=n(54),f=n(8),h=n(4),m=n(1),j=n(105),b=n(95),g=n(19),p=n(10),v=n(0),O=window.shared.pageOptions,w=O.repoID,k=O.sharedToken,x=O.rawPath,y=O.err,N=function(e){Object(o.a)(n,e);var t=Object(i.a)(n);function n(){return Object(a.a)(this,n),t.apply(this,arguments)}return Object(r.a)(n,[{key:"render",value:function(){return Object(v.jsx)(j.a,{content:Object(v.jsx)(C,{}),fileType:"md"})}}]),n}(s.a.Component),C=function(e){Object(o.a)(n,e);var t=Object(i.a)(n);function n(e){var r;return Object(a.a)(this,n),(r=t.call(this,e)).changeImageURL=function(e){if("image"==e.type){var t=e.data.src;if(!new RegExp(m.gc+"/lib/"+w+"/file.*raw=1").test(t))return;var n=t.substring(m.gc.length),a=n.indexOf("/file"),r=n.indexOf("?");n=n.substring(a+5,r),e.data.src=m.gc+"/view-image-via-share-link/?token="+k+"&path="+n}return e},r.modifyValueBeforeRender=function(e){return h.a.changeMarkdownNodes(e,r.changeImageURL)},r.updateForNoOutline=function(){var e=document.querySelector(".md-view .seafile-markdown-outline"),t=document.querySelector(".md-view .article");e.className+=" d-none",t.className+=" article-no-outline"},r.state={markdownContent:"",loading:!y},r}return Object(r.a)(n,[{key:"componentDidMount",value:function(){var e=this;f.b.getFileContent(x).then((function(t){e.setState({markdownContent:t.data,loading:!1})})).catch((function(e){var t=h.a.getErrorMsg(e);p.a.danger(t)}))}},{key:"render",value:function(){return y?Object(v.jsx)(b.a,{}):this.state.loading?Object(v.jsx)(g.a,{}):Object(v.jsx)("div",{className:"shared-file-view-body",children:Object(v.jsx)("div",{className:"md-view",children:Object(v.jsx)(l.d,{scriptSource:m.Nb+"js/mathjax/tex-svg.js",markdownContent:this.state.markdownContent,showTOC:!0,updateForNoOutline:this.updateForNoOutline,activeTitleIndex:"",serviceURL:m.gc,sharedToken:k,repoID:w,modifyValueBeforeRender:this.modifyValueBeforeRender})})})}}]),n}(s.a.Component);u.a.render(Object(v.jsx)(N,{}),document.getElementById("wrapper"))}},[[1736,1,0]]]);
//# sourceMappingURL=sharedFileViewMarkdown.chunk.js.map