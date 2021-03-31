/*Starlight.js: A sparkling visual effects library
Created by Serj Babayan
View on Github at https://www.github.com/sergei1152/Starlight.js
Licence: MIT
*/

//TODO Fix resizing issues
//TODO 1: ADD SVG support
//TODO 2: FIX the keep_list true and rotation false instant expand glitch

//put your custom configuration settings here
var user_configuration = {
	shape:"circle",				// "circle" or "square"
	initial_size:"6px",		// 星形尺寸（以像素为单位）
	final_size:"24px",			// 膨胀后恒星的最终大小
	expand_speed:"0.5s",		// 星星变大的速度（以毫秒为单位）
	fade_delay:"0.5s",			// 直到多久星星开始消失
	fade_duration:"0.6s",		// 星星消失了多长时间
	// 各种颜色的星星。 可以是任何符合CSS的颜色（例如，十六进制，rgba，hsl）
	colors:[
		"#81C784",
		"#B3E5FC",
		"#B39DDB",
	],
	frequency:500,  			// 新一波新星弹出的频率（以毫秒为单位。更大==更长）
	density:10,  				// 每波会弹出多少颗星星
	keep_lit:false,				// 恒星创建后是否消失
	rotation:false,				// 恒星是否旋转通过其膨胀
	coverage:1,					// 星星将在（0-1）中显示多少个元素区域
	target_class:'.starlight',	// 脚本基于类名称定位的元素
	custom_svg:""

};

//这是如果您要真正自定义星星的显示方式
var advanced_configuration = {
	expand_transition_timing: "linear", //could be ease, ease-in, ease-out, etc
	expand_delay: "0s",  //恒星多久开始膨胀
	rotation_transition_timing: "linear",  //could be ease, ease-in, ease-out, etc
	rotation_angle: "360deg", //最多旋转到
	rotation_duration: "1s", //旋转将发生多长时间
	rotation_delay: "0s", //多长时间开始旋转
	fade_transition_timing: "linear", //could be ease, ease-in, ease-out, etc
	z_index: 1 //星星的位置绝对正确，因此您可以根据需要为其指定z-index
};

//星体及其位置
function Star(width, height) {
	//需要偏移量，以便当用户指定coverage时，coverage围绕div的中心而不是左上角
	leftOffset = Math.round((width - width * user_configuration.coverage) / 2);
	topOffset = (height - Math.round(height * user_configuration.coverage)) / 2;
	this.xposition = Math.floor(Math.random() * width * user_configuration.coverage) + leftOffset;
	this.yposition = Math.floor(Math.random() * height * user_configuration.coverage) + topOffset;
}

//the star CSS properties
Star.prototype.create = function (parent_element, id) {
	//容器在那里，所以当恒星膨胀时它们会围绕中心膨胀
	var star = $('<div></div>');
	var star_container = $('<div id=\"starlight-star' + id + '\"></div>');
	// star_container.attr("id","star"+id);
	star_container.append(star);

	//因此，随着容器的扩展，恒星保持居中
	star.css({
		position: "absolute",
		top: "-50%",
		left: "-50%",
		width: "100%",
		height: "100%",
	});

	//星星的初始CSS属性，包括颜色，位置和大小
	star_container.css({
		width: user_configuration.initial_size,
		height: user_configuration.initial_size,
		position: 'absolute',
		top: this.yposition,
		left: this.xposition,
		"z-index": advanced_configuration.z_index
	});

	//设置星形的过渡CSS属性
	setTimeout(function () {
		star_container.css({ //尺寸扩展属性
			transition: "height " + user_configuration.expand_speed + " " + advanced_configuration.expand_transition_timing + " " + advanced_configuration.expand_delay + "," +
				"width " + user_configuration.expand_speed + " " + advanced_configuration.expand_transition_timing + " " + advanced_configuration.expand_delay,
			width: user_configuration.final_size,
			height: user_configuration.final_size
		});

		//因为过渡属性相互覆盖，所以必须创建过渡变量并将过渡附加到变量上
		if (user_configuration.rotation) { //旋转特性
			star.css({
				transform: "rotate(" + advanced_configuration.rotation_angle + ")"
			});
			var transition = advanced_configuration.rotation_duration + " " + advanced_configuration.rotation_transition_timing + " " + advanced_configuration.rotation_delay;
		}

		if (!user_configuration.keep_lit) {//隐藏特性
			star.css({
				opacity: 0
			});
			if (transition) {
				transition += ",opacity " + user_configuration.fade_duration + " " + advanced_configuration.fade_transition_timing + " " + user_configuration.fade_delay;
			}
			else {
				var transition = "opacity " + user_configuration.fade_duration + " " + advanced_configuration.fade_transition_timing + " " + user_configuration.fade_delay;
			}

			//淡出后从dom中删除该元素
			setTimeout(function () {
				$("#starlight-star" + id).remove();
			}, css_time_to_milliseconds(user_configuration.fade_duration) + css_time_to_milliseconds(user_configuration.fade_delay));
		}

		if (transition) {
			star.css({
				transition: transition
			});
		}

	}, 10);

	//设置星星的形状和颜色
	if (user_configuration.shape === 'circle') {
		star.css('border-radius', '50%');
	}
	if (user_configuration.custom_svg === '' || user_configuration.custom_svg === false) {
		star.css('background-color', user_configuration.colors[Math.floor(Math.random() * user_configuration.colors.length)]); //picks one of the colors
	}
	parent_element.append(star_container);
};


//根据用户定义的频率和密度处理恒星的实际生成
$(document).ready(function () {
	var id = 0;
	//通过'starlight'类遍历所有元素
	$(user_configuration.target_class).each(function (index) {
		var currentElement = $(this);
		var width = currentElement.width();
		var height = currentElement.height();
		setInterval(function () { //根据频率和所需密度创建星星
			for (var i = 0; i < user_configuration.density; i++) {
				var newStar = new Star(width, height);
				newStar.create(currentElement, id);
				newStar = null; //以防万一垃圾收集器清除此值
				id++;
			}
		}, user_configuration.frequency);
	});
});

//retrieved from https://gist.github.com/jakebellacera/9261266
function css_time_to_milliseconds(time_string) {
	var num = parseFloat(time_string, 10),
		unit = time_string.match(/m?s/),
		milliseconds;

	if (unit) {
		unit = unit[0];
	}

	switch (unit) {
		case "s": // seconds
			milliseconds = num * 1000;
			break;
		case "ms": // milliseconds
			milliseconds = num;
			break;
		default:
			milliseconds = 0;
			break;
	}

	return milliseconds;
}