// --------------------------------------------------------------------

// inherit the base methods and variables
webviz__Justgage.prototype = new maxiv__common__Base();

// provide an explicit name for the base class
webviz__Justgage.prototype.base = maxiv__common__Base.prototype;

// override the constructor
webviz__Justgage.prototype.constructor = webviz__Justgage;

// -------------------------------------------------------------------------------
// constructor (functioning as a prototype, this constructor cannot take arguments)

function webviz__Justgage(runtime, classname) {
    var F = "webviz__Justgage";

    // we are not doing a prototype construction?
    if (arguments.length > 0) {
        var F = "webviz__Justgage";

        // call the base class constructor helper 
        webviz__Justgage.prototype.base.constructor.call(
            this,
            runtime,
            classname != undefined ? classname : F);

        this.tag = "";
        this.metric = "";
        this.minimum_value = 0;
        this.maximum_value = 100;
        this.current_value = 0;
    }

} // end constructor

// -------------------------------------------------------------------------------
// Connect to server.

webviz__Justgage.prototype.activate = function (div_id, options) {
    var F = "webviz__Justgage::activate";

    this.div_id = div_id;

    this.gauge = new JustGage({
        title: options["title"],
        id: this.div_id,
        value: this.current_value,
        min: this.minimum_value,
        max: this.maximum_value,
        decimals: 0,
        label: "bytes/sec",
        gaugeWidthScale: 1.0,
        humanFriendly: true
    });

} // end method

// -------------------------------------------------------------
webviz__Justgage.prototype.poke_metrics = function (metrics) {
    var F = "webviz__Justgage::poke_metrics";

    this.current_value = metrics[this.metric];

    if (isNaN(this.current_value))
        this.current_value = 0;

    // console.log(F + ": current value is " + this.current_value + ", maximum value is " + this.maximum_value);

    if (this.current_value > this.maximum_value)
        this.maximum_value = Math.ceil(this.current_value);

    this.render();
}

// -------------------------------------------------------------

webviz__Justgage.prototype.render = function () {
    var F = "webviz__Justgage::handle_success";

    this.gauge.refresh(this.current_value, this.maximum_value);
}

