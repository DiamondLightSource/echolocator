

class webviz__sprite__Ring extends common__Base {

    constructor(page, name, classname, precisionLine = false) {
        super(page.runtime);

        this.page = page;
        this.name = name;
        this.debug_identifier = name;
        this.precisionLine = precisionLine;
    } // end constructor

    // -------------------------------------------------------------

    activate(raphael, color) {
        var F = "webviz__sprite__Ring[" + this.name + "]::activate";

        this._raphael = raphael

        raphael.setStart();

        // this._group = this._raphael.path("M0,0:L10,0:L0,10:L0,0").attr({ 
        //     fill: "#FF0000", 
        //     stroke: "#000000", 
        //     "stroke-width": 1 
        // }); 

        // Dot at the center.
        // this._center = this._raphael.circle(0, 0, 5).attr({
        //     fill: color,
        //     stroke: "black",
        //     "stroke-width": 1
        // });

        this._raphael.circle(0, 0, 1).attr({
            fill: "transparent",
            stroke: "white",
            "stroke-width": 5,
            "stroke-dasharray": "--",
        });

        this._raphael.circle(0, 0, 1).attr({
            fill: "transparent",
            stroke: "black",
            "stroke-width": 2,
            "stroke-dasharray": "--",
        });

        // matrix = Raphael.matrix(1, 0, 0, 1, 0, 0, 0, 0, 0);
        // matrix.translate(0, 0)
        // console.log(F + " raphael matrix is \"" + matrix.toTransformString() + "\"")
        // this._group.translate(1, 1);
        // console.log(F + " ball matrix is \"" + this._group.matrix.toTransformString() + "\"")

        this._group = this._raphael.setFinish()

        console.log(F + ": activated")
    } // end method

    // -------------------------------------------------------------
    set(settings) {
        var F = "webviz__sprite__Ring[" + this.name + "]::set";

        for (var k in settings) {
            var setting = settings[k];

            if (k == "position") {
                // console.log(F + ": [CENTPO] setting position [" + setting.x + ", " + setting.y + "]");

                // Something wrong with settings?
                if (!isNaN(setting.x) && !isNaN(setting.y)) {
                    this._group.transform("");
                    this._group.translate(setting.x, setting.y);
                }
                else {
                    console.log(F + ": something is wrong with the position setting")
                }
            }
            if (k == "scale") {
                // console.log(F + ": [CENTPO] setting scale " + setting)

                // Something wrong with settings?
                if (!isNaN(setting)) {
                    this._group.scale(setting);
                }
                else {
                    console.log(F + ": [CENTPO] something is wrong with the scale setting")
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
        var F = "webviz__sprite__Ring[" + this.name + "]::get";

        var settings = {};

        // Position to where the group's anchor point has been moved.
        var x = this._group.matrix.x(0, 0);
        var y = this._group.matrix.y(0, 0);

        settings.position = { x: x, y: y };

        return settings;
    } // end method

} // end class
