// --------------------------------------------------------------------

// inherit the base methods and variables
webviz__Histogram.prototype = new maxiv__common__Base();

// provide an explicit name for the base class
webviz__Histogram.prototype.base = maxiv__common__Base.prototype;

// override the constructor
webviz__Histogram.prototype.constructor = webviz__Histogram;

// -------------------------------------------------------------------------------
// constructor (functioning as a prototype, this constructor cannot take arguments)

function webviz__Histogram(runtime, classname) {
    var F = "webviz__Histogram";

    // we are not doing a prototype construction?
    if (arguments.length > 0) {
        var F = "webviz__Histogram";

        // call the base class constructor helper 
        webviz__Histogram.prototype.base.constructor.call(
            this,
            runtime,
            classname != undefined ? classname : F);

        this.paper = undefined;
        this.dots = [];
    }

} // end constructor

// -------------------------------------------------------------------------------
// Connect to server.

webviz__Histogram.prototype.activate = function (div_id, options) {
    var F = "webviz__Histogram::activate";

    this.div_id = div_id;
    this.$div = $("#" + div_id);

    this.canvas = Raphael(this.div_id, "100%", "100%");

    this.maximum_points = 900;
    this.total_poked_dot_count = 0;

    // World coordinate rate.
    // TODO: make these configurable.
    let xmin = -50;
    let ymin = -50;
    let xmax = 50;
    let ymax = 50;

    // Matrix to scale world coordinates to pixels;
    this.matrix = Raphael.matrix(1, 0, 0, 1, 0, 0);
    this.matrix.scale((this.$div.width() / (xmax - xmin)));
    this.matrix.translate(-xmin, -ymin);

} // end method

// -------------------------------------------------------------
webviz__Histogram.prototype.poke_dot = function (x, y, t) {
    var F = "webviz__Histogram::poke_dot";

    // Transform world coordinates to pixels.
    // TODO: use embedded element matrix attribute instead.
    x = this.matrix.x(x, y);
    y = this.matrix.y(x, y);
    radius = 2;

    // Color change count.
    let dot_repeat_length = 101;

    // Color regime.
    let dot_repeat_number = Math.floor(this.total_poked_dot_count / dot_repeat_length);

    if (dot_repeat_number % 3 === 1)
        dot_color = "blue";
    else
        if (dot_repeat_number % 3 === 2)
            dot_color = "orange";
        else
            dot_color = "red";

    dot = this.canvas.circle(x, y, radius).attr({ fill: dot_color });

    this.dots.push(dot)

    if (this.dots.length > this.maximum_points) {
        dot = this.dots.shift();
        dot.remove();
    }

    this.render();

    this.total_poked_dot_count++;
}

// -------------------------------------------------------------

webviz__Histogram.prototype.clear = function () {
    var F = "webviz__Histogram::clear";

    console.log(F + ": clearing");

    this.canvas.clear();

}

// -------------------------------------------------------------

webviz__Histogram.prototype.render = function () {
    var F = "webviz__Histogram::render";

}

