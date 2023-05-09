// Class backing the actions ux.

class echolocator__PlateListUx extends echolocator__UxAutoUpdate {
    COOKIE_NAME = "PLATE_LIST_UX";
    REPORT_PLATES = "echolocator_guis::commands::report_plates";

    #jquery_objects = {};

    constructor(runtime, plugin_link_name, $interaction_parent) {
        super(runtime);

        this.plugin_link_name = plugin_link_name;
        this.$interaction_parent = $interaction_parent;
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

            console.log(F + ": displaying on this.#jquery_objects.$div len " + this.#jquery_objects.$div.length)
            this.#jquery_objects.$div.html(html);
            // Attach events to all the individual job links in the plates grid.
            this._attach_links();
        }
    }

    // -------------------------------------------------------------

    _handle_undecided_crystals_clicked(jquery_event_object) {

        var $plate_row = $(jquery_event_object.target).closest("TR");

        // The row has the attribute holding the crystal plate of this row.
        var crystal_plate_uuid = $plate_row.attr("crystal_plate_uuid");

        var visit = $("#visit", $plate_row).text();
        var barcode = $("#barcode", $plate_row).text();

        // Trigger an event that the index.js will use to coordinate cross-widget changes.
        var custom_event = new CustomEvent(echolocator__Events_PLATE_PICKED_EVENT,
            {
                detail: {
                    crystal_plate_uuid: crystal_plate_uuid,
                    barcode: barcode,
                    visit: visit
                }
            });

        this.dispatchEvent(custom_event);

    } // end method

    // -------------------------------------------------------------
    // Attach events to all the individual job links in the grid.

    _attach_links() {
        var F = "echolocator__PlateListUx::_attach_links";

        var that = this;

        var $undecided_crystals = $("TD.T_undecided_crystals_count", this.$interaction_parent);
        $undecided_crystals.click(function (jquery_event_object) { that._handle_undecided_crystals_clicked(jquery_event_object); })

        var $usable_unexported = $("TD.T_usable_unexported_count", this.$interaction_parent);
        $usable_unexported.click(function (jquery_event_object) { that._handle_usable_unexported_clicked(jquery_event_object); })

    }

}
