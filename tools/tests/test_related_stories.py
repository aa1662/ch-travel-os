import unittest
import json
import re
from pathlib import Path

from tools.build_trip_html import render_related_stories


class RelatedStoriesTests(unittest.TestCase):
    def test_card_uses_short_title_and_teaser(self):
        item = {"id": "current", "related": ["target"]}
        entries = {
            "current": item,
            "target": {
                "id": "target",
                "title": "A very long canonical article title",
                "nav_title": "Short card title",
                "teaser": "One useful reason to continue reading.",
                "output": "docs/trip/blog/target.html",
                "image_folder": "day-02",
                "og_image": "https://example.com/hero-desktop-1200w.webp",
            },
        }
        images = {
            "day-02/hero.jpg": {
                "derivatives": [
                    {
                        "profile": "thumb",
                        "filename": "hero-thumb-480w.webp",
                        "width": 480,
                        "height": 270,
                    },
                    {
                        "profile": "desktop",
                        "filename": "hero-desktop-1200w.webp",
                        "width": 1200,
                        "height": 675,
                    },
                ]
            }
        }
        errors = []

        result = render_related_stories(item, entries, images, errors)

        self.assertEqual(errors, [])
        self.assertIn("Short card title", result)
        self.assertIn("One useful reason to continue reading.", result)
        self.assertNotIn("A very long canonical article title", result)
        self.assertIn("hero-thumb-480w.webp", result)

    def test_existing_photo_resolves_actual_sizes_and_preserves_portrait(self):
        item = {"id": "current", "related": ["target"]}
        target = {"id": "target", "title": "Portrait", "output": "docs/trip/blog/target.html",
                  "image_folder": "day-01", "og_image": "https://example.com/hero-desktop-1200w.webp"}
        images = {"day-01/hero.jpg": {"derivatives": [
            {"profile": "thumb", "filename": "hero-thumb-360w.webp", "width": 360, "height": 480},
            {"profile": "desktop", "filename": "hero-desktop-900w.webp", "width": 900, "height": 1200},
        ]}}
        errors = []
        result = render_related_stories(item, {"target": target}, images, errors)
        self.assertEqual(errors, [])
        self.assertIn('class="related-story-portrait"', result)
        self.assertIn('hero-thumb-360w.webp', result)

    def test_every_published_article_has_curated_cards_and_existing_thumbnails(self):
        root = Path(__file__).resolve().parents[2]
        total = 0
        for path in (root / 'trips').glob('*/blog-migration.json'):
            entries = json.loads(path.read_text(encoding='utf-8'))['entries']
            published = {e['id']: e for e in entries if e.get('status') != 'draft'}
            for entry in published.values():
                total += 1
                ids = entry.get('related', [])
                self.assertEqual(len(ids), min(2, len(published) - 1))
                self.assertEqual(len(ids), len(set(ids)))
                self.assertNotIn(entry['id'], ids)
                self.assertTrue(all(target in published for target in ids))
                self.assertTrue(entry.get('nav_title'))
                self.assertTrue(entry.get('teaser'))
                page_path = root / entry['output']
                page = page_path.read_text(encoding='utf-8')
                sections = re.findall(r'<section class="related-stories"[\s\S]*?</section>', page)
                self.assertEqual(len(sections), 1)
                cards = sections[0]
                self.assertEqual(cards.count('class="related-story-card"'), len(ids))
                self.assertEqual(cards.count('class="related-story-teaser"'), len(ids))
                for src in re.findall(r'<img[^>]*src="([^"]+)"', cards):
                    self.assertIn('-thumb-', src)
                    self.assertTrue((page_path.parent / src).is_file(), src)
        self.assertEqual(total, 31)


if __name__ == "__main__":
    unittest.main()
