(this["webpackJsonpseahub-frontend"]=this["webpackJsonpseahub-frontend"]||[]).push([[11],{1743:function(e,t,n){n(48),e.exports=n(1786)},1744:function(e,t,n){},1786:function(e,t,n){"use strict";n.r(t);var a=n(6),c=n(7),i=n(9),r=n(8),o=n(2),s=n.n(o),l=n(20),j=n.n(l),u=n(278),p=n.n(u),b=n(1),d=n(0),f=window.app.pageOptions,O=f.fileName,h=f.repoID,v=f.objID,m=f.path;var x=function(){return Object(d.jsx)("a",{href:"".concat(b.mc,"repo/").concat(h,"/").concat(v,"/download/?file_name=").concat(encodeURIComponent(O),"&p=").concat(encodeURIComponent(m)),className:"btn btn-secondary",children:Object(b.nb)("Download")})},w=(n(898),window.app.pageOptions),y=w.fromTrash,g=w.fileName,k=w.commitTime,N=w.canDownloadFile,C=w.enableWatermark,F=w.userNickName,I=function(e){Object(i.a)(n,e);var t=Object(r.a)(n);function n(e){return Object(a.a)(this,n),t.call(this,e)}return Object(c.a)(n,[{key:"render",value:function(){return Object(d.jsxs)("div",{className:"h-100 d-flex flex-column",children:[Object(d.jsxs)("div",{className:"file-view-header d-flex justify-content-between align-items-center",children:[Object(d.jsxs)("div",{children:[Object(d.jsx)("h2",{className:"file-title",children:g}),Object(d.jsx)("p",{className:"meta-info m-0",children:y?"".concat(Object(b.nb)("Current Path: ")).concat(Object(b.nb)("Trash")):k})]}),N&&Object(d.jsx)(x,{})]}),Object(d.jsx)("div",{className:"file-view-body flex-auto d-flex o-hidden",children:this.props.content})]})}}]),n}(s.a.Component);C&&p.a.init({watermark_txt:"".concat(b.lc," ").concat(F),watermark_alpha:.075});var P=I,D=window.app.pageOptions,E=D.canDownloadFile,T=D.err,L="File preview unsupported",S=function(e){Object(i.a)(n,e);var t=Object(r.a)(n);function n(){return Object(a.a)(this,n),t.apply(this,arguments)}return Object(c.a)(n,[{key:"render",value:function(){var e;return e=T==L||this.props.err==L?Object(d.jsx)("p",{children:Object(b.nb)("Online view is not applicable to this file format")}):Object(d.jsx)("p",{className:"error",children:T}),Object(d.jsx)("div",{className:"file-view-content flex-1 o-auto",children:Object(d.jsxs)("div",{className:"file-view-tip",children:[e,E&&Object(d.jsx)(x,{})]})})}}]),n}(s.a.Component),R=S,W=n(282),_=n(351),B=n(352),J=n(5),M=n(279),U=n.n(M),V=(n(262),n(219),n(404),n(531),n(532),n(533),n(253),n(534),n(535),n(329),n(393),n(536),window.app.pageOptions),z=V.fileExt,A=V.fileContent,G={lineNumbers:!0,mode:J.a.chooseLanguage(z),extraKeys:{Ctrl:"autocomplete"},theme:"default",textWrapping:!0,lineWrapping:!0,readOnly:!0,cursorBlinkRate:-1},K=function(e){Object(i.a)(n,e);var t=Object(r.a)(n);function n(){return Object(a.a)(this,n),t.apply(this,arguments)}return Object(c.a)(n,[{key:"render",value:function(){return Object(d.jsx)("div",{className:"file-view-content flex-1 text-file-view",children:Object(d.jsx)(U.a,{ref:"code-mirror-editor",value:A,options:G})})}}]),n}(s.a.Component),q=K,H=n(35),Q=(n(1744),window.app.pageOptions.fileContent),X=function(e){Object(i.a)(n,e);var t=Object(r.a)(n);function n(){return Object(a.a)(this,n),t.apply(this,arguments)}return Object(c.a)(n,[{key:"render",value:function(){return Object(d.jsx)("div",{className:"file-view-content flex-1 o-auto",children:Object(d.jsx)("div",{className:"md-content",children:Object(d.jsx)(H.d,{markdownContent:Q,showTOC:!1,scriptSource:b.Lb+"js/mathjax/tex-svg.js"})})})}}]),n}(s.a.Component),Y=X,Z=n(353),$=n(354),ee=window.app.pageOptions,te=ee.fileType,ne=ee.err,ae=function(e){Object(i.a)(n,e);var t=Object(r.a)(n);function n(){return Object(a.a)(this,n),t.apply(this,arguments)}return Object(c.a)(n,[{key:"render",value:function(){if(ne)return Object(d.jsx)(P,{content:Object(d.jsx)(R,{})});var e;switch(te){case"Image":e=Object(d.jsx)(W.a,{tip:Object(d.jsx)(R,{})});break;case"SVG":e=Object(d.jsx)(_.a,{});break;case"PDF":e=Object(d.jsx)(B.a,{});break;case"Text":e=Object(d.jsx)(q,{});break;case"Markdown":e=Object(d.jsx)(Y,{});break;case"Video":e=Object(d.jsx)(Z.a,{});break;case"Audio":e=Object(d.jsx)($.a,{});break;default:e=Object(d.jsx)(R,{err:"File preview unsupported"})}return Object(d.jsx)(P,{content:e})}}]),n}(s.a.Component);j.a.render(Object(d.jsx)(ae,{}),document.getElementById("wrapper"))},282:function(e,t,n){"use strict";var a,c,i=n(6),r=n(7),o=n(9),s=n(8),l=n(2),j=n.n(l),u=n(5),p=n(1),b=(n(537),n(0)),d=window.app.pageOptions,f=d.repoID,O=d.repoEncrypted,h=d.fileExt,v=d.filePath,m=d.fileName,x=d.thumbnailSizeForOriginal,w=d.previousImage,y=d.nextImage,g=d.rawPath,k=d.xmindImageSrc;w&&(a="".concat(p.mc,"lib/").concat(f,"/file").concat(u.a.encodePath(w))),y&&(c="".concat(p.mc,"lib/").concat(f,"/file").concat(u.a.encodePath(y)));var N=function(e){Object(o.a)(n,e);var t=Object(s.a)(n);function n(e){var a;return Object(i.a)(this,n),(a=t.call(this,e)).handleLoadFailure=function(){a.setState({loadFailed:!0})},a.state={loadFailed:!1},a}return Object(r.a)(n,[{key:"componentDidMount",value:function(){document.addEventListener("keydown",(function(e){w&&37==e.keyCode&&(location.href=a),y&&39==e.keyCode&&(location.href=c)}))}},{key:"render",value:function(){if(this.state.loadFailed)return this.props.tip;var e="";!O&&["tif","tiff","psd"].includes(h)&&(e="".concat(p.mc,"thumbnail/").concat(f,"/").concat(x).concat(u.a.encodePath(v)));var t=k?"".concat(p.mc).concat(k):"";return Object(b.jsxs)("div",{className:"file-view-content flex-1 image-file-view",children:[w&&Object(b.jsx)("a",{href:a,id:"img-prev",title:Object(p.nb)("you can also press \u2190 "),children:Object(b.jsx)("span",{className:"fas fa-chevron-left"})}),y&&Object(b.jsx)("a",{href:c,id:"img-next",title:Object(p.nb)("you can also press \u2192"),children:Object(b.jsx)("span",{className:"fas fa-chevron-right"})}),Object(b.jsx)("img",{src:t||e||g,alt:m,id:"image-view",onError:this.handleLoadFailure})]})}}]),n}(j.a.Component);t.a=N},351:function(e,t,n){"use strict";var a=n(6),c=n(7),i=n(9),r=n(8),o=n(2),s=n.n(o),l=(n(540),n(0)),j=window.app.pageOptions,u=j.fileName,p=j.rawPath,b=function(e){Object(i.a)(n,e);var t=Object(r.a)(n);function n(){return Object(a.a)(this,n),t.apply(this,arguments)}return Object(c.a)(n,[{key:"render",value:function(){return Object(l.jsx)("div",{className:"file-view-content flex-1 svg-file-view",children:Object(l.jsx)("img",{src:p,alt:u,id:"svg-view"})})}}]),n}(s.a.Component);t.a=b},352:function(e,t,n){"use strict";var a=n(6),c=n(7),i=n(9),r=n(8),o=n(2),s=n.n(o),l=n(133),j=(n(263),n(0)),u=function(e){Object(i.a)(n,e);var t=Object(r.a)(n);function n(){return Object(a.a)(this,n),t.apply(this,arguments)}return Object(c.a)(n,[{key:"render",value:function(){return Object(j.jsx)("div",{className:"file-view-content flex-1 pdf-file-view",children:Object(j.jsx)(l.a,{})})}}]),n}(s.a.Component);t.a=u},353:function(e,t,n){"use strict";var a=n(28),c=n(6),i=n(7),r=n(9),o=n(8),s=n(2),l=n.n(s),j=n(280),u=(n(539),n(0)),p=window.app.pageOptions.rawPath,b=function(e){Object(r.a)(n,e);var t=Object(o.a)(n);function n(){return Object(c.a)(this,n),t.apply(this,arguments)}return Object(i.a)(n,[{key:"render",value:function(){var e={autoplay:!1,controls:!0,preload:"auto",sources:[{src:p}]};return Object(u.jsx)("div",{className:"file-view-content flex-1 video-file-view",children:Object(u.jsx)(j.a,Object(a.a)({},e))})}}]),n}(l.a.Component);t.a=b},354:function(e,t,n){"use strict";var a=n(28),c=n(6),i=n(7),r=n(9),o=n(8),s=n(2),l=n.n(s),j=n(281),u=(n(541),n(0)),p=window.app.pageOptions.rawPath,b=function(e){Object(r.a)(n,e);var t=Object(o.a)(n);function n(){return Object(c.a)(this,n),t.apply(this,arguments)}return Object(i.a)(n,[{key:"render",value:function(){var e={autoplay:!1,controls:!0,preload:"auto",sources:[{src:p}]};return Object(u.jsx)("div",{className:"file-view-content flex-1 audio-file-view",children:Object(u.jsx)(j.a,Object(a.a)({},e))})}}]),n}(l.a.Component);t.a=b}},[[1743,1,0]]]);
//# sourceMappingURL=historyTrashFileView.chunk.js.map