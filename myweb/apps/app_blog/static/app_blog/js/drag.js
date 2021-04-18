/* 
 * date 2021-02-18
 * 拖动滑块
 */
(function($){

    var Drag = function(ele, options){
        this.x, 
        this.drag = ele, 
        this.isMove = false, 
        this.defaults = {};
        this.options = $.extend(this.defaults, options);
    }

    Drag.prototype = {
        init: function(){
            var _this = this;
            //添加背景，文字，滑块
            var html = '<div class="drag_bg"></div>'+
                        '<div class="drag_text" onselectstart="return false;" unselectable="on">拖动滑块验证</div>'+
                        '<div class="handler handler_bg"></div>';
            this.drag.append(html);

            var handler ;
            _this.handler = handler = this.drag.find('.handler');
            var drag_bg = this.drag.find('.drag_bg');
            var maxWidth = this.drag.width() - handler.width();  //能滑动的最大间距

            //鼠标按下时候的x轴的位置
            handler.mousedown(function(e){
                _this.isMove = true;
                _this.x = e.pageX - parseInt(handler.css('left'), 10);
            });

            //鼠标指针在上下文移动时，移动距离大于0小于最大间距，滑块x轴位置等于鼠标移动距离
            $(document).mousemove(function(e){
                var _x = e.pageX - _this.x;
                if(_this.isMove){
                    if(_x > 0 && _x <= maxWidth){
                        handler.css({'left': _x});
                        drag_bg.css({'width': _x+20});
                    }else if(_x > maxWidth){  //鼠标指针移动距离达到最大时清空事件
                        _this.dragOk();
                    }
                }
            }).mouseup(function(e){
                _this.isMove = false;
                var _x = e.pageX - _this.x;
                if(_x < maxWidth){ //鼠标松开时，如果没有达到最大距离位置，滑块就返回初始位置
                    handler.css({'left': 0});
                    drag_bg.css({'width': 0});
                }
            });
        },

        //清空事件
        dragOk: function(){

            this.handler.removeClass('handler_bg').addClass('handler_ok_bg');
            this.drag.find('.drag_text').text('验证通过');
            this.drag.css({'color': '#fff'});
            this.handler.unbind('mousedown');
            $(document).unbind('mousemove');
            $(document).unbind('mouseup');

            $('#login_submit').attr('disabled', false)
        }
    }

    $.fn.drag = function(options){
		var d = new Drag(this, options);
		d.init();
        return d
    };

})(jQuery);


