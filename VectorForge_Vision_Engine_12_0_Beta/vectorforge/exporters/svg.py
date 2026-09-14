from pathlib import Path
from vectorforge.exporters.common import bounds

def export_svg(path, geometry, width_mm):
    min_x,min_y,max_x,max_y = bounds(geometry)
    width_px = max(max_x-min_x,1e-6)
    height_px = max(max_y-min_y,1e-6)
    scale = width_mm/width_px
    height_mm = height_px*scale

    items = []

    for item in geometry:
        if item["kind"] == "circle":
            cx,cy = item["center"]
            items.append(
                f'<circle cx="{(cx-min_x)*scale:.5f}" '
                f'cy="{(cy-min_y)*scale:.5f}" '
                f'r="{item["radius"]*scale:.5f}" '
                f'fill="none" stroke="#000" stroke-width="0.1"/>'
            )
            continue

        points = item.get("points",[])
        if len(points) < 2:
            continue

        commands = [
            f"{'M' if index == 0 else 'L'} "
            f"{(x-min_x)*scale:.5f} {(y-min_y)*scale:.5f}"
            for index,(x,y) in enumerate(points)
        ]
        if item.get("closed",False):
            commands.append("Z")

        items.append(
            f'<path d="{" ".join(commands)}" '
            f'fill="none" stroke="#000" stroke-width="0.1"/>'
        )

    svg = "\\n".join([
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'width="{width_mm:.5f}mm" height="{height_mm:.5f}mm" '
        f'viewBox="0 0 {width_mm:.5f} {height_mm:.5f}">',
        *items,
        '</svg>'
    ])

    Path(path).write_text(svg,encoding="utf-8")
