# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase
import json

from data_facility_metadata import gmeta_serializer


def example_search_gmeta():
    with open('data/datasets/example_gmeta.json') as f:
        return json.load(f)['gmeta']


def example_detailed_gmeta():
    return None


# Create your tests here.
class GmetaTests(TestCase):

    def setUp(self):
        self.example_search_gmeta = example_search_gmeta()
        self.example_detailed_gmeta = example_detailed_gmeta()
        self.dataset = gmeta_serializer.load(self.example_search_gmeta, self.example_detailed_gmeta)

    def test_load_gmeta_has_title(self):
        self.assertIsNotNone(self.dataset.title)

    def test_load_gmeta_has_description(self):
        self.assertIsNotNone(self.dataset.description)

    def test_load_gmeta_has_version(self):
        self.assertIsNotNone(self.dataset.version)

    def test_load_gmeta_has_dataset_id(self):
        self.assertIsNotNone(self.dataset.dataset_id)

    def test_load_gmeta_has_expected_search_gmeta(self):
        self.assertEqual(self.example_search_gmeta, self.dataset.search_gmeta)

    def test_load_gmeta_has_expected_detailed_gmeta(self):
        self.assertEqual(self.example_detailed_gmeta, self.dataset.detailed_gmeta)
