(this["webpackJsonpseahub-frontend"]=this["webpackJsonpseahub-frontend"]||[]).push([[34],{1548:function(e,t,a){a(48),e.exports=a(1549)},1549:function(e,t,a){"use strict";a.r(t);var r=a(6),n=a(7),s=a(9),i=a(8),c=a(2),o=a.n(c),g=a(20),h=a.n(g),l=a(15),b=a(5),d=a(1),u=a(10),j=a(14),p=a(30),P=a(46),f=a(376),m=(a(97),a(107),a(1555),a(0)),x=function(e){Object(s.a)(a,e);var t=Object(i.a)(a);function a(e){var n;return Object(r.a)(this,a),(n=t.call(this,e)).getItems=function(e){var t=n.state.perPage;u.b.listNotifications(e,t).then((function(a){n.setState({isLoading:!1,items:a.data.notification_list,currentPage:e,hasNextPage:b.a.hasNextPage(e,t,a.data.count)})})).catch((function(e){n.setState({isLoading:!1,errorMsg:b.a.getErrorMsg(e,!0)})}))},n.resetPerPage=function(e){n.setState({perPage:e},(function(){n.getItems(1)}))},n.onSearchedClick=function(e){if(!0===e.is_dir){var t=d.mc+"library/"+e.repo_id+"/"+e.repo_name+e.path;Object(l.c)(t,{repalce:!0})}else{var a=d.mc+"lib/"+e.repo_id+"/file"+b.a.encodePath(e.path);window.open("about:blank").location.href=a}},n.markAllRead=function(){u.b.updateNotifications().then((function(e){n.setState({items:n.state.items.map((function(e){return e.seen=!0,e}))})})).catch((function(e){n.setState({isLoading:!1,errorMsg:b.a.getErrorMsg(e,!0)})}))},n.clearAll=function(){u.b.deleteNotifications().then((function(e){n.setState({items:[]})})).catch((function(e){n.setState({isLoading:!1,errorMsg:b.a.getErrorMsg(e,!0)})}))},n.state={isLoading:!0,errorMsg:"",currentPage:1,perPage:25,hasNextPage:!1,items:[]},n}return Object(n.a)(a,[{key:"componentDidMount",value:function(){var e=this,t=new URL(window.location).searchParams,a=this.state,r=a.currentPage,n=a.perPage;this.setState({perPage:parseInt(t.get("per_page")||n),currentPage:parseInt(t.get("page")||r)},(function(){e.getItems(e.state.currentPage)}))}},{key:"render",value:function(){return Object(m.jsx)(o.a.Fragment,{children:Object(m.jsxs)("div",{className:"h-100 d-flex flex-column",children:[Object(m.jsxs)("div",{className:"top-header d-flex justify-content-between",children:[Object(m.jsx)("a",{href:d.mc,children:Object(m.jsx)("img",{src:d.Lb+d.Gb,height:d.Fb,width:d.Hb,title:d.nc,alt:"logo"})}),Object(m.jsx)(P.a,{onSearchedClick:this.onSearchedClick})]}),Object(m.jsx)("div",{className:"flex-auto container-fluid pt-4 pb-6 o-auto",children:Object(m.jsx)("div",{className:"row",children:Object(m.jsxs)("div",{className:"col-md-10 offset-md-1",children:[Object(m.jsxs)("div",{className:"d-flex justify-content-between align-items-center flex-wrap op-bar",children:[Object(m.jsx)("h2",{className:"h4 m-0 my-1",children:Object(d.nb)("Notifications")}),Object(m.jsxs)("div",{children:[Object(m.jsx)("button",{className:"btn btn-secondary op-bar-btn",onClick:this.markAllRead,children:Object(d.nb)("Mark all read")}),Object(m.jsx)("button",{className:"btn btn-secondary op-bar-btn ml-2",onClick:this.clearAll,children:Object(d.nb)("Clear")})]})]}),Object(m.jsx)(O,{isLoading:this.state.isLoading,errorMsg:this.state.errorMsg,items:this.state.items,currentPage:this.state.currentPage,hasNextPage:this.state.hasNextPage,curPerPage:this.state.perPage,resetPerPage:this.resetPerPage,getListByPage:this.getItems})]})})})]})})}}]),a}(o.a.Component),O=function(e){Object(s.a)(a,e);var t=Object(i.a)(a);function a(e){var n;return Object(r.a)(this,a),(n=t.call(this,e)).getPreviousPage=function(){n.props.getListByPage(n.props.currentPage-1)},n.getNextPage=function(){n.props.getListByPage(n.props.currentPage+1)},n}return Object(n.a)(a,[{key:"render",value:function(){var e=this.props,t=e.isLoading,a=e.errorMsg,r=e.items,n=e.curPerPage,s=e.currentPage,i=e.hasNextPage;if(t)return Object(m.jsx)(j.a,{});if(a)return Object(m.jsx)("p",{className:"error mt-6 text-center",children:a});var c=b.a.isDesktop()?[{width:"7%",text:""},{width:"73%",text:Object(d.nb)("Message")},{width:"20%",text:Object(d.nb)("Time")}]:[{width:"15%",text:""},{width:"52%",text:Object(d.nb)("Message")},{width:"33%",text:Object(d.nb)("Time")}];return Object(m.jsxs)(o.a.Fragment,{children:[Object(m.jsxs)("table",{className:"table-hover",children:[Object(m.jsx)("thead",{children:Object(m.jsx)("tr",{children:c.map((function(e,t){return Object(m.jsx)("th",{width:e.width,children:e.text},t)}))})}),Object(m.jsx)("tbody",{children:r.map((function(e,t){return Object(m.jsx)(f.a,{noticeItem:e,tr:!0},t)}))})]}),r.length>0&&Object(m.jsx)(p.a,{gotoPreviousPage:this.getPreviousPage,gotoNextPage:this.getNextPage,currentPage:s,hasNextPage:i,curPerPage:n,resetPerPage:this.props.resetPerPage})]})}}]),a}(o.a.Component);h.a.render(Object(m.jsx)(x,{}),document.getElementById("wrapper"))},1555:function(e,t,a){}},[[1548,1,0]]]);
//# sourceMappingURL=userNotifications.chunk.js.map