(this["webpackJsonpseahub-frontend"]=this["webpackJsonpseahub-frontend"]||[]).push([[15],{1799:function(e,t,n){n(71),e.exports=n(1800)},1800:function(e,t,n){"use strict";n.r(t);var r=n(3),i=n(5),a=n(7),s=n(6),c=n(2),o=n.n(c),l=n(28),h=n.n(l),d=n(1),u=n(383),p=n(384),b=n.n(p),f=(n(701),n(0)),j=window.libraryDetails.pageOptions,m=j.repoName,O=j.repoDesc,v=j.institute,x=j.authors,w=j.year,y=j.doi_repos,g=j.archive_repos,T=j.bloxberg_certs,_=j.owner_contact_email,k=function(e){Object(a.a)(n,e);var t=Object(s.a)(n);function n(e){var i;return Object(r.a)(this,n),console.log(T),(i=t.call(this,e)).archiveTheadData=[{width:"20%",text:Object(d.pb)("Version")},{width:"50%",text:Object(d.pb)("Date")},{width:"30%",text:Object(d.pb)("Link to Archive")}],i.doiTheadData=[{width:"50%",text:Object(d.pb)("Date")},{width:"50%",text:Object(d.pb)("DOI")}],i.certTheadData=[{width:"20%",text:Object(d.pb)("Name")},{width:"50%",text:Object(d.pb)("Date")},{width:"30%",text:Object(d.pb)("Link")}],i.state={showArchives:JSON.parse(g).length>0,showDoi:JSON.parse(y).length>0,showCerts:JSON.parse(T).length>0},i}return Object(i.a)(n,[{key:"render",value:function(){return Object(f.jsxs)("div",{className:"h-100 d-flex flex-column",children:[Object(f.jsx)("div",{className:"top-header d-flex justify-content-between",children:Object(f.jsx)("a",{href:d.qc,children:Object(f.jsx)("img",{src:d.Nb+d.Ib,height:d.Hb,width:d.Jb,title:d.rc,alt:"logo"})})}),Object(f.jsx)("div",{className:"flex-auto container-fluid pt-4 pb-6 o-auto",children:Object(f.jsx)("div",{className:"row",children:Object(f.jsxs)("div",{className:"col-md-6 offset-md-1",children:[Object(f.jsx)("h1",{children:Object(f.jsx)(u.a,{maxLength:40,className:"cert_title",text:m})}),Object(f.jsx)(b.a,{lines:3,more:"Show more",less:"Show less",anchorClass:"",children:O}),Object(f.jsx)("br",{}),Object(f.jsxs)("div",{className:"table_row",children:[Object(f.jsxs)("b",{children:[Object(d.pb)("Author(s)"),": "]}),x]}),v&&Object(f.jsxs)("div",{className:"cert_table_row",children:[Object(f.jsxs)("b",{children:[Object(d.pb)("Institute"),": "]}),v]}),w&&Object(f.jsxs)("div",{className:"cert_table_row",children:[Object(f.jsxs)("b",{children:[Object(d.pb)("Year"),": "]}),w]}),Object(f.jsx)("br",{}),this.state.showArchives&&Object(f.jsx)("div",{className:"d-flex justify-content-between align-items-center op-bar",children:Object(f.jsx)("p",{className:"m-0",children:Object(d.pb)("Archives")})}),this.state.showArchives&&Object(f.jsx)(N,{theadData:this.archiveTheadData,data:JSON.parse(g),type:"archive"}),this.state.showArchives&&Object(f.jsx)("br",{}),this.state.showDoi&&Object(f.jsx)("div",{className:"d-flex justify-content-between align-items-center op-bar",children:Object(f.jsx)("p",{className:"m-0",children:Object(d.pb)("Digital Object Identifier(DOI)")})}),this.state.showDoi&&Object(f.jsx)(N,{theadData:this.doiTheadData,data:JSON.parse(y),type:"doi"}),this.state.showDoi&&Object(f.jsx)("br",{}),this.state.showCerts&&Object(f.jsx)("div",{className:"d-flex justify-content-between align-items-center op-bar",children:Object(f.jsx)("p",{className:"m-0",children:Object(d.pb)("bloxberg Transactions")})}),this.state.showCerts&&Object(f.jsx)(N,{theadData:this.certTheadData,data:JSON.parse(T),type:"cert"}),this.state.showCerts&&Object(f.jsx)("br",{}),Object(f.jsxs)("div",{className:"table_row",children:[Object(f.jsxs)("b",{children:[Object(d.pb)("Contact"),": "]}),Object(f.jsx)("a",{href:"mailto:"+_,children:_})]})]})})})]})}}]),n}(o.a.Component),N=function(e){Object(a.a)(n,e);var t=Object(s.a)(n);function n(e){var i;return Object(r.a)(this,n),(i=t.call(this,e)).renderTbody=function(e,t){switch(t){case"archive":return e.map((function(e,t){return Object(f.jsxs)("tr",{children:[Object(f.jsxs)("td",{children:[e.version," "]}),Object(f.jsxs)("td",{children:[e.created," "]}),Object(f.jsx)("td",{children:Object(f.jsx)("a",{href:"".concat(d.qc,"archive/libs/").concat(e.repo_id,"/").concat(e.version,"/0/"),title:Object(d.pb)("Link"),children:Object(d.pb)("Link")})})]},t)}));case"doi":return e.map((function(e,t){return Object(f.jsxs)("tr",{children:[Object(f.jsxs)("td",{children:[e.created," "]}),Object(f.jsx)("td",{children:Object(f.jsx)("a",{href:e.doi,children:e.doi})})]},t)}));case"cert":return e.map((function(e,t){return Object(f.jsxs)("tr",{children:[Object(f.jsxs)("td",{children:[e.content_name," "]}),Object(f.jsxs)("td",{children:[e.created," "]}),"/"==e.path?Object(f.jsx)("td",{children:Object(f.jsx)("a",{href:"".concat(d.qc,"bloxberg-cert/transaction/").concat(e.transaction_id,"/"),children:Object(d.pb)("Link to certificates")})}):Object(f.jsx)("td",{children:Object(f.jsx)("a",{href:"".concat(d.qc,"bloxberg-cert/transaction/").concat(e.transaction_id,"/").concat(e.checksum,"/"),children:Object(d.pb)("Link to certificate")})})]},t)}))}},i}return Object(i.a)(n,[{key:"render",value:function(){var e=this.props,t=e.theadData,n=e.data,r=e.type;return Object(f.jsxs)("table",{className:"table-hover",children:[Object(f.jsx)("thead",{children:Object(f.jsx)("tr",{children:t.map((function(e,t){return Object(f.jsx)("th",{width:e.width,children:e.text},t)}))})}),Object(f.jsx)("tbody",{children:this.renderTbody(n,r)})]})}}]),n}(o.a.Component);h.a.render(Object(f.jsx)(k,{}),document.getElementById("wrapper"))},383:function(e,t,n){"use strict";var r=n(3),i=n(5),a=n(7),s=n(6),c=n(2),o=n(0),l=function(e){Object(a.a)(n,e);var t=Object(s.a)(n);function n(e){var i;return Object(r.a)(this,n),(i=t.call(this,e)).state={showFull:!1},i}return Object(i.a)(n,[{key:"render",value:function(){var e=null;if(this.state.showFull||this.props.text.length<=this.props.maxLength)e=this.props.text;else{var t=this.props.text.substring(0,this.props.maxLength/2),n=this.props.text.substring(this.props.text.length-this.props.maxLength/2,this.props.text.length);e="".concat(t,"...").concat(n)}var r=this;return Object(o.jsx)("span",{onClick:function(){r.setState({showFull:!r.state.showFull})},className:this.props.className,children:e})}}]),n}(c.Component);l.defaultProps={className:""},t.a=l},384:function(e,t,n){"use strict";Object.defineProperty(t,"__esModule",{value:!0});var r=function(){function e(e,t){for(var n=0;n<t.length;n++){var r=t[n];r.enumerable=r.enumerable||!1,r.configurable=!0,"value"in r&&(r.writable=!0),Object.defineProperty(e,r.key,r)}}return function(t,n,r){return n&&e(t.prototype,n),r&&e(t,r),t}}(),i=n(2),a=o(i),s=o(n(9)),c=o(n(700));function o(e){return e&&e.__esModule?e:{default:e}}function l(e,t){if(!(e instanceof t))throw new TypeError("Cannot call a class as a function")}function h(e,t){if(!e)throw new ReferenceError("this hasn't been initialised - super() hasn't been called");return!t||"object"!==typeof t&&"function"!==typeof t?e:t}var d=function(e){function t(){var e,n,r;l(this,t);for(var i=arguments.length,a=Array(i),s=0;s<i;s++)a[s]=arguments[s];return n=r=h(this,(e=t.__proto__||Object.getPrototypeOf(t)).call.apply(e,[this].concat(a))),r.state={expanded:!1,truncated:!1},r.handleTruncate=function(e){e!==r.state.truncated&&r.setState({truncated:e})},r.toggleLines=function(e){e.preventDefault(),r.setState({expanded:!r.state.expanded})},h(r,n)}return function(e,t){if("function"!==typeof t&&null!==t)throw new TypeError("Super expression must either be null or a function, not "+typeof t);e.prototype=Object.create(t&&t.prototype,{constructor:{value:e,enumerable:!1,writable:!0,configurable:!0}}),t&&(Object.setPrototypeOf?Object.setPrototypeOf(e,t):e.__proto__=t)}(t,e),r(t,[{key:"render",value:function(){var e=this.props,t=e.children,n=e.more,r=e.less,i=e.lines,s=e.anchorClass,o=this.state,l=o.expanded,h=o.truncated;return a.default.createElement("div",null,a.default.createElement(c.default,{lines:!l&&i,ellipsis:a.default.createElement("span",null,"... ",a.default.createElement("a",{href:"#",className:s,onClick:this.toggleLines},n)),onTruncate:this.handleTruncate},t),!h&&l&&a.default.createElement("span",null," ",a.default.createElement("a",{href:"#",className:s,onClick:this.toggleLines},r)))}}]),t}(i.Component);d.defaultProps={lines:3,more:"Show more",less:"Show less",anchorClass:""},d.propTypes={children:s.default.node,lines:s.default.number,more:s.default.node,less:s.default.node,anchorClass:s.default.string},t.default=d,e.exports=t.default},700:function(e,t,n){"use strict";n.r(t);var r=n(2),i=n.n(r),a=n(9),s=n.n(a),c=Object.assign||function(e){for(var t=1;t<arguments.length;t++){var n=arguments[t];for(var r in n)Object.prototype.hasOwnProperty.call(n,r)&&(e[r]=n[r])}return e},o=function(){function e(e,t){for(var n=0;n<t.length;n++){var r=t[n];r.enumerable=r.enumerable||!1,r.configurable=!0,"value"in r&&(r.writable=!0),Object.defineProperty(e,r.key,r)}}return function(t,n,r){return n&&e(t.prototype,n),r&&e(t,r),t}}();function l(e,t){if(!(e instanceof t))throw new TypeError("Cannot call a class as a function")}function h(e,t){if(!e)throw new ReferenceError("this hasn't been initialised - super() hasn't been called");return!t||"object"!==typeof t&&"function"!==typeof t?e:t}var d=function(e){function t(){var e;l(this,t);for(var n=arguments.length,r=Array(n),i=0;i<n;i++)r[i]=arguments[i];var a=h(this,(e=t.__proto__||Object.getPrototypeOf(t)).call.apply(e,[this].concat(r)));return a.state={},a.styles={ellipsis:{position:"fixed",visibility:"hidden",top:0,left:0}},a.elements={},a.onResize=a.onResize.bind(a),a.onTruncate=a.onTruncate.bind(a),a.calcTargetWidth=a.calcTargetWidth.bind(a),a.measureWidth=a.measureWidth.bind(a),a.getLines=a.getLines.bind(a),a.renderLine=a.renderLine.bind(a),a}return function(e,t){if("function"!==typeof t&&null!==t)throw new TypeError("Super expression must either be null or a function, not "+typeof t);e.prototype=Object.create(t&&t.prototype,{constructor:{value:e,enumerable:!1,writable:!0,configurable:!0}}),t&&(Object.setPrototypeOf?Object.setPrototypeOf(e,t):e.__proto__=t)}(t,e),o(t,[{key:"componentDidMount",value:function(){var e=this.elements.text,t=this.calcTargetWidth,n=this.onResize,r=document.createElement("canvas");this.canvasContext=r.getContext("2d"),t((function(){e&&e.parentNode.removeChild(e)})),window.addEventListener("resize",n)}},{key:"componentDidUpdate",value:function(e){this.props.children!==e.children&&this.forceUpdate(),this.props.width!==e.width&&this.calcTargetWidth()}},{key:"componentWillUnmount",value:function(){var e=this.elements.ellipsis,t=this.onResize,n=this.timeout;e.parentNode.removeChild(e),window.removeEventListener("resize",t),window.cancelAnimationFrame(n)}},{key:"innerText",value:function(e){var t=document.createElement("div"),n="innerText"in window.HTMLElement.prototype?"innerText":"textContent";t.innerHTML=e.innerHTML.replace(/\r\n|\r|\n/g," ");var r=t[n],i=document.createElement("div");return i.innerHTML="foo<br/>bar","foo\nbar"!==i[n].replace(/\r\n|\r/g,"\n")&&(t.innerHTML=t.innerHTML.replace(/<br.*?[\/]?>/gi,"\n"),r=t[n]),r}},{key:"onResize",value:function(){this.calcTargetWidth()}},{key:"onTruncate",value:function(e){var t=this.props.onTruncate;"function"===typeof t&&(this.timeout=window.requestAnimationFrame((function(){t(e)})))}},{key:"calcTargetWidth",value:function(e){var t=this.elements.target,n=this.calcTargetWidth,r=this.canvasContext,i=this.props.width;if(t){var a=i||Math.floor(t.parentNode.getBoundingClientRect().width);if(!a)return window.requestAnimationFrame((function(){return n(e)}));var s=window.getComputedStyle(t),c=[s["font-weight"],s["font-style"],s["font-size"],s["font-family"]].join(" ");r.font=c,this.setState({targetWidth:a},e)}}},{key:"measureWidth",value:function(e){return this.canvasContext.measureText(e).width}},{key:"ellipsisWidth",value:function(e){return e.offsetWidth}},{key:"trimRight",value:function(e){return e.replace(/\s+$/,"")}},{key:"getLines",value:function(){for(var e=this.elements,t=this.props,n=t.lines,r=t.ellipsis,a=t.trimWhitespace,s=this.state.targetWidth,c=this.innerText,o=this.measureWidth,l=this.onTruncate,h=this.trimRight,d=[],u=c(e.text).split("\n").map((function(e){return e.split(" ")})),p=!0,b=this.ellipsisWidth(this.elements.ellipsis),f=1;f<=n;f++){var j=u[0];if(0!==j.length){var m=j.join(" ");if(o(m)<=s&&1===u.length){p=!1,d.push(m);break}if(f===n){for(var O=j.join(" "),v=0,x=O.length-1;v<=x;){var w=Math.floor((v+x)/2);o(O.slice(0,w+1))+b<=s?v=w+1:x=w-1}var y=O.slice(0,v);if(a)for(y=h(y);!y.length&&d.length;){y=h(d.pop())}m=i.a.createElement("span",null,y,r)}else{for(var g=0,T=j.length-1;g<=T;){var _=Math.floor((g+T)/2);o(j.slice(0,_+1).join(" "))<=s?g=_+1:T=_-1}if(0===g){f=n-1;continue}m=j.slice(0,g).join(" "),u[0].splice(0,g)}d.push(m)}else d.push(),u.shift(),f--}return l(p),d}},{key:"renderLine",value:function(e,t,n){if(t===n.length-1)return i.a.createElement("span",{key:t},e);var r=i.a.createElement("br",{key:t+"br"});return e?[i.a.createElement("span",{key:t},e),r]:r}},{key:"render",value:function(){var e=this,t=this.elements.target,n=this.props,r=n.children,a=n.ellipsis,s=n.lines,o=function(e,t){var n={};for(var r in e)t.indexOf(r)>=0||Object.prototype.hasOwnProperty.call(e,r)&&(n[r]=e[r]);return n}(n,["children","ellipsis","lines"]),l=this.state.targetWidth,h=this.getLines,d=this.renderLine,u=this.onTruncate,p=void 0;return"undefined"!==typeof window&&!(!t||!l)&&(s>0?p=h().map(d):(p=r,u(!1))),delete o.onTruncate,delete o.trimWhitespace,i.a.createElement("span",c({},o,{ref:function(t){e.elements.target=t}}),i.a.createElement("span",null,p),i.a.createElement("span",{ref:function(t){e.elements.text=t}},r),i.a.createElement("span",{ref:function(t){e.elements.ellipsis=t},style:this.styles.ellipsis},a))}}]),t}(r.Component);d.propTypes={children:s.a.node,ellipsis:s.a.node,lines:s.a.oneOfType([s.a.oneOf([!1]),s.a.number]),trimWhitespace:s.a.bool,width:s.a.number,onTruncate:s.a.func},d.defaultProps={children:"",ellipsis:"\u2026",lines:1,trimWhitespace:!1,width:0},t.default=d},701:function(e,t,n){}},[[1799,1,0]]]);
//# sourceMappingURL=libraryDetails.chunk.js.map