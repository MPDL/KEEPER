(this["webpackJsonpseahub-frontend"]=this["webpackJsonpseahub-frontend"]||[]).push([[5],{1677:function(e,t,n){n(49),e.exports=n(1678)},1678:function(e,t,n){"use strict";n.r(t);var r=n(6),i=n(7),a=n(9),s=n(8),o=n(2),l=n.n(o),c=n(20),u=n.n(c),h=n(1),d=n(127),f=n(327),p=n(328),b=n.n(p),m=(n(596),n(238),n(0)),v=window.bloxbergCertificate.pageOptions,j=v.repoName,g=v.repoDesc,y=v.institute,O=v.authors,w=v.year,x=v.transactionId,T=v.pdfUrl,_=v.metadataUrl,k=v.historyFileUrl,E=function(e){Object(a.a)(n,e);var t=Object(s.a)(n);function n(e){var i;return Object(r.a)(this,n),(i=t.call(this,e)).toggleModal=function(){i.setState({modalIsOpen:!i.state.modalIsOpen,metadataUrl:""})},i.state={modalIsOpen:!1,metadataUrl:_},i}return Object(i.a)(n,[{key:"render",value:function(){var e=this.state.modalIsOpen?"file-view-content-full flex-1 pdf-file-view col-md-8 offset-md-2":"file-view-content flex-1 pdf-file-view col-md-6 offset-md-1",t="https://blockexplorer.bloxberg.org/tx/"+x;return Object(m.jsxs)("div",{className:"h-100 d-flex flex-column",children:[Object(m.jsx)("div",{className:"top-header d-flex justify-content-between",children:Object(m.jsx)("a",{href:h.mc,children:Object(m.jsx)("img",{src:h.Lb+h.Gb,height:h.Fb,width:h.Hb,title:h.nc,alt:"logo"})})}),!this.state.modalIsOpen&&Object(m.jsx)("div",{className:"container-fluid pt-4 pb-6 o-auto",children:Object(m.jsxs)("div",{className:"row",children:[Object(m.jsxs)("div",{className:"col-md-6 offset-md-1 shadow",children:[Object(m.jsx)("h1",{children:Object(m.jsx)(f.a,{maxLength:40,className:"cert_title",text:j})}),Object(m.jsx)(b.a,{lines:3,more:"Show more",less:"Show less",anchorClass:"",children:g}),Object(m.jsxs)("div",{className:"table_row",children:[Object(m.jsxs)("b",{children:[Object(h.nb)("Author(s)"),": "]}),O]}),y&&Object(m.jsxs)("div",{className:"cert_table_row",children:[Object(m.jsxs)("b",{children:[Object(h.nb)("Institute"),": "]}),y]}),w&&Object(m.jsxs)("div",{className:"cert_table_row",children:[Object(m.jsxs)("b",{children:[Object(h.nb)("Year"),": "]}),w]}),Object(m.jsxs)("div",{className:"cert_table_row",children:[Object(m.jsxs)("b",{children:[Object(h.nb)("Transaction"),": "]}),Object(m.jsx)("a",{href:t,target:"_blank",children:x})]}),Object(m.jsx)("div",{className:"cert_table_row",children:Object(m.jsx)("a",{href:k,download:!0,children:Object(h.nb)("Download File")})}),Object(m.jsx)("div",{className:"cert_table_row",children:Object(m.jsx)("a",{href:T,download:!0,children:Object(h.nb)("Download Certificate")})})]}),Object(m.jsx)("div",{className:"col-md-4",children:Object(m.jsx)("blockcerts-verifier",{"display-mode":"card",src:this.state.metadataUrl})})]})}),Object(m.jsx)("div",{className:e,onClick:this.toggleModal,children:Object(m.jsx)(d.a,{})})]})}}]),n}(l.a.Component);u.a.render(Object(m.jsx)(E,{}),document.getElementById("wrapper"))},327:function(e,t,n){"use strict";var r=n(6),i=n(7),a=n(9),s=n(8),o=n(2),l=n(0),c=function(e){Object(a.a)(n,e);var t=Object(s.a)(n);function n(e){var i;return Object(r.a)(this,n),(i=t.call(this,e)).state={showFull:!1},i}return Object(i.a)(n,[{key:"render",value:function(){var e=null;if(this.state.showFull||this.props.text.length<=this.props.maxLength)e=this.props.text;else{var t=this.props.text.substring(0,this.props.maxLength/2),n=this.props.text.substring(this.props.text.length-this.props.maxLength/2,this.props.text.length);e="".concat(t,"...").concat(n)}var r=this;return Object(l.jsx)("span",{onClick:function(){r.setState({showFull:!r.state.showFull})},className:this.props.className,children:e})}}]),n}(o.Component);c.defaultProps={className:""},t.a=c},328:function(e,t,n){"use strict";Object.defineProperty(t,"__esModule",{value:!0});var r=function(){function e(e,t){for(var n=0;n<t.length;n++){var r=t[n];r.enumerable=r.enumerable||!1,r.configurable=!0,"value"in r&&(r.writable=!0),Object.defineProperty(e,r.key,r)}}return function(t,n,r){return n&&e(t.prototype,n),r&&e(t,r),t}}(),i=n(2),a=l(i),s=l(n(3)),o=l(n(595));function l(e){return e&&e.__esModule?e:{default:e}}function c(e,t){if(!(e instanceof t))throw new TypeError("Cannot call a class as a function")}function u(e,t){if(!e)throw new ReferenceError("this hasn't been initialised - super() hasn't been called");return!t||"object"!==typeof t&&"function"!==typeof t?e:t}var h=function(e){function t(){var e,n,r;c(this,t);for(var i=arguments.length,a=Array(i),s=0;s<i;s++)a[s]=arguments[s];return n=r=u(this,(e=t.__proto__||Object.getPrototypeOf(t)).call.apply(e,[this].concat(a))),r.state={expanded:!1,truncated:!1},r.handleTruncate=function(e){e!==r.state.truncated&&r.setState({truncated:e})},r.toggleLines=function(e){e.preventDefault(),r.setState({expanded:!r.state.expanded})},u(r,n)}return function(e,t){if("function"!==typeof t&&null!==t)throw new TypeError("Super expression must either be null or a function, not "+typeof t);e.prototype=Object.create(t&&t.prototype,{constructor:{value:e,enumerable:!1,writable:!0,configurable:!0}}),t&&(Object.setPrototypeOf?Object.setPrototypeOf(e,t):e.__proto__=t)}(t,e),r(t,[{key:"render",value:function(){var e=this.props,t=e.children,n=e.more,r=e.less,i=e.lines,s=e.anchorClass,l=this.state,c=l.expanded,u=l.truncated;return a.default.createElement("div",null,a.default.createElement(o.default,{lines:!c&&i,ellipsis:a.default.createElement("span",null,"... ",a.default.createElement("a",{href:"#",className:s,onClick:this.toggleLines},n)),onTruncate:this.handleTruncate},t),!u&&c&&a.default.createElement("span",null," ",a.default.createElement("a",{href:"#",className:s,onClick:this.toggleLines},r)))}}]),t}(i.Component);h.defaultProps={lines:3,more:"Show more",less:"Show less",anchorClass:""},h.propTypes={children:s.default.node,lines:s.default.number,more:s.default.node,less:s.default.node,anchorClass:s.default.string},t.default=h,e.exports=t.default},595:function(e,t,n){"use strict";n.r(t);var r=n(2),i=n.n(r),a=n(3),s=n.n(a),o=Object.assign||function(e){for(var t=1;t<arguments.length;t++){var n=arguments[t];for(var r in n)Object.prototype.hasOwnProperty.call(n,r)&&(e[r]=n[r])}return e},l=function(){function e(e,t){for(var n=0;n<t.length;n++){var r=t[n];r.enumerable=r.enumerable||!1,r.configurable=!0,"value"in r&&(r.writable=!0),Object.defineProperty(e,r.key,r)}}return function(t,n,r){return n&&e(t.prototype,n),r&&e(t,r),t}}();function c(e,t){if(!(e instanceof t))throw new TypeError("Cannot call a class as a function")}function u(e,t){if(!e)throw new ReferenceError("this hasn't been initialised - super() hasn't been called");return!t||"object"!==typeof t&&"function"!==typeof t?e:t}var h=function(e){function t(){var e;c(this,t);for(var n=arguments.length,r=Array(n),i=0;i<n;i++)r[i]=arguments[i];var a=u(this,(e=t.__proto__||Object.getPrototypeOf(t)).call.apply(e,[this].concat(r)));return a.state={},a.styles={ellipsis:{position:"fixed",visibility:"hidden",top:0,left:0}},a.elements={},a.onResize=a.onResize.bind(a),a.onTruncate=a.onTruncate.bind(a),a.calcTargetWidth=a.calcTargetWidth.bind(a),a.measureWidth=a.measureWidth.bind(a),a.getLines=a.getLines.bind(a),a.renderLine=a.renderLine.bind(a),a}return function(e,t){if("function"!==typeof t&&null!==t)throw new TypeError("Super expression must either be null or a function, not "+typeof t);e.prototype=Object.create(t&&t.prototype,{constructor:{value:e,enumerable:!1,writable:!0,configurable:!0}}),t&&(Object.setPrototypeOf?Object.setPrototypeOf(e,t):e.__proto__=t)}(t,e),l(t,[{key:"componentDidMount",value:function(){var e=this.elements.text,t=this.calcTargetWidth,n=this.onResize,r=document.createElement("canvas");this.canvasContext=r.getContext("2d"),t((function(){e&&e.parentNode.removeChild(e)})),window.addEventListener("resize",n)}},{key:"componentDidUpdate",value:function(e){this.props.children!==e.children&&this.forceUpdate(),this.props.width!==e.width&&this.calcTargetWidth()}},{key:"componentWillUnmount",value:function(){var e=this.elements.ellipsis,t=this.onResize,n=this.timeout;e.parentNode.removeChild(e),window.removeEventListener("resize",t),window.cancelAnimationFrame(n)}},{key:"innerText",value:function(e){var t=document.createElement("div"),n="innerText"in window.HTMLElement.prototype?"innerText":"textContent";t.innerHTML=e.innerHTML.replace(/\r\n|\r|\n/g," ");var r=t[n],i=document.createElement("div");return i.innerHTML="foo<br/>bar","foo\nbar"!==i[n].replace(/\r\n|\r/g,"\n")&&(t.innerHTML=t.innerHTML.replace(/<br.*?[\/]?>/gi,"\n"),r=t[n]),r}},{key:"onResize",value:function(){this.calcTargetWidth()}},{key:"onTruncate",value:function(e){var t=this.props.onTruncate;"function"===typeof t&&(this.timeout=window.requestAnimationFrame((function(){t(e)})))}},{key:"calcTargetWidth",value:function(e){var t=this.elements.target,n=this.calcTargetWidth,r=this.canvasContext,i=this.props.width;if(t){var a=i||Math.floor(t.parentNode.getBoundingClientRect().width);if(!a)return window.requestAnimationFrame((function(){return n(e)}));var s=window.getComputedStyle(t),o=[s["font-weight"],s["font-style"],s["font-size"],s["font-family"]].join(" ");r.font=o,this.setState({targetWidth:a},e)}}},{key:"measureWidth",value:function(e){return this.canvasContext.measureText(e).width}},{key:"ellipsisWidth",value:function(e){return e.offsetWidth}},{key:"trimRight",value:function(e){return e.replace(/\s+$/,"")}},{key:"getLines",value:function(){for(var e=this.elements,t=this.props,n=t.lines,r=t.ellipsis,a=t.trimWhitespace,s=this.state.targetWidth,o=this.innerText,l=this.measureWidth,c=this.onTruncate,u=this.trimRight,h=[],d=o(e.text).split("\n").map((function(e){return e.split(" ")})),f=!0,p=this.ellipsisWidth(this.elements.ellipsis),b=1;b<=n;b++){var m=d[0];if(0!==m.length){var v=m.join(" ");if(l(v)<=s&&1===d.length){f=!1,h.push(v);break}if(b===n){for(var j=m.join(" "),g=0,y=j.length-1;g<=y;){var O=Math.floor((g+y)/2);l(j.slice(0,O+1))+p<=s?g=O+1:y=O-1}var w=j.slice(0,g);if(a)for(w=u(w);!w.length&&h.length;){w=u(h.pop())}v=i.a.createElement("span",null,w,r)}else{for(var x=0,T=m.length-1;x<=T;){var _=Math.floor((x+T)/2);l(m.slice(0,_+1).join(" "))<=s?x=_+1:T=_-1}if(0===x){b=n-1;continue}v=m.slice(0,x).join(" "),d[0].splice(0,x)}h.push(v)}else h.push(),d.shift(),b--}return c(f),h}},{key:"renderLine",value:function(e,t,n){if(t===n.length-1)return i.a.createElement("span",{key:t},e);var r=i.a.createElement("br",{key:t+"br"});return e?[i.a.createElement("span",{key:t},e),r]:r}},{key:"render",value:function(){var e=this,t=this.elements.target,n=this.props,r=n.children,a=n.ellipsis,s=n.lines,l=function(e,t){var n={};for(var r in e)t.indexOf(r)>=0||Object.prototype.hasOwnProperty.call(e,r)&&(n[r]=e[r]);return n}(n,["children","ellipsis","lines"]),c=this.state.targetWidth,u=this.getLines,h=this.renderLine,d=this.onTruncate,f=void 0;return"undefined"!==typeof window&&!(!t||!c)&&(s>0?f=u().map(h):(f=r,d(!1))),delete l.onTruncate,delete l.trimWhitespace,i.a.createElement("span",o({},l,{ref:function(t){e.elements.target=t}}),i.a.createElement("span",null,f),i.a.createElement("span",{ref:function(t){e.elements.text=t}},r),i.a.createElement("span",{ref:function(t){e.elements.ellipsis=t},style:this.styles.ellipsis},a))}}]),t}(r.Component);h.propTypes={children:s.a.node,ellipsis:s.a.node,lines:s.a.oneOfType([s.a.oneOf([!1]),s.a.number]),trimWhitespace:s.a.bool,width:s.a.number,onTruncate:s.a.func},h.defaultProps={children:"",ellipsis:"\u2026",lines:1,trimWhitespace:!1,width:0},t.default=h},596:function(e,t,n){}},[[1677,1,0]]]);
//# sourceMappingURL=bloxbergCertificate.chunk.js.map