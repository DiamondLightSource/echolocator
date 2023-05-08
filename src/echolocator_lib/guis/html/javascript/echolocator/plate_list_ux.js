// Class backing the actions ux.

class echolocator__PlateListUx extends echolocator__UxAutoUpdate {
    COOKIE_NAME = "PLATE_LIST_UX";
    REPORT_PLATES = "echolocator_guis::commands::report_plates";

    #jquery_objects = {};

    constructor(runtime, plugin_link_name, $interaction_parent) {
        super(runtime);

        this.plugin_link_name = plugin_link_name;
        this.$interaction_parent = $interaction_parent;
        this.plate_rows = undefined;
    }

    // -------------------------------------------------------------
    // Activate things on the UX.

    activate() {
        super.activate()

        this.#jquery_objects.$div = $(".T_composed", this.$interaction_parent);

    } // end method

    // -------------------------------------------------------------
    // Request update from database.

    request_update() {

        var json_object = {}
        json_object[this.COMMAND] = this.REPORT_PLATES;
        json_object[this.ENABLE_COOKIES] = [this.COOKIE_NAME];

        this.send(json_object);

    } // end method

    // -------------------------------------------------------------
    // Handle the response when it comes.

    handle_ajax_success(response, status, jqXHR) {
        var F = "echolocator__PlateListUx::_handle_ajax_success";

        // Let the base class have a look at the response.
        super.handle_ajax_success(response, status, jqXHR);

        var html = response.html;

        if (html !== undefined) {
            this.#jquery_objects.$div.html(html);
            // Attach events to all the individual job links in the "recent jobs" grid.
            this._attach_links();
        }
    }

    // -------------------------------------------------------------

    _handle_plate_clicked(jquery_event_object) {

        var $plate_row = $(jquery_event_object.target);

        // User clicked on a cell within the row?
        if ($plate_row.get(0).tagName == "TD")
            $plate_row = $plate_row.parent();

        // The row has the attribute holding the crystal plate of this row.
        var crystal_plate_uuid = $plate_row.attr("crystal_plate_uuid");

        this._load_plate(crystal_plate_uuid);

        this.set_and_render_auto_update(false);

    } // end method

    // -------------------------------------------------------------

    _load_plate(crystal_plate_uuid) {
        var F = "echolocator__PlateListUx::_load_plate";

        console.log(F + ": loading plate for crystal_plate_uuid " + crystal_plate_uuid)

        //     this.$plate_rows.removeClass("T_picked");
        //     plate_info.$plate_row.addClass("T_picked");

        // Trigger an event that the index.js will use to coordinate cross-widget changes.
        var custom_event = new CustomEvent(echolocator__Events_PLATE_PICKED_EVENT,
            {
                detail: { crystal_plate_uuid: crystal_plate_uuid }
            });

        this.dispatchEvent(custom_event);

    } // end method

    // -------------------------------------------------------------
    // Attach events to all the individual job links in the grid.

    _attach_links() {
        var F = "echolocator__PlateListUx::_attach_links";

        var that = this;

        this.$plate_rows = $(".T_plate_list TR", this.$interaction_parent);
        this.$plate_rows.click(function (jquery_event_object) { that._handle_plate_clicked(jquery_event_object); })

    }

}
