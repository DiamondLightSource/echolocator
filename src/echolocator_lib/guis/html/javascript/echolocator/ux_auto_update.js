// Class support auto update for a ux object.

echolocator__UxAutoUpdate__AUTO_UPDATE_EVENT = "echolocator__UxAutoUpdate__AUTO_UPDATE_EVENT";

class echolocator__UxAutoUpdate extends echolocator__UxBase {

    #$auto_update_toggle = undefined;
    #$auto_update_status = undefined;
    #last_updated_time = undefined;
    #auto_update_sleep_ms = 2000;
    #auto_update_request_timer = undefined;
    #auto_update_status_interval = undefined;

    constructor(runtime, plugin_link_name, $interaction_parent) {
        super(runtime, plugin_link_name, $interaction_parent);

        this.auto_update_enabled = "undefined";
        this.#last_updated_time = new Date().getTime();
    }

    // -------------------------------------------------------------
    // Activate things on the UX.

    activate() {
        super.activate();

        this.#$auto_update_toggle = $(".T_auto_update .T_toggle", this.$interaction_parent);
        this.#$auto_update_status = $(".T_auto_update .T_status", this.$interaction_parent);

        var that = this;
        this.#$auto_update_toggle
            .click(function (jquery_event_object) { that._handle_auto_update_clicked(jquery_event_object); })

        this.#auto_update_status_interval = setInterval(function () { that._handle_auto_update_status_interval(); }, 1000)

    } // end method

    // -------------------------------------------------------------
    // Set sleep update time in milliseconds.

    set_auto_update_sleep_ms(auto_update_sleep_ms) {
        this.#auto_update_sleep_ms = auto_update_sleep_ms;

    } // end method

    // -------------------------------------------------------------

    _handle_auto_update_clicked(jquery_event_object) {
        var F = "echolocator__UxAutoUpdate::_handle_auto_update_clicked[" + this.plugin_link_name + "]";

        this.set_and_render_auto_update(!this.auto_update_enabled, F);

        // Call the method provided by the ux to request its update.
        this.request_update();

    } // end method

    // -------------------------------------------------------------

    _handle_auto_update_request_timer() {
        if (this.auto_update_enabled === true) {
            this.request_update();

            let custom_event = new CustomEvent(
                echolocator__UxAutoUpdate__AUTO_UPDATE_EVENT,
                {});
            this.dispatchEvent(custom_event);
        }
    } // end method

    // -------------------------------------------------------------

    _handle_auto_update_status_interval() {
        var now_ms = new Date().getTime();
        var delta_ms = ((now_ms - this.#last_updated_time) / 1000.0).toFixed(0)
        this.#$auto_update_status.html("last " + delta_ms + " seconds ago")

    } // end method

    // -------------------------------------------------------------

    set_and_render_auto_update(enabled, dispatched_by) {

        var F = "echolocator__UxAutoUpdate::set_and_render_auto_update[" + this.plugin_link_name + "]";

        var that = this;

        this.auto_update_enabled = enabled;

        // console.log(F + ": enabled is " + enabled + " dispatched_by " + dispatched_by);

        if (enabled) {
            this.#$auto_update_toggle.removeClass("T_disabled");

            // Set timer to trigger another auto update.
            this.#auto_update_request_timer = setTimeout(
                function () { that._handle_auto_update_request_timer(); }, this.#auto_update_sleep_ms)

        }
        else {
            this.#$auto_update_toggle.addClass("T_disabled");
        }


    } // end method    



    // -------------------------------------------------------------
    // Handle the response when it comes.

    handle_ajax_success(response, status, jqXHR) {
        var F = "echolocator__UxAutoUpdate::handle_ajax_success[" + this.plugin_link_name + "]";

        var error_message = super.handle_ajax_success(response, status, jqXHR);

        // console.log(F + ": response.auto_update_enabled " + response.auto_update_enabled + ", error_message " + error_message)

        if (error_message !== null)
            return error_message;

        if (response.auto_update_enabled !== undefined) {
            // Set and render the auto_update setting which came back with the response.
            this.set_and_render_auto_update(response.auto_update_enabled, F);
        }

        this.#last_updated_time = new Date().getTime();

        return error_message;
    }

    // -------------------------------------------------------------
    send(json_object) {
        var F = "echolocator__UxAutoUpdate::send[" + this.plugin_link_name + "]";

        // console.log(F + ": adding to send this.auto_update_enabled " + this.auto_update_enabled);

        json_object["auto_update_enabled"] = this.auto_update_enabled;

        super.send(json_object);

    } // end method
}
