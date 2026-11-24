import argparse
import json
from pathlib import Path
from time import sleep
from urllib.parse import urlencode
from urllib.request import urlopen

from src.weather_ingest import build_weather_mapping
from src.yield_ingest import parse_yield_export

ROOT = Path(__file__).resolve().parents[1]
METADATA_URL = "https://www.geoboundaries.org/api/current/gbOpen/IND/ADM2/"
NASA_URL = "https://power.larc.nasa.gov/api/temporal/daily/point"
BOUNDARY_ID = "IND-ADM2-76128533"


def download_json(url, destination):
    with urlopen(url, timeout=120) as response:
        payload = response.read()
    document = json.loads(payload)
    temporary = destination.with_suffix(destination.suffix + ".part")
    temporary.write_bytes(payload)
    temporary.replace(destination)
    return document


def prepare_weather_inputs(raw_dir):
    districts = sorted({
        record[0] for record in parse_yield_export(raw_dir / "apy_query_report.xls")
    })

    metadata_file = raw_dir / "india_district_boundary_metadata.json"
    metadata = (
        json.loads(metadata_file.read_bytes()) if metadata_file.exists()
        else download_json(METADATA_URL, metadata_file)
    )
    if metadata["boundaryID"] != BOUNDARY_ID:
        raise ValueError(f"Expected boundary {BOUNDARY_ID}; got {metadata['boundaryID']}")

    boundary_file = raw_dir / "india_adm2_full.geojson"
    if not boundary_file.exists():
        download_json(metadata["gjDownloadURL"], boundary_file)

    _, cells = build_weather_mapping(raw_dir, districts)
    cache = raw_dir / "nasa_power"
    cache.mkdir(exist_ok=True)
    downloaded = 0

    for lon, lat in sorted(cells):
        destination = cache / f"lon_{lon:.3f}_lat_{lat:.3f}.json"
        if destination.exists():
            continue
        query = urlencode({
            "parameters": "T2M,PRECTOTCORR",
            "community": "AG",
            "longitude": lon,
            "latitude": lat,
            "start": "19980101",
            "end": "20220731",
            "format": "JSON",
        }, safe=",")
        print(f"Downloading cell {lon}, {lat}", flush=True)
        download_json(f"{NASA_URL}?{query}", destination)
        downloaded += 1
        sleep(1)

    print(f"Weather inputs ready: {len(cells)} grid cells | New NASA downloads: {downloaded}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Prepare cached weather inputs")
    parser.add_argument("--raw", type=Path, default=ROOT / "data" / "raw")
    prepare_weather_inputs(parser.parse_args().raw)
