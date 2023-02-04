// --------------------------------------------------------------------

// inherit the base methods and variables
webviz__ImageArea.prototype = new maxiv__common__Base();

// provide an explicit name for the base class
webviz__ImageArea.prototype.base = maxiv__common__Base.prototype;

// override the constructor
webviz__ImageArea.prototype.constructor = webviz__ImageArea;

// -------------------------------------------------------------------------------
// constructor (functioning as a prototype, this constructor cannot take arguments)

function webviz__ImageArea(runtime, classname) {
    var F = "webviz__ImageArea";

    // we are not doing a prototype construction?
    if (arguments.length > 0) {
        var F = "webviz__ImageArea";

        // call the base class constructor helper 
        webviz__ImageArea.prototype.base.constructor.call(
            this,
            runtime,
            classname != undefined ? classname : F);

    }

} // end constructor

// -------------------------------------------------------------------------------
// Connect to server.

webviz__ImageArea.prototype.activate = function (div_id, options) {
    var F = "webviz__ImageArea::activate";

    this.div_id = div_id;
    this.$div = $("#" + div_id);

} // end method


// -------------------------------------------------------------

webviz__ImageArea.prototype.clear = function () {
    var F = "webviz__ImageArea::clear";

    console.log(F + ": clearing");

}

// -------------------------------------------------------------

webviz__ImageArea.prototype.render = function () {
    var F = "webviz__ImageArea::render";

}

