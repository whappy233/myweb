(function(window) {
    var initPhotoSwipeFromDOM = function (gallerySelector) {
        // 获取容器内图片的信息
        // {% verbatim %}
        // {{"src": 图片url, "w":宽, "h":高, "author":null, "el":{}, "msrc":缩略图url, "o"(原始图片):{"src":"图片路径", "w":宽, "h":高}},...}
        // {% endverbatim %}
        var parseThumbnailElements = function (el) {  // el: 图片容器
            var thumbElements = el.childNodes,  // 图片容器的所有子节点
                numNodes = thumbElements.length,  // 子节点个数
                items = [],
                el,
                childElements,
                thumbnailEl,
                size,
                item;

            for (var i = 0; i < numNodes; i++) {

                el = thumbElements[i];

                // include only element nodes
                // 1	Element	代表元素	Element, Text, Comment, ProcessingInstruction, CDATASection, EntityReference
                // 2	Attr	代表属性	Text, EntityReference
                // 3	Text	代表元素或属性中的文本内容。	None
                // 4	CDATASection	代表文档中的 CDATA 部分（不会由解析器解析的文本）。	None
                // 5	EntityReference	代表实体引用。	Element, ProcessingInstruction, Comment, Text, CDATASection, EntityReference
                // 6	Entity	代表实体。	Element, ProcessingInstruction, Comment, Text, CDATASection, EntityReference
                // 7	ProcessingInstruction	代表处理指令。	None
                // 8	Comment	代表注释。	None
                // 9	Document	代表整个文档（DOM 树的根节点）。	Element, ProcessingInstruction, Comment, DocumentType
                // 10	DocumentType	向为文档定义的实体提供接口	None
                // 11	DocumentFragment	代表轻量级的 Document 对象，能够容纳文档的某个部分	Element, ProcessingInstruction, Comment, Text, CDATASection, EntityReference
                // 12	Notation	代表 DTD 中声明的符号。

                if (el.nodeType !== 1) continue;

                // el:
                //  <a href="/media/photo/backgrou-5e0198e221ce.jpg" class="box" data-size="1280x720">
                //      <img src="/media/photo/thumbs/thumb-backgrou-5e0198e221ce.jpg" alt="backgrou-5e0198e221ce.jpg">
                //      <p>backgrou-5e0198e221ce.jpg</p>
                //  </a>

                el = el.childNodes[1]
                size = el.getAttribute('data-size').split('x');  // data-size="1280x720"  --> ["1280", "720"]

                item = {  // 结果对象
                    src: el.getAttribute('href'),  // /media/photo/backgrou-5e0198e221ce.jpg
                    w: parseInt(size[0], 10),  // 1280
                    h: parseInt(size[1], 10),  // 720
                };

                item.el = el; // save link to element for getThumbBoundsFn

                childElements = el.children;  // [<img>, <i>]

                if (childElements.length > 0) {
                    item.msrc = childElements[0].getAttribute('src');  // 缩略图 url
                    item.title = childElements[0].getAttribute('title');  // 图像 title
                    item.time = childElements[0].getAttribute('date-time')  // time
                }

                var mediumSrc = el.getAttribute('data-med');
                if (mediumSrc) {
                    size = el.getAttribute('data-med-size').split('x');
                    item.m = {
                        src: mediumSrc,
                        w: parseInt(size[0], 10),
                        h: parseInt(size[1], 10)
                    };
                }
                // 原始图像
                item.o = {
                    src: item.src,
                    w: item.w,
                    h: item.h
                };

                items.push(item);
            }

            return items;
        };

        // 查找最近的父元素
        var closest = function closest(el, fn) {
            return el && (fn(el) ? el : closest(el.parentNode, fn));
        };

        // 缩略图点击, 激活 PhotoSwipe
        var onThumbnailsClick = function (e) {
            e = e || window.event;
            e.preventDefault ? e.preventDefault() : e.returnValue = false;

            var eTarget = e.target || e.srcElement;  // 触发当前事件的元素

            var clickedListItem = closest(eTarget, function (el) {
                return el.tagName === 'A';
            });

            if (!clickedListItem) return;

            var clickedGallery = clickedListItem.parentNode.parentNode; // 获取父节点 ('.my-gallery')
            var childnodes = clickedGallery.childNodes,  // 父节点的子节点
                numChildNodes = childnodes.length,  // 子节点数量
                nodeIndex = 0, index;

            // 获取触发当前事件的元素的索引
            for (var i = 0; i < numChildNodes; i++) {
                if (childnodes[i].nodeType !== 1) continue;
                if (childnodes[i].childNodes[1] === clickedListItem) {
                    index = nodeIndex;
                    break;
                }
                nodeIndex++;
            }

            if (index >= 0) openPhotoSwipe(index, clickedGallery);  // 激活 PhotoSwipe
            return false;
        };

        // 解析 #&pid=3&gid=1  --> {gid: 1, pid: "3"}
        var photoswipeParseHash = function () {
            var hash = window.location.hash.substring(1), // --> "&gid=0&pid=9"
                params = {};

            if (hash.length < 5) return params;// pid=1

            var vars = hash.split('&');  //  --> ["", "gid=1", "pid=1"]

            for (var i = 0; i < vars.length; i++) {
                if (!vars[i]) continue;
                var pair = vars[i].split('=');
                if (pair.length < 2) continue;
                params[pair[0]] = pair[1];
            }

            if (params.gid) params.gid = parseInt(params.gid, 10);  // --> int
            return params;
        };

        // index: 图片索引号, galleryElement: 图片所在的容器, disableAnimation: 是否开启动画, fromURL
        var openPhotoSwipe = function (index, galleryElement, disableAnimation, fromURL) {
            var pswpElement = document.querySelectorAll('.pswp')[0],  // PhotoSwipe UI
                gallery, options, items;

            // {% verbatim %}
            // {{"src": 图片url, "w":宽, "h":高, "author":null, "el":{}, "msrc":缩略图url, "o"(原始图片):{"src":"图片路径", "w":宽, "h":高}},...}
            // {% endverbatim %}

            items = parseThumbnailElements(galleryElement);  // 图片容器里的所有图片

            // define options (if needed)
            options = {
                showHideOpacity: true,  // 缩略图的纵横比与原始图像匹配, 但缩略图区域通过 CSS裁剪
                bgOpacity: 0.8,  // 背景不透明度(0~1)

                galleryUID: galleryElement.getAttribute('data-pswp-uid'), // 图片所在的容器索引号

                // {% verbatim %} 分享按钮配置
                shareButtons: [
                    // {{url}}  当前页面的完整URL: http://127.0.0.1:8000/gallery/detail/11/29d877dc44124dad8ffc259f8abf85d0/?before=/gallery/#&gid=1&pid=3
                    // {{text}} 图片名称: backgrou-8e143b1e00b3.jpg
                    // {{image_url}}  图片url: /media/photo/backgrou-8e143b1e00b3.jpg
                    // {{raw_image_url}} 图片url: /media/photo/backgrou-8e143b1e00b3.jpg
                    { id: "download", label: "下载图片", url: "{{raw_image_url}}", download: true },
                ],
                // {% endverbatim %}

                // 获取给点图片索引的缩略图 在 window 的矩形位置
                // 函数应返回具有坐标的对象，从该坐标开始初始放大动画（或缩小动画将结束）
                getThumbBoundsFn: function (index) {
                    var thumbnail = items[index].el.children[0],  // 图片的缩略图 <img src="/media/photo/thumbs/thumb-backgrou-50fa3d0c97e4.jpg">
                        pageYScroll = window.pageYOffset || document.documentElement.scrollTop,  // 当前滚动条的位置(Y轴)
                        rect = thumbnail.getBoundingClientRect();
                    return { x: rect.left, y: rect.top + pageYScroll, w: rect.width };
                },

                // 插入图像 title time 信息到底部
                addCaptionHTMLFn: function (item, captionEl, isFake) {
                    if (!item.title) {
                        captionEl.children[0].innerText = '';
                        return false;
                    }
                    captionEl.children[0].innerHTML = `<div class="pswp__caption__center">${item.title}<br><small>${item.time}</small></div>`
                    return true;
                },
            };

            if (fromURL) {
                if (options.galleryPIDs) {
                    // parse real index when custom PIDs are used
                    // http://photoswipe.com/documentation/faq.html#custom-pid-in-url
                    for (var j = 0; j < items.length; j++) {
                        if (items[j].pid == index) {
                            options.index = j;
                            break;
                        }
                    }
                } else options.index = parseInt(index, 10) - 1;
            } else options.index = parseInt(index, 10);

            // exit if index not found
            if (isNaN(options.index)) return;

            if (disableAnimation) options.showAnimationDuration = 0;

            // see: http://photoswipe.com/documentation/responsive-images.html
            var realViewportWidth,
                useLargeImages = false,
                firstResize = true,
                imageSrcWillChange;

            // 将数据传递给 PhotoSwipe 并初始化
            photo_swipe = new PhotoSwipe(pswpElement, PhotoSwipeUI_Default, items, options);
            photo_swipe.listen('beforeResize', function () {

                // photo_swipe.viewportSize  当前窗口尺寸
                // photo_swipe.likelyTouchDevice  是否支持触摸
                // screen 屏幕信息

                var dpiRatio = window.devicePixelRatio ? window.devicePixelRatio : 1;  // 屏幕 dpi
                dpiRatio = Math.min(dpiRatio, 2.5);
                realViewportWidth = photo_swipe.viewportSize.x * dpiRatio;

                if (realViewportWidth >= 1200 || (!photo_swipe.likelyTouchDevice && realViewportWidth > 800) || screen.width > 1200) {
                    if (!useLargeImages) {
                        useLargeImages = true;
                        imageSrcWillChange = true;
                    }

                } else {
                    if (useLargeImages) {
                        useLargeImages = false;
                        imageSrcWillChange = true;
                    }
                }

                if (imageSrcWillChange && !firstResize) {
                    photo_swipe.invalidateCurrItems();
                }

                if (firstResize) {
                    firstResize = false;
                }

                imageSrcWillChange = false;

            });

            photo_swipe.listen('gettingData', function (index, item) {
                if (useLargeImages) {
                    item.src = item.o.src;
                    item.w = item.o.w;
                    item.h = item.o.h;
                } else {
                    item.src = item.m.src;
                    item.w = item.m.w;
                    item.h = item.m.h;
                }
            });

            photo_swipe.init();
        };

        // 获取所有 gallery 元素, 添加属性, 绑定事件
        var galleryElements = document.querySelectorAll(gallerySelector);
        galleryElements.forEach(function (ele, index) {
            ele.setAttribute('data-pswp-uid', index + 1);
            ele.onclick = onThumbnailsClick;  // 图像容器绑定事件, 通过点击激活 PhotoSwipe
        })

        // 如果 URL 包含 #&pid=3&gid=1, 则直接激活 PhotoSwipe
        var hashData = photoswipeParseHash();  // {gid: 1, pid: "2"} 相当于 {element(gid): 1, index(pid):2}
        if (hashData.pid && hashData.gid) {
            openPhotoSwipe(hashData.pid, galleryElements[hashData.gid - 1], true, true);
        }
    };

    initPhotoSwipeFromDOM('.my-gallery');
})(window);