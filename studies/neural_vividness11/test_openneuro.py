import unittest
from inspect_openneuro import locate

class TestPublicManifestInspector(unittest.TestCase):
    def test_match_one_correct_url(self):
        rows=[{'path':'other.tsv','bytes_url':'https://example.net/x'},
              {'path':'mydir/derivatives/Behavioural_Ratings/P101.csv','bytes_url':'https://example.net/a'}]
        self.assertEqual(locate(rows),'https://example.net/a')
    def test_fails_missing_manifest_entry(self):
        with self.assertRaises(ValueError):locate([])
    def test_rejects_untrusted_non_https_url(self):
        with self.assertRaises(ValueError):locate([{'path':'derivatives/Behavioural_Ratings/P101.csv','bytes_url':'file:///etc/passwd'}])

if __name__=='__main__':unittest.main()