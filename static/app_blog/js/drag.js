/* 
 * date 2021-04-29
 * 拖动滑块
 */
(function ($) {

    var Drag = function (ele, options) {
        this.x,
            this.drag = ele,
            this.isMove = false,
            this.defaults = {
				success: function () { }
            };
        this.options = $.extend(this.defaults, options);
    }

    Drag.prototype = {
        init: function () {
            var _this = this;
            //添加背景，文字，滑块
            var html = '<div class="drag_bg"></div>' +
                '<div class="drag_text background-animation" onselectstart="return false;" unselectable="on">拖动滑块验证</div>' +
                '<div class="handler handler_bg"></div>';
            this.drag.append(html);

            var handler;
            _this.handler = handler = this.drag.find('.handler');
            var drag_bg = this.drag.find('.drag_bg');
            var maxWidth = this.drag.width() - handler.width();  //能滑动的最大间距

            handler.on('mousedown', handleDragStart);
            handler.on('touchstart', handleDragStart);

            $(document).on('mousemove', handleDragMove);
            $(document).on('touchmove', handleDragMove);

            $(document).on('mouseup', handleDragEnd);
            $(document).on('touchend', handleDragEnd);


            //鼠标按下时候的x轴的位置
            function handleDragStart(e) {
                console.log('down')
                _this.isMove = true;
                var originX = e.clientX || e.touches[0].pageX;
                _this.x = originX - parseInt(handler.css('left'), 10);
            };

            //鼠标指针在上下文移动时，移动距离大于0小于最大间距，滑块x轴位置等于鼠标移动距离
            function handleDragMove(e) {
                var originX = e.clientX || e.touches[0].pageX;
                var _x = originX - _this.x;
                if (_this.isMove) {
                    if (_x > 0 && _x <= maxWidth) {
                        handler.css({ 'left': _x });
                        drag_bg.css({ 'width': _x + 20 });
                        _this.drag.find('.drag_text').text('拖动滑块验证');
                    } else if (_x > maxWidth) {  //鼠标指针移动距离达到最大时清空事件
                        _this.drag.find('.drag_text').text('松开验证');
                    }
                }
            };

            function handleDragEnd(e) {
                if (_this.isMove){
                    var originX = e.clientX || e.changedTouches[0].pageX;
                    var _x = originX - _this.x;
                    if (_this.x) {
                        if (_x < maxWidth) { //鼠标松开时，如果没有达到最大距离位置，滑块就返回初始位置
                            console.log('reset')
                            handler.css({ 'left': 0 });
                            drag_bg.css({ 'width': 0 });
                            _this.drag.find('.drag_text').text('拖动滑块验证');
                        } else {
                            _this.dragOk();
                        }
                    }
                    _this.isMove = false;
                }
            };
        },

        //清空事件
        dragOk: function () {

            this.handler.removeClass('handler_bg').addClass('handler_ok_bg');
            this.drag.find('.drag_text').text('验证通过');
            this.drag.css({ 'color': '#fff' });

            this.handler.unbind('mousedown touchstart');

            // $(document).unbind('mousemove');
            // $(document).unbind('touchmove');
            // $(document).unbind('mouseup');
            // $(document).unbind('touchend');

            this.options.success();

            $('#login_submit').attr('disabled', false)
        }
    }

    // window.Drag = Drag;

	//在插件中使用 drag 对象
	$.fn.drag = function (options) {
		var d = new Drag(this, options);
		d.init();
	};



})(jQuery);


