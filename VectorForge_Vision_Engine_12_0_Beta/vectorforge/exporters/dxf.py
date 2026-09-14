from pathlib import Path
from vectorforge.exporters.common import bounds

def export_dxf(path, geometry, width_mm):
    min_x,min_y,max_x,max_y = bounds(geometry)
    width_px = max(max_x-min_x,1e-6)
    height_px = max(max_y-min_y,1e-6)
    scale = width_mm/width_px
    height_mm = height_px*scale

    out = [
        "0","SECTION","2","HEADER",
        "9","$ACADVER","1","AC1009",
        "9","$INSUNITS","70","4",
        "0","ENDSEC",
        "0","SECTION","2","ENTITIES"
    ]

    for item in geometry:
        layer = item.get("layer","VECTOR").upper()[:31]

        if item["kind"] == "circle":
            cx,cy = item["center"]
            out += [
                "0","CIRCLE","8",layer,
                "10",f"{(cx-min_x)*scale:.6f}",
                "20",f"{height_mm-(cy-min_y)*scale:.6f}",
                "30","0.0",
                "40",f"{item['radius']*scale:.6f}"
            ]
            continue

        points = item.get("points",[])
        if len(points) < 2:
            continue

        out += [
            "0","POLYLINE","8",layer,
            "66","1",
            "70",str(1 if item.get("closed",False) else 0)
        ]

        for x,y in points:
            out += [
                "0","VERTEX","8",layer,
                "10",f"{(x-min_x)*scale:.6f}",
                "20",f"{height_mm-(y-min_y)*scale:.6f}",
                "30","0.0"
            ]

        out += ["0","SEQEND","8",layer]

    out += ["0","ENDSEC","0","EOF"]
    Path(path).write_text("\\n".join(out),encoding="ascii")
