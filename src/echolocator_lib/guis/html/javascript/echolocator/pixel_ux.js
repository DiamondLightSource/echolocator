var echolocator__PixelUx__UserMotionEvent = "echolocator__PixelUx__UserMotionEvent";
var echolocator__PixelUx__UserChangeEvent = "echolocator__PixelUx__UserChangeEvent";

class echolocator__PixelUx extends echolocator__UxBase {
    SET_TARGET_POSITION = "echolocator_guis::commands::set_target_position";

    #raphael = null;
    #transformer = null;
    #guide = null;
    #autoid = null;
    #target_position = null;

    constructor(runtime, plugin_link_name, $interaction_parent, raphael) {
        super(runtime);

        this.plugin_link_name = plugin_link_name;
        this.$interaction_parent = $interaction_parent;
    }

    // -------------------------------------------------------------
    // Activate things on the UX.

    activate(raphael) {
        super.activate()
        this.#raphael = raphael;

        // TODO: Try to use raphael normal transformation instead of transformer class.
        this.#transformer = this.#raphael.webviz_transformer;

        var that = this;

        this.#guide = new webviz__hair__Guide2(this, this.plugin_link_name);

        // Guide is moving.
        this.#guide.addEventListener(
            webviz__hair__Guide2__UserMotionEvent,
            function (event) { that.handle_guide_motion_event(event); });

        // Guide stops.
        this.#guide.addEventListener(
            webviz__hair__Guide2__UserChangeEvent,
            function (event) { that.handle_guide_change_event(event); });

        this.#guide.activate(this.#raphael, "yellowgreen");

        // Set box to appear guaranteed on-screen somewhere.
        this.#guide.set_box({ position: { x: 110, y: 110 }, visible: true });

    } // end method

    // -------------------------------------------------------------
    // When the selected image changes, we get notified.
    // We will move the guide to the image's target location.
    // We will update the x and y as the guid moves.

    set_autoid(autoid, target_position) {
        var F = "echolocator__PixelUx::set_autoid"

        // Remember the image info.
        this.#autoid = autoid;
        this.#target_position = target_position;

        this.render();

    } // end method

    // -----------------------------------------------------------------------
    // Render the viewable things according to the current tranformer settings.
    render(event) {
        var F = "echolocator__PixelUx::render"

        // Everything we send or receive from the outside is data coordinates.
        // Convert it to view coordinates which is are used by the guide.
        var view_position = this.#transformer.data_to_view(this.#target_position);

        // Move the guide to the canvas view location.
        this.#guide.set_box({ position: view_position })

    } // end method

    // -----------------------------------------------------------------------
    // Guide is moving (dragging).
    handle_guide_motion_event(event) {
        var F = "echolocator__PixelUx::handle_guide_motion_event"

        // console.log(F + " guide moving")

    } // end method


    // -----------------------------------------------------------------------
    // Guide has changed (mouse up after dragging).
    // Also can be called by image_edit_ux after click on canvas.
    handle_guide_change_event(event) {
        var F = "echolocator__PixelUx::handle_guide_change_event"

        console.log(F + " guide changed")

        // The guide gives view coordinates.
        var view_position = this.#guide.get().position;

        // Everything we send or receive from the outside is data coordinates.
        this.#target_position = this.#transformer.view_to_data(view_position)

        console.log(F + ": dragged view_position" +
            " [" + view_position.x + ", " + view_position.y + "]" +
            " transformed to target_position" +
            " [" + this.#target_position.x + ", " + this.#target_position.y + "]");

        this.update_database();

        // Trigger an event that image_edit.js will use to advance to the next image.
        var custom_event = new CustomEvent(echolocator__PixelUx__UserChangeEvent,
            {
                detail: { target_position: this.#target_position }
            });

        this.dispatchEvent(custom_event);

    } // end method

    // -----------------------------------------------------------------------
    // Called after guide changed by a user action.
    // Also can be called by image_edit_ux after click on canvas has set a new position.

    update_database(event) {
        var F = "echolocator__PixelUx::update_database"

        var json_object = {}
        json_object[this.COMMAND] = this.SET_TARGET_POSITION;
        json_object["autoid"] = this.#autoid;
        json_object["target_position"] = this.#target_position;

        this.send(json_object);

    } // end method

}