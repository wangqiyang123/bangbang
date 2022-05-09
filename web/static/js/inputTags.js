/**
 @ Name：输入框标签
 @ Author：Jioho
 */

class inputTags {

    // 初始化配置
    constructor(config = {}) {
        var tmp_content = config.content ? new Set(config.content) : [];
        // 基础配置
        this.content = [...tmp_content]; // 标签内容  Set去重
        this.theme = config.theme || '#1e9fff'; // 标签样式
        this.elem = config.elem; //绑定的 id 或者 class
        this.inputType = config.inputType || 'text';
        this.placeholder = config.placeholder || '回车生成标签';

        // 回调事件
        this.beforeEnter = config.beforeEnter; // 回车前事件
        this.afterEnter = config.afterEnter; // 回车回调

        // 事件代理
        this.proxy = {};

        this.init();
        return this;
    };

    // 事件监听
    on(event, callback) {
        this.proxy[event] = callback;
    }

    // 公共方法获取tag标签
    getTagsHtml(content) {
        return "<div class='inputTags--tag' style='background:" + this.theme + ";'><span name='value'>" + content + "</span><span class='icon'>×</span></div>";
    };

    // 初始化
    init() {
        var self = this,
            inputTags_input = "<input class='inputTags--input' type='" + self.inputType + "' placeholder='" + self.placeholder + "' autocomplete='off' >",
            tags_html = "";

        // 设置主色调
        $(self.elem + " .inputTags--tag").css('background', '#FFB800');
        // 添加容器样式  添加主input框
        $(self.elem).addClass('inputTags--container').html(inputTags_input);

        // 循环添加标签
        self.content.forEach((v, k) => {
            tags_html += self.getTagsHtml(v);
        });
        $(self.elem + " input").before(tags_html);

        // 监听事件
        self.bindEvent();
        self.bindDelTag();
    }

    // 监听回车
    bindEvent() {
        var self = this;
        $(self.elem + " input").keypress(function (e) {
            var keynum = e.keyCode ? e.keyCode : e.which;

            if (keynum == '13') {
                var input_obj = this;
                // 生成标签前
                if (self.beforeEnter && self.beforeEnter() == false) {
                    return false;
                }
                // 生成标签
                self.render([$(input_obj).val().trim()]);
                // 生成标签回调
                self.afterEnter && self.afterEnter(self.content);
            }
        })
    }

    // 渲染标签
    render(tag_text_array) {
        var self = this;
        tag_text_array.forEach((v, k) => {
            if (v != '' && self.content.indexOf(v) == -1) {
                // 添加标签
                $(self.elem + " input").before(self.getTagsHtml(v));
                self.content.push(v);
            }
        })

        // 清空input内容
        $(self.elem + " input").val('');
    }

    // 绑定删除标签事件
    bindDelTag() {
        var self = this;
        $(self.elem).on('click', '.inputTags--tag', function (obj) {
            self.delTag(this);
        })
    }

    // 删除标签事件
    delTag(obj) {
        var self = this;
        var del_text = $(obj).find('span').text(),
            del_index = self.content.indexOf(del_text);

        // 删除索引
        self.content.splice(del_index, 1);
        // 删除标签
        $(obj).remove();

        // 订阅者模式
        self.proxy['delTag'] && self.proxy['delTag'](self.content);
    }

    // 清空输入框
    clearAll() {
        this.content = [];
        $(this.elem + " .inputTags--tag").remove();
    }

    // 重新加载内容
    reload(conetnt) {
        var tmp_content = conetnt ? new Set(conetnt) : [];
        // 先清空
        this.clearAll();
        // 渲染
        this.render([...tmp_content]);
    }

    // 获取全部数据
    getValue() {
        return this.content;
    }

}