// Class backing the actions ux.


class echolocator__TabsManager extends echolocator__UxBase {
    COOKIE_NAME = "TABS_MANAGER";
    LOAD_TABS = "echolocator_guis::commands::load_tabs";
    SELECT_TAB = "echolocator_guis::commands::select_tab";
    TAB_ID_KEYWORD = "echolocator_guis::keywords::tab_id"

    #jquery_objects = {};

    constructor(runtime, plugin_link_name, $interaction_parent) {
        super(runtime);

        this.plugin_link_name = plugin_link_name;
        this.$interaction_parent = $interaction_parent;
    }

    // -------------------------------------------------------------
    // Activate things on the UX.

    activate() {
        var F = "echolocator__TabsManager::activate";

        super.activate();

        var that = this;

        this.#jquery_objects.$tabs = $(".T_tabs", this.$interaction_parent);
        this.#jquery_objects.$tabs.hide();
        this.#jquery_objects.$tabs.tabs(
            {
                create: function (jquery_event_object, ui) { that._handle_tabs_created(jquery_event_object, ui); },
                activate: function (jquery_event_object, ui) { that._handle_tab_selected(jquery_event_object, ui); }
            }
        );

        // Kick off an initial query.
        this._load();

    } // end method

    // -------------------------------------------------------------

    _handle_tabs_created(jquery_event_object, ui) {
        var F = "echolocator__TabsManager::_handle_tabs_created";

        console.log(F + ": tabs created");

        // Tell the index.js to notify the tabs about possible layout changes.
        var custom_event = new CustomEvent(echolocator__Events_TABS_CREATED_EVENT,
            {
            });
        this.dispatchEvent(custom_event);

    } // end method


    // -------------------------------------------------------------

    _load() {
        var F = "echolocator__TabsManager::_load";

        var json_object = {}
        json_object[this.COMMAND] = this.LOAD_TABS;
        json_object[this.ENABLE_COOKIES] = [this.COOKIE_NAME];

        console.log(F + ": submitting " + JSON.stringify(json_object))

        this.send(json_object);

    } // end method

    // -------------------------------------------------------------

    switch_to_tab(tab_id) {
        var F = "echolocator__TabsManager::switch_to_tab";

        // Get the tab index from the tab_id.
        var tab_index = $('a[href="#' + tab_id + '"]').parent().index();

        console.log(F + ": switching to tab_id " + tab_id + " which is tab_index" + tab_index);

        this.#jquery_objects.$tabs.tabs("option", "active", tab_index);

    } // end method

    // -------------------------------------------------------------

    _handle_tab_selected(jquery_event_object, ui) {
        var F = "echolocator__TabsManager::_handle_tab_selected";

        var tab_index = this.#jquery_objects.$tabs.tabs("option", "active");

        // console.log(F + ": ui.newTab " + this.selector_description(ui.newTab))
        // console.log(F + ": ui.newTab.selector " + ui.newTab.selector)
        // console.log(F + ": ui.newPanel " + this.selector_description(ui.newPanel))
        // console.log(F + ": ui.newPanel.selector " + ui.newPanel.selector)
        var $new_panel = ui.newPanel
        if ($new_panel !== undefined) {
        }

        var tab_id = $new_panel.attr("id");

        console.log(F + ": tab index " + tab_index + " selected which is tab_id " + tab_id);

        var json_object = {}
        json_object[this.COMMAND] = this.SELECT_TAB;
        json_object[this.ENABLE_COOKIES] = [this.COOKIE_NAME];
        json_object[this.TAB_ID_KEYWORD] = tab_id;

        this.send(json_object);

        // Tell the index.js to notify the tab that was just selected.
        var custom_event = new CustomEvent(echolocator__Events_TAB_OPENED,
            {
                detail: { tab_id: tab_id, dispatched_by: F }
            });
        this.dispatchEvent(custom_event);

    } // end method

    // -------------------------------------------------------------
    // Handle the response when it comes.

    handle_ajax_success(response, status, jqXHR) {
        var F = "echolocator__TabsManager::handle_ajax_success";

        // Let the base class check for and display any error in the response.
        var error_message = super.handle_ajax_success(response, status, jqXHR);

        if (error_message !== null)
            return;

        var tab_id = response[this.TAB_ID_KEYWORD];
        var tab_index = undefined;

        // Only LOAD_TABS gives us back a tab_id.
        if (tab_id !== undefined) {
            // Server doesn't know which tab to suggest?
            if (tab_id === null) {
                tab_index = 0;
                var $first_tab = this.#jquery_objects.$tabs.find("LI A").first();
                // console.log(F + ": tabs length is " + this.#jquery_objects.$tabs.find("LI A").length + " and $first_tab is " + $first_tab);
                tab_id = $first_tab.attr("href").substr(1);
                // console.log(F + ": response[TAB_ID_KEYWORD] is null so choosing tab_id " + tab_id + " which is tab_index " + tab_index);
            }
            else {
                // Get the tab index from the tab_id.
                var tab_index = $('a[href="#' + tab_id + '"]').parent().index();
                // console.log(F + ": response[TAB_ID_KEYWORD] is " + tab_id + " which is tab_index " + tab_index);
            }

            // Let the tabs show.
            this.#jquery_objects.$tabs.show();
            this.#jquery_objects.$tabs.tabs("option", "active", tab_index);

            // Tell the index.js to notify the tab that was just selected.
            var custom_event = new CustomEvent(echolocator__Events_TAB_OPENED,
                {
                    detail: { tab_id: tab_id, dispatched_by: F }
                });
            this.dispatchEvent(custom_event);
        }
    }

}
