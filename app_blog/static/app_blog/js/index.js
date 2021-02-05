function main() {

  var root = document.getElementById("root");
  function appendContainer(text) {
    var container = document.createElement("div");
    // container.className = "";
    root.appendChild(container);

    if (text) {
      var introduce = document.createElement("div");
      introduce.className = "introduce";
      var textNode = document.createTextNode(text);
      introduce.appendChild(textNode);
      container.appendChild(introduce);
    }
    return container;
  }

  function azxvz() {
    var text = "";
    var images = ["./assets/1.png", "./assets/2.png", "./assets/3.png"];
    var images = [
      {
        tagName: "div",
        attrs: {
          style:
            "width:100%; height: 100%; background-color: pink; font-size: 32px; color: #fff;"
        },
        children: [
          "It's not just picture",
          {
            tagName: "div",
            attrs: {
              style:
                "width:100%; height: 100%; background-color: pink; font-size: 14px; color: #fff;"
            },
            children: [
              "text text text text text text text text text text text text text"
            ]
          }
        ]
      },
      {
        tagName: "a",
        attrs: {
          href: "https://metxnbr.github.io/awesome-slider/demo/assets/2.png",
          style: "width:100%; height: 100%",
          target: "_blank"
        },
        children: [
          {
            tagName: "img",
            attrs: {
              src: "./assets/2.png",
              style: "width:100%; height: 100%"
            }
          }
        ]
      },
      {
        tagName: "img",
        attrs: {
          src: "./assets/3.png",
          style: "width:100%; height: 100%"
        }
      },
      {
        tagName: "img",
        attrs: {
          src: "./assets/none.png",
          style: "width:100%; height: 100%"
        }
      }
    ];
    var container = appendContainer(text);
    var awesomeSlider = new AwesomeSlider(images, container, {
      autoplay: true,  // 自动播放
      manual: manual(), // 手动切换按钮
      // ratio: 2 / 1, // 图片的宽高比
      // indicator: indicator(), // 自定义指示器
      // initIndex: 1, // 初始展示第2张
      imageDownloading: imageDownloading(), // 加载时的效果
      imagePlaceholder: imagePlaceholder(), // 加载失败时的占位
      duration: 1000 * 1,
      timing: "easeOutCubic"  // 轮播切换效果
    });
  }
  azxvz();

}

// 指示器
function indicator() {
  var text = "";
  var wrap = null;
  return {
    style: function () {
      text = this.options.initIndex + 1 + " / " + this.realLen;
      wrap = document.createElement("div");
      wrap.className = "custom-indicator-wrap";
      var textNode = document.createTextNode(text);
      wrap.appendChild(textNode);
      this.eleCollections.listWrap.appendChild(wrap);
    },

    active: function () {
      text = this.current + " / " + this.realLen;
      wrap.innerText = text;
    }
  };
}

// 切换
function manual() {
  var previous = document.createElement("div");
  previous.className = "manual-btn manual-previous";

  var next = document.createElement("div");
  next.className = "manual-btn manual-next";

  return {
    previous: previous,
    next: next
  };
}

function imageDownloading() {
  var ele = document.createElement("div");
  ele.className = "image-downloading";
  var text = document.createTextNode("loading...");
  ele.appendChild(text);
  return ele;
}

// 图片占位
function imagePlaceholder() {
  var ele = document.createElement("div");
  ele.className = "image-placeholder";
  var text = document.createTextNode("error");
  ele.appendChild(text);
  return ele;
}

function readyGo(func) {
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", func);
  } else {
    func();
  }
}

readyGo(main);
