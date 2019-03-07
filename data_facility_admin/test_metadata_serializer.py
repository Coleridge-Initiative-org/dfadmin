# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase
import json

from data_facility_admin import metadata_serializer as serializer


def example_search_gmeta():
    with open('data/datasets/example_gmeta.json') as f:
        return json.load(f)['gmeta']

def example_search_metadata():
    with open('data/datasets/example_gmeta.json') as f:
        return json.load(f)['gmeta'][0]['adrf-000005']['content']


def example_detailed_gmeta():
    return None


# Create your tests here.
class GmetaTests(TestCase):

    def setUp(self):
        self.example_search_gmeta = example_search_gmeta()
        self.example_detailed_gmeta = example_detailed_gmeta()
        self.dataset = serializer.load(self.example_search_gmeta, self.example_detailed_gmeta)

    def test_load_gmeta_has_name(self):
        self.assertIsNotNone(self.dataset.name)

    def test_load_gmeta_has_description(self):
        self.assertIsNotNone(self.dataset.description)

    def test_load_gmeta_has_version(self):
        self.assertIsNotNone(self.dataset.version)

    def test_load_gmeta_has_dataset_id(self):
        self.assertIsNotNone(self.dataset.dataset_id)

    def test_load_gmeta_has_expected_search_gmeta_keys(self):
        # self.assertEqual(example_search_metadata(), self.dataset.metadata)
        expected_metadata = example_search_metadata()
        for key in expected_metadata:
            self.assertIn(key, self.dataset.search_metadata)

    def test_load_gmeta_has_expected_detailed_gmeta(self):
        self.assertEqual({}, self.dataset.detailed_metadata())
