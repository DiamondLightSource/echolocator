// Class backing the actions ux.


class echolocator__UxBase extends common__Base {
    COMMAND = "echolocator_guis::keywords::command";
    PAYLOAD = "echolocator_guis::keywords::payload";
    ENABLE_COOKIES = "dls_servbase_api::keywords::enable_cookies";
    UPDATE_JOB = "echolocator_guis::commands::update_job";
    CANCEL_JOB = "echolocator_guis::commands::cancel_job";
    DELETE_JOB = "echolocator_guis::commands::delete_job";
    UNBLOCK_JOB = "echolocator_guis::commands::unblock_job";
    JOB_COMMENT = "comment"
    JOB_RATING = "rating"

    #jquery_objects = {};

    constructor(runtime, plugin_link_name, $interaction_parent) {
        super(runtime);

        this.plugin_link_name = plugin_link_name;
        this.$interaction_parent = $interaction_parent;
    }

    // -------------------------------------------------------------
    // Activate things on the UX.

    activate() {

        // Activate confirmation message display place on the UX.
        this.activate_confirmation_message();

        // Activate error message display place on the UX.
        this.activate_error_message();

    } // end method

    // -------------------------------------------------------------
    // Activate confirmation message display place on the UX.

    activate_confirmation_message() {

        var cm_class = "T_ajax_confirmation_message";
        var $cm_container = $("." + cm_class + "_container", this.$interaction_parent);
        var $cm = $("." + cm_class, this.$interaction_parent);

        if ($cm_container.length == 0) {
            this.$interaction_parent.prepend("<div class='" + cm_class + "_container'><div class='" + cm_class + "'></div></div>");
            $cm_container = $("." + cm_class + "_container", this.$interaction_parent);
            $cm = $("." + cm_class, this.$interaction_parent);
        }

        $cm_container.hide();
        this.#jquery_objects.$confirmation_message_container = $cm_container;
        this.#jquery_objects.$confirmation_message = $cm;

    } // end method

    // -------------------------------------------------------------
    // Activate error message display place on the UX.

    activate_error_message() {

        var em_class = "T_ajax_error_message";
        var $em_container = $("." + em_class + "_container", this.$interaction_parent);
        var $em = $("." + em_class, this.$interaction_parent);

        if ($em_container.length == 0) {
            this.$interaction_parent.prepend("<div class='" + em_class + "_container'><xmp class='" + em_class + "'></xmp></div>");
            $em_container = $("." + em_class + "_container", this.$interaction_parent);
            $em = $("." + em_class, this.$interaction_parent);
        }

        $em_container.hide();
        this.#jquery_objects.$error_message_container = $em_container;
        this.#jquery_objects.$error_message = $em;

    } // end method

    // -------------------------------------------------------------
    // Handle the response when it comes.

    handle_ajax_success(response, status, jqXHR) {
        var F = "echolocator__UxBase::handle_ajax_success[" + this.plugin_link_name + "]";

        var error_message = null;
        var confirmation_message = null;
        var http_code = jqXHR.status;

        // With 200, we presumably we probably got a cogent json response.
        if (http_code === 200) {
            // Check if the content has an error field.
            if (response.exception || response.error) {
                error_message = "exception in server response\n" + JSON.stringify(response);
            }

            // Check if the content has a confirmation field.
            // We could, theoretically, have both an error and a confirmation.
            if (response.confirmation) {
                confirmation_message = response.confirmation;
            }
        }
        // If not 200, then we don't likely have response as json.
        else {
            error_message = "error " + http_code + " (" + status + ")" + "\n" + response;
        }

        this.display_ajax_confirmation(confirmation_message);
        this.display_ajax_error(error_message);

        return error_message;
    }

    // -------------------------------------------------------------
    // Handle the response failure if it comes.
    handle_ajax_failure(jqXHR, status, error_thrown) {
        var F = "echolocator__UxBase::handle_ajax_failure[" + this.plugin_link_name + "]";


        var http_code = jqXHR.status;
        var error_message = null;

        if (error_thrown.name != undefined)
            error_message = error_thrown.name + ": " + error_thrown.message;
        else
            error_message = error_thrown;

        error_message = "error " + http_code + " " + error_message + "\n" + jqXHR.responseText;

        console.log(F + ": " + error_message);

        this.display_ajax_error(error_message);

        return error_message;
    }

    // -------------------------------------------------------------
    // Display any confirmation from ajax response.
    display_ajax_confirmation(confirmation_message) {
        var F = "echolocator__UxBase::display_ajax_confirmation[" + this.plugin_link_name + "]";

        if (confirmation_message === null) {
            this.#jquery_objects.$confirmation_message_container.hide();
        }
        else {
            console.log(F + ": displaying confirmation " + confirmation_message);

            this.#jquery_objects.$confirmation_message.text(confirmation_message);
            this.#jquery_objects.$confirmation_message_container.show();
        }
    }

    // -------------------------------------------------------------
    // Display any error from ajax response.
    display_ajax_error(error_message) {
        var F = "echolocator__UxBase::display_ajax_error[" + this.plugin_link_name + "]";

        if (error_message === null) {
            this.#jquery_objects.$error_message_container.hide();
        }
        else {
            console.log(F + ": displaying error " + error_message);

            this.#jquery_objects.$error_message.text(error_message);
            this.#jquery_objects.$error_message_container.show();
        }
    }

    // -------------------------------------------------------------
    send(json_object) {
        var F = "echolocator__ImageListUx::send[" + this.plugin_link_name + "]";

        var json_string = JSON.stringify(json_object);

        // console.log(F + ": sending " + json_string);

        var url = window.location.protocol +
            "//" + window.location.hostname +
            ":" + window.location.port +
            "/protocolj";

        var that = this;

        var $request = $.ajax(
            {
                url: url,
                cache: false,
                data: json_string,
                method: "POST",
                processData: false,
                contentType: "application/json",
                success: function (response, status, jqXHR) { that.handle_ajax_success(response, status, jqXHR); },
                error: function (jqXHR, status, error_thrown) { that.handle_ajax_failure(jqXHR, status, error_thrown); }
            }
        );

    } // end method

    // -------------------------------------------------------------

    _handle_cancel_job_clicked(jquery_event_object) {

        var $cancel_job = $(jquery_event_object.target);

        this._request_cancel_job($cancel_job.attr("echolocator_job_uuid"));

    } // end method

    // -------------------------------------------------------------
    // Request cancel job in the database.

    _request_cancel_job(echolocator_job_uuid) {

        var json_object = {}
        json_object[this.COMMAND] = this.CANCEL_JOB;
        json_object["echolocator_job_uuid"] = echolocator_job_uuid;
        json_object[this.ENABLE_COOKIES] = [this.COOKIE_NAME];

        this.send(json_object);

    } // end method

    // -------------------------------------------------------------

    _handle_delete_job_clicked(jquery_event_object) {

        var $delete_job = $(jquery_event_object.target);

        this._request_delete_job($delete_job.attr("echolocator_job_uuid"));

    } // end method

    // -------------------------------------------------------------
    // Request delete job in the database.

    _request_delete_job(echolocator_job_uuid) {

        var json_object = {}
        json_object[this.COMMAND] = this.DELETE_JOB;
        json_object["echolocator_job_uuid"] = echolocator_job_uuid;
        json_object[this.ENABLE_COOKIES] = [this.COOKIE_NAME];

        this.send(json_object);

    } // end method

    // -------------------------------------------------------------

    _handle_unblock_job_clicked(jquery_event_object) {

        var $unblock_job = $(jquery_event_object.target);

        this._request_unblock_job($unblock_job.attr("echolocator_job_uuid"));

    } // end method

    // -------------------------------------------------------------
    // Request unblock job in the database.

    _request_unblock_job(echolocator_job_uuid) {

        var json_object = {}
        json_object[this.COMMAND] = this.UNBLOCK_JOB;
        json_object["echolocator_job_uuid"] = echolocator_job_uuid;
        json_object[this.ENABLE_COOKIES] = [this.COOKIE_NAME];

        this.send(json_object);

    } // end method



    // -------------------------------------------------------------

    _handle_job_comment_changed(jquery_event_object) {
        var F = "echolocator__ImageListUx::_handle_job_comment_changed[" + this.plugin_link_name + "]";

        var $textarea = $(jquery_event_object.target);

        // The echolocator_job_uuid is an attribute of the containing row.
        var $row = $textarea.closest("TR")
        var echolocator_job_uuid = $row.attr("echolocator_job_uuid")

        console.log(F +
            ": $textarea " + $textarea.length +
            ", $row " + $row.length +
            ", echolocator_job_uuid " + echolocator_job_uuid)

        var json_object = {}
        json_object[this.COMMAND] = this.UPDATE_JOB;
        json_object["echolocator_job_uuid"] = echolocator_job_uuid;
        json_object[this.JOB_COMMENT] = $textarea.val()

        this.send(json_object);

    } // end method


    // -------------------------------------------------------------

    _handle_job_rating_changed(jquery_event_object) {
        var F = "echolocator__ImageListUx::_handle_job_rating_changed[" + this.plugin_link_name + "]";

        var $rating = $(jquery_event_object.target);
        var new_rating = $rating.attr("rating")
        var was_selected = $rating.hasClass("T_selected");
        if (was_selected) {
            new_rating = 0;
        }

        // The echolocator_job_uuid is an attribute of the containing row.
        var $row = $rating.closest("TR")
        var echolocator_job_uuid = $row.attr("echolocator_job_uuid")

        console.log(F +
            ": $rating " + $rating.length +
            ", $row " + $row.length +
            ", echolocator_job_uuid " + echolocator_job_uuid +
            ", new_rating " + new_rating);

        var $parent = $rating.parent()
        $parent.children().removeClass("T_selected");
        if (!was_selected)
            $rating.addClass("T_selected");

        var json_object = {}
        json_object[this.COMMAND] = this.UPDATE_JOB;
        json_object["echolocator_job_uuid"] = echolocator_job_uuid;
        json_object[this.JOB_RATING] = new_rating;

        this.send(json_object);

    } // end method    
}
