
(function ($) {
    function _ngpGetAttributes(node) {
        var d = {},
            re_dataAttr = /^data-nrad\-(.+)$/;

        $.each(node.get(0).attributes, function (index, attr) {
            if (re_dataAttr.test(attr.nodeName)) {
                var key = attr.nodeName.match(re_dataAttr)[1];
                d[key] = isNaN(attr.nodeValue) ? attr.nodeValue : +attr.nodeValue;
            }
        });

        return d;
    }

    $.fn.ninjaRadial = function (options) {
        this.each(function () {
            var _nrad = $(this);

            var _parameters = $.extend({
                data: {},
                innerSize: 180,
                borderSize: 10,
                distance: 60,
                backColor: "transparent",
                borderColor: "transparent",
                itemHeight: 40,
                itemWidth: 40,
                lineHeight: 40,
                buttons: null,
                onLoad: null
            }, options);

            if (_parameters == null)
                _parameters = new Array();

            _nrad.css({ "position": "relative" });
            _nrad.on("click", { nrad: _nrad, parameters: _parameters }, function (e) {
                var nrad = e.data.nrad;
                var parameters = e.data.parameters;

                var dataItem = _ngpGetAttributes(nrad);

                var px = e.pageX;
                var py = e.pageY;

                var wrapper = $(".ninjaRadial");
                if (wrapper.length == 0) {
                    wrapper = $('<div>', { "class": "ninjaRadial" }).bind("click", function (e) {
                        $(this).toggleClass("open");
                    });
                }

                if (!wrapper.hasClass("open")) {
                    wrapper.css({
                        left: px,
                        top: py,
                        marginLeft: -parameters.borderSize - (parameters.innerSize / 2),
                        marginTop: -parameters.borderSize - (parameters.innerSize / 2),
                        width: parameters.innerSize + 'px',
                        height: parameters.innerSize + 'px',
                        borderWidth: parameters.borderSize + 'px',
                        backgroundColor: parameters.backColor,
                        borderColor: parameters.borderColor
                    }).html("");
                }
                else {
                    wrapper.toggleClass("open");
                    return;
                }

                var params = $.extend(true, {}, parameters);

                if (typeof parameters.onLoad === 'function') {
                    parameters.onLoad(nrad, params);
                }

                var qtd = params.buttons.length;
                for (var i = 0; i < qtd; i++) {
                    var button = params.buttons[i];

                    var left = (params.innerSize / 2) + (params.distance * (Math.cos(((2 * Math.PI / qtd) * i) - (Math.PI / 2)).toFixed(4)));
                    var top = (params.innerSize / 2) + (params.distance * (Math.sin(((2 * Math.PI / qtd) * i) - (Math.PI / 2)).toFixed(4)));

                    var divItem = $("<div>", { "class": "nradItem" }).css({
                        width: params.itemWidth,
                        height: params.itemHeight,
                        left: left - (params.itemWidth / 2),
                        top: top - (params.itemHeight / 2),
                        lineHeight: params.itemHeight + 'px'
                    }).addClass(button.cssItem);

                    divItem.bind("click", { btn: button, dataItem: dataItem }, function (e) {
                        if (typeof button.click === 'function') {
                            e.data.btn.click(e, e.data.dataItem, nrad);
                        }
                    });

                    var icon = $("<i>", { "class": button.cssIcon }).addClass(button.cssIcon);

                    var label = $("<label>", { "class": button.cssLabel }).css({
                        fontSize: '10px',
                        lineHeight: '12px',
                        width: params.itemWidth,
                    }).addClass(button.cssLabel).html(button.text);

                    divItem.append(icon);
                    divItem.append(label);
                    wrapper.append(divItem);
                }

                if ($(".ninjaRadial").length == 0) {
                    $('body').append(wrapper);
                }

                $(document).bind("click", function () {
                    var wrapper = $(".ninjaRadial.open");
                    if (wrapper.length > 0) {
                        wrapper.toggleClass("open");
                    }
                });
                setTimeout(function () {
                    wrapper.toggleClass("open");
                }, 1);
            });

            _nrad.data("_ninjaRadial", _nrad);
        });
    };
}(jQuery));