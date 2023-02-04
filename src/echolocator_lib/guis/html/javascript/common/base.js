// Implement the logic common to all classes.

class common__Base extends EventTarget {
  constructor(runtime) {
    super();
    this.runtime = runtime;
  }

  // --------------------------------------------------------------------
  // return something which describes a jquery selector

  selector_description(selector) {
    return this.node_description($(selector).get(0));
  } // end method


  // --------------------------------------------------------------------
  // return something which describes a DOM node

  node_description(node) {
    if (node == undefined)
      return "<undefined>";

    var description = "";

    description = "<";

    if (node.tagName)
      description += node.tagName;
    else
      description += node.nodeName;

    if (description == "<INPUT")
      description += " " + node.type;

    if (node.id != undefined &&
      node.id != "")
      description += " id=\"" + node.id + "\"";

    /* better description for nodes with names and hrefs */
    /* watchfrog #42 */
    if (node.name != undefined && node.name != "")
      description += " name=\"" + node.name + "\"";

    if (node.href != undefined && node.href != "")
      description += " href=\"" + node.href + "\"";

    // add value to a radio button description
    // watchfrog #94
    if (node.type != undefined && node.type == "radio")
      description += " value=\"" + node.value + "\"";

    description += ">";

    return description;

  } // end method

} // end class.
