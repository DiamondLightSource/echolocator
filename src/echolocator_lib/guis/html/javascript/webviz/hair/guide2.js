var webviz__hair__Guide2__UserChangeEvent = "webviz__hair__Guide2__UserChangeEvent";
var webviz__hair__Guide2__UserMotionEvent = "webviz__hair__Guide2__UserMotionEvent";


class webviz__hair__Guide2 extends common__Base {

    constructor(page, name, classname, precisionLine = false) {
        super(page.runtime);

        this.page = page;
        this.name = name;
        this.debug_identifier = name;
        this.precisionLine = precisionLine;
    } // end constructor

    // -------------------------------------------------------------

    activate(raphael, color) {
        var F = "webviz__hair__Guide2::activate";

        this._raphael = raphael

        raphael.setStart();

        this._hline = this._raphael.path("M0,0:L1,0").attr({
            stroke: color,
            "stroke-width": 1
        });

        this._vline = this._raphael.path("M0,0:L0,1").attr({
            stroke: color,
            "stroke-width": 1
        });

        // this._ball = this._raphael.path("M0,0:L10,0:L0,10:L0,0").attr({ 
        //     fill: "#FF0000", 
        //     stroke: "#000000", 
        //     "stroke-width": 1 
        // }); 

        this._ball = this._raphael.circle(0, 0, 5).attr({
            fill: color,
            stroke: "#000000",
            "stroke-width": 1
        });

        // matrix = Raphael.matrix(1, 0, 0, 1, 0, 0, 0, 0, 0);
        // matrix.translate(0, 0)
        // console.log(F + " raphael matrix is \"" + matrix.toTransformString() + "\"")
        // this._ball.translate(1, 1);
        // console.log(F + " ball matrix is \"" + this._ball.matrix.toTransformString() + "\"")

        this._group = this._raphael.setFinish()
        this._group._parent_object = this;

        this._hline._group = this._group;
        this._hline._parent_object = this;

        this._vline._group = this._group;
        this._vline._parent_object = this;

        this._ball._group = this._group;
        this._ball._parent_object = this;

        this._group.drag(this._drag_move, this._drag_start, this._drag_stop);

        console.log(F + " activated")
    } // end method

    // -------------------------------------------------------------
    set_box(settings) {
        var F = "webviz__hair__Guide2::set_box";

        for (var k in settings) {
            var setting = settings[k];

            if (k == "position") {
                console.log(F + ": setting position [" + setting.x + ", " + setting.y + "]")

                // Something wrong with settings?
                if (!isNaN(setting.x) && !isNaN(setting.y)) {
                    this._group.transform("");
                    this._group.translate(setting.x, setting.y);

                    var hpath = "M" + 0 + "," + -10000 + ":L" + 0 + "," + 10000;
                    var vpath = "M" + -10000 + "," + 0 + ":L" + 10000 + "," + 0;

                    // console.log(F + " hpath " + hpath)
                    // console.log(F + " vpath " + vpath)
                    this._hline.attr("path", hpath)
                    this._vline.attr("path", vpath)
                }
                else {
                    console.log(F + ": something is wrong with the position setting")
                }
            }
            // The setting is for visibility?
            else if (k == "visible") {
                if (setting)
                    this._group.show();
                else
                    this._group.hide();
            }

        }
    } // end method

    // -------------------------------------------------------------
    // Returns the currents settings in a JSON-serializable structure.

    get() {
        var F = "webviz__hair__Guide2::get";

        var settings = {};

        // Position to where the group's anchor point has been moved.
        var x = this._ball.matrix.x(0, 0);
        var y = this._ball.matrix.y(0, 0);

        settings.position = { x: x, y: y };

        return settings;
    } // end method

    // -------------------------------------------------------------
    _drag_move(dx, dy) {
        this._group.translate(dx - this.odx, dy - this.ody);
        this.odx = dx;
        this.ody = dy;

        this._parent_object._trigger_change_event(webviz__hair__Guide2__UserMotionEvent);

    } // end method

    // -------------------------------------------------------------
    _drag_start() {
        var F = "webviz__hair__Guide2::_drag_start";

        console.log(F + " drag start")

        // var keys = new Array();
        // for (var k in this)
        // {
        //     keys.push(k);
        // }
        // console.log("this is " + this.toString() + "\n" + JSON.stringify(keys));
        this.odx = 0;
        this.ody = 0;

        this.timeout = undefined;
    }

    // -------------------------------------------------------------
    _drag_stop() {
        var F = "webviz__hair__Guide2::_drag_stop";

        // Not yet started the timeout?
        if (this.timeout === undefined) {
            console.log(F + " drag stop");
            var that = this;
            // Notify listeners in separate thread.
            this.timeout = setTimeout(function () {
                that._parent_object._trigger_change_event(webviz__hair__Guide2__UserChangeEvent)
            }, 1);
        }
    }

    // -------------------------------------------------------------
    _trigger_change_event(event, detail) {
        var F = "webviz__hair__Guide2::_trigger_change_event";

        if (event == webviz__hair__Guide2__UserChangeEvent)
            console.log(F + " triggering " + event);

        // Trigger an event that the index.js will use to coordinate cross-widget changes.
        var custom_event = new CustomEvent(event,
            {
                detail: detail
            });

        this.dispatchEvent(custom_event);
    }
} // end class

// document.onclick = function(event_object) { for (var property in event_object) console.log(property + ": " + event_object[property]); }

// isTrusted: true
// screenX: 307
// screenY: 214
// clientX: 159
// clientY: 101
// ctrlKey: false
// shiftKey: false
// altKey: false
// metaKey: false
// button: 0
// buttons: 0
// relatedTarget: null
// pageX: 159
// pageY: 101
// x: 159
// y: 101
// offsetX: 154
// offsetY: 96
// movementX: 0
// movementY: 0
// fromElement: null
// toElement: [object SVGCircleElement]
// layerX: 154
// layerY: 96
// getModifierState: function getModifierState() { [native code] }
// initMouseEvent: function initMouseEvent() { [native code] }
// view: [object Window]
// detail: 1
// sourceCapabilities: [object InputDeviceCapabilities]
// which: 1
// initUIEvent: function initUIEvent() { [native code] }
// type: click
// target: [object SVGCircleElement]
// currentTarget: [object HTMLDocument]
// eventPhase: 3
// bubbles: true
// cancelable: true
// defaultPrevented: false
// composed: true
// timeStamp: 2730.014999397099
// srcElement: [object SVGCircleElement]
// returnValue: true
// cancelBubble: false
// path: [object SVGCircleElement],[object SVGSVGElement],[object HTMLDivElement],[object HTMLBodyElement],[object HTMLHtmlElement],[object HTMLDocument],[object Window]
// NONE: 0
// CAPTURING_PHASE: 1
// AT_TARGET: 2
// BUBBLING_PHASE: 3
// composedPath: function composedPath() { [native code] }
// initEvent: function initEvent() { [native code] }
// preventDefault: function preventDefault() { [native code] }
// stopImmediatePropagation: function stopImmediatePropagation() { [native code] }
// topPropagation: function stopPropagation() { [native code] }
