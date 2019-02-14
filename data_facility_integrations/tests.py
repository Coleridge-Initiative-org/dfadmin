# # -*- coding: utf-8 -*-
# from __future__ import unicode_literals
# from .rds_hooks import *
#
# from django.test import TestCase
#
# class TestDatabaseRDS(TestCase):
#
#     def test_should(self):
#         self.signal_was_called = False
#         self.total = None
#         def handler(sender, total, **kwargs):
#             self.signal_was_called = True
#             self.total = total
#         charge_completed.connect(handler)
#         charge(100)
#         self.assertTrue(self.signal_was_called)
#         self.assertEqual(self.total, 100)
#         charge_completed.disconnect(handler)