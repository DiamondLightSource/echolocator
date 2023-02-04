class Targeting extends echolocator__Page {
    #raphael = null;
    #transformer = null;
    #image_list_ux = null;
    #image_edit_ux = null;
    #pixel_ux = null;
    #last_loaded_image_info = null;

    constructor(runtime) {
        super(runtime);
    } // end constructor


    // -------------------------------------------------------------------------------
    _stretch_height(thing, height) {
        var $thing = $(thing)
        var available = height - $thing.offset().top;
        $thing.innerHeight(available);
        return thing +
            " from top " + $thing.offset().top.toFixed(0) +
            " to height " + height.toFixed(0) +
            " has " + available.toFixed(0) + " available\n"
    }
    // -------------------------------------------------------------------------------
    _sizewatch_thing(thing) {
        return thing + " top " + $(thing).offset().top.toFixed(0) + ", height " + $(thing).innerHeight().toFixed(0) + "\n";
    }

    // -------------------------------------------------------------------------------
    _sizewatch() {
        var text = "";

        var window_height = $("BODY").innerHeight();
        text += this._stretch_height("#image_edit_ux_interaction_parent", window_height - 16);

        text += this._sizewatch_thing("BODY");
        text += this._sizewatch_thing("#image_edit_ux_interaction_parent");
        $("#sizewatch").text(text);

        console.log(text);
    }

    // -------------------------------------------------------------------------------
    // Called after page is loaded and all DOM elements are available.
    activate() {
        var F = "Targeting::activate";
        super.activate();

        var that = this;

        // Make a raphael drawing object.
        this.#raphael = Raphael("raphael1_paper", 4000, 4000);

        // For transforming coordinates between data and view.
        this.#transformer = new webviz__Transformer(this.runtime);

        // Pass this transformer to anyone who wants to use the raphael for drawing.
        this.#raphael.webviz_transformer = this.#transformer;

        // Make a spreader which reacts to resizing of the window.
        this.image1_spreader = new webviz__Spreader(this);

        // -------------------------------------------------------------------

        this.#image_list_ux = new echolocator__ImageListUx(
            self.runtime,
            "image_list",
            $("#image_list_ux_interaction_parent"));

        this.#image_edit_ux = new echolocator__ImageEditUx(
            self.runtime,
            "image_edit",
            $("#image_edit_ux_interaction_parent"));

        this.#pixel_ux = new echolocator__PixelUx(
            self.runtime,
            "pixel",
            $("#pixel_ux_interaction_parent"));

        // -------------------------------------------------------------------

        var that = this;

        // User picks an image from the image list.
        this.#image_list_ux.addEventListener(
            echolocator__Events_IMAGE_PICKED_EVENT,
            function (event) { that.handle_image_picked(event); });

        // Window size changes.
        this.image1_spreader.addEventListener(
            webviz__Spreader__SpreadEvent,
            function (event) { that.handle_spread_event(event); });

        // -------------------------------------------------------------------

        this.#image_list_ux.activate();
        this.#image_edit_ux.activate();
        this.#pixel_ux.activate(this.#raphael);

        // Activate the spreader to react on window size changes.
        this.image1_spreader.activate($("#image1"), window);


        // -------------------------------------------------------------------
        // $(window).resize(function (jquery_event_object) { that._sizewatch(); });

        // TODO: Remove index.js sizewatch debug later.
        setTimeout(function () { that.image1_spreader.spread(); }, 1000);

    } // end method

    // -----------------------------------------------------------------------
    // Propagate event where user clicks a filename, such as in image_list_ux.
    handle_image_picked(event) {
        var F = "Targeting::handle_image_picked";

        var image_info = event.detail.image_info;

        // Save last loaded info to use when screen resizes.
        this.#last_loaded_image_info = image_info;

        // Tell the image editor to show the new image.
        this.#image_edit_ux.set_image_info(image_info);

        // The the pixel ux about the filename so it can be included in sending changes.
        this.#pixel_ux.set_image_info(image_info);

        // Resize the displayed image according to the current screen size.
        this.resize_image()

    } // end method

    // -----------------------------------------------------------------------
    // Callback from the spreader event (window resize), after the image size is calculated.
    handle_spread_event(event) {
        var F = "Targeting::handle_spread_event";

        var w = $("#image1_viewport").width()
        var h = $("#image1_viewport").height()

        console.log(F + " image1_viewport size is given as [" + w + ", " + h + "]");

        // Resize the annotation overlay.
        $("#raphael1_viewport").width(w)
        $("#raphael1_viewport").height(h)

        // To transform coordinates.
        this.#transformer.set_view({ x1: 0, y1: 0, x2: w, y2: h })

        // Resize the displayed image according to the current screen size.
        this.resize_image()

    } // end method

    // -----------------------------------------------------------------------
    // Resize the displayed image according to the current screen size.

    resize_image() {
        var F = "Targeting::resize_image";

        if (this.#last_loaded_image_info === null)
            return;

        var image_info = this.#last_loaded_image_info;

        var w = image_info.width;
        var h = image_info.height;

        console.log(F + " image data size is given as [" + w + ", " + h + "]");

        // To transform coordinates.
        this.#transformer.set_data({ x1: 0, y1: 0, x2: w, y2: h })

        // Transform data to view.
        var view_position = this.#transformer.data_to_view({ x: w, y: h })

        console.log(F + " data to view is [" + view_position.x + ", " + view_position.y + "]");

        // TODO: Move detector1_image resize into image_edit_ux.
        var $img = $("#detector1_image")
        $img.prop("width", view_position.x)
        $img.prop("height", view_position.y)

    } // end method

} // end class

// -------------------------------------------------------------
// All elements on the page ready.
$(document).ready(function () {
    // Make an object to handle the page logic.
    var page = new Targeting(global_runtime);
    page.activate();
});

