def bounds(geometry):
    points = []

    for item in geometry:
        if item["kind"] == "circle":
            cx, cy = item["center"]
            r = item["radius"]
            points.extend([
                (cx-r,cy-r),
                (cx+r,cy+r)
            ])
        else:
            points.extend(item.get("points",[]))

    if not points:
        return 0,0,1,1

    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    return min(xs),min(ys),max(xs),max(ys)
