import json
import unicodedata
from collections import defaultdict
from math import floor

from shapely.geometry import shape


DISTRICT_ALIASES = {
    "Chengalpattu": "Chengalputtu",
    "Kanchipuram": "Kancheepuram",
    "Thenkasi": "Tenkasi",
    "Thoothukudi": "Thoothukkudi",
    "Villupuram": "Viluppuram",
}


def name_key(name):
    text = unicodedata.normalize("NFKC", name).casefold()
    return "".join(character for character in text if character.isalnum())


def build_weather_mapping(raw_dir, district_names):
    metadata = json.loads(
        (raw_dir / "india_district_boundary_metadata.json").read_bytes()
    )
    if metadata["boundaryID"] != "IND-ADM2-76128533":
        raise ValueError("Unexpected district boundary release")

    boundaries = json.loads((raw_dir / "india_adm2_full.geojson").read_bytes())
    by_name = defaultdict(list)
    for feature in boundaries["features"]:
        by_name[name_key(feature["properties"]["shapeName"])].append(feature)

    points = {}
    cells = defaultdict(list)
    shape_ids = set()

    for name in sorted(district_names):
        candidates = by_name[name_key(DISTRICT_ALIASES.get(name, name))]
        if len(candidates) != 1:
            raise ValueError(f"{name}: expected one shape, found {len(candidates)}")

        feature = candidates[0]
        shape_id = feature["properties"]["shapeID"]
        if shape_id in shape_ids:
            raise ValueError(f"Boundary shape reused for {name}")
        shape_ids.add(shape_id)

        polygon = shape(feature["geometry"])
        if polygon.is_empty or not polygon.is_valid:
            raise ValueError(f"Invalid district shape: {name}")
        point = polygon.representative_point()
        if not polygon.contains(point) or not (75.5 <= point.x <= 81 and 7.5 <= point.y <= 14):
            raise ValueError(f"Unexpected representative point: {name}")

        points[name] = (point.x, point.y)
        cell = (floor(point.x / 0.625 + 0.5) * 0.625,
                floor(point.y / 0.5 + 0.5) * 0.5)
        cells[cell].append(name)

    return points, dict(cells)
