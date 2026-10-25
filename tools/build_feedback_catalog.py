"""Generate the cloud whitelist from the shared config eligibility contract."""
import json
from pathlib import Path
from feedback_eligibility import feedback_eligible

ROOT = Path(__file__).resolve().parents[1]


def catalog():
    result = {}
    for path in sorted((ROOT / "trips").glob("*/blog-migration.json")):
        config = json.loads(path.read_text(encoding="utf-8"))
        trip = path.parent.name
        for entry in config.get("entries", []):
            if feedback_eligible(entry, trip, config.get("dest", trip)):
                if not (ROOT / entry["output"]).is_file():
                    raise ValueError("Eligible article has no public output")
                identifier = f"{trip}:{entry['id']}"
                result[identifier] = dict(article_id=identifier, trip=trip,
                                          title=entry.get("title", ""), output=entry["output"])
    return result


if __name__ == "__main__":
    target = ROOT / "workers/reader-feedback/articles.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(catalog(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Feedback catalog: {len(catalog())} articles")
