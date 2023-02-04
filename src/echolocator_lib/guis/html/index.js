// $(window).resize(function (jquery_event_object) { console.log("WINDOW RESIZE"); });

class Index extends echolocator__Page {
    #tabs_manager = null;
    #image_list_ux = null;
    #image_edit_ux = null;

    #tab_id_last_opened = null;

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

        return;

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
        var F = "Index::activate";
        super.activate();

        var that = this;

        // -------------------------------------------------------------------

        this.#tabs_manager = new echolocator__TabsManager(
            self.runtime,
            "tabs_manager",
            $("#tabs_manager_interaction_parent"));

        this.#image_list_ux = new echolocator__ImageListUx(
            self.runtime,
            "image_list",
            $("#image_list_ux_interaction_parent"));

        this.#image_edit_ux = new echolocator__ImageEditUx(
            self.runtime,
            "image_edit",
            $("#image_edit_ux_interaction_parent"));

        // -------------------------------------------------------------------

        var that = this;

        // Tabs have created, which may need some tweaking inside the tab.
        this.#tabs_manager.addEventListener(
            echolocator__Events_TABS_CREATED_EVENT,
            function (event) { that.handle_tabs_created(event); });

        // User picks an image from the image list.
        this.#image_list_ux.addEventListener(
            echolocator__Events_IMAGE_PICKED_EVENT,
            function (event) { that.handle_image_picked(event); });

        // User wants to go to previous or next image in the list.
        this.#image_edit_ux.addEventListener(
            echolocator__Events_IMAGE_PREVIOUS_OR_NEXT_EVENT,
            function (event) { that.handle_image_previous_or_next(event); });

        // -------------------------------------------------------------------

        this.#tabs_manager.activate()
        this.#image_list_ux.activate();
        this.#image_edit_ux.activate();

        // Tab has been opened (made current).
        this.#tabs_manager.addEventListener(
            echolocator__Events_TAB_OPENED,
            function (event) { that.handle_tab_opened(event); });


        // -------------------------------------------------------------------

        // TODO: Remove index.js sizewatch debug later.
        // setTimeout(function () { that.image1_spreader.spread(); }, 1000);

    } // end method

    // -----------------------------------------------------------------------
    // Propagate event where user clicks a particular job.
    handle_tabs_created(event) {
        var F = "Index::handle_tabs_created";
        console.log(F + ": tabs created");
        this._sizewatch();
    } // end method

    // -----------------------------------------------------------------------
    // Propagate event where user clicks a particular job.
    handle_tab_opened(event) {
        var F = "Index::handle_tab_opened";

        // Have to hide the top-level error or the sizewatch doesn't compute right.
        this.#tabs_manager.display_ajax_error(null);
        // Adjust the sizing for the new tab.
        // TODO: Move sizewatch inside particular ux that needs it.
        // commented out 2022-11-21 this._sizewatch();

        var tab_id = event.detail.tab_id;

        if (tab_id == this.#tab_id_last_opened)
            return;

        this.#tab_id_last_opened = tab_id;

        // console.log(F + ": tab_id is \"" + tab_id + "\" dispatched by " + event.detail.dispatched_by);

        var $interaction_parent = $("#" + tab_id).children().first();

        var interaction_parent_id = $interaction_parent.attr("id");

        // console.log(F + ": $interaction_parent_id is \"" + interaction_parent_id + "\"");

        if (interaction_parent_id == "image_list_ux_interaction_parent") {
            this.#image_list_ux.request_update()
        }
        else if (interaction_parent_id == "image_edit_ux_interaction_parent") {
            this.#image_edit_ux.request_update()
        }

    } // end method

    // -----------------------------------------------------------------------
    // Propagate event where user clicks a filename, such as in image_list_ux.
    handle_image_picked(event) {
        var F = "Index::handle_image_picked";

        var autoid = event.detail.autoid;

        // Tell the image editor to show the new image.
        this.#image_edit_ux.set_autoid(autoid);

        this.#tabs_manager.switch_to_tab("tab-image-edit")

        // Resize the displayed image according to the current screen size.
        // this.resize_image()

    } // end method

    // -----------------------------------------------------------------------
    // User wants to go to previous or next image in the list.
    handle_image_previous_or_next(event) {
        var F = "Index::handle_image_previous_or_next";

        this.#image_list_ux.image_previous_or_next(
            event.detail.autoid,
            event.detail.direction);

    } // end method

} // end class

// -------------------------------------------------------------
// All elements on the page ready.
$(document).ready(function () {
    // Make an object to handle the page logic.
    var page = new Index(global_runtime);
    page.activate();
});

