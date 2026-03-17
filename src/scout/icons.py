from slash.basic import SVG, SVGElem


def icon_table() -> SVG:
    return SVG(
        SVGElem(
            "path",
            fill="none",
            stroke="currentColor",
            d="M3 5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2zm0 5h18M10 3v18",
        )
        .set_attr("stroke-linecap", "round")
        .set_attr("stroke-linejoin", "round")
        .set_attr("stroke-width", "2"),
        width="24",
        height="24",
        viewBox="0 0 24 24",
    )


def icon_scatter() -> SVG:
    return SVG(
        SVGElem("circle", cx="7.5", cy="7.5", r="1.25", fill="currentColor"),
        SVGElem("circle", cx="18.5", cy="5.5", r="1.25", fill="currentColor"),
        SVGElem("circle", cx="11.5", cy="11.5", r="1.25", fill="currentColor"),
        SVGElem("circle", cx="7.5", cy="16.5", r="1.25", fill="currentColor"),
        SVGElem("circle", cx="17.5", cy="14.5", r="1.25", fill="currentColor"),
        SVGElem("path", d="M3 3v16a2 2 0 0 0 2 2h16")
        .set_attr("stroke-linecap", "round")
        .set_attr("stroke-linejoin", "round")
        .set_attr("stroke-width", "2")
        .set_attr("fill", "none")
        .set_attr("stroke", "currentColor"),
        width="24",
        height="24",
        viewBox="0 0 24 24",
    )


def icon_filter() -> SVG:
    return SVG(
        SVGElem("path", d="M4.5 7h15M7 12h10m-7 5h4")
        .set_attr("stroke-linecap", "round")
        .set_attr("stroke-linejoin", "round")
        .set_attr("stroke-width", "2")
        .set_attr("fill", "none")
        .set_attr("stroke", "currentColor"),
        width="24",
        height="24",
        viewBox="0 0 24 24",
    )


def icon_dots() -> SVG:
    return SVG(
        SVGElem(
            "path",
            fill="none",
            stroke="currentColor",
            d="M4 12a1 1 0 1 0 2 0a1 1 0 1 0-2 0m7 0a1 1 0 1 0 2 0a1 1 0 1 0-2 0m7 0a1 1 0 1 0 2 0a1 1 0 1 0-2 0",
        )
        .set_attr("stroke-linecap", "round")
        .set_attr("stroke-linejoin", "round")
        .set_attr("stroke-width", "2"),
        width="24",
        height="24",
        viewBox="0 0 24 24",
    )


def icon_theme() -> SVG:
    return SVG(
        SVGElem(
            "g",
            SVGElem(
                "path",
                fill="currentColor",
                d="M2.75 12A9.25 9.25 0 0 0 12 21.25V2.75A9.25 9.25 0 0 0 2.75 12",
            ),
            SVGElem(
                "path",
                stroke="currentColor",
                d="M12 21.25a9.25 9.25 0 0 0 0-18.5m0 18.5a9.25 9.25 0 0 1 0-18.5m0 18.5V2.75",
            )
            .set_attr("stroke-linecap", "round")
            .set_attr("stroke-linejoin", "round")
            .set_attr("stroke-width", "2"),
            fill="none",
        ),
        width="24",
        height="24",
        viewBox="0 0 24 24",
    )
