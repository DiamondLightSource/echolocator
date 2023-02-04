// --------------------------------------------------------------------

// inherit the base methods and variables
webviz__ChartArea.prototype = new maxiv__common__Base();

// provide an explicit name for the base class
webviz__ChartArea.prototype.base = maxiv__common__Base.prototype;

// override the constructor
webviz__ChartArea.prototype.constructor = webviz__ChartArea;

// -------------------------------------------------------------------------------
// constructor (functioning as a prototype, this constructor cannot take arguments)

function webviz__ChartArea(runtime, classname) {
    var F = "webviz__ChartArea";

    // we are not doing a prototype construction?
    if (arguments.length > 0) {
        var F = "webviz__ChartArea";

        // call the base class constructor helper 
        webviz__ChartArea.prototype.base.constructor.call(
            this,
            runtime,
            classname != undefined ? classname : F);

    }

} // end constructor

// -------------------------------------------------------------------------------
// Connect to server.

webviz__ChartArea.prototype.activate = function (div_id, options) {
    var F = "webviz__ChartArea::activate";

    this.div_id = div_id;
    this.$div = $("#" + div_id);

} // end method


// -------------------------------------------------------------

webviz__ChartArea.prototype.clear = function () {
    var F = "webviz__ChartArea::clear";

    console.log(F + ": clearing");

}

// -------------------------------------------------------------

webviz__ChartArea.prototype.render = function () {
    var F = "webviz__ChartArea::render";

}

