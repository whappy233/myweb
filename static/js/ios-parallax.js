(function($){
  $.iosParallax = function(el, options){
    // 为避免范围问题，请使用 'base' 而不是 'this' 从内部事件和函数中引用此类。
    var base = this;

    // 访问元素的jQuery和DOM版本
    base.$el = $(el);
    base.el = el;

    // 添加对DOM对象的反向引用
    base.$el.data("iosParallax", base);

    var centerCoordinates = {x: 0, y: 0};
    var targetCoordinates = {x: 0, y: 0};
    var transitionCoordinates = {x: 0, y: 0};

    function getBackgroundImageUrl(){
      var backgroundImage = base.$el.css('background-image').match(/url\(.*\)/ig);
      if ( ! backgroundImage || backgroundImage.length < 1) {
        throw 'No background image found';
      }
      return backgroundImage[0].replace(/url\(|'|"|'|"|\)$/ig, "");
    }

    function getBackgroundImageSize(){
      var img = new Image;
      img.src = getBackgroundImageUrl();
      return {width: img.width, height: img.height};
    }

    function setCenterCoordinates(){
      var bgImgSize = getBackgroundImageSize();
      centerCoordinates.x = -1 * Math.abs(bgImgSize.width - base.$el.width()) / 2;
      centerCoordinates.y = -1 * Math.abs(bgImgSize.height - base.$el.height()) / 2;
      targetCoordinates.x = centerCoordinates.x;
      targetCoordinates.y = centerCoordinates.y;
      transitionCoordinates.x = centerCoordinates.x;
      transitionCoordinates.y = centerCoordinates.y;
    }

    function bindEvents(){
      base.$el.mousemove(function(e){
        var width = base.options.movementFactor / base.$el.width();
        var height = base.options.movementFactor / base.$el.height();
        var cursorX = e.pageX - ($(window).width() / 2);
        var cursorY = e.pageY - ($(window).height() / 2);
        targetCoordinates.x = width * cursorX * -1 + centerCoordinates.x;
        targetCoordinates.y = height * cursorY * -1 + centerCoordinates.y;
      });


      // 以60 FPS的速度将背景图像位置缓慢收敛到目标坐标
      var loop = setInterval(function(){
        transitionCoordinates.x += ((targetCoordinates.x - transitionCoordinates.x) / base.options.dampenFactor);
        transitionCoordinates.y += ((targetCoordinates.y - transitionCoordinates.y) / base.options.dampenFactor);
        base.$el.css("background-position", transitionCoordinates.x+"px "+transitionCoordinates.y+"px");
      }, 16);

      $(window).resize(function(){
        // 使图片居中
        setCenterCoordinates();
      });

      // 未加载图像时获取图像的高度和宽度存在问题。
      var img = new Image;
      img.src = getBackgroundImageUrl();
      $(img).on('load',function(){setCenterCoordinates();})
    };

    base.init = function(){
      base.options = $.extend({}, $.iosParallax.defaultOptions, options);
      bindEvents();
    };

    base.init();
  };

  $.iosParallax.defaultOptions = {
    // 背景移动的速度
    movementFactor: 50,
    // 多大程度地抑制运动（越大速度越慢）
    dampenFactor: 36
  };

  $.fn.iosParallax = function(options){
    return this.each(function(){
      (new $.iosParallax(this, options));
    });
  };

})(jQuery);

