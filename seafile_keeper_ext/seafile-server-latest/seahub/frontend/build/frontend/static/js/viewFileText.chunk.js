(this["webpackJsonpseahub-frontend"]=this["webpackJsonpseahub-frontend"]||[]).push([[37],{1650:function(t,e,n){n(48),t.exports=n(1651)},1651:function(t,e,n){"use strict";n.r(e);var a=n(6),i=n(7),s=n(22),c=n(9),r=n(8),o=n(2),p=n.n(o),u=n(20),d=n.n(u),h=n(11),l=n(5),v=n(1),f=n(161),b=n(131),j=n(10),g=n(253),S=n.n(g),O=(n(236),n(199),n(368),n(485),n(486),n(487),n(227),n(488),n(489),n(297),n(357),n(490),n(0)),P=window.app.pageOptions,m=P.err,x=P.fileExt,C=P.fileContent,y=P.repoID,k=P.filePath,w=P.fileName,F=P.canEditFile,E=P.username,N={lineNumbers:!0,mode:l.a.chooseLanguage(x),extraKeys:{Ctrl:"autocomplete"},theme:"default",textWrapping:!0,lineWrapping:!0,readOnly:!F,cursorBlinkRate:F?530:-1},B=function(t){Object(c.a)(n,t);var e=Object(r.a)(n);function n(t){var i;return Object(a.a)(this,n),(i=e.call(this,t)).updateContent=function(t){i.setState({needSave:!0,content:t})},i.addParticipant=function(){j.b.addFileParticipants(y,k,[E]).then((function(t){200===t.status&&(i.isParticipant=!0,i.getParticipants())}))},i.getParticipants=function(){j.b.listFileParticipants(y,k).then((function(t){var e=t.data.participant_list;i.setState({participants:e}),e.length>0&&(i.isParticipant=e.every((function(t){return t.email==E})))}))},i.onParticipantsChange=function(){i.getParticipants()},i.state={content:C,needSave:!1,isSaving:!1,participants:[]},i.onSave=i.onSave.bind(Object(s.a)(i)),i.isParticipant=!1,i}return Object(i.a)(n,[{key:"onSave",value:function(){var t=this;this.isParticipant||this.addParticipant();return j.b.getUpdateLink(y,"/").then((function(e){var n=e.data;return t.setState({isSaving:!0}),j.b.updateFile(n,k,w,t.state.content).then((function(){h.a.success(Object(v.nb)("Successfully saved"),{duration:2}),t.setState({isSaving:!1,needSave:!1})}))}))}},{key:"componentDidMount",value:function(){this.getParticipants()}},{key:"render",value:function(){return Object(O.jsx)(f.a,{content:Object(O.jsx)(D,{content:this.state.content,updateContent:this.updateContent}),isSaving:this.state.isSaving,needSave:this.state.needSave,onSave:this.onSave,participants:this.state.participants,onParticipantsChange:this.onParticipantsChange})}}]),n}(p.a.Component),D=function(t){Object(c.a)(n,t);var e=Object(r.a)(n);function n(){return Object(a.a)(this,n),e.apply(this,arguments)}return Object(i.a)(n,[{key:"render",value:function(){return m?Object(O.jsx)(b.a,{}):Object(O.jsx)("div",{className:"file-view-content flex-1 text-file-view",children:Object(O.jsx)(S.a,{ref:"code-mirror-editor",value:this.props.content,options:N,onChange:this.props.updateContent})})}}]),n}(p.a.Component);d.a.render(Object(O.jsx)(B,{}),document.getElementById("wrapper"))}},[[1650,1,0]]]);
//# sourceMappingURL=viewFileText.chunk.js.map