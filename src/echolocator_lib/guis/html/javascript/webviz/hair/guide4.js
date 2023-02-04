
// --------------------------------------------------------------------
// class representing a spreading operation

// inherit the base methods and variables
webviz__hair__Guide4.prototype = new maxiv__common__Base();

// override the constructor
webviz__hair__Guide4.prototype.constructor = webviz__hair__Guide4;

// -------------------------------------------------------------------------------
// constructor (functioning as a prototype, this constructor cannot take arguments)

function webviz__hair__Guide4(page, name, classname) {
    // we are not doing a prototype construction?
    if (arguments.length > 0) {
        var F = "webviz__hair__Guide4";

        this.parent = maxiv__common__Base.prototype;
        /* call the base class constructor helper */
        this.parent.constructor.call(
            this,
            page !== undefined ? page.runtime : undefined,
            classname !== undefined ? classname : F);

        this.page = page;
        this.name = name;
        this.debug_identifier = name;
    }
} // end constructor

// -------------------------------------------------------------

webviz__hair__Guide4.prototype.activate = function (raphael) {
    var F = "activate";

    this._raphael = raphael

    this._ul_guide = new webviz__hair__Guide2(this.page, this.name + "_ul", "red");
    this._lr_guide = new webviz__hair__Guide2(this.page, this.name + "_lr", "red");

    this._pi_ul_guide = new webviz__hair__Guide2(this.page, this.name + "_pi_ul", "yellow");
    this._pi_lr_guide = new webviz__hair__Guide2(this.page, this.name + "_pi_lr", "yellow");

    this._bg_ul_guide = new webviz__hair__Guide2(this.page, this.name + "_bg_ul", "blue");
    this._bg_lr_guide = new webviz__hair__Guide2(this.page, this.name + "_bg_lr", "blue");

    this._ul_guide.activate(raphael, "red");
    this._lr_guide.activate(raphael, "red");

    this._pi_ul_guide.activate(raphael, "yellow");
    this._pi_lr_guide.activate(raphael, "yellow");

    this._bg_ul_guide.activate(raphael, "blue");
    this._bg_lr_guide.activate(raphael, "blue");

    settings = this._ul_guide.get();
    this.debug(F, "ul guide is at [" + settings.position.x + ", " + settings.position.y + "]")

    this.aoi_lr_set = { position: { x: 200, y: 200 } };
    this.aoi_ul_set = { position: { x: 0, y: 0 } };
    this.aoi_set_pointers(this.aoi_ul_set, this.aoi_lr_set);
    settings = this._lr_guide.get();

    this.debug(F, "lr guide is at [" + settings.position.x + ", " + settings.position.y + "]")

    this.pi_ul_set = { position: { x: 50, y: 50 } }
    this.pi_lr_set = { position: { x: 150, y: 150 } }
    this.pi_set_pointers(this.pi_ul_set, this.pi_lr_set);

    this.bg_ul_set = { position: { x: 75, y: 75 } }
    this.bg_lr_set = { position: { x: 125, y: 125 } }
    this.bg_set_pointers(this.bg_ul_set, this.bg_lr_set);

    var that = this;

    //this.$aoi_rect_button = $("#aoi_rect_button")
    //this.$aoi_rect_button.click(function(jquery_event_object) {that.aoi_set_pointers();})

    this._lr_guide._group.drag(function () { that.drawlines_aoi(); });
    this._ul_guide._group.drag(function () { that.drawlines_aoi(); });
    this._pi_lr_guide._group.drag(function () { that.drawlines_pi(); });
    this._pi_ul_guide._group.drag(function () { that.drawlines_pi(); });
    this._bg_lr_guide._group.drag(function () { that.drawlines_bg(); });
    this._bg_ul_guide._group.drag(function () { that.drawlines_bg(); });

}



webviz__hair__Guide4.prototype.toggle_elements = function (element, action) {
    if (element == "pi") {
        this._pi_ul_guide.toggle_visibility(action);
        this._pi_lr_guide.toggle_visibility(action);
    }
    if (element == "aoi") {
        this._ul_guide.toggle_visibility(action);
        this._lr_guide.toggle_visibility(action);
    }
    if (element == "bg") {
        this._bg_ul_guide.toggle_visibility(action);
        this._bg_lr_guide.toggle_visibility(action);
    }
}

// -------------------------------------------------------------
// Returns the currents settings in a JSON-serializable structure.

webviz__hair__Guide4.prototype.get = function () {
    var F = "get";

    ul_settings = this._ul_guide.get();
    lr_settings = this._lr_guide.get();
    pi_ul_settings = this._pi_ul_guide.get();
    pi_lr_settings = this._pi_lr_guide.get();
    bg_ul_settings = this._bg_ul_guide.get();
    bg_lr_settings = this._bg_lr_guide.get();

    // this.debug(F, "ul_settings is \"" + JSON.stringify(ul_settings) + "\"");
    // this.debug(F, "lr_settings is \"" + JSON.stringify(lr_settings) + "\"");

    settings = { ul: ul_settings, lr: lr_settings, pi_ul: pi_ul_settings, pi_lr: pi_lr_settings, bg_ul: bg_ul_settings, bg_lr: bg_lr_settings }

    return settings;
}

webviz__hair__Guide4.prototype.drawlines_aoi = function () {
    var F = "drawlines_aoi";

    ul_settings = this._ul_guide.get();
    lr_settings = this._lr_guide.get();

    var lr_hpath = "M" + 0 + "," + (-lr_settings.position.y + ul_settings.position.y) + ":L" + 0 + "," + 0;
    var lr_vpath = "M" + (-lr_settings.position.x + ul_settings.position.x) + "," + 0 + ":L" + 0 + "," + 0;
    this._lr_guide._hline.attr("path", lr_hpath)
    this._lr_guide._vline.attr("path", lr_vpath)

    var ul_hpath = "M" + 0 + "," + (-ul_settings.position.y + lr_settings.position.y) + ":L" + 0 + "," + 0;
    var ul_vpath = "M" + (-ul_settings.position.x + lr_settings.position.x) + "," + 0 + ":L" + 0 + "," + 0;
    this._ul_guide._hline.attr("path", ul_hpath)
    this._ul_guide._vline.attr("path", ul_vpath)

}

webviz__hair__Guide4.prototype.drawlines_pi = function () {
    var F = "drawlines_pi";

    ul_settings = this._pi_ul_guide.get();
    lr_settings = this._pi_lr_guide.get();

    var lr_hpath = "M" + 0 + "," + (-lr_settings.position.y + ul_settings.position.y) + ":L" + 0 + "," + 0;
    var lr_vpath = "M" + (-lr_settings.position.x + ul_settings.position.x) + "," + 0 + ":L" + 0 + "," + 0;
    this._pi_lr_guide._hline.attr("path", lr_hpath)
    this._pi_lr_guide._vline.attr("path", lr_vpath)

    var ul_hpath = "M" + 0 + "," + (-ul_settings.position.y + lr_settings.position.y) + ":L" + 0 + "," + 0;
    var ul_vpath = "M" + (-ul_settings.position.x + lr_settings.position.x) + "," + 0 + ":L" + 0 + "," + 0;
    this._pi_ul_guide._hline.attr("path", ul_hpath)
    this._pi_ul_guide._vline.attr("path", ul_vpath)

} // end method

webviz__hair__Guide4.prototype.drawlines_bg = function () {
    var F = "drawlines_bg";

    ul_settings = this._bg_ul_guide.get();
    lr_settings = this._bg_lr_guide.get();

    var lr_hpath = "M" + 0 + "," + (-lr_settings.position.y + ul_settings.position.y) + ":L" + 0 + "," + 0;
    var lr_vpath = "M" + (-lr_settings.position.x + ul_settings.position.x) + "," + 0 + ":L" + 0 + "," + 0;
    this._bg_lr_guide._hline.attr("path", lr_hpath)
    this._bg_lr_guide._vline.attr("path", lr_vpath)

    var ul_hpath = "M" + 0 + "," + (-ul_settings.position.y + lr_settings.position.y) + ":L" + 0 + "," + 0;
    var ul_vpath = "M" + (-ul_settings.position.x + lr_settings.position.x) + "," + 0 + ":L" + 0 + "," + 0;
    this._bg_ul_guide._hline.attr("path", ul_hpath)
    this._bg_ul_guide._vline.attr("path", ul_vpath)

} // end method

// Reset distance line
webviz__hair__Guide4.prototype.reset_element_position = function (element) {
    var F = "reset_element_position";

    if (element == "pi") {
        this.pi_set_pointers(this.pi_ul_set, this.pi_lr_set);
    }
    if (element == "bg") {
        this.bg_set_pointers(this.bg_ul_set, this.bg_lr_set);
    }
    if (element == "aoi") {
        this.aoi_set_pointers(this.aoi_ul_set, this.aoi_lr_set);
    }
    this.toggle_elements(element, "show")

}

webviz__hair__Guide4.prototype.aoi_set_pointers = function (setting_ul, setting_lr) {
    var F = "aoi_set_pointers";

    this._ul_guide.set_pointer(setting_ul);
    this._lr_guide.set_pointer(setting_lr);

    this.drawlines_aoi();

} // end method

webviz__hair__Guide4.prototype.pi_set_pointers = function (setting_pi_ul, setting_pi_lr) {
    var F = "pi_set_pointers";

    this._pi_ul_guide.set_pointer(setting_pi_ul);
    this._pi_lr_guide.set_pointer(setting_pi_lr);

    this.drawlines_pi();

} // end method

webviz__hair__Guide4.prototype.bg_set_pointers = function (setting_bg_ul, setting_bg_lr) {
    var F = "bg_set_pointers";

    this._bg_ul_guide.set_pointer(setting_bg_ul);
    this._bg_lr_guide.set_pointer(setting_bg_lr);

    this.drawlines_bg();

} // end method