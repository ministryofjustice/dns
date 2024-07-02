import os
import tempfile
import unittest

import yaml
from remove_sectigo_blocks import find_and_remove_sectigo_block, process_yaml_file


class TestRemoveSectigoBlocks(unittest.TestCase):

    def test_find_and_remove_sectigo_block_dict(self):
        data = {
            "domain": {"type": "A", "value": "example.com"},
            "sectigo_domain": {"type": "CAA", "value": "sectigo.com"},
        }
        result, changed = find_and_remove_sectigo_block(data)
        self.assertTrue(changed)
        self.assertEqual(result, "sectigo_domain")
        self.assertNotIn("sectigo_domain", data)

    def test_find_and_remove_sectigo_block_list(self):
        data = [{"domain": "example.com"}, {"sectigo_domain": "sectigo.com"}]
        result, changed = find_and_remove_sectigo_block(data)
        self.assertTrue(changed)
        self.assertEqual(len(data), 1)
        self.assertNotIn("sectigo_domain", data[0])

    def test_find_and_remove_sectigo_block_nested(self):
        data = {
            "domain": {
                "subdomains": [
                    {"name": "www", "value": "example.com"},
                    {"name": "secure", "value": "sectigo.com"},
                ]
            }
        }
        result, changed = find_and_remove_sectigo_block(data)
        self.assertTrue(changed)
        self.assertEqual(result, "domain")

    def test_process_yaml_file(self):
        yaml_content = """
        domain:
          type: A
          value: example.com
        sectigo_domain:
          type: CAA
          value: sectigo.com
        """
        with tempfile.NamedTemporaryFile(mode="w+", delete=False) as temp_file:
            temp_file.write(yaml_content)
            temp_file_path = temp_file.name

        try:
            result = process_yaml_file(temp_file_path)
            self.assertTrue(result)

            with open(temp_file_path, "r") as file:
                processed_yaml = yaml.safe_load(file)

            self.assertIn("domain", processed_yaml)
            self.assertNotIn("sectigo_domain", processed_yaml)
        finally:
            os.unlink(temp_file_path)

    def test_process_yaml_file_no_sectigo(self):
        yaml_content = """
        domain:
          type: A
          value: example.com
        another_domain:
          type: CNAME
          value: example.net
        """
        with tempfile.NamedTemporaryFile(mode="w+", delete=False) as temp_file:
            temp_file.write(yaml_content)
            temp_file_path = temp_file.name

        try:
            result = process_yaml_file(temp_file_path)
            self.assertFalse(result)

            with open(temp_file_path, "r") as file:
                processed_yaml = yaml.safe_load(file)

            self.assertIn("domain", processed_yaml)
            self.assertIn("another_domain", processed_yaml)
        finally:
            os.unlink(temp_file_path)


if __name__ == "__main__":
    unittest.main()
