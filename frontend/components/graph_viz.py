from pyvis.network import Network

TYPE_COLORS = {
    "Person": "#FF6B6B",
    "Organization": "#4ECDC4",
    "Technology": "#45B7D1",
    "Concept": "#96CEB4",
    "Location": "#FFEAA7"
}

def build_graph_html(graph_data: dict, output_path: str = "/tmp/graph.html") -> str:
    """Build a Pyvis network from graph data and save as HTML.
    Returns the path to the saved HTML file."""

    net = Network(
        height="600px",
        width="100%",
        bgcolor="#0e1117",
        font_color="white"
    )

    for node in graph_data["nodes"]:
        if node["id"] is None:
            continue
        color = TYPE_COLORS.get(node.get("type", ""), "#FFFFFF")
        net.add_node(
            node["id"],
            label=node["name"],
            title=f"Type: {node.get('type', 'Unknown')}",
            color=color,
            size=25
        )

    for edge in graph_data["edges"]:
        if edge["source"] is not None and edge["target"] is not None:
            net.add_edge(
                edge["source"],
                edge["target"],
                label=edge.get("type", ""),
                color="#AAAAAA"
            )

    net.set_options("""
    {
      "physics": {
        "forceAtlas2Based": {
          "gravitationalConstant": -50,
          "springLength": 200
        },
        "solver": "forceAtlas2Based"
      }
    }
    """)

    net.save_graph(output_path)
    return output_path