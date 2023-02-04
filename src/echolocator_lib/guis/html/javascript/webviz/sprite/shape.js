var webviz__sprite__Shape__UserFinalEvent = "webviz__sprite__Shape__UserFinalEvent";
var webviz__sprite__Shape__UserMotionEvent = "webviz__sprite__Shape__UserMotionEvent";

// --------------------------------------------------------------------
// class representing a spreading operation

// inherit the base methods and variables
webviz__sprite__Shape.prototype = new maxiv__common__Base();

// override the constructor
webviz__sprite__Shape.prototype.constructor = webviz__sprite__Shape;

// -------------------------------------------------------------------------------
// constructor (functioning as a prototype, this constructor cannot take arguments)

function webviz__sprite__Shape(runtime, name, classname) {
    // we are not doing a prototype construction?
    if (arguments.length > 0) {
        var F = "webviz__sprite__Shape";

        this.parent = maxiv__common__Base.prototype;
        /* call the base class constructor helper */
        this.parent.constructor.call(
            this,
            runtime,
            classname !== undefined ? classname : F);

        this.name = name;
        this.debug_identifier = name;
    }
} // end constructor

// -------------------------------------------------------------

webviz__sprite__Shape.prototype.activate = function (raphael, color) {
    var F = "webviz__sprite__Shape::activate";

    this._raphael = raphael

    raphael.setStart();

    this._ball = this._raphael.circle(0, 0, 5).attr({
        fill: color,
        stroke: "#000000",
        "stroke-width": 1
    });

    this._group = this._raphael.setFinish()
    this._group._parent_object = this;

    this._ball._group = this._group;

    this._group.drag(this._drag_move, this._drag_start, this._drag_stop);

    this.debug(F, "activated color " + color);
} // end method

// -------------------------------------------------------------
webviz__sprite__Shape.prototype.set = function (settings) {
    var F = "set_pointer";

    for (var k in settings) {
        setting = settings[k];

        if (k == "position") {
            this._group.transform("");
            this._group.translate(setting.x, setting.y);
        }

        else
            // The setting is for visibility?
            if (k == "visible") {
                if (setting)
                    this._group.show();
                else
                    this._group.hide();
            }
    }
} // end method

// -------------------------------------------------------------
// Returns the currents settings in a JSON-serializable structure.

webviz__sprite__Shape.prototype.get = function () {
    var F = "get";

    settings = {};

    // Position to where the group's anchor point has been moved.
    x = this._ball.matrix.x(0, 0);
    y = this._ball.matrix.y(0, 0);

    settings.position = { x: x, y: y };

    return settings;
} // end method

// -------------------------------------------------------------
webviz__sprite__Shape.prototype._drag_move = function (dx, dy) {
    this._group.translate(dx - this.odx, dy - this.ody);
    this.odx = dx;
    this.ody = dy;

    parent = this._group._parent_object
    parent.pull_triggers(webviz__sprite__Shape__UserMotionEvent, undefined);

} // end method

// -------------------------------------------------------------
webviz__sprite__Shape.prototype._drag_start = function () {
    var F = "_drag_start";

    this._group._parent_object.debug(F, "drag start")

    this.odx = 0;
    this.ody = 0;

    this.timeout = undefined;
}

// -------------------------------------------------------------
webviz__sprite__Shape.prototype._drag_stop = function () {
    var F = "_drag_stop";

    // Not yet started the timeout?
    if (this.timeout === undefined) {
        parent = this._group._parent_object
        parent.debug(F, "drag stop");
        var that = this;
        // Notify listeners in separate thread.
        this.timeout = setTimeout(function () { parent.pull_triggers(webviz__sprite__Shape__UserFinalEvent, undefined); }, 1);
    }
}
