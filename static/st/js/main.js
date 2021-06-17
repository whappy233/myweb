(function ($) {
    "use strict";


    // ------------------------------------------------------------------------------------------------------------------
    // 主题切换 
    // 响应系统主题切换
    let listeners = {
        dark: (mediaQueryList) => {
            if (mediaQueryList.matches) {
                $(".sticky-header").attr('data-theme', 'dark');
            }
        },
        light: (mediaQueryList) => {
            if (mediaQueryList.matches) {
                $(".sticky-header").attr('data-theme', 'light');
            }
        }
    };
    try {
        window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', listeners.dark);
        window.matchMedia('(prefers-color-scheme: light)').addEventListener('change', listeners.light);
    } catch (error) {
        // Safari
        window.matchMedia('(prefers-color-scheme: dark)').addListener(listeners.dark);
        window.matchMedia('(prefers-color-scheme: light)').addListener(listeners.light);
    }
    // 手动切换主题
    $('.sticky-header').on('click', '.dark_mode', function(){
        let body = $(".sticky-header"),
            theme = body.attr('data-theme'),
            theme_n = theme=='light'?'dark':'light'
        $(".sticky-header").attr('data-theme', theme_n);
        window.localStorage.setItem("theme", theme_n);
    });


    // ------------------------------------------------------------------------------------------------------------------
    // 页面加载动画 Page Preloader
    $("#preloader").fadeOut(1000, function () {
        $(this).remove();
    });


    // ------------------------------------------------------------------------------------------------------------------
    // 背景动画
    let $stars = $(".stars"),
        stars = 500,     // 星星的密集程度，数字越大越多
        r = 800;        // 星星的看起来的距离,值越大越远,可自行调制到自己满意的样子
    for (var i = 0; i < stars; i++) {
        var $star = $("<div/>").addClass("star");
        $stars.append($star);
    }
    $(".star").each(function () {
        var cur = $(this);
        var s = 0.2 + (Math.random() * 1);
        var curR = r + (Math.random() * 300);
        cur.css({
        transformOrigin: "0 0 " + curR + "px",
        transform: " translate3d(0,0,-" + curR + "px) rotateY(" + (Math.random() * 360) + "deg) rotateX(" + (Math.random() * -50) + "deg) scale(" + s + "," + s + ")"
        })
    });


    // ------------------------------------------------------------------------------------------------------------------
    // 消息提示插件
    toastr.options = {
        timeOut: 3000,
        progressBar: true,
        showMethod: "slideDown",
        hideMethod: "slideUp",
        showDuration: 200,
        hideDuration: 200
        // toastr.success('Successfully completed');
        // toastr.error('Something went wrong');
        // toastr.info('This is an informational message');
        // toastr.warning('You are currently not authorized');
        // toastr.clear();
    };


    // ------------------------------------------------------------------------------------------------------------------
    // 平滑滚动到指定位置
    function scrollTo(ele, speed, top, callback=function(){return false;}) {
        // ele 目标元素
        // speed 滚动速度
        // top 距离顶部尺寸
        // callback 回调函数
        let win = $("html, body");
        if (top) {
            top = ($(ele).offset().top - top);
        } else {
            top = $(ele).offset().top;
        }
        $('img').addClass('ease-out img-light-low');
        win.animate({
            // scrollTop:  win.scrollTop() - win.offset().top + top
            scrollTop: win.offset().top + top
        }, speed == undefined ? 1000 : speed, function(){
            callback();
            $('img').removeClass('img-light-low');
            setTimeout(() => {
                $('img').removeClass('ease-out');
            }, 350);
        });
        return this;
    };


    // ------------------------------------------------------------------------------------------------------------------
    // 图片懒加载
    //用来判断bound.top<=clientHeight的函数，返回一个bool值
    function isIn(el) {
        var bound = el.getBoundingClientRect();
        var clientHeight = window.innerHeight;
        return bound.top <= clientHeight;
    } ;
    //检查图片是否在可视区内，如果不在，则加载
    function check() {
        Array.from(document.querySelectorAll('img')).forEach(function(el){
            if(isIn(el)){
                loadImg(el);
            }
        })
    };
    function loadImg(el) {
        if (!el.src) {
            // el.src = '/static/st/img/loading.gif'
            var source = el.dataset.src;
            var img = new Image();
            img.src = source;
            img.onload = function () {  // 图片下载完毕时异步调用callback函数
                el.style.opacity = 0;
                el.src = img.src;
                $(el).animate({ opacity: '1' }, 300);
                $(el).removeClass('loading').addClass('img-animation').removeAttr('data-src');
            };
            img.onerror = function () {
                let ett_text = 'Image 404 🥶';
                let s = Math.max(el.offsetWidth, el.offsetHeight, 25);
                console.log(`${s}x${s}`);
                el.style.opacity = 0;
                el.src = placeholder.getData({ size: `${s}x${s}`, text: ett_text, bgcolor: '#7dbcff', color: '#fff' });
                $(el).animate({ opacity: '1' }, 300);
                $(el).removeClass('loading').addClass('img-animation').removeAttr('data-src');
            };
        }
    };
    window.onload = window.onscroll = function () { //onscroll()在滚动条滚动的时候触发
        check();
    };

    function ImgLoadError(e) {
        let target = e.target, // 当前dom节点
            tagName = target.tagName,
            default_src = target.src;
        let count = Number(target.dataset.count) || 0, // 以失败的次数，默认为0
            max = 2, // 总失败次数，总共加载 max + 1 次
            ett_text = 'Image 404 🥶';

        // 当前异常是由图片加载异常引起的
        if (tagName.toUpperCase() === 'IMG') {
            if (count >= max) {
                let s = Math.max(target.offsetWidth, target.offsetHeight, 25);
                console.log(`${s}x${s}`);
                target.src = placeholder.getData({ size: `${s}x${s}`, text: ett_text, bgcolor: '#7dbcff', color: '#fff' });
            } else {
                target.dataset.count = count + 1;
                target.src = default_src;
            }
        };
    };

    // 图片加载失败占位图
    window.addEventListener('error', ImgLoadError, true)


    // ------------------------------------------------------------------------------------------------------------------
    // 点击带有 data-scroll 属性元素跳转到指定位置 data-scroll="#wrapper"
    $('[data-scroll]').on('click', function () {
        let aim = this.dataset.scroll;
        scrollTo(aim, 500, 100);
    });


    // ------------------------------------------------------------------------------------------------------------------
    // 点击带有 data-href 属性的元素进行URL跳转
    $('#main').on('click', '[data-href]', function (e) {
        let target = e.target,
            currtarget = e.currentTarget;
        var target_href = target.href || target.parentNode.href;
        if (target_href == undefined){
            target_href = target.dataset.href || currtarget.dataset.href || '';
        }
        console.log('跳转到: ', target_href);
        window.location.href = target_href;
        e.stopPropagation();   // 阻止事件冒泡
        return false;
    });


    // ------------------------------------------------------------------------------------------------------------------
    // 对 data-event="show_hide" mousedown 显示密码
    $('[data-event="show_hide"]').on('mousedown', function(e){
        var $this = $(this);
        e.stopPropagation();
        e.preventDefault();
        $this.siblings('input').prop('type', 'text')
    }).on('mouseup', function(e){
        var $this = $(this);
        e.stopPropagation();
        e.preventDefault();
        $this.siblings('input').prop('type', 'password')
    });


    // ------------------------------------------------------------------------------------------------------------------
    // 对带有data-bg-image属性的标签设置给定的背景图片 data-bg-image='img/product/top-product1.jpg' 
    $("[data-bg-image]").each(function () {
        let img = $(this).data("bg-image");
        $(this).css({
            backgroundImage: "url(" + img + ")"
        });
    });


    // ------------------------------------------------------------------------------------------------------------------
    // MeanMenu 响应式导航栏
    // if ($.fn.meanmenu) {
    //     $('nav#dropdown').meanmenu({
    //         meanMenuClose: "✕",
    //         siteLogo: `
    //         <div class='mobile-menu-nav-back'>
    //             <a class='logo-mobile' href='index.html'>
    //                 <img src="{% static 'st/img/logo-mobile.png' %}" alt='logo' class='img-fluid'/>
    //             </a>
    //         </div>
    //         `
    //     });
    // };


    // ------------------------------------------------------------------------------------------------------------------
    // Offcanvas Menu activation code
    $('#wrapper').on('click', '.offcanvas-menu-btn', function (e) {
        e.preventDefault();
        var $this = $(this),
            wrapper = $(this).parents('body').find('>#wrapper'),
            wrapMask = $('<div />').addClass('offcanvas-mask'),
            offCancas = $('#offcanvas-wrap'),
            position = offCancas.data('position') || 'left';

        if ($this.hasClass('menu-status-open')) {
            wrapper.addClass('open').append(wrapMask);
            $this.removeClass('menu-status-open').addClass('menu-status-close');
            offCancas.css({
                'transform': 'translateX(0)'
            });
        } else {
            removeOffcanvas();
        };

        function removeOffcanvas() {
            wrapper.removeClass('open').find('> .offcanvas-mask').remove();
            $this.removeClass('menu-status-close').addClass('menu-status-open');
            if (position === 'left') {
                offCancas.css({
                    'transform': 'translateX(-100%)'
                });
            } else {
                offCancas.css({
                    'transform': 'translateX(100%)'
                });
            }
        }
        $(".offcanvas-mask, .offcanvas-close").on('click', function () {
            removeOffcanvas();
        });

        return false;
    });


    // ------------------------------------------------------------------------------------------------------------------
    // 目录相关
    // 小尺寸屏幕显示或隐藏目录按钮
    $('.showdirectory').on('click', function(){
        let $this = $(this),
            $toc = $('.widget#Toc');
        if ($toc.hasClass('fixed')){
            $toc.animate({opacity: 0, bottom: 0}, 300, function(){
                $toc.removeClass(['fixed', 'run']);
                $this.html('<i class="fas fa-align-left"></i>');
            });
        }else{
            $toc.addClass('fixed');
            $toc.css('opacity', 0);
            $toc.animate({opacity: 1, bottom: '46px'}, 300, function(){
                $this.html('<i class="fas fa-times"></i>');
            });
        }
    });

    // 跳转到目录指定位置
    $('.widget-toc .toc li').on('click', function (e, trigger) {
        let $this = $(this),
            $widget_toc = $('.widget#Toc'),
            ul_child = $this.children('ul'),
            this_siblings = $this.siblings('li'),
            $a = $this.children('a').first(),
            aim = $a.attr('href');

        if (ul_child.length > 0) {
            this_siblings.children('ul').slideUp(300);
            ul_child.slideDown(300);
        };
        $('.widget-toc .toc a').removeClass('active');
        $a.addClass('active');
        if (trigger==true){
            $this.parent('ul').parent('li').siblings('li').children('ul').slideUp(300);
            $this.parent('ul').slideDown(300);
        }else{
            $widget_toc[0].dataset.isscroll = true;
            scrollTo(aim, 500, 70, function(){$widget_toc[0].dataset.isscroll = false});
        };
        return false;
    });

    // 鼠标是否位于目录组件上
    $(".widget#Toc").hover(
        function(e){
            // over
            this.dataset.hover='true';
        }, 
        function(e){
            // leave
            this.dataset.hover='false';
            var $this = $(this);
            if (this.dataset.needhide == 'true'){
                this.dataset.needhide='false';
                $this.addClass('run');
                $this.animate({opacity: 0, bottom: 0}, 300, function(){
                    $this.removeClass(['fixed', 'run']);
                    $this.css('opacity', 1);
                    $('.showdirectory').html('<i class="fas fa-align-left"></i>');
                });
            }
        }
    );

    // 检查鼠标向上还是向下滚动
    var wheelHandle = function (e) {
        var e = e || window.event;
        if (e.wheelDelta) {
            if (e.wheelDelta > 0) { //当鼠标滚轮向上滚动时
                document.querySelector('.widget#Toc').dataset.scrollup='true';
            }
            if (e.wheelDelta < 0) { //当鼠标滚轮向下滚动时
                document.querySelector('.widget#Toc').dataset.scrollup='false';
            }
        } else if (e.detail) {
            if (e.detail < 0) { //当鼠标滚轮向上滚动时
                document.querySelector('.widget#Toc').dataset.scrollup='true';
            }
            if (e.detail > 0) { //当鼠标滚轮向下滚动时
                document.querySelector('.widget#Toc').dataset.scrollup='false';
            }
        }
    };
    if(document.querySelector('.widget#Toc')){
        window.addEventListener("DOMMouseScroll", wheelHandle) // 火狐
        window.addEventListener("wheel", wheelHandle);  // Google
    };

    // 获取 Toc href 队列
    let TocArray = $.map($('.widget#Toc a[href]'), function(e){return $(e).attr('href').slice(1)});

    // 重叠观察者. 在平屏幕滚动时更新目录当前显示高亮
    let options = {
        root: null,
        rootMargin: '0% 0% -30% 0%',
        threshold: 1.0,
    };
    let callback = function(entries, observer) { 
        if (document.querySelector('.widget#Toc').dataset.isscroll=='false'){
            entries.forEach(entry => {

                if (entry.isIntersecting){
                    let target_id = entry.target.id;
                    $(`a[href="#${target_id}"]`).parent('li').trigger("click", true);
                }else if(document.querySelector('.widget#Toc').dataset.scrollup=='true'){
                    // 向上滚动
                    let target_id = TocArray[TocArray.indexOf(entry.target.id)-1];
                    if (target_id){
                        $(`a[href="#${target_id}"]`).parent('li').trigger("click", true);
                    };
                };
            });
        }
    };
    let observer = new IntersectionObserver(callback, options);  // 创建重叠观察者
    document.querySelectorAll('.markdown-body>[id]').forEach(ele=>{
        observer.observe(ele);  // 给定观察者观察的目标对象
    });


    // ------------------------------------------------------------------------------------------------------------------
    // 滚动事件
    $(window).on('scroll', function (e) {
        let $toc = $('.widget#Toc');
        // Back Top Button
        if ($(window).scrollTop() > 700) {
            $('.scrollup').addClass('back-top');
            $('.showdirectory').addClass('back-top');
            $toc.attr('data-needhide', 'false');
        } else {
            $('.scrollup').removeClass('back-top');
            $('.showdirectory').removeClass('back-top');

            if ($toc.hasClass('fixed') == true && $toc.hasClass('run')==false){
                if($toc.attr('data-hover') ==  'false'){
                    $toc.attr('data-needhide', 'false');
                    $toc.addClass('run');
                    $toc.animate({opacity: 0, bottom: 0}, 300, function(){
                        $toc.removeClass(['fixed', 'run']);
                        $toc.css('opacity', 1);
                        $('.showdirectory').html('<i class="fas fa-align-left"></i>');
                    });
                }else{
                    $toc.attr('data-needhide', 'true');
                };
            };
        };

        if ($('body').hasClass('sticky-header')) {
            var menu = $("#header-menu"),
                mobile_menu = $('.mean-bar');

            if ($(window).scrollTop() > 70) {
                menu.addClass('rt-sticky');
                mobile_menu.addClass('rt-sticky');
            } else {
                menu.removeClass('rt-sticky');
                mobile_menu.removeClass('rt-sticky');
            }
        }
    });


    /*---------------------------------------
    Comments list event
    点击对应的消息列表进入详情
    class="go_comment_detail" data-comment_detail='www.abc.com'
    --------------------------------------- */
    // 点击跳转到目标地址
    $('#wrapper').on('click', '.go_comment_detail', function (e){
        var $this = $(this),
        aim_url = $(this).data('comment_detail'),
        status = $this.find('.comment_status>i');
        if (aim_url && status[0]){
            $this.attr('data-isread', true);
            status.removeClass().addClass('fas fa-spin fa-circle-notch');
            setTimeout(()=>{
                status.removeClass().addClass('far fa-circle');
                window.location = aim_url;
            }, 2000);
        }else{
            console.log('Nothing !')
        }
    });
    // 阻止事件冒泡
    $('#wrapper').on('click', '.go_comment_detail .user_name_a', function (e){
        e.stopPropagation();
    });
    // 删除消息
    $('#wrapper').on('click', '.go_comment_detail>.remove_msg i', function (e){
        // e.stopPropagation();  // 阻止事件向上冒泡
        // e.preventDefault(); // 取消一个目标元素的默认行为, 如果元素本身就没有默认行为, 调用当然就无效了.
        // 在jQuery中使用return false 时，相当于同时使用event.preventDefault和event.stopPropagation，它会阻止冒泡也会阻止默认行为。 
        // 但是使用原生js写时，return false只会阻止默认行为
        var $this = $(this);
        if ($this.hasClass('trash')){
            $this.parent().children().toggle()
        }
        if ($this.hasClass('cancel')){
            $this.parent().children().toggle()
        }
        if ($this.hasClass('delete')){
            var item = $this.parents().filter('li.go_comment_detail');
            var item_siblings = item.siblings().length;
            var item_parent = item.parent();
            $this.parents().filter('li.go_comment_detail').removeClass('ease-in-out').animate({right: item.width()+'px'}, 500, ()=>{
                item.remove();
                if (!item_siblings){
                    item_parent.html(`<div style='align-items:center;position:absolute;top:0;left:0;margin:0 43%;bottom:0;right:0;display:flex;text-align:center;'
                    ><i class="fas fa-inbox" style='font-size:60px; color:grey;'></i></div>
                    `);
                    // item_parent.css('background', 'url("/Users/carlos/Desktop/Blogxer/img/figure/figure1.jpg")');
                    item_parent.css('height', '240px');
                    item_parent.css('border-radius', '0 0 0 10px');
                }
            });
        }
        return false;
    });


    // ------------------------------------------------------------------------------------------------------------------
    // 点击显示搜索 Jquery Serch Box
    $('.sticky-header').on('click', 'li[data=header-search]', function (event) {
        event.preventDefault();
        var target = $("#header-search");
        target.addClass("open");
        setTimeout(function () {
            target.find('input').focus();
        }, 600);
        return false;
    });

    $("#header-search, #header-search button.close").on("click keyup", function (event) {
        if (
            event.target === this ||
            event.target.className === "close" ||
            event.keyCode === 27
        ) {
            $(this).removeClass("open");
        }
    });


    // ------------------------------------------------------------------------------------------------------------------
    // Masonry 画廊
    var galleryIsoContainer = $("#no-equal-gallery");
    if (galleryIsoContainer.length) {
        var blogGallerIso = galleryIsoContainer.imagesLoaded(function () {
            blogGallerIso.isotope({
                itemSelector: ".no-equal-item",
                masonry: {
                    columnWidth: ".no-equal-item"
                }
            });
        });
    }


    // ------------------------------------------------------------------------------------------------------------------
    // Video Popup
    // 视频弹出
    var yPopup = $(".popup-youtube");
    if (yPopup.length) {
        yPopup.magnificPopup({
            disableOn: 700,
            type: 'iframe',
            mainClass: 'mfp-fade',
            removalDelay: 160,
            preloader: false,
            fixedContentPos: false
        });
    }


    // ------------------------------------------------------------------------------------------------------------------
    // 轮播图
    if ($.fn.owlCarousel) {
        $('.rc-carousel').each(function () {
            var carousel = $(this),
                loop = carousel.data('loop'),
                items = carousel.data('items'),
                margin = carousel.data('margin'),
                stagePadding = carousel.data('stage-padding'),
                autoplay = carousel.data('autoplay'),
                autoplayTimeout = carousel.data('autoplay-timeout'),
                smartSpeed = carousel.data('smart-speed'),
                dots = carousel.data('dots'),
                nav = carousel.data('nav'),
                navSpeed = carousel.data('nav-speed'),
                rXsmall = carousel.data('r-x-small'),
                rXsmallNav = carousel.data('r-x-small-nav'),
                rXsmallDots = carousel.data('r-x-small-dots'),
                rXmedium = carousel.data('r-x-medium'),
                rXmediumNav = carousel.data('r-x-medium-nav'),
                rXmediumDots = carousel.data('r-x-medium-dots'),
                rSmall = carousel.data('r-small'),
                rSmallNav = carousel.data('r-small-nav'),
                rSmallDots = carousel.data('r-small-dots'),
                rMedium = carousel.data('r-medium'),
                rMediumNav = carousel.data('r-medium-nav'),
                rMediumDots = carousel.data('r-medium-dots'),
                rLarge = carousel.data('r-large'),
                rLargeNav = carousel.data('r-large-nav'),
                rLargeDots = carousel.data('r-large-dots'),
                rExtraLarge = carousel.data('r-extra-large'),
                rExtraLargeNav = carousel.data('r-extra-large-nav'),
                rExtraLargeDots = carousel.data('r-extra-large-dots'),
                center = carousel.data('center'),
                custom_nav = carousel.data('custom-nav') || '';
            carousel.addClass('owl-carousel');
            var owl = carousel.owlCarousel({
                loop: (loop ? true : false),
                items: (items ? items : 4),
                lazyLoad: true,
                margin: (margin ? margin : 0),
                autoplay: (autoplay ? true : false),
                autoplayTimeout: (autoplayTimeout ? autoplayTimeout : 1000),
                smartSpeed: (smartSpeed ? smartSpeed : 250),
                dots: (dots ? true : false),
                nav: (nav ? true : false),
                navText: ['<i class="fa fa-angle-left" aria-hidden="true"></i>', '<i class="fa fa-angle-right" aria-hidden="true"></i>'],
                navSpeed: (navSpeed ? true : false),
                center: (center ? true : false),
                responsiveClass: true,
                responsive: {
                    0: {
                        items: (rXsmall ? rXsmall : 1),
                        nav: (rXsmallNav ? true : false),
                        dots: (rXsmallDots ? true : false)
                    },
                    576: {
                        items: (rXmedium ? rXmedium : 2),
                        nav: (rXmediumNav ? true : false),
                        dots: (rXmediumDots ? true : false)
                    },
                    768: {
                        items: (rSmall ? rSmall : 3),
                        nav: (rSmallNav ? true : false),
                        dots: (rSmallDots ? true : false)
                    },
                    992: {
                        items: (rMedium ? rMedium : 4),
                        nav: (rMediumNav ? true : false),
                        dots: (rMediumDots ? true : false)
                    },
                    1200: {
                        items: (rLarge ? rLarge : 5),
                        nav: (rLargeNav ? true : false),
                        dots: (rLargeDots ? true : false)
                    },
                    1400: {
                        items: (rExtraLarge ? rExtraLarge : 6),
                        nav: (rExtraLargeNav ? true : false),
                        dots: (rExtraLargeDots ? true : false)
                    }
                }
            });
            if (custom_nav) {
                var nav = $(custom_nav),
                    nav_next = $('.rt-next', nav),
                    nav_prev = $('.rt-prev', nav);

                nav_next.on('click', function (e) {
                    e.preventDefault();
                    owl.trigger('next.owl.carousel');
                    return false;
                });

                nav_prev.on('click', function (e) {
                    e.preventDefault();
                    owl.trigger('prev.owl.carousel');
                    return false;
                });
            }
        });
    }


})(jQuery);