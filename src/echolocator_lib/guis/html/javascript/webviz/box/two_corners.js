var webviz__box__TwoCorners__MotionChangeEvent = "webviz__box__TwoCorners__MotionChangeEvent";
var webviz__box__TwoCorners__UserChangeEvent = "webviz__box__TwoCorners__UserChangeEvent";

// --------------------------------------------------------------------
// class representing a spreading operation

// inherit the base methods and variables
webviz__box__TwoCorners.prototype = new maxiv__common__Base();

// override the constructor
webviz__box__TwoCorners.prototype.constructor = webviz__box__TwoCorners;

// -------------------------------------------------------------------------------
// constructor (functioning as a prototype, this constructor cannot take arguments)

function webviz__box__TwoCorners(runtime, name, classname) {
    // we are not doing a prototype construction?
    if (arguments.length > 0) {
        var F = "webviz__box__TwoCorners";

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

webviz__box__TwoCorners.prototype.activate = function (raphael, color) {
    var F = "webviz__box__TwoCorners::activate";

    this._raphael = raphael;

    // Put edge primitive in the canvas first so the balls will have higher click priority.
    this._edge_primitive = raphael.path("M0,0:L0,1").attr({
        stroke: color,
        "stroke-width": 1
    });

    this._corner1 = new webviz__sprite__Shape(this.runtime, this.name + "_corner1", color);
    this._corner2 = new webviz__sprite__Shape(this.runtime, this.name + "_corner2", color);

    this._corner1.activate(raphael, color);
    this._corner2.activate(raphael, color);

    var that = this;

    // Listen for motion changes on corner1.
    this._corner1.attach_trigger(
        webviz__sprite__Shape__UserMotionEvent,
        function (unused) {
            that._handle_motion_change();
        }
    );

    // Listen for motion changes on corner2.
    this._corner2.attach_trigger(
        webviz__sprite__Shape__UserMotionEvent,
        function (unused) {
            that._handle_motion_change();
        }
    );

    // Listen for final changes on corner1.
    this._corner1.attach_trigger(
        webviz__sprite__Shape__UserFinalEvent,
        function (unused) {
            that._handle_final_change();
        }
    );

    // Listen for final changes on corner2.
    this._corner2.attach_trigger(
        webviz__sprite__Shape__UserFinalEvent,
        function (unused) {
            that._handle_final_change();
        }
    );

} // end method

// -------------------------------------------------------------
// Motion change in a corner position.

webviz__box__TwoCorners.prototype._handle_motion_change = function () {
    var F = "_handle_motion_change";

    this._draw_edges();

    this.pull_triggers(webviz__box__TwoCorners__MotionChangeEvent, undefined)

} // end method

// -------------------------------------------------------------
// Final change in a corner position.

webviz__box__TwoCorners.prototype._handle_final_change = function () {
    var F = "_handle_final_change";

    // Normalize corner positions so that corner1 is in the upper left.
    this._normalize();

    this._draw_edges();

    this.pull_triggers(webviz__box__TwoCorners__UserChangeEvent, undefined)

} // end method


// -------------------------------------------------------------
// Draw box edges.

webviz__box__TwoCorners.prototype._draw_edges = function () {
    var F = "_draw_edges";

    p1 = this._corner1.get().position;
    p2 = this._corner2.get().position;

    dx = p2.x - p1.x;
    dy = p2.y - p1.y;
    pos_dx = dx.toFixed(3);
    pos_dy = dy.toFixed(3);
    neg_dx = (-dx).toFixed(3);
    neg_dy = (-dy).toFixed(3);

    path = "M" + p1.x.toFixed(3) + "," + p1.y.toFixed(3);
    path += " l" + pos_dx + ",0"
    path += " l0," + pos_dy;
    path += " l" + neg_dx + ",0"
    path += " l0," + neg_dy;

    this._edge_primitive.attr("path", path)

} // end method

// -------------------------------------------------------------
webviz__box__TwoCorners.prototype.set = function (settings) {
    var F = "set";

    // Look for known settings.
    for (var k in settings) {
        setting = settings[k];

        if (k == "position1") {
            this._corner1.set({ position: setting });
        }
        else
            if (k == "position2") {
                this._corner2.set({ position: setting });
            }
            else
                // The setting is for visibility?
                if (k == "visible") {
                    this._corner1.set({ visible: setting });
                    this._corner2.set({ visible: setting });
                    if (setting)
                        this._edge_primitive.show();
                    else
                        this._edge_primitive.hide();
                }
    }

    this._draw_edges();

} // end method

// -------------------------------------------------------------
// Returns the currents settings in a JSON-serializable structure.

webviz__box__TwoCorners.prototype.get = function () {
    var F = "get";

    settings = { position1: this._corner1.get().position, position2: this._corner2.get().position };

    return settings;
} // end method

// -------------------------------------------------------------
// Normalize corner positions.

webviz__box__TwoCorners.prototype._normalize = function () {
    var F = "_normalize";

    position1 = this._corner1.get().position;
    position2 = this._corner2.get().position;

    if (position1.x > position2.x ||
        position1.y > position2.y) {
        this._corner1.set({ position: { x: Math.min(position1.x, position2.x), y: Math.min(position1.y, position2.y) } })
        this._corner2.set({ position: { x: Math.max(position1.x, position2.x), y: Math.max(position1.y, position2.y) } })
    }


} // end method
