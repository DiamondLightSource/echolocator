class webviz__Transformer extends common__Base {

    constructor(runtime) {
        super(runtime);
        this.set_data({ x1: 0, y1: 0, x2: 100, y2: 100 });
        this.set_view({ x1: 0, y1: 0, x2: 100, y2: 100 });
    } // end constructor

    // -------------------------------------------------------------

    set_data(data_rect) {
        var F = "webviz__Transformer::set_data";

        this._data_rect = data_rect;

        // this.debug(F, "[DEROI] data rect is " + JSON.stringify(this._data_rect));

        this._data_width = this._data_rect.x2 - this._data_rect.x1;
        this._data_height = this._data_rect.y2 - this._data_rect.y1;

        var xscale = this._view_width / this._data_width;
        var yscale = this._view_height / this._data_height;
        this._scale_data_to_view = Math.min(xscale, yscale);

    } // end method

    // -------------------------------------------------------------

    set_view(view_rect) {
        var F = "webviz__Transformer::set_view";

        this._view_rect = view_rect;

        // this.debug(F, "[DEROI] view rect is " + JSON.stringify(this._view_rect));

        this._view_width = this._view_rect.x2 - this._view_rect.x1;
        this._view_height = this._view_rect.y2 - this._view_rect.y1;

        var xscale = this._view_width / this._data_width;
        var yscale = this._view_height / this._data_height;
        this._scale_data_to_view = Math.min(xscale, yscale);

    } // end method

    // -------------------------------------------------------------
    // Transform data position to view position.

    data_to_view(data_position) {
        var F = "webviz__Transformer::data_to_view";

        // this.debug(F, "[DEROI] data rect is " + JSON.stringify(this._data_rect));
        // this.debug(F, "[DEROI] view rect is " + JSON.stringify(this._view_rect));

        var data_tx = this._data_rect.x1;
        var data_ty = this._data_rect.y1;

        var view_position = {
            x: (data_position.x - data_tx) * this._scale_data_to_view,
            y: (data_position.y - data_ty) * this._scale_data_to_view
        };

        // Invert sense of y axis.
        // view_position.y = this._view_height - view_position.y;

        view_position.x = parseInt(view_position.x.toFixed(0))
        view_position.y = parseInt(view_position.y.toFixed(0))

        return view_position;
    } // end method

    // -------------------------------------------------------------
    // Transform data position to view position.

    view_to_data(view_position) {

        var data_tx = this._data_rect.x1;
        var data_ty = this._data_rect.y1;

        var data_position = {
            x: view_position.x / this._scale_data_to_view + data_tx,
            y: view_position.y / this._scale_data_to_view + data_ty
        };

        // Invert sense of y axis.
        // data_position.y = this._data_height - data_position.y;

        data_position.x = parseInt(data_position.x.toFixed(0))
        data_position.y = parseInt(data_position.y.toFixed(0))

        return data_position;
    } // end method
} // end class
