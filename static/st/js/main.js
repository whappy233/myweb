(function ($) {
    "use strict";
    /*-------------------------------------
    Theia Side Bar
    -------------------------------------*/
    if (typeof ($.fn.theiaStickySidebar) !== "undefined") {
        $('#fixed-bar-coloum').theiaStickySidebar({
            'additionalMarginTop': 50,
            'sidebarBehavior': 'stick-to-top'
        });
    }

    // 消息提示插件
    toastr.options = {
        timeOut: 3000,
        progressBar: true,
        showMethod: "slideDown",
        hideMethod: "slideUp",
        showDuration: 200,
        hideDuration: 200
    };
    // toastr.success('Successfully completed');
    // toastr.error('Something went wrong');
    // toastr.info('This is an informational message');
    // toastr.warning('You are currently not authorized');
    // toastr.clear();




    /*-------------------------------------
    图片懒加载
    --------------------------------------*/
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
        if(!el.src){
            var source = el.dataset.src;
            el.src = source;
            $(el).animate({opacity:'1'}, 500);
            $(el).removeClass('loading').addClass('img-animation').removeAttr('data-src');

        }
    };
    window.onload = window.onscroll = function () { //onscroll()在滚动条滚动的时候触发
        check();
    };


    /*-------------------------------------
    对带有 data-href 属性的元素进行跳转
    -------------------------------------*/
    $('#main').on('click', '[data-href]', function () {
        console.log($(this).data("href"));
        window.location = $(this).data("href");
    });



    /*-------------------------------------
    对 data-event="show_hide" mousedown 显示密码
    -------------------------------------*/
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





    /*-------------------------------------
    MeanMenu 响应式导航栏
    --------------------------------------*/
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

    /*-------------------------------------
    Offcanvas Menu activation code
    -------------------------------------*/
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
        }

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

    /*-------------------------------------
    On Scroll 
    -------------------------------------*/
    $(window).on('scroll', function () {
        // Back Top Button
        if ($(window).scrollTop() > 700) {
            $('.scrollup').addClass('back-top');
        } else {
            $('.scrollup').removeClass('back-top');
        }
        if ($('body').hasClass('sticky-header')) {
            var stickyPlaceHolder = $("#rt-sticky-placeholder"),
                menu = $("#header-menu"),
                mobile_menu = $('.mean-bar'),
                menuH = menu.outerHeight(),
                topHeaderH = $('#header-topbar').outerHeight() || 0,
                middleHeaderH = $('#header-middlebar').outerHeight() || 0,
                targrtScroll = topHeaderH + middleHeaderH;
            if ($(window).scrollTop() > targrtScroll) {
                menu.addClass('rt-sticky');
                mobile_menu.addClass('rt-sticky');
                stickyPlaceHolder.height(menuH);
            } else {
                menu.removeClass('rt-sticky');
                mobile_menu.removeClass('rt-sticky');
                stickyPlaceHolder.height(0);
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

    // appendTo


    /*---------------------------------------
    On Click Section Switch
    --------------------------------------- */
    $('[data-type="section-switch"]').on('click', function () {
        if (location.pathname.replace(/^\//, '') === this.pathname.replace(/^\//, '') && location.hostname === this.hostname) {
            var target = $(this.hash);
            if (target.length > 0) {
                target = target.length ? target : $('[name=' + this.hash.slice(1) + ']');
                $('html,body').animate({
                    scrollTop: target.offset().top
                }, 1000);
                return false;
            }
        }
    });

    /*-------------------------------------
    点击显示搜索 Jquery Serch Box
    -------------------------------------*/
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


    /*-------------------------------------
    主题切换 Dark/Light mode
    -------------------------------------*/
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
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', listeners.dark);
    window.matchMedia('(prefers-color-scheme: light)').addEventListener('change', listeners.light);

    // 手动切换
    $('.sticky-header').on('click', '.dark_mode', function(){
        let body = $(".sticky-header"),
            theme = body.attr('data-theme'),
            theme_n = theme=='light'?'dark':'light'
        $(".sticky-header").attr('data-theme', theme_n);
        window.localStorage.setItem("theme", theme_n);
    });

    /*-------------------------------------
    对 data-bg-image='img/product/top-product1.jpg' 带有
    该属性的标签设置对应的背景图片
    -------------------------------------*/
    // data-bg-image='img/product/top-product1.jpg'
    $("[data-bg-image]").each(function () {
        var img = $(this).data("bg-image");
        $(this).css({
            backgroundImage: "url(" + img + ")"
        });
    });

    /*-------------------------------------
    页面加载动画 Page Preloader
    -------------------------------------*/
    $(".preloader").fadeOut(1000, function () {
        $(this).remove();
    });

    /*-------------------------------------
    Masonry
    -------------------------------------*/
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

    $(function () {

        /*-------------------------------------
        Video Popup
        -------------------------------------*/
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

        /*-------------------------------------
        Carousel slider initiation
        -------------------------------------*/
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
    });

})(jQuery);