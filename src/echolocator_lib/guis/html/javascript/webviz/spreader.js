// --------------------------------------------------------------------
var webviz__Spreader__SpreadEvent = "webviz__Spreader__SpreadEvent";

// --------------------------------------------------------------------
// class representing a spreading operation
class webviz__Spreader extends common__Base {

    constructor(page) {
        super(page.runtime);
        this.page = page;
        this._timer = undefined;
    } // end constructor


    // -------------------------------------------------------------

    activate(spreadable, container) {
        var F = "webviz__Spreader::activate";

        this.$spreadable = $(spreadable);
        this.$container = $(container);

        console.log(F + " activating spreadable " + this.selector_description(this.$spreadable))

        // Do the initial spread when activating.
        // this.spread();

        // Re-spread every time the container changes size, but not more often than 250ms.
        var that = this;
        this.$container.resize(function () {
            clearTimeout(this._timer);
            this._timer = setTimeout(function () {
                that.spread()
            }, 250);
        });

    } // end method


    // -------------------------------------------------------------

    spread() {
        var F = "webviz__Spreader::spread";

        console.log(F + " spreading " + this.selector_description(this.$spreadable) + " ------------------------ ")

        var container_outer_width = this.$container.outerWidth();
        var container_outer_height = this.$container.outerHeight();
        console.log(F + " container outer size is " + container_outer_width + ", " + container_outer_height);

        var container_inner_width = this.$container.innerWidth();
        var container_inner_height = this.$container.innerHeight();
        console.log(F + " container inner size is " + container_inner_width + ", " + container_inner_height);

        var spreadable_offset = this.$spreadable.offset();
        var spreadable_inner_width = this.$spreadable.innerWidth()
        var spreadable_inner_height = this.$spreadable.innerHeight()
        var spreadable_outer_width = this.$spreadable.outerWidth()
        var spreadable_outer_height = this.$spreadable.outerHeight()

        console.log(F + " spreadable offset is " + spreadable_offset.left + ", " + spreadable_offset.top);
        console.log(F + " spreadable inner size is " + spreadable_inner_width + ", " + spreadable_inner_height);
        console.log(F + " spreadable outer size is " + spreadable_outer_width + ", " + spreadable_outer_height);

        var spreadable_border_width = spreadable_outer_width - spreadable_inner_width;
        var spreadable_border_height = spreadable_outer_height - spreadable_inner_height;

        var remaining_w = container_outer_width - spreadable_offset.left
        var remaining_h = container_outer_height - spreadable_offset.top

        var padding = 8;
        this.$spreadable.innerWidth(remaining_w - spreadable_border_width - padding)
        this.$spreadable.innerHeight(remaining_h - spreadable_border_height - padding)

        // console.log(F + " pulling triggger " + webviz__Spreader__SpreadEvent);

        // Trigger an event that the index.js will use to coordinate cross-widget changes.
        var custom_event = new CustomEvent(webviz__Spreader__SpreadEvent,
            {
                detail: undefined
            });
        this.dispatchEvent(custom_event);

    } // end method

} // end class


