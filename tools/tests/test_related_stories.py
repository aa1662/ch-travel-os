import unittest

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


if __name__ == "__main__":
    unittest.main()
