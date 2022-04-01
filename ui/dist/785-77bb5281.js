"use strict";(self.webpackChunkseqr=self.webpackChunkseqr||[]).push([[785],{79479:function(t,n,e){e.d(n,{e1:function(){return d}});var r=e(73078),i=e(3839),o=e(5540),u=e(49390),a=(0,i.Z)("start","end","cancel","interrupt"),s=[];function l(t,n,e,r,i,l){var f=t.__transition;if(f){if(e in f)return}else t.__transition={};!function(t,n,e){var r,i=t.__transition;function a(t){e.state=1,e.timer.restart(s,e.delay,e.time),e.delay<=t&&s(t-e.delay)}function s(o){var a,c,h,d;if(1!==e.state)return f();for(a in i)if((d=i[a]).name===e.name){if(3===d.state)return(0,u.Z)(s);4===d.state?(d.state=6,d.timer.stop(),d.on.call("interrupt",t,t.__data__,d.index,d.group),delete i[a]):+a<n&&(d.state=6,d.timer.stop(),d.on.call("cancel",t,t.__data__,d.index,d.group),delete i[a])}if((0,u.Z)((function(){3===e.state&&(e.state=4,e.timer.restart(l,e.delay,e.time),l(o))})),e.state=2,e.on.call("start",t,t.__data__,e.index,e.group),2===e.state){for(e.state=3,r=new Array(h=e.tween.length),a=0,c=-1;a<h;++a)(d=e.tween[a].value.call(t,t.__data__,e.index,e.group))&&(r[++c]=d);r.length=c+1}}function l(n){for(var i=n<e.duration?e.ease.call(null,n/e.duration):(e.timer.restart(f),e.state=5,1),o=-1,u=r.length;++o<u;)r[o].call(t,i);5===e.state&&(e.on.call("end",t,t.__data__,e.index,e.group),f())}function f(){for(var r in e.state=6,e.timer.stop(),delete i[n],i)return;delete t.__transition}i[n]=e,e.timer=(0,o.HT)(a,0,e.time)}(t,e,{name:n,index:r,group:i,on:a,tween:s,time:l.time,delay:l.delay,duration:l.duration,ease:l.ease,timer:null,state:0})}function f(t,n){var e=h(t,n);if(e.state>0)throw new Error("too late; already scheduled");return e}function c(t,n){var e=h(t,n);if(e.state>3)throw new Error("too late; already running");return e}function h(t,n){var e=t.__transition;if(!e||!(e=e[n]))throw new Error("transition not found");return e}function d(t,n){var e,r,i,o=t.__transition,u=!0;if(o){for(i in n=null==n?null:n+"",o)(e=o[i]).name===n?(r=e.state>2&&e.state<5,e.state=6,e.timer.stop(),e.on.call(r?"interrupt":"cancel",t,t.__data__,e.index,e.group),delete o[i]):u=!1;u&&delete t.__transition}}var v=e(78725),p=e(60447);function _(t,n){var e,r;return function(){var i=c(this,t),o=i.tween;if(o!==e)for(var u=0,a=(r=e=o).length;u<a;++u)if(r[u].name===n){(r=r.slice()).splice(u,1);break}i.tween=r}}function y(t,n,e){var r,i;if("function"!=typeof e)throw new Error;return function(){var o=c(this,t),u=o.tween;if(u!==r){i=(r=u).slice();for(var a={name:n,value:e},s=0,l=i.length;s<l;++s)if(i[s].name===n){i[s]=a;break}s===l&&i.push(a)}o.tween=i}}function g(t,n,e){var r=t._id;return t.each((function(){var t=c(this,r);(t.value||(t.value={}))[n]=e.apply(this,arguments)})),function(t){return h(t,r).value[n]}}var w=e(85959),m=e(30017),Z=e(54684),b=e(70906);function x(t,n){var e;return("number"==typeof n?m.Z:n instanceof w.ZP?Z.ZP:(e=(0,w.ZP)(n))?(n=e,Z.ZP):b.Z)(t,n)}function A(t){return function(){this.removeAttribute(t)}}function P(t){return function(){this.removeAttributeNS(t.space,t.local)}}function k(t,n,e){var r,i,o=e+"";return function(){var u=this.getAttribute(t);return u===o?null:u===r?i:i=n(r=u,e)}}function M(t,n,e){var r,i,o=e+"";return function(){var u=this.getAttributeNS(t.space,t.local);return u===o?null:u===r?i:i=n(r=u,e)}}function S(t,n,e){var r,i,o;return function(){var u,a,s=e(this);if(null!=s)return(u=this.getAttribute(t))===(a=s+"")?null:u===r&&a===i?o:(i=a,o=n(r=u,s));this.removeAttribute(t)}}function E(t,n,e){var r,i,o;return function(){var u,a,s=e(this);if(null!=s)return(u=this.getAttributeNS(t.space,t.local))===(a=s+"")?null:u===r&&a===i?o:(i=a,o=n(r=u,s));this.removeAttributeNS(t.space,t.local)}}function T(t,n){return function(e){this.setAttribute(t,n.call(this,e))}}function N(t,n){return function(e){this.setAttributeNS(t.space,t.local,n.call(this,e))}}function O(t,n){var e,r;function i(){var i=n.apply(this,arguments);return i!==r&&(e=(r=i)&&N(t,i)),e}return i._value=n,i}function C(t,n){var e,r;function i(){var i=n.apply(this,arguments);return i!==r&&(e=(r=i)&&T(t,i)),e}return i._value=n,i}function z(t,n){return function(){f(this,t).delay=+n.apply(this,arguments)}}function Y(t,n){return n=+n,function(){f(this,t).delay=n}}function X(t,n){return function(){c(this,t).duration=+n.apply(this,arguments)}}function j(t,n){return n=+n,function(){c(this,t).duration=n}}function q(t,n){if("function"!=typeof n)throw new Error;return function(){c(this,t).ease=n}}var B=e(40597);function I(t,n,e){var r,i,o=function(t){return(t+"").trim().split(/^|\s+/).every((function(t){var n=t.indexOf(".");return n>=0&&(t=t.slice(0,n)),!t||"start"===t}))}(n)?f:c;return function(){var u=o(this,t),a=u.on;a!==r&&(i=(r=a).copy()).on(n,e),u.on=i}}var $=e(86408);var H=e(43912);var R=r.ZP.prototype.constructor;var D=e(40721);function F(t){return function(){this.style.removeProperty(t)}}function G(t,n,e){return function(r){this.style.setProperty(t,n.call(this,r),e)}}function J(t,n,e){var r,i;function o(){var o=n.apply(this,arguments);return o!==i&&(r=(i=o)&&G(t,o,e)),r}return o._value=n,o}function K(t){return function(n){this.textContent=t.call(this,n)}}function L(t){var n,e;function r(){var r=t.apply(this,arguments);return r!==e&&(n=(e=r)&&K(r)),n}return r._value=t,r}var Q=0;function U(t,n,e,r){this._groups=t,this._parents=n,this._name=e,this._id=r}function V(){return++Q}var W=r.ZP.prototype;U.prototype=function(t){return(0,r.ZP)().transition(t)}.prototype={constructor:U,select:function(t){var n=this._name,e=this._id;"function"!=typeof t&&(t=(0,$.Z)(t));for(var r=this._groups,i=r.length,o=new Array(i),u=0;u<i;++u)for(var a,s,f=r[u],c=f.length,d=o[u]=new Array(c),v=0;v<c;++v)(a=f[v])&&(s=t.call(a,a.__data__,v,f))&&("__data__"in a&&(s.__data__=a.__data__),d[v]=s,l(d[v],n,e,v,d,h(a,e)));return new U(o,this._parents,n,e)},selectAll:function(t){var n=this._name,e=this._id;"function"!=typeof t&&(t=(0,H.Z)(t));for(var r=this._groups,i=r.length,o=[],u=[],a=0;a<i;++a)for(var s,f=r[a],c=f.length,d=0;d<c;++d)if(s=f[d]){for(var v,p=t.call(s,s.__data__,d,f),_=h(s,e),y=0,g=p.length;y<g;++y)(v=p[y])&&l(v,n,e,y,p,_);o.push(p),u.push(s)}return new U(o,u,n,e)},filter:function(t){"function"!=typeof t&&(t=(0,B.Z)(t));for(var n=this._groups,e=n.length,r=new Array(e),i=0;i<e;++i)for(var o,u=n[i],a=u.length,s=r[i]=[],l=0;l<a;++l)(o=u[l])&&t.call(o,o.__data__,l,u)&&s.push(o);return new U(r,this._parents,this._name,this._id)},merge:function(t){if(t._id!==this._id)throw new Error;for(var n=this._groups,e=t._groups,r=n.length,i=e.length,o=Math.min(r,i),u=new Array(r),a=0;a<o;++a)for(var s,l=n[a],f=e[a],c=l.length,h=u[a]=new Array(c),d=0;d<c;++d)(s=l[d]||f[d])&&(h[d]=s);for(;a<r;++a)u[a]=n[a];return new U(u,this._parents,this._name,this._id)},selection:function(){return new R(this._groups,this._parents)},transition:function(){for(var t=this._name,n=this._id,e=V(),r=this._groups,i=r.length,o=0;o<i;++o)for(var u,a=r[o],s=a.length,f=0;f<s;++f)if(u=a[f]){var c=h(u,n);l(u,t,e,f,a,{time:c.time+c.delay+c.duration,delay:0,duration:c.duration,ease:c.ease})}return new U(r,this._parents,t,e)},call:W.call,nodes:W.nodes,node:W.node,size:W.size,empty:W.empty,each:W.each,on:function(t,n){var e=this._id;return arguments.length<2?h(this.node(),e).on.on(t):this.each(I(e,t,n))},attr:function(t,n){var e=(0,p.Z)(t),r="transform"===e?v.w:x;return this.attrTween(t,"function"==typeof n?(e.local?E:S)(e,r,g(this,"attr."+t,n)):null==n?(e.local?P:A)(e):(e.local?M:k)(e,r,n))},attrTween:function(t,n){var e="attr."+t;if(arguments.length<2)return(e=this.tween(e))&&e._value;if(null==n)return this.tween(e,null);if("function"!=typeof n)throw new Error;var r=(0,p.Z)(t);return this.tween(e,(r.local?O:C)(r,n))},style:function(t,n,e){var r="transform"==(t+="")?v.Y:x;return null==n?this.styleTween(t,function(t,n){var e,r,i;return function(){var o=(0,D.S)(this,t),u=(this.style.removeProperty(t),(0,D.S)(this,t));return o===u?null:o===e&&u===r?i:i=n(e=o,r=u)}}(t,r)).on("end.style."+t,F(t)):"function"==typeof n?this.styleTween(t,function(t,n,e){var r,i,o;return function(){var u=(0,D.S)(this,t),a=e(this),s=a+"";return null==a&&(this.style.removeProperty(t),s=a=(0,D.S)(this,t)),u===s?null:u===r&&s===i?o:(i=s,o=n(r=u,a))}}(t,r,g(this,"style."+t,n))).each(function(t,n){var e,r,i,o,u="style."+n,a="end."+u;return function(){var s=c(this,t),l=s.on,f=null==s.value[u]?o||(o=F(n)):void 0;l===e&&i===f||(r=(e=l).copy()).on(a,i=f),s.on=r}}(this._id,t)):this.styleTween(t,function(t,n,e){var r,i,o=e+"";return function(){var u=(0,D.S)(this,t);return u===o?null:u===r?i:i=n(r=u,e)}}(t,r,n),e).on("end.style."+t,null)},styleTween:function(t,n,e){var r="style."+(t+="");if(arguments.length<2)return(r=this.tween(r))&&r._value;if(null==n)return this.tween(r,null);if("function"!=typeof n)throw new Error;return this.tween(r,J(t,n,null==e?"":e))},text:function(t){return this.tween("text","function"==typeof t?function(t){return function(){var n=t(this);this.textContent=null==n?"":n}}(g(this,"text",t)):function(t){return function(){this.textContent=t}}(null==t?"":t+""))},textTween:function(t){var n="text";if(arguments.length<1)return(n=this.tween(n))&&n._value;if(null==t)return this.tween(n,null);if("function"!=typeof t)throw new Error;return this.tween(n,L(t))},remove:function(){return this.on("end.remove",function(t){return function(){var n=this.parentNode;for(var e in this.__transition)if(+e!==t)return;n&&n.removeChild(this)}}(this._id))},tween:function(t,n){var e=this._id;if(t+="",arguments.length<2){for(var r,i=h(this.node(),e).tween,o=0,u=i.length;o<u;++o)if((r=i[o]).name===t)return r.value;return null}return this.each((null==n?_:y)(e,t,n))},delay:function(t){var n=this._id;return arguments.length?this.each(("function"==typeof t?z:Y)(n,t)):h(this.node(),n).delay},duration:function(t){var n=this._id;return arguments.length?this.each(("function"==typeof t?X:j)(n,t)):h(this.node(),n).duration},ease:function(t){var n=this._id;return arguments.length?this.each(q(n,t)):h(this.node(),n).ease},end:function(){var t,n,e=this,r=e._id,i=e.size();return new Promise((function(o,u){var a={value:u},s={value:function(){0==--i&&o()}};e.each((function(){var e=c(this,r),i=e.on;i!==t&&((n=(t=i).copy())._.cancel.push(a),n._.interrupt.push(a),n._.end.push(s)),e.on=n}))}))}};var tt={time:null,delay:0,duration:250,ease:e(56606).tw};function nt(t,n){for(var e;!(e=t.__transition)||!(e=e[n]);)if(!(t=t.parentNode))return tt.time=(0,o.zO)(),tt;return e}r.ZP.prototype.interrupt=function(t){return this.each((function(){d(this,t)}))},r.ZP.prototype.transition=function(t){var n,e;t instanceof U?(n=t._id,t=t._name):(n=V(),(e=tt).time=(0,o.zO)(),t=null==t?null:t+"");for(var r=this._groups,i=r.length,u=0;u<i;++u)for(var a,s=r[u],f=s.length,c=0;c<f;++c)(a=s[c])&&l(a,t,n,c,s,e||nt(a,n));return new U(r,this._parents,t,n)}},1300:function(t,n,e){e.d(n,{Z:function(){return o}});var r=e(5130),i=e(42274);e(79479);class o{constructor(t,n=!1,e=30,r=-40,i=100){this.id=t,this.verbose=n,this.offsetX=e,this.offsetY=r,this.duration=i}show(t){this.verbose&&console.log(t),this.edit(t),this.move(),(0,r.Z)("#"+this.id).style("display","inline").transition().duration(this.duration).style("opacity",1)}hide(){(0,r.Z)("#"+this.id).transition().duration(this.duration).style("opacity",0),this.edit("")}move(t=i.B.pageX,n=i.B.pageY){this.verbose&&(console.log(t),console.log(n)),t+=this.offsetX,n=n+this.offsetY<0?10:n+this.offsetY;(0,r.Z)("#"+this.id).style("left",`${t}px`).style("top",`${n}px`)}edit(t){(0,r.Z)("#"+this.id).html(t)}}},80066:function(t,n,e){function r(t,n,e){t=+t,n=+n,e=(i=arguments.length)<2?(n=t,t=0,1):i<3?1:+e;for(var r=-1,i=0|Math.max(0,Math.ceil((n-t)/e)),o=new Array(i);++r<i;)o[r]=t+r*e;return o}e.d(n,{Z:function(){return h}});var i=e(24228);class o extends Map{constructor(t,n=l){if(super(),Object.defineProperties(this,{_intern:{value:new Map},_key:{value:n}}),null!=t)for(const[n,e]of t)this.set(n,e)}get(t){return super.get(u(this,t))}has(t){return super.has(u(this,t))}set(t,n){return super.set(a(this,t),n)}delete(t){return super.delete(s(this,t))}}Set;function u({_intern:t,_key:n},e){const r=n(e);return t.has(r)?t.get(r):e}function a({_intern:t,_key:n},e){const r=n(e);return t.has(r)?t.get(r):(t.set(r,e),e)}function s({_intern:t,_key:n},e){const r=n(e);return t.has(r)&&(e=t.get(r),t.delete(r)),e}function l(t){return null!==t&&"object"==typeof t?t.valueOf():t}const f=Symbol("implicit");function c(){var t=new o,n=[],e=[],r=f;function u(i){let o=t.get(i);if(void 0===o){if(r!==f)return r;t.set(i,o=n.push(i)-1)}return e[o%e.length]}return u.domain=function(e){if(!arguments.length)return n.slice();n=[],t=new o;for(const r of e)t.has(r)||t.set(r,n.push(r)-1);return u},u.range=function(t){return arguments.length?(e=Array.from(t),u):e.slice()},u.unknown=function(t){return arguments.length?(r=t,u):r},u.copy=function(){return c(n,e).unknown(r)},i.o.apply(u,arguments),u}function h(){var t,n,e=c().unknown(void 0),o=e.domain,u=e.range,a=0,s=1,l=!1,f=0,d=0,v=.5;function p(){var e=o().length,i=s<a,c=i?s:a,h=i?a:s;t=(h-c)/Math.max(1,e-f+2*d),l&&(t=Math.floor(t)),c+=(h-c-t*(e-f))*v,n=t*(1-f),l&&(c=Math.round(c),n=Math.round(n));var p=r(e).map((function(n){return c+t*n}));return u(i?p.reverse():p)}return delete e.unknown,e.domain=function(t){return arguments.length?(o(t),p()):o()},e.range=function(t){return arguments.length?([a,s]=t,a=+a,s=+s,p()):[a,s]},e.rangeRound=function(t){return[a,s]=t,a=+a,s=+s,l=!0,p()},e.bandwidth=function(){return n},e.step=function(){return t},e.round=function(t){return arguments.length?(l=!!t,p()):l},e.padding=function(t){return arguments.length?(f=Math.min(1,d=+t),p()):f},e.paddingInner=function(t){return arguments.length?(f=Math.min(1,t),p()):f},e.paddingOuter=function(t){return arguments.length?(d=+t,p()):d},e.align=function(t){return arguments.length?(v=Math.max(0,Math.min(1,t)),p()):v},e.copy=function(){return h(o(),[a,s]).round(l).paddingInner(f).paddingOuter(d).align(v)},i.o.apply(p(),arguments)}}}]);