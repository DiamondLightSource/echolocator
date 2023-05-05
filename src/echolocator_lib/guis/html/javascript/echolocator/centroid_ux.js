var echolocator__CentroidUx__UserMotionEvent = "echolocator__CentroidUx__UserMotionEvent";
var echolocator__CentroidUx__UserChangeEvent = "echolocator__CentroidUx__UserChangeEvent";

class echolocator__CentroidUx extends echolocator__UxBase {
    UPDATE = "echolocator_guis::commands::update";

    #raphael = null;
    #color = null;
    #transformer = null;
    #shape = null;
    #position = null;
    #image_size = null;

    constructor(runtime, plugin_link_name, $interaction_parent, color) {
        super(runtime);

        this.plugin_link_name = plugin_link_name;
        this.$interaction_parent = $interaction_parent;
        this.#color = color;
    }

    // -------------------------------------------------------------
    // Activate things on the UX.

    activate(raphael) {
        super.activate()
        this.#raphael = raphael;

        // TODO: Try to use raphael normal transformation instead of transformer class.
        this.#transformer = this.#raphael.webviz_transformer;

        var that = this;

        this.#shape = new webviz__sprite__Ring(this, this.plugin_link_name);

        this.#shape.activate(this.#raphael, this.#color);

        // Set box to appear guaranteed on-screen somewhere.
        this.#shape.set({ position: { x: 220, y: 330 }, scale: 100, visible: true });

    } // end method

    // -------------------------------------------------------------
    // When the selected image changes, we get notified.
    // We will move the guide to the image's position location.
    // We will update the x and y as the guid moves.

    set(position, image_size) {
        var F = "echolocator__PixelUx[" + this.plugin_link_name + "]::set_position"

        // Remember the image info.
        this.#position = position;
        this.#image_size = image_size;

        this.render();

    } // end method


    // -----------------------------------------------------------------------
    // Render the viewable things according to the current tranformer settings.
    render(event) {
        var F = "echolocator__CentroidUx[" + this.plugin_link_name + "]::render"

        // console.log(F + ": [CENTPO] rendering position [" + this.#position.x + ", " + this.#position.y + "]")

        // Everything we send or receive from the outside is data coordinates.
        // Convert it to view coordinates which is are used by the guide.
        var view_position = this.#transformer.data_to_view(this.#position);

        // Use radius of 35% of image width.
        // TODO: Make displayed well centroid radius configurable.
        var scale = this.#transformer.data_to_view({ x: this.#image_size.w * 0.35, y: 0 });

        // console.log(F + ": [CENTPO] rendering to view position [" + view_position.x + ", " + view_position.y + "] scale " + scale.x + "")

        // Move the guide to the canvas view location.
        this.#shape.set({ position: view_position, scale: scale.x })

    } // end method


}