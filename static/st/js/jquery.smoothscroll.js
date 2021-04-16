!function() {
    function e() {
        if (!C && document.body) {
            C = !0;
            var e = document.body
              , t = document.documentElement
              , o = window.innerHeight
              , a = e.scrollHeight;
            if (z = document.compatMode.indexOf("CSS") >= 0 ? t : e,
            v = e,
            M.keyboardSupport && s("keydown", n),
            top != self)
                E = !0;
            else if (a > o && (e.offsetHeight <= o || t.offsetHeight <= o)) {
                var r, i = document.createElement("div");
                i.style.cssText = "position:absolute; z-index:-10000; top:0; left:0; right:0; height:" + z.scrollHeight + "px",
                document.body.appendChild(i),
                y = function() {
                    r || (r = setTimeout(function() {
                        T || (i.style.height = "0",
                        i.style.height = z.scrollHeight + "px",
                        r = null)
                    }, 500))
                }
                ,
                setTimeout(y, 10),
                s("resize", y);
                if ((g = new j(y)).observe(e, {
                    attributes: !0,
                    childList: !0,
                    characterData: !1
                }),
                z.offsetHeight <= o) {
                    var l = document.createElement("div");
                    l.style.clear = "both",
                    e.appendChild(l)
                }
            }
            M.fixedBackground || T || (e.style.backgroundAttachment = "scroll",
            t.style.backgroundAttachment = "scroll")
        }
    }
    function t(e, t, o) {
        if (r = (r = t) > 0 ? 1 : -1,
        i = (i = o) > 0 ? 1 : -1,
        (H.x !== r || H.y !== i) && (H.x = r,
        H.y = i,
        A = [],
        N = 0),
        1 != M.accelerationMax) {
            var n = Date.now() - N;
            if (n < M.accelerationDelta) {
                var a = (1 + 50 / n) / 2;
                a > 1 && (a = Math.min(a, M.accelerationMax),
                t *= a,
                o *= a)
            }
            N = Date.now()
        }
        var r, i;
        if (A.push({
            x: t,
            y: o,
            lastX: 0 > t ? .99 : -.99,
            lastY: 0 > o ? .99 : -.99,
            start: Date.now()
        }),
        !B) {
            var l = e === document.body
              , c = function(n) {
                for (var a = Date.now(), r = 0, i = 0, u = 0; u < A.length; u++) {
                    var d = A[u]
                      , s = a - d.start
                      , m = s >= M.animationTime
                      , f = m ? 1 : s / M.animationTime;
                    M.pulseAlgorithm && (f = (b = f) >= 1 ? 1 : 0 >= b ? 0 : (1 == M.pulseNormalize && (M.pulseNormalize /= p(1)),
                    p(b)));
                    var w = d.x * f - d.lastX >> 0
                      , h = d.y * f - d.lastY >> 0;
                    r += w,
                    i += h,
                    d.lastX += w,
                    d.lastY += h,
                    m && (A.splice(u, 1),
                    u--)
                }
                var b;
                l ? window.scrollBy(r, i) : (r && (e.scrollLeft += r),
                i && (e.scrollTop += i)),
                t || o || (A = []),
                A.length ? R(c, e, 1e3 / M.frameRate + 1) : B = !1
            };
            R(c, e, 0),
            B = !0
        }
    }
    function o(o) {
        C || e();
        var n = o.target
          , a = l(n);
        if (!a || o.defaultPrevented || o.ctrlKey)
            return !0;
        if (f(v, "embed") || f(n, "embed") && /\.pdf/i.test(n.src) || f(v, "object"))
            return !0;
        var i, c = -o.wheelDeltaX || o.deltaX || 0, u = -o.wheelDeltaY || o.deltaY || 0;
        return X && (o.wheelDeltaX && w(o.wheelDeltaX, 120) && (c = o.wheelDeltaX / Math.abs(o.wheelDeltaX) * -120),
        o.wheelDeltaY && w(o.wheelDeltaY, 120) && (u = o.wheelDeltaY / Math.abs(o.wheelDeltaY) * -120)),
        c || u || (u = -o.wheelDelta || 0),
        1 === o.deltaMode && (c *= 40,
        u *= 40),
        !(M.touchpadSupport || (!(i = u) || (L.length || (L = [i, i, i]),
        i = Math.abs(i),
        L.push(i),
        L.shift(),
        clearTimeout(x),
        x = setTimeout(function() {
            window.localStorage && (localStorage.SS_deltaBuffer = L.join(","))
        }, 1e3),
        h(120) || h(100)))) || (Math.abs(c) > 1.2 && (c *= M.stepSize / 120),
        Math.abs(u) > 1.2 && (u *= M.stepSize / 120),
        t(a, c, u),
        // o.preventDefault(),
        void r())
    }
    function n(e) {
        var o = e.target
          , n = e.ctrlKey || e.altKey || e.metaKey || e.shiftKey && e.keyCode !== Y.spacebar;
        document.body.contains(v) || (v = document.activeElement);
        var a = /^(button|submit|radio|checkbox|file|color|image)$/i;
        if (/^(textarea|select|embed|object)$/i.test(o.nodeName) || f(o, "input") && !a.test(o.type) || f(v, "video") || function(e) {
            var t = e.target
              , o = !1;
            if (-1 != document.URL.indexOf("www.youtube.com/watch"))
                do {
                    if (o = t.classList && t.classList.contains("html5-video-controls"))
                        break
                } while (t = t.parentNode);
            return o
        }(e) || o.isContentEditable || e.defaultPrevented || n)
            return !0;
        if ((f(o, "button") || f(o, "input") && a.test(o.type)) && e.keyCode === Y.spacebar)
            return !0;
        var i = 0
          , c = 0
          , u = l(v)
          , d = u.clientHeight;
        switch (u == document.body && (d = window.innerHeight),
        e.keyCode) {
        case Y.up:
            c = -M.arrowScroll;
            break;
        case Y.down:
            c = M.arrowScroll;
            break;
        case Y.spacebar:
            c = -(e.shiftKey ? 1 : -1) * d * .9;
            break;
        case Y.pageup:
            c = .9 * -d;
            break;
        case Y.pagedown:
            c = .9 * d;
            break;
        case Y.home:
            c = -u.scrollTop;
            break;
        case Y.end:
            var s = u.scrollHeight - u.scrollTop - d;
            c = s > 0 ? s + 10 : 0;
            break;
        case Y.left:
            i = -M.arrowScroll;
            break;
        case Y.right:
            i = M.arrowScroll;
            break;
        default:
            return !0
        }
        t(u, i, c),
        e.preventDefault(),
        r()
    }
    function a(e) {
        v = e.target
    }
    function r() {
        clearTimeout(S),
        S = setInterval(function() {
            K = {}
        }, 1e3)
    }
    function i(e, t) {
        for (var o = e.length; o--; )
            K[O(e[o])] = t;
        return t
    }
    function l(e) {
        var t = []
          , o = document.body
          , n = z.scrollHeight;
        do {
            var a = K[O(e)];
            if (a)
                return i(t, a);
            if (t.push(e),
            n === e.scrollHeight) {
                var r = u(z) && u(o) || d(z);
                if (E && c(z) || !E && r)
                    return i(t, F())
            } else if (c(e) && d(e))
                return i(t, e)
        } while (e = e.parentElement)
    }
    function c(e) {
        return e.clientHeight + 10 < e.scrollHeight
    }
    function u(e) {
        return "hidden" !== getComputedStyle(e, "").getPropertyValue("overflow-y")
    }
    function d(e) {
        var t = getComputedStyle(e, "").getPropertyValue("overflow-y");
        return "scroll" === t || "auto" === t
    }
    function s(e, t, xx=!1) {
        window.addEventListener(e, t, xx)
    }
    function m(e, t) {
        window.removeEventListener(e, t, !1)
    }
    function f(e, t) {
        return (e.nodeName || "").toLowerCase() === t.toLowerCase()
    }
    function w(e, t) {
        return Math.floor(e / t) == e / t
    }
    function h(e) {
        return w(L[0], e) && w(L[1], e) && w(L[2], e)
    }
    function p(e) {
        var t, o;
        return 1 > (e *= M.pulseScale) ? t = e - (1 - Math.exp(-e)) : (e -= 1,
        t = (o = Math.exp(-1)) + (1 - Math.exp(-e)) * (1 - o)),
        t * M.pulseNormalize
    }
    function b(e) {
        for (var t in e)
            D.hasOwnProperty(t) && (M[t] = e[t])
    }
    var v, g, y, S, x, k, D = {
        frameRate: 150,
        animationTime: 500,
        stepSize: 100,
        pulseAlgorithm: !0,
        pulseScale: 4,
        pulseNormalize: 1,
        accelerationDelta: 50,
        accelerationMax: 3,
        keyboardSupport: !0,
        arrowScroll: 50,
        touchpadSupport: !1,
        fixedBackground: !0,
        excluded: ""
    }, M = D, T = !1, E = !1, H = {
        x: 0,
        y: 0
    }, C = !1, z = document.documentElement, L = [], X = /^Mac/.test(navigator.platform), Y = {
        left: 37,
        up: 38,
        right: 39,
        down: 40,
        spacebar: 32,
        pageup: 33,
        pagedown: 34,
        end: 35,
        home: 36
    }, A = [], B = !1, N = Date.now(), O = (k = 0,
    function(e) {
        return e.uniqueID || (e.uniqueID = k++)
    }
    ), K = {};
    window.localStorage && localStorage.SS_deltaBuffer && (L = localStorage.SS_deltaBuffer.split(","));
    var q, P, R = window.requestAnimationFrame || window.webkitRequestAnimationFrame || window.mozRequestAnimationFrame || function(e, t, o) {
        window.setTimeout(e, o || 1e3 / 60)
    }
    , j = window.MutationObserver || window.WebKitMutationObserver || window.MozMutationObserver, F = function() {
        if (!P) {
            var e = document.createElement("div");
            e.style.cssText = "height:10000px;width:1px;",
            document.body.appendChild(e);
            var t = document.body.scrollTop;
            document.documentElement.scrollTop,
            window.scrollBy(0, 3),
            P = document.body.scrollTop != t ? document.body : document.documentElement,
            window.scrollBy(0, -3),
            document.body.removeChild(e)
        }
        return P
    }, I = window.navigator.userAgent, _ = /Edge/.test(I), V = /chrome/i.test(I) && !_, W = /safari/i.test(I) && !_, $ = /mobile/i.test(I), U = /Windows NT 6.1/i.test(I) && /rv:11/i.test(I), G = (V || W || U) && !$;
    "onwheel"in document.createElement("div") ? q = "wheel" : "onmousewheel"in document.createElement("div") && (q = "mousewheel"),
    q && G && (s(q, o),
    s("mousedown", a),
    s("load", e)),
    b.destroy = function() {
        g && g.disconnect(),
        m(q, o),
        m("mousedown", a),
        m("keydown", n),
        m("resize", y),
        m("load", e)
    }
    ,
    window.SmoothScrollOptions && b(window.SmoothScrollOptions),
    "function" == typeof define && define.amd ? define(function() {
        return b
    }) : "object" == typeof exports ? module.exports = b : window.SmoothScroll = b
}();
