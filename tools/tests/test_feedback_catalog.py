import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools'))
from build_feedback_catalog import catalog


class FeedbackCatalogTests(unittest.TestCase):
    def test_generated_catalog_matches_config_and_public_output(self):
        generated = json.loads((ROOT / 'workers/reader-feedback/articles.json').read_text(encoding='utf-8'))
        self.assertEqual(generated, catalog())
        self.assertEqual(len(generated), 31)
        self.assertNotIn('2026-Tokyo', {a['trip'] for a in generated.values()})
        for identifier, article in generated.items():
            self.assertIn(f'data-article-id="{identifier}"', (ROOT / article['output']).read_text(encoding='utf-8'))
