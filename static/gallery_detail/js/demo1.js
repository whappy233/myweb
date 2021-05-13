/**
 * demo1.js
 * http://www.codrops.com
 *
 * Licensed under the MIT license.
 * http://www.opensource.org/licenses/mit-license.php
 * 
 * Copyright 2019, Codrops
 * http://www.codrops.com
 */
{
    const MathUtils = {
        lineEq: (y2, y1, x2, x1, currentVal) => {
            // y = mx + b 
            var m = (y2 - y1) / (x2 - x1), b = y1 - m * x1;
            return m * currentVal + b;
        },
        lerp: (a, b, n) =>  (1 - n) * a + n * b
    };

    // Window size
    let winsize;
    const calcWinsize = () => winsize = {width: window.innerWidth, height: window.innerHeight};
    calcWinsize();
    window.addEventListener('resize', calcWinsize);

    const getMousePos = (ev) => {
        let posx = 0;
        let posy = 0;
        if (!ev) ev = window.event;
        if (ev.pageX || ev.pageY) {
            posx = ev.pageX;
            posy = ev.pageY;
        }
        else if (ev.clientX || ev.clientY) 	{
            posx = ev.clientX + body.scrollLeft + docEl.scrollLeft;
            posy = ev.clientY + body.scrollTop + docEl.scrollTop;
        }
        return {x: posx, y: posy};
    }
    // 追踪鼠标位置
    let mousePos = {x: winsize.width/2, y: winsize.height/2};
    window.addEventListener('mousemove', ev => mousePos = getMousePos(ev));
    
    // 自定义鼠标光标
    class CursorFx {
        constructor(el) {
            this.DOM = {el: el};
            this.DOM.toggle = this.DOM.el.querySelector('.cursor__inner--circle');
            
            this.DOM.title = this.DOM.el.querySelector('.cursor__inner--text');
            this.bounds = {
                toggle: this.DOM.toggle.getBoundingClientRect(),
                title: this.DOM.title.getBoundingClientRect()
            };
            this.lastMousePos = {
                toggle: {x: mousePos.x - this.bounds.toggle.width/2, y: mousePos.y - this.bounds.toggle.height/2},
                title: {x: mousePos.x - this.bounds.title.width/2, y: mousePos.y - this.bounds.title.height/2}
            };
            this.lastScale = 1;
            this.lastOpacity = 1;
            requestAnimationFrame(() => this.render());
        }
        render() {
            // 鼠标在X轴上的移动距离
            const diff = this.lastMousePos.toggle.x - (mousePos.x - this.bounds.toggle.width/2);
            // 检查鼠标是否在窗口的右侧
            const rightSide = mousePos.x >= winsize.width/2;
            // Switch the side of the title element
            // 切换标题元素的侧面
            this.DOM.title.style.left = rightSide ? 'auto' : '30px';
            this.DOM.title.style.right = rightSide ? '30px' : 'auto';
            // The position of the title/toggle and the viewport side will determine the speed for both of these elements
            // 标题/切换和视口侧的位置将决定这两个元素的速度
            const lerpFactor = {
                toggle: rightSide ? diff < 0 ? 0.15 : 0.1 : diff < 0 ? 0.1 : 0.15,
                title: rightSide ? diff < 0 ? 0.1 : 0.15 : diff < 0 ? 0.15 : 0.1
            };
            // 给定先前计算的lerp值，更新鼠标位置值
            this.lastMousePos.toggle.x = MathUtils.lerp(this.lastMousePos.toggle.x, mousePos.x - this.bounds.toggle.width/2, lerpFactor.toggle);
            this.lastMousePos.toggle.y = MathUtils.lerp(this.lastMousePos.toggle.y, mousePos.y - this.bounds.toggle.height/2, lerpFactor.toggle);
            this.lastMousePos.title.x = MathUtils.lerp(this.lastMousePos.title.x, mousePos.x - this.bounds.title.width/2, lerpFactor.title);
            this.lastMousePos.title.y = MathUtils.lerp(this.lastMousePos.title.y, mousePos.y - this.bounds.title.height/2, lerpFactor.title);
            // 切换比例和不透明度值
            this.lastScale = MathUtils.lerp(this.lastScale, 1, 0.15);
            this.lastOpacity = MathUtils.lerp(this.lastOpacity, 1, 0.1);
            // 应用样式
            this.DOM.toggle.style.transform = `translateX(${(this.lastMousePos.toggle.x)}px) translateY(${this.lastMousePos.toggle.y}px) scale(${this.lastScale})`;
            this.DOM.toggle.style.opacity = this.lastOpacity;
            this.DOM.title.style.transform = `translateX(${(this.lastMousePos.title.x)}px) translateY(${this.lastMousePos.title.y}px)`;
            
            requestAnimationFrame(() => this.render());
        }
        setTitle(title) {
            // 设置跟随的标题
            this.DOM.title.innerHTML = title;
        }
        click() {
            // 缩小并淡出鼠标切换
            this.lastScale = .5;
            this.lastOpacity = 0;
        }
        toggle() {
            const isCircle = this.DOM.toggle.classList.contains('cursor__inner--circle');
            this.DOM.toggle.classList[isCircle ? 'remove' : 'add']('cursor__inner--circle');
            this.DOM.toggle.classList[isCircle ? 'add' : 'remove']('cursor__inner--cross');
            this.DOM.title.style.opacity = isCircle ? 0 : 1;
        }
    }

    const cursor = new CursorFx(document.querySelector('.cursor'));

    class Grid {
        constructor(el) {
            this.DOM = {el: el};
            // grid element
            this.DOM.grid = this.DOM.el.querySelector('.grid');
            // grid items
            this.DOM.items = [...this.DOM.grid.children];
            // 网格总数
            this.itemsTotal = this.DOM.items.length;
            // The content element (grid 的后面) 
            this.DOM.content = document.querySelector('.detail-content');
            this.DOM.contentTitle = this.DOM.content.querySelector('.info .title');
            this.DOM.contentTime = this.DOM.content.querySelector('.info .time');
            // 计算网格wrap和网格的高度，以及它们之间的区别（用于 grid/mousemove 平移）以及行数/列数
            this.calculateSize();
            // 网格初始化平移到中心
            this.gridTranslation = {x: 0, y: -1*this.extraHeight/2};
            // 线性插值缓动百分比（用于鼠标移动时的网格移动）
            this.lerpFactor = 0.04;
            this.initEvents();
            requestAnimationFrame(() => this.render());
        }
        calculateSize() {
            // The height of the grid wrap 网格包裹的高度
            this.height = this.DOM.el.offsetHeight;
            // The difference between the height of the grid wrap and the height of the grid. This is the amount we can translate the grid
            // 网格包装的高度和网格高度之间的差异。 这是我们可以转换网格的数量
            this.extraHeight = this.DOM.grid.offsetHeight - this.height;
            // Number of grid columns. The CSS variable --cell-number gives us the number of rows
            // 网格列数。 CSS变量 --cell-number 给出了行数
            this.columns = this.itemsTotal/getComputedStyle(this.DOM.grid).getPropertyValue('--cell-number');
            // The animejs stagger function needs an array [cols,rows]
            // animejs stagger 函数需要一个数组[cols，rows]
            this.gridDef = [this.columns, this.itemsTotal/this.columns];
        }
        initEvents() {
            // Window resize event 
            // 睡眠因子(lerpFactor)将更改为1，因此在转换网格时没有延迟（否则我们将看到顶部和底部的间隙）
            window.addEventListener('resize', () => {
                this.lerpFactor = 1;
                // Recalculate..
                this.calculateSize();
                this.columns = this.itemsTotal/getComputedStyle(this.DOM.grid).getPropertyValue('--cell-number');
                clearTimeout(this.resizeTimer);
                this.resizeTimer = setTimeout(() => this.lerpFactor = 0.04, 250);
            });

            this.DOM.items.forEach((item, pos) => {
                // The item's title.
                const title = item.dataset.title;
                const time = item.dataset.time;
                // 在光标旁边显示标题。
                item.addEventListener('mouseenter', () => cursor.setTitle(`${time}<br/>${title}`));
                item.addEventListener('click', () => {
                    // Position of the clicked item 点击项目的位置
                    this.pos = pos;
                    this.title = title;
                    this.time = time;
                    this.showContent();  // 开始效果并显示背后的内容
                    // Force to show the title next to the cursor (it might not update because of the grid animation - the item under the mouse can be a different one than the one the user moved the mouse to)
                    // 强制在光标旁边显示标题（由于网格动画它可能不会更新-鼠标下的项可以与用户将鼠标移到的项不同）
                    cursor.setTitle(title);
                });
            });
            
            // 显示网格
            this.DOM.content.addEventListener('click', () => this.showGrid());
        }
        // 这是发生主网格效果的地方，对框进行动画处理并显示 '背后' 的内容
        showContent() {
            if ( this.isAnimating ) {
                return false;
            }
            this.isAnimating = true;
            // 设置 content 背景图片和标题
            this.DOM.content.style.backgroundImage = this.DOM.items[this.pos].querySelector('.grid__item-inner').style.backgroundImage.replace(/img/g, 'img/large');
            this.DOM.contentTitle.innerHTML = this.title;
            this.DOM.contentTime.innerHTML = this.time;
            // 缩小并淡出鼠标切换
            cursor.click();
            cursor.toggle();
            
            this.animation = anime({
                targets: this.DOM.items,
                duration: 20,
                easing: 'easeOutQuad',
                opacity: 0,
                delay: anime.stagger(70, {grid: this.gridDef, from: this.pos})
            });
            this.animation.finished.then(() => {
                // Pointer events class
                this.DOM.el.classList.add('grid-wrap--hidden');
                this.isAnimating = false;
            });

            /*
            // Animates the title
            anime({
                targets: this.DOM.contentTitle,
                duration: 1700,
                delay: 200,
                easing: 'easeOutExpo',
                opacity: [0,1],
                translateY: [50,0]
            });
            */
        }
        showGrid() {
            if ( this.isAnimating ) {
                return false;
            }
            this.isAnimating = true;
            cursor.click();
            cursor.toggle();
            this.DOM.el.classList.remove('grid-wrap--hidden');
            // 本来可以使用reverse（），但似乎有一个错误（glitch 毛刺）。
            this.animation = anime({
                targets: this.DOM.items,
                duration: 20,
                easing: 'easeOutQuad',
                opacity: [0,1],
                delay: anime.stagger(70, {grid: this.gridDef, from: this.pos, direction: 'reverse'})
            });
            this.animation.finished.then(() => this.isAnimating = false);
        }
        // 鼠标移动时平移grid
        render() {
            // 平移将为 0 或 -1 * this.extraHeight, 具体取决于鼠标在y轴上的位置
            this.gridTranslation.y = MathUtils.lerp(
                this.gridTranslation.y, 
                Math.min(
                    Math.max(
                        MathUtils.lineEq(-1*this.extraHeight, 0, this.height-this.height*.1, this.height*.1, mousePos.y),
                        -1*this.extraHeight),
                    0),
                this.lerpFactor);

            this.DOM.grid.style.transform = `translateY(${this.gridTranslation.y}px)`; 
            requestAnimationFrame(() => this.render());
        }
    }

    // grid 初始化
    new Grid(document.querySelector('.grid-wrap'));

    // 预加载页面中的所有图像
    imagesLoaded(document.querySelectorAll('.grid__item-inner, img'), {background: true}, () => document.body.classList.remove('loading'));
}