// Class backing the actions ux.

class echolocator__PlateListUx extends echolocator__UxAutoUpdate {
    COOKIE_NAME = "PLATE_LIST_UX";
    REPORT_PLATES = "echolocator_guis::commands::report_plates";
    EXPORT_TO_SOAKDB3 = "echolocator_guis::commands::export_to_soakdb3";
    EXPORT_TO_CSV = "echolocator_guis::commands::export_to_csv";

    #jquery_objects = {};
    #visit_filter = undefined;
    #should_show_only_needing_intervention = undefined;

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
        this.#jquery_objects.$visit_filter = $("#visit_filter", this.$interaction_parent);
        this.#jquery_objects.$should_show_only_needing_intervention = $("#should_show_only_needing_intervention", this.$interaction_parent);

        var that = this;
        this.#jquery_objects.$visit_filter.change(
            function (jquery_event_object) {
                that._handle_filter_change(jquery_event_object);
            });

        this.#jquery_objects.$should_show_only_needing_intervention.change(
            function (jquery_event_object) {
                that._handle_filter_change(jquery_event_object);
            });

    } // end method

    // -------------------------------------------------------------
    // Request update from database.

    request_update() {

        var json_object = {}
        json_object[this.COMMAND] = this.REPORT_PLATES;
        json_object[this.ENABLE_COOKIES] = [this.COOKIE_NAME];

        // Don't post any value if none defined yet, this will allow them to come from cookie, if any.
        if (this.#visit_filter !== undefined)
            json_object["visit_filter"] = this.#visit_filter;
        if (this.#should_show_only_needing_intervention !== undefined)
            json_object["should_show_only_needing_intervention"] = this.#should_show_only_needing_intervention;

        this.send(json_object);

    } // end method

    // -------------------------------------------------------------

    _handle_filter_change(jquery_event_object) {
        var F = "echolocator__PlateListUx::_handle_filter_change"

        this.#visit_filter = this.#jquery_objects.$visit_filter.val()
        this.#should_show_only_needing_intervention = this.#jquery_objects.$should_show_only_needing_intervention.prop("checked")
        this.request_update()

    } // end method

    // -------------------------------------------------------------
    // Handle the response when it comes.

    handle_ajax_success(response, status, jqXHR) {
        var F = "echolocator__PlateListUx::_handle_ajax_success";

        // Let the base class have a look at the response.
        super.handle_ajax_success(response, status, jqXHR);

        var filters = response.filters;
        if (filters !== undefined) {
            var t;

            t = filters["visit_filter"];
            if (t === undefined)
                t = "";
            this.#jquery_objects.$visit_filter.val(t);

            t = filters["should_show_only_needing_intervention"];
            if (t === undefined)
                t = false;
            this.#jquery_objects.$should_show_only_needing_intervention.prop("checked", t);
        }

        var html = response.html;

        if (html !== undefined) {

            console.log(F + ": displaying on this.#jquery_objects.$div len " + this.#jquery_objects.$div.length)
            this.#jquery_objects.$div.html(html);
            // Attach events to all the individual job links in the plates grid.
            this._attach_links();
        }
    }

    // -------------------------------------------------------------

    _handle_needing_intervention_crystals_clicked(jquery_event_object) {

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
                    visit: visit,
                    barcode: barcode
                }
            });

        this.dispatchEvent(custom_event);

    } // end method

    // -------------------------------------------------------------

    _handle_usable_unexported_clicked(jquery_event_object) {

        var $plate_row = $(jquery_event_object.target).closest("TR");

        // Get the visit and barcode from the other cells in the row.
        var visit = $("#visit", $plate_row).text();
        var barcode = $("#barcode", $plate_row).text();

        // Enable no cookie for this request.
        var json_object = {}
        json_object[this.COMMAND] = this.EXPORT_TO_SOAKDB3;

        json_object["visit_filter"] = visit;
        json_object["barcode_filter"] = barcode;

        this.send(json_object);

    } // end method

    // -------------------------------------------------------------
    // Attach events to all the individual job links in the grid.

    _attach_links() {
        var F = "echolocator__PlateListUx::_attach_links";

        var that = this;

        var $needing_intervention_crystals = $("TD.T_undecided_crystals_count", this.$interaction_parent);
        $needing_intervention_crystals.each(function () {
            if ($(this).text() !== "0") {
                $(this).addClass("T_clickable");
                $(this).click(function (jquery_event_object) { that._handle_needing_intervention_crystals_clicked(jquery_event_object); })
            }
        })

        var $usable_unexported = $("TD.T_usable_unexported_count", this.$interaction_parent);
        $usable_unexported.each(function () {
            if ($(this).text() !== "0") {
                $(this).addClass("T_clickable");
                $(this).click(function (jquery_event_object) { that._handle_usable_unexported_clicked(jquery_event_object); })
            }
        })

    }

}
