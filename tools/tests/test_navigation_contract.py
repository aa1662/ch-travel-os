import unittest

from tools.build_trip_html import (
    build_reading_navigation,
    journey_href_to_article_href,
    replace_mobile_overview,
)


class NavigationContractTests(unittest.TestCase):
    def setUp(self):
        self.entries = [
            {"id": "day-01"},
            {"id": "day-03"},
        ]
        self.config = {
            "reading_units": [
                {
                    "id": "day-01",
                    "type": "story",
                    "entry_id": "day-01",
                    "href": "blog/day-01.html",
                    "title": "Day 01",
                },
                {
                    "id": "day-02-interlude",
                    "type": "interlude",
                    "href": "index.html#interlude",
                    "title": "Day 02",
                },
                {
                    "id": "day-03",
                    "type": "story",
                    "entry_id": "day-03",
                    "href": "blog/day-03.html",
                    "title": "Day 03",
                },
            ]
        }

    def test_interlude_is_part_of_linear_reading_order(self):
        errors = []

        navigation = build_reading_navigation(self.config, self.entries, errors)

        self.assertEqual(errors, [])
        self.assertEqual(navigation["day-01"]["next"]["id"], "day-02-interlude")
        self.assertEqual(navigation["day-03"]["previous"]["id"], "day-02-interlude")
        self.assertEqual(
            journey_href_to_article_href("index.html#interlude"),
            "../index.html#interlude",
        )

    def test_missing_published_story_is_rejected(self):
        errors = []
        config = {"reading_units": self.config["reading_units"][:-1]}

        build_reading_navigation(config, self.entries, errors)

        self.assertTrue(any("缺少已發布文章: day-03" in error for error in errors))

    def test_mobile_overview_replaces_only_first_dock_item(self):
        source = '''<div class="mobile-dock">
    <a href="../index.html" class="dock-item">
      <span class="dock-icon">🏠</span>
      <span>首頁</span>
    </a>
    <a href="javascript:void(0)" class="dock-item btn-share">分享</a>
  </div>'''

        result = replace_mobile_overview(
            source,
            {"href": "../index.html", "icon": "🇦🇺", "label": "澳洲總覽"},
        )

        self.assertIn('<span class="dock-icon">🇦🇺</span>', result)
        self.assertIn("<span>澳洲總覽</span>", result)
        self.assertIn("btn-share", result)
        self.assertNotIn("<span>首頁</span>", result)


if __name__ == "__main__":
    unittest.main()
