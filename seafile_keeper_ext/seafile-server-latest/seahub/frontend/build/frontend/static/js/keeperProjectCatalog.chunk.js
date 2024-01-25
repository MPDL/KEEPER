(this["webpackJsonpseahub-frontend"]=this["webpackJsonpseahub-frontend"]||[]).push([[14],{1801:function(e,t,r){r(71),e.exports=r(1826)},1802:function(e,t,r){},1826:function(e,t,r){"use strict";r.r(t);var n=r(50),a=r(17),o=r(16),c=r(3),i=r(5),s=r(7),l=r(6),u=r(2),h=r.n(u),p=r(1054),d=r(1055),f=r(452),m=r(28),g=r.n(m),j=r(388),b=r(4),v=r(1),O=r(8),y=r(19),x=r(49),C=r(67),k=r(46),F=r(1053),w=r(123),S=r(108),P=r(109),D=r(1056),_=r(147),T=r(83),E=r(0),N=function(e){Object(s.a)(r,e);var t=Object(l.a)(r);function r(e){var n;Object(c.a)(this,r),(n=t.call(this,e)).getTerms=function(){var e=n.state.termsChecked,t=n.props.values.termEntries,r=Object.keys(t).sort((function(e,r){var n=t[e].length,a=t[r].length;return n==a?e.localeCompare(r):a-n}));return r.length>0&&e.length>0&&(r=r.filter((function(t){return!e.includes(t)}))),r},n.toggle=function(){n.props.toggleDialog()},n.setOrder=function(e){n.setState({order:e.target.value,isSubmitBtnActive:!0})},n.inputSearchTerm=function(e){n.setState({searchTerm:e.target.value})},n.handleCheckboxChange=function(e){var t=e.target.name;-1==n.state.termsChecked.indexOf(t)?n.addToTermsChecked(t):n.addToTerms(t),n.setState({isSubmitBtnActive:!0,searchTerm:""})},n.handleApply=function(){n.props.applyFacet(n.props.name,n.state.termsChecked,n.state.order),n.toggle()},n.handleCleanAll=function(){n.props.applyFacet(n.props.name,[],"asc"),n.toggle()},n.isTermInScope=function(e){var t=n.props.catalogScope||[];return 0==t.length||n.props.values.termEntries[e].some((function(e){return t.includes(e)}))},n.getTermFragment=function(e,t){var r=n.props.values.termEntries;return Object(E.jsx)(u.Fragment,{children:Object(E.jsx)(d.a,{className:"ml-5 mb-0",children:Object(E.jsxs)(F.a,{children:[Object(E.jsx)(f.a,{type:"checkbox",name:e,checked:n.isChecked(e),onChange:n.handleCheckboxChange}),e+" ("+r[e].length+")"]})})},"".concat(e,"~").concat(t))},n.getOrderFragment=function(e,t){return Object(E.jsx)(d.a,{check:!0,children:Object(E.jsxs)(F.a,{check:!0,children:[Object(E.jsx)(f.a,{type:"radio",name:"order",value:e,checked:n.state.order==e,onChange:n.setOrder,className:"mr-1"}),Object(v.pb)(t)]})})};var a=n.props.values;return n.state={errorMsg:"",searchTerm:"",isSubmitBtnActive:!1,order:a.order||"asc",termsChecked:Object(k.a)(a.termsChecked)||[]},n.state.terms=n.getTerms(),n}return Object(i.a)(r,[{key:"addToTermsChecked",value:function(e){var t=this;this.state.termsChecked.unshift(e),this.setState({termsChecked:this.state.termsChecked},(function(){t.setState({terms:t.getTerms()})}))}},{key:"addToTerms",value:function(e){var t=this,r=this.state.termsChecked;r=r.filter((function(t){return t!==e})),this.setState({termsChecked:r},(function(){t.setState({terms:t.getTerms()})}))}},{key:"isChecked",value:function(e){return-1!=this.state.termsChecked.indexOf(e)}},{key:"render",value:function(){var e=this,t=this.props,r=(t.dialogTitle,t.name),n=t.hasCatalogSearchTerm,a=this.state,o=a.errorMsg,c=a.searchTerm,i=a.termsChecked,s=a.terms,l=a.isSubmitBtnActive,u=n?s.filter((function(t){return e.isTermInScope(t)})):s;return Object(E.jsxs)(w.a,{isOpen:!0,toggle:this.toggle,children:[Object(E.jsx)(S.a,{toggle:this.toggle,children:Object(v.pb)("Select "+r.charAt(0).toUpperCase()+r.slice(1)+"(s)")}),Object(E.jsxs)(P.a,{children:[Object(E.jsxs)(p.a,{children:[this.getOrderFragment("asc","Ascending"),this.getOrderFragment("desc","Descending"),Object(E.jsx)(d.a,{className:"mt-3",children:Object(E.jsx)(f.a,{style:{width:"60%",height:"60%"},placeholder:Object(v.pb)("Search"),value:c,onChange:this.inputSearchTerm})}),i.map((function(t,r){return e.getTermFragment(t,r)})),u.filter((function(e){return"undefined"===typeof c||null===c||e&&e.toLowerCase().includes(c.toLowerCase())})).map((function(t,r){return r+i.length<30&&e.getTermFragment(t,r)})),u.length+i.length>=30&&Object(E.jsx)("div",{className:"ml-1",children:"..."})]}),o&&Object(E.jsx)(D.a,{color:"danger",children:o})]}),Object(E.jsxs)(_.a,{children:[Object(E.jsx)(T.a,{color:"primary",className:"w-9",onClick:this.handleApply,disabled:!l,children:Object(v.pb)("Apply")}),Object(E.jsx)(T.a,{className:"ml-4",color:"primary",onClick:this.handleCleanAll,children:Object(v.pb)("Reset")}),Object(E.jsx)(T.a,{className:"ml-4",color:"secondary",onClick:this.toggle,children:Object(v.pb)("Cancel")})]})]})}}]),r}(h.a.Component),A=(r(130),r(143),r(1802),window.app.pageOptions),I=(A.repoID,A.repoName,A.userPerm,{order:"asc",termEntries:{},termsChecked:[]}),R=function(e){Object(s.a)(r,e);var t=Object(l.a)(r);function r(e){var i;return Object(c.a)(this,r),(i=t.call(this,e)).doResetFacets=function(){i.state.facets={author:Object(o.a)({},I),year:Object(o.a)({},I),institute:Object(o.a)({},I),director:Object(o.a)({},I)}},i.calculateScopeFromFacets=function(){for(var e=i.state.facets,t=new Set,r=0,n=Object.keys(e);r<n.length;r++){var o=e[n[r]];if("termsChecked"in o&&o.termsChecked.length>0){var c,s=Object(a.a)(o.termsChecked);try{for(s.s();!(c=s.n()).done;){var l,u=c.value,h=Object(a.a)(o.termEntries[u]);try{for(h.s();!(l=h.n()).done;){var p=l.value;t.add(p)}}catch(d){h.e(d)}finally{h.f()}}}catch(d){s.e(d)}finally{s.f()}}}return Array.from(t)},i.updateFacets=function(e,t){for(var r={},n=0,a=Object.keys(e);n<a.length;n++){var c=a[n],s=i.state.facets[c].termEntries;r[c]=Object(o.a)(Object(o.a)({},i.state.facets[c]),{},{termEntries:0==Object.keys(s).length?e[c].termEntries:s,termsChecked:e[c].termsChecked})}return r},i.getItems=function(e,t){i.setHasTermsChecked();var r=i.state,n=i.state.facets,a=t?[]:i.calculateScopeFromFacets();O.a.getProjectCatalog(e,r.perPage,n.author,n.year,n.institute,n.director,a,r.searchTerm).then((function(t){var r=t.data;i.setState({isLoading:!1,currentPage:e,items:r.items,hasNextPage:r.more,catalogScope:r.scope,facets:i.updateFacets(r.facets),isAccessDenied:"is_access_denied"in r&&r.is_access_denied})})).catch((function(e){i.setState({isLoading:!1,errorMsg:b.a.getErrorMsg(e,!0)})}))},i.resetPerPage=function(e){i.setState({perPage:e},(function(){i.getItems(1,!1)}))},i._chk=function(e){return e&&"termsChecked"in e&&e.termsChecked.length>0},i.setHasTermsChecked=function(){var e=i.state.facets;i.setState({hasTermsChecked:i._chk(e.author)||i._chk(e.year)||i._chk(e.director)||i._chk(e.institute)})},i.applyFacet=function(e,t,r){i.setState({facets:Object(o.a)(Object(o.a)({},i.state.facets),{},Object(n.a)({},e,Object(o.a)(Object(o.a)({},i.state.facets[e]),{},{termsChecked:t,order:r})))},(function(){i.getItems(1,t&&0==t.length)}))},i.cleanAllFacets=function(){i.doResetFacets(),i.getItems(1,!0)},i.onSearchedClick=function(e){if(!0===e.is_dir){var t=v.qc+"library/"+e.repo_id+"/"+e.repo_name+e.path;Object(j.a)(t,{repalce:!0})}else{var r=v.qc+"lib/"+e.repo_id+"/file"+b.a.encodePath(e.path);window.open("about:blank").location.href=r}},i.toggleAuthorFacetDialog=function(){i.setState({isAuthorFacetDialogOpen:!i.state.isAuthorFacetDialogOpen})},i.toggleYearFacetDialog=function(){i.setState({isYearFacetDialogOpen:!i.state.isYearFacetDialogOpen})},i.toggleInstituteFacetDialog=function(){i.setState({isInstituteFacetDialogOpen:!i.state.isInstituteFacetDialogOpen})},i.toggleDirectorFacetDialog=function(){i.setState({isDirectorFacetDialogOpen:!i.state.isDirectorFacetDialogOpen})},i.inputSearchTerm=function(e){i.setState({searchTerm:e.target.value},(function(){i.getItems(1,!0)}))},i.getFacetFragment=function(e){var t=i.state.facets[e];return Object(E.jsxs)(u.Fragment,{children:[Object(E.jsx)("a",{href:"#",style:{color:"#575859",fontWeight:"lighter"},children:Object(v.pb)(e.charAt(0).toUpperCase()+e.slice(1))}),t.termsChecked.length>0&&Object(E.jsx)("i",{className:"ml-1 fa fa-arrow-"+("desc"==t.order?"up":"down")}),Object(E.jsx)("ul",{children:t.termsChecked.map((function(e,r){return e in t.termEntries&&Object(E.jsx)(u.Fragment,{children:Object(E.jsx)("li",{className:"ml-5 mb-0",children:e+(e in t.termEntries?" ("+t.termEntries[e].length+")":"")})},"".concat(e,"~").concat(r))}))})]})},i.state={isLoading:!0,errorMsg:"",currentPage:1,perPage:25,hasNextPage:!1,items:[],catalogScope:[],searchTerm:"",isAuthorFacetDialogOpen:!1,isYearFacetDialogOpen:!1,isInstituteFacetDialogOpen:!1,isDirectorFacetDialogOpen:!1,hasTermsChecked:!1},i.doResetFacets(),i}return Object(i.a)(r,[{key:"componentDidMount",value:function(){var e=this,t=new URL(window.location).searchParams,r=this.state,n=r.currentPage,a=r.perPage;this.setState({perPage:parseInt(t.get("per_page")||a),currentPage:parseInt(t.get("page")||n)},(function(){e.getItems(e.state.currentPage,!0)}));var o=document.createElement("script");o.src="https://static.zdassets.com/ekr/snippet.js?key=32977f9b-455d-428b-8dd5-f4c65aad0daa",o.id="ze-snippet",o.async=!0,document.body.appendChild(o)}},{key:"render",value:function(){var e=this,t=this.state,r=t.isAuthorFacetDialogOpen,n=t.isYearFacetDialogOpen,a=t.isInstituteFacetDialogOpen,o=t.isDirectorFacetDialogOpen,c=t.facets,i=t.searchTerm,s=Boolean(i&&""!=i.trim());return Object(E.jsxs)(u.Fragment,{children:[Object(E.jsxs)("div",{className:"h-100 d-flex flex-column",children:[Object(E.jsxs)("div",{className:"top-header d-flex justify-content-between",children:[Object(E.jsx)("a",{href:v.qc,children:Object(E.jsx)("img",{src:v.Nb+v.Ib,height:v.Hb,width:v.Jb,title:v.rc,alt:"logo"})}),Object(E.jsx)(C.a,{onSearchedClick:this.onSearchedClick})]}),Object(E.jsx)("div",{className:"flex-auto container-fluid pt-4 pb-6 o-auto",children:Object(E.jsx)("div",{className:"row",children:this.state.isAccessDenied?Object(E.jsx)("h3",{className:"offset-md-2 col-md-8 mt-9 text-center error",children:Object(v.pb)("Sie sind leider nicht berechtigt den Projektkatalog zu \xf6ffnen. Bitte wenden Sie sich an den Keeper Support.")}):Object(E.jsxs)("div",{className:"col-md-8 offset-md-2",children:[Object(E.jsx)("h3",{className:"d-flex offset-md-3",id:"header",children:Object(v.pb)("The KEEPER Project Catalog of the Max Planck Society")}),Object(E.jsxs)("div",{className:"row",children:[Object(E.jsxs)("div",{id:"facet",className:"col-md-3",children:[Object(E.jsxs)("h3",{style:{color:"#57a5b8",fontSize:"1.75em",fontWeight:500},children:[Object(v.pb)("Show Projects")," (",this.state.catalogScope.length,")"]}),Object(E.jsx)("div",{onClick:this.toggleAuthorFacetDialog,children:this.getFacetFragment("author")}),Object(E.jsx)("div",{onClick:this.toggleYearFacetDialog,children:this.getFacetFragment("year")}),Object(E.jsx)("div",{onClick:this.toggleInstituteFacetDialog,children:this.getFacetFragment("institute")}),Object(E.jsx)("div",{onClick:this.toggleDirectorFacetDialog,children:this.getFacetFragment("director")}),this.state.hasTermsChecked&&Object(E.jsx)("div",{className:"mt-1",children:Object(E.jsx)("a",{href:"#",onClick:this.cleanAllFacets,children:Object(v.pb)("Reset all")})})]}),Object(E.jsxs)("div",{className:"col-md-9",children:[Object(E.jsx)(p.a,{children:Object(E.jsx)(d.a,{children:Object(E.jsx)(f.a,{type:"search",style:{height:"60%"},placeholder:Object(v.pb)("Search")+"...",value:this.state.searchTerm,onChange:this.inputSearchTerm})})}),Object(E.jsx)(L,{isLoading:this.state.isLoading,errorMsg:this.state.errorMsg,items:this.state.items})]})]}),Object(E.jsx)("div",{className:"row justify-content-center",children:Object(E.jsx)(x.a,{gotoPreviousPage:function(){e.getItems(e.state.currentPage-1,!1)},gotoNextPage:function(){e.getItems(e.state.currentPage+1,!1)},currentPage:this.state.currentPage,hasNextPage:this.state.hasNextPage,curPerPage:this.state.perPage,resetPerPage:this.resetPerPage})}),Object(E.jsx)(U,{})]})})})]}),r&&Object(E.jsx)(N,{name:"author",values:c.author,hasCatalogSearchTerm:s,catalogScope:this.state.catalogScope,toggleDialog:this.toggleAuthorFacetDialog,applyFacet:this.applyFacet}),n&&Object(E.jsx)(N,{name:"year",values:c.year,hasCatalogSearchTerm:s,catalogScope:this.state.catalogScope,toggleDialog:this.toggleYearFacetDialog,applyFacet:this.applyFacet}),a&&Object(E.jsx)(N,{name:"institute",values:c.institute,hasCatalogSearchTerm:s,catalogScope:this.state.catalogScope,toggleDialog:this.toggleInstituteFacetDialog,applyFacet:this.applyFacet}),o&&Object(E.jsx)(N,{name:"director",values:c.director,hasCatalogSearchTerm:s,catalogScope:this.state.catalogScope,toggleDialog:this.toggleDirectorFacetDialog,applyFacet:this.applyFacet})]})}}]),r}(h.a.Component),L=function(e){Object(s.a)(r,e);var t=Object(l.a)(r);function r(){return Object(c.a)(this,r),t.apply(this,arguments)}return Object(i.a)(r,[{key:"render",value:function(){var e=this.props,t=e.isLoading,r=e.errorMsg,n=e.items;return t?Object(E.jsx)(y.a,{}):r?Object(E.jsx)("p",{className:"error mt-6 text-center",children:r}):Object(E.jsx)(u.Fragment,{children:n.map((function(e,t){return Object(E.jsx)(M,{item:e},t)}))})}}]),r}(h.a.Component),M=function(e){Object(s.a)(r,e);var t=Object(l.a)(r);function r(e){var n;return Object(c.a)(this,r),(n=t.call(this,e)).toggleDescription=function(){n.setState({descExpanded:!n.state.descExpanded})},n.toTitleCase=function(e){return e.replace(/([^\W_]+[^\s-]*) */g,(function(e){return e.charAt(0).toUpperCase()+e.substr(1).toLowerCase()}))},n.getAuthors=function(e){var t=[];if("authors"in e&&e.authors.length>0)for(var r=e.authors,a=0;a<r.length;a++){for(var o="",c=n.toTitleCase(r[a].name).split(", "),i=0;i<c.length;i++)0==i&&c[i].trim().length?o+=c[i]+", ":c[i].trim().length>1&&(o+=c[i].trim().charAt(0)+"., ");if(o=o.trim().slice(0,-1),a>=5&&(o="et al."),t.push(o),a>=5)break;"affs"in r[a]&&t.push(n.toTitleCase(r[a].affs.join(", ")))}return t.join("; ")},n.getDirectors=function(e){var t=e.split("|").map((function(e){return e.trim()})).filter((function(e){return e.length>0}));return t.length>0?t.join("; "):null},n.instituteFragment=function(e){var t=e.split(";").map((function(e){return e.trim()})).filter((function(e){return e.length>0}));if(t&&t.length&&t.length>0){t.length>=3&&n.getDirectors(t[2]);return Object(E.jsxs)(u.Fragment,{children:[t[0]&&Object(E.jsx)("p",{children:Object(v.pb)("Institute")+": "+t[0]}),t[1]&&Object(E.jsx)("p",{children:Object(v.pb)("Department")+": "+t[1]})]})}},n.state={descExpanded:!1},n}return Object(i.a)(r,[{key:"render",value:function(){var e=this.props.item,t=e.description&&e.description.length>500;return Object(E.jsx)(u.Fragment,{children:Object(E.jsx)("div",{className:"item-block",id:e.repo_id,children:Object(E.jsxs)("div",{className:"row",children:[Object(E.jsx)("div",{className:"col-md-1",children:e.is_certified&&Object(E.jsx)("img",{src:"/media/custom/certified.png"})}),Object(E.jsxs)("div",{className:"col-md-11",children:[Object(E.jsx)("h3",{children:e.landing_page_url?Object(E.jsx)("a",{href:"/landing-page/libs/"+e.repo_id+"/",children:e.title}):e.title||Object(v.pb)("Project archive no.")+": "+e.catalog_id}),e.description&&Object(E.jsxs)("p",{children:[t?this.state.descExpanded?e.description:e.description.substring(0,496)+"...":e.description,t&&Object(E.jsx)("i",{onClick:this.toggleDescription,className:"keeper-icon-triangle-"+(this.state.descExpanded?"up":"down")})]}),e.authors&&Object(E.jsx)("p",{children:this.getAuthors(e)}),e.year&&Object(E.jsx)("p",{children:Object(v.pb)("Year")+": "+e.year}),e.institute&&this.instituteFragment(e.institute),e.owner&&Object(E.jsx)("p",{children:Object(v.pb)("Contact")+": "+e.owner.toLowerCase()}),e.landing_page_url&&Object(E.jsx)("p",{children:Object(E.jsx)("a",{href:"/landing-page/libs/"+e.repo_id+"/",children:Object(v.pb)("Landing Page")})})]})]})})})}}]),r}(h.a.Component),U=function(e){Object(s.a)(r,e);var t=Object(l.a)(r);function r(){return Object(c.a)(this,r),t.apply(this,arguments)}return Object(i.a)(r,[{key:"render",value:function(){return Object(E.jsx)(u.Fragment,{children:Object(E.jsx)("div",{id:"lg_footer",children:Object(E.jsxs)("div",{className:"container",children:[Object(E.jsxs)("div",{id:"keeper-links",className:"row",children:[Object(E.jsxs)("div",{className:"col-md-3",children:[Object(E.jsx)("h4",{children:"Be informed"}),Object(E.jsx)("a",{href:"https://keeper.mpdl.mpg.de/f/d17ecbb967/",target:"_blank",children:"About Keeper"}),Object(E.jsx)("br",{}),Object(E.jsx)("a",{href:"https://keeper.mpdl.mpg.de/f/1b0bfceac2/",target:"_blank",children:"Cared Data Commitment"}),Object(E.jsx)("br",{}),Object(E.jsx)("a",{href:"/project-catalog",target:"_blank",children:"Project Catalog"}),Object(E.jsx)("br",{})]}),Object(E.jsxs)("div",{className:"col-md-3",children:[Object(E.jsx)("h4",{children:"Get the desktop sync client"}),Object(E.jsx)("a",{href:"/download_client_program/",target:"_blank",children:"Download the Keeper client for Windows, Linux and Mac"})]}),Object(E.jsxs)("div",{className:"col-md-3",children:[Object(E.jsx)("h4",{children:"Find help"}),Object(E.jsx)("a",{href:"mailto:keeper@mpdl.mpg.de",children:"Contact Keeper Support"})," ",Object(E.jsx)("br",{}),Object(E.jsx)("a",{href:"https://mpdl.zendesk.com/hc/en-us/categories/360001234340-Keeper",target:"_blank",children:"Help / Knowledge Base"})]}),Object(E.jsxs)("div",{className:"col-md-3",children:[Object(E.jsx)("h4",{children:"Check terms"}),Object(E.jsx)("a",{href:"https://keeper.mpdl.mpg.de/f/2206ad0c0a8346cb8f9e/",target:"_blank",children:"Terms of Services"})," ",Object(E.jsx)("br",{}),Object(E.jsx)("a",{href:"https://keeper.mpdl.mpg.de/f/17e4e9d648/",target:"_blank",children:"Disclaimer"}),Object(E.jsx)("br",{}),Object(E.jsx)("a",{href:"https://keeper.mpdl.mpg.de/f/bf2c8a977f70428587eb/",target:"_blank",children:"Privacy Policy"})]})]}),Object(E.jsx)("div",{id:"seafile-credits",className:"row",children:Object(E.jsx)("div",{className:"col-md-12 text-center",children:Object(E.jsx)("div",{children:Object(E.jsxs)("a",{href:"https://www.seafile.com/en/home/",target:"_blank",children:["The software behind Keeper"," ",Object(E.jsx)("img",{id:"seafile-logo",src:"/media/custom/seafile_logo_footer.png",height:"35"}),"\xa9 2024 Seafile"]})})})})]})})})}}]),r}(h.a.Component);g.a.render(Object(E.jsx)(R,{}),document.getElementById("wrapper"))},385:function(e,t,r){"use strict";t.__esModule=!0;var n=o(r(2)),a=o(r(700));function o(e){return e&&e.__esModule?e:{default:e}}t.default=n.default.createContext||a.default,e.exports=t.default},388:function(e,t,r){"use strict";r.d(t,"a",(function(){return w}));var n=r(2),a=r.n(n),o=r(89),c=r.n(o),i=r(385),s=r.n(i),l=r(117),u=function(e,t){return e.substr(0,t.length)===t},h=function(e,t){for(var r=void 0,n=void 0,a=t.split("?")[0],o=v(a),i=""===o[0],s=b(e),l=0,u=s.length;l<u;l++){var h=!1,p=s[l].route;if(p.default)n={route:p,params:{},uri:t};else{for(var d=v(p.path),m={},j=Math.max(o.length,d.length),O=0;O<j;O++){var x=d[O],C=o[O];if(g(x)){m[x.slice(1)||"*"]=o.slice(O).map(decodeURIComponent).join("/");break}if(void 0===C){h=!0;break}var k=f.exec(x);if(k&&!i){-1===y.indexOf(k[1])||c()(!1);var F=decodeURIComponent(C);m[k[1]]=F}else if(x!==C){h=!0;break}}if(!h){r={route:p,params:m,uri:"/"+o.slice(0,O).join("/")};break}}}return r||n||null},p=function(e,t){if(u(e,"/"))return e;var r=e.split("?"),n=r[0],a=r[1],o=t.split("?")[0],c=v(n),i=v(o);if(""===c[0])return O(o,a);if(!u(c[0],".")){var s=i.concat(c).join("/");return O(("/"===o?"":"/")+s,a)}for(var l=i.concat(c),h=[],p=0,d=l.length;p<d;p++){var f=l[p];".."===f?h.pop():"."!==f&&h.push(f)}return O("/"+h.join("/"),a)},d=function(e,t){var r=e.split("?"),n=r[0],a=r[1],o=void 0===a?"":a,c="/"+v(n).map((function(e){var r=f.exec(e);return r?t[r[1]]:e})).join("/"),i=t.location,s=(i=void 0===i?{}:i).search,l=(void 0===s?"":s).split("?")[1]||"";return c=O(c,o,l)},f=/^:(.+)/,m=function(e){return f.test(e)},g=function(e){return e&&"*"===e[0]},j=function(e,t){return{route:e,score:e.default?0:v(e.path).reduce((function(e,t){return e+=4,!function(e){return""===e}(t)?m(t)?e+=2:g(t)?e-=5:e+=3:e+=1,e}),0),index:t}},b=function(e){return e.map(j).sort((function(e,t){return e.score<t.score?1:e.score>t.score?-1:e.index-t.index}))},v=function(e){return e.replace(/(^\/+|\/+$)/g,"").split("/")},O=function(e){for(var t=arguments.length,r=Array(t>1?t-1:0),n=1;n<t;n++)r[n-1]=arguments[n];return e+((r=r.filter((function(e){return e&&e.length>0})))&&r.length>0?"?"+r.join("&"):"")},y=["uri","path"],x=Object.assign||function(e){for(var t=1;t<arguments.length;t++){var r=arguments[t];for(var n in r)Object.prototype.hasOwnProperty.call(r,n)&&(e[n]=r[n])}return e},C=function(e){var t=e.location,r=t.search,n=t.hash,a=t.href,o=t.origin,c=t.protocol,i=t.host,s=t.hostname,l=t.port,u=e.location.pathname;!u&&a&&k&&(u=new URL(a).pathname);return{pathname:encodeURI(decodeURI(u)),search:r,hash:n,href:a,origin:o,protocol:c,host:i,hostname:s,port:l,state:e.history.state,key:e.history.state&&e.history.state.key||"initial"}},k=!("undefined"===typeof window||!window.document||!window.document.createElement),F=function(e,t){var r=[],n=C(e),a=!1,o=function(){};return{get location(){return n},get transitioning(){return a},_onTransitionComplete:function(){a=!1,o()},listen:function(t){r.push(t);var a=function(){n=C(e),t({location:n,action:"POP"})};return e.addEventListener("popstate",a),function(){e.removeEventListener("popstate",a),r=r.filter((function(e){return e!==t}))}},navigate:function(t){var c=arguments.length>1&&void 0!==arguments[1]?arguments[1]:{},i=c.state,s=c.replace,l=void 0!==s&&s;if("number"===typeof t)e.history.go(t);else{i=x({},i,{key:Date.now()+""});try{a||l?e.history.replaceState(i,null,t):e.history.pushState(i,null,t)}catch(h){e.location[l?"replace":"assign"](t)}}n=C(e),a=!0;var u=new Promise((function(e){return o=e}));return r.forEach((function(e){return e({location:n,action:"PUSH"})})),u}}}(k?window:function(){var e=arguments.length>0&&void 0!==arguments[0]?arguments[0]:"/",t=e.indexOf("?"),r={pathname:t>-1?e.substr(0,t):e,search:t>-1?e.substr(t):""},n=0,a=[r],o=[null];return{get location(){return a[n]},addEventListener:function(e,t){},removeEventListener:function(e,t){},history:{get entries(){return a},get index(){return n},get state(){return o[n]},pushState:function(e,t,r){var c=r.split("?"),i=c[0],s=c[1],l=void 0===s?"":s;n++,a.push({pathname:i,search:l.length?"?"+l:l}),o.push(e)},replaceState:function(e,t,r){var c=r.split("?"),i=c[0],s=c[1],l=void 0===s?"":s;a[n]={pathname:i,search:l},o[n]=e},go:function(e){var t=n+e;t<0||t>o.length-1||(n=t)}}}}()),w=F.navigate,S=Object.assign||function(e){for(var t=1;t<arguments.length;t++){var r=arguments[t];for(var n in r)Object.prototype.hasOwnProperty.call(r,n)&&(e[n]=r[n])}return e};function P(e,t){var r={};for(var n in e)t.indexOf(n)>=0||Object.prototype.hasOwnProperty.call(e,n)&&(r[n]=e[n]);return r}function D(e,t){if(!(e instanceof t))throw new TypeError("Cannot call a class as a function")}function _(e,t){if(!e)throw new ReferenceError("this hasn't been initialised - super() hasn't been called");return!t||"object"!==typeof t&&"function"!==typeof t?e:t}function T(e,t){if("function"!==typeof t&&null!==t)throw new TypeError("Super expression must either be null or a function, not "+typeof t);e.prototype=Object.create(t&&t.prototype,{constructor:{value:e,enumerable:!1,writable:!0,configurable:!0}}),t&&(Object.setPrototypeOf?Object.setPrototypeOf(e,t):e.__proto__=t)}var E=function(e,t){var r=s()(t);return r.displayName=e,r},N=E("Location"),A=function(e){var t=e.children;return a.a.createElement(N.Consumer,null,(function(e){return e?t(e):a.a.createElement(I,null,t)}))},I=function(e){function t(){var r,n;D(this,t);for(var a=arguments.length,o=Array(a),c=0;c<a;c++)o[c]=arguments[c];return r=n=_(this,e.call.apply(e,[this].concat(o))),n.state={context:n.getContext(),refs:{unlisten:null}},_(n,r)}return T(t,e),t.prototype.getContext=function(){var e=this.props.history;return{navigate:e.navigate,location:e.location}},t.prototype.componentDidCatch=function(e,t){if(!J(e))throw e;(0,this.props.history.navigate)(e.uri,{replace:!0})},t.prototype.componentDidUpdate=function(e,t){t.context.location!==this.state.context.location&&this.props.history._onTransitionComplete()},t.prototype.componentDidMount=function(){var e=this,t=this.state.refs,r=this.props.history;r._onTransitionComplete(),t.unlisten=r.listen((function(){Promise.resolve().then((function(){requestAnimationFrame((function(){e.unmounted||e.setState((function(){return{context:e.getContext()}}))}))}))}))},t.prototype.componentWillUnmount=function(){var e=this.state.refs;this.unmounted=!0,e.unlisten()},t.prototype.render=function(){var e=this.state.context,t=this.props.children;return a.a.createElement(N.Provider,{value:e},"function"===typeof t?t(e):t||null)},t}(a.a.Component);I.defaultProps={history:F};var R=E("Base",{baseuri:"/",basepath:"/"}),L=function(e){return a.a.createElement(R.Consumer,null,(function(t){return a.a.createElement(A,null,(function(r){return a.a.createElement(M,S({},t,r,e))}))}))},M=function(e){function t(){return D(this,t),_(this,e.apply(this,arguments))}return T(t,e),t.prototype.render=function(){var e=this.props,t=e.location,r=e.navigate,n=e.basepath,o=e.primary,c=e.children,i=(e.baseuri,e.component),s=void 0===i?"div":i,l=P(e,["location","navigate","basepath","primary","children","baseuri","component"]),u=a.a.Children.toArray(c).reduce((function(e,t){var r=Q(n)(t);return e.concat(r)}),[]),d=t.pathname,f=h(u,d);if(f){var m=f.params,g=f.uri,j=f.route,b=f.route.value;n=j.default?n:j.path.replace(/\*$/,"");var v=S({},m,{uri:g,location:t,navigate:function(e,t){return r(p(e,g),t)}}),O=a.a.cloneElement(b,v,b.props.children?a.a.createElement(L,{location:t,primary:o},b.props.children):void 0),y=o?B:s,x=o?S({uri:g,location:t,component:s},l):l;return a.a.createElement(R.Provider,{value:{baseuri:g,basepath:n}},a.a.createElement(y,x,O))}return null},t}(a.a.PureComponent);M.defaultProps={primary:!0};var U=E("Focus"),B=function(e){var t=e.uri,r=e.location,n=e.component,o=P(e,["uri","location","component"]);return a.a.createElement(U.Consumer,null,(function(e){return a.a.createElement(W,S({},o,{component:n,requestFocus:e,uri:t,location:r}))}))},K=!0,q=0,W=function(e){function t(){var r,n;D(this,t);for(var a=arguments.length,o=Array(a),c=0;c<a;c++)o[c]=arguments[c];return r=n=_(this,e.call.apply(e,[this].concat(o))),n.state={},n.requestFocus=function(e){!n.state.shouldFocus&&e&&e.focus()},_(n,r)}return T(t,e),t.getDerivedStateFromProps=function(e,t){if(null==t.uri)return S({shouldFocus:!0},e);var r=e.uri!==t.uri,n=t.location.pathname!==e.location.pathname&&e.location.pathname===e.uri;return S({shouldFocus:r||n},e)},t.prototype.componentDidMount=function(){q++,this.focus()},t.prototype.componentWillUnmount=function(){0===--q&&(K=!0)},t.prototype.componentDidUpdate=function(e,t){e.location!==this.props.location&&this.state.shouldFocus&&this.focus()},t.prototype.focus=function(){var e=this.props.requestFocus;e?e(this.node):K?K=!1:this.node&&(this.node.contains(document.activeElement)||this.node.focus())},t.prototype.render=function(){var e=this,t=this.props,r=(t.children,t.style),n=(t.requestFocus,t.component),o=void 0===n?"div":n,c=(t.uri,t.location,P(t,["children","style","requestFocus","component","uri","location"]));return a.a.createElement(o,S({style:S({outline:"none"},r),tabIndex:"-1",ref:function(t){return e.node=t}},c),a.a.createElement(U.Provider,{value:this.requestFocus},this.props.children))},t}(a.a.Component);Object(l.polyfill)(W);var Y=function(){},z=a.a.forwardRef;function H(e){this.uri=e}"undefined"===typeof z&&(z=function(e){return e}),z((function(e,t){var r=e.innerRef,n=P(e,["innerRef"]);return a.a.createElement(R.Consumer,null,(function(e){e.basepath;var o=e.baseuri;return a.a.createElement(A,null,(function(e){var c=e.location,i=e.navigate,s=n.to,l=n.state,h=n.replace,d=n.getProps,f=void 0===d?Y:d,m=P(n,["to","state","replace","getProps"]),g=p(s,o),j=encodeURI(g),b=c.pathname===j,v=u(c.pathname,j);return a.a.createElement("a",S({ref:t||r,"aria-current":b?"page":void 0},m,f({isCurrent:b,isPartiallyCurrent:v,href:g,location:c}),{href:g,onClick:function(e){if(m.onClick&&m.onClick(e),X(e)){e.preventDefault();var t=h;if("boolean"!==typeof h&&b){var r=S({},c.state),n=(r.key,P(r,["key"]));t=function(e,t){var r=Object.keys(e);return r.length===Object.keys(t).length&&r.every((function(r){return t.hasOwnProperty(r)&&e[r]===t[r]}))}(S({},l),n)}i(g,{state:l,replace:t})}}}))}))}))})).displayName="Link";var J=function(e){return e instanceof H},V=function(e){function t(){return D(this,t),_(this,e.apply(this,arguments))}return T(t,e),t.prototype.componentDidMount=function(){var e=this.props,t=e.navigate,r=e.to,n=(e.from,e.replace),a=void 0===n||n,o=e.state,c=(e.noThrow,e.baseuri),i=P(e,["navigate","to","from","replace","state","noThrow","baseuri"]);Promise.resolve().then((function(){var e=p(r,c);t(d(e,i),{replace:a,state:o})}))},t.prototype.render=function(){var e=this.props,t=(e.navigate,e.to),r=(e.from,e.replace,e.state,e.noThrow),n=e.baseuri,a=P(e,["navigate","to","from","replace","state","noThrow","baseuri"]),o=p(t,n);return r||function(e){throw new H(e)}(d(o,a)),null},t}(a.a.Component),$=function(e){return a.a.createElement(R.Consumer,null,(function(t){var r=t.baseuri;return a.a.createElement(A,null,(function(t){return a.a.createElement(V,S({},t,{baseuri:r},e))}))}))},G=function(e){return e.replace(/(^\/+|\/+$)/g,"")},Q=function e(t){return function(r){if(!r)return null;if(r.type===a.a.Fragment&&r.props.children)return a.a.Children.map(r.props.children,e(t));if(r.props.path||r.props.default||r.type===$||c()(!1),r.type!==$||r.props.from&&r.props.to||c()(!1),r.type!==$||function(e,t){var r=function(e){return m(e)};return v(e).filter(r).sort().join("/")===v(t).filter(r).sort().join("/")}(r.props.from,r.props.to)||c()(!1),r.props.default)return{value:r,default:!0};var n=r.type===$?r.props.from:r.props.path,o="/"===n?t:G(t)+"/"+G(n);return{value:r,default:r.props.default,path:r.props.children?G(o)+"/*":o}}},X=function(e){return!e.defaultPrevented&&0===e.button&&!(e.metaKey||e.altKey||e.ctrlKey||e.shiftKey)}},700:function(e,t,r){"use strict";t.__esModule=!0;var n=r(2),a=(c(n),c(r(9))),o=c(r(501));c(r(286));function c(e){return e&&e.__esModule?e:{default:e}}function i(e,t){if(!(e instanceof t))throw new TypeError("Cannot call a class as a function")}function s(e,t){if(!e)throw new ReferenceError("this hasn't been initialised - super() hasn't been called");return!t||"object"!==typeof t&&"function"!==typeof t?e:t}function l(e,t){if("function"!==typeof t&&null!==t)throw new TypeError("Super expression must either be null or a function, not "+typeof t);e.prototype=Object.create(t&&t.prototype,{constructor:{value:e,enumerable:!1,writable:!0,configurable:!0}}),t&&(Object.setPrototypeOf?Object.setPrototypeOf(e,t):e.__proto__=t)}var u=1073741823;function h(e){var t=[];return{on:function(e){t.push(e)},off:function(e){t=t.filter((function(t){return t!==e}))},get:function(){return e},set:function(r,n){e=r,t.forEach((function(t){return t(e,n)}))}}}t.default=function(e,t){var r,c,p="__create-react-context-"+(0,o.default)()+"__",d=function(e){function r(){var t,n;i(this,r);for(var a=arguments.length,o=Array(a),c=0;c<a;c++)o[c]=arguments[c];return t=n=s(this,e.call.apply(e,[this].concat(o))),n.emitter=h(n.props.value),s(n,t)}return l(r,e),r.prototype.getChildContext=function(){var e;return(e={})[p]=this.emitter,e},r.prototype.componentWillReceiveProps=function(e){if(this.props.value!==e.value){var r=this.props.value,n=e.value,a=void 0;((o=r)===(c=n)?0!==o||1/o===1/c:o!==o&&c!==c)?a=0:(a="function"===typeof t?t(r,n):u,0!==(a|=0)&&this.emitter.set(e.value,a))}var o,c},r.prototype.render=function(){return this.props.children},r}(n.Component);d.childContextTypes=((r={})[p]=a.default.object.isRequired,r);var f=function(t){function r(){var e,n;i(this,r);for(var a=arguments.length,o=Array(a),c=0;c<a;c++)o[c]=arguments[c];return e=n=s(this,t.call.apply(t,[this].concat(o))),n.state={value:n.getValue()},n.onUpdate=function(e,t){0!==((0|n.observedBits)&t)&&n.setState({value:n.getValue()})},s(n,e)}return l(r,t),r.prototype.componentWillReceiveProps=function(e){var t=e.observedBits;this.observedBits=void 0===t||null===t?u:t},r.prototype.componentDidMount=function(){this.context[p]&&this.context[p].on(this.onUpdate);var e=this.props.observedBits;this.observedBits=void 0===e||null===e?u:e},r.prototype.componentWillUnmount=function(){this.context[p]&&this.context[p].off(this.onUpdate)},r.prototype.getValue=function(){return this.context[p]?this.context[p].get():e},r.prototype.render=function(){return(e=this.props.children,Array.isArray(e)?e[0]:e)(this.state.value);var e},r}(n.Component);return f.contextTypes=((c={})[p]=a.default.object,c),{Provider:d,Consumer:f}},e.exports=t.default}},[[1801,1,0]]]);
//# sourceMappingURL=keeperProjectCatalog.chunk.js.map