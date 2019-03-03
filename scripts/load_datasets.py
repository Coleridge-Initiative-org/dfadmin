# Author Daniel Castellani - daniel.castellani@nyu.edu
#
# This script populates the initial data required for DFAdmin and ADRF to work properly.

import json
import urllib

from django.db import transaction

from data_facility_admin.models import *
from data_facility_admin.factories import *
from data_facility_metadata.models import *
import csv
from os import listdir
from os.path import isfile, join
from data_facility_metadata import gmeta_serializer

DATASETS_FOLDER = 'data/datasets/search_metadata'

import logging
logger = logging.getLogger(__name__)

def get_dataset_list():
    return (f.rstrip('.json') for f in listdir(DATASETS_FOLDER) if
            isfile(join(DATASETS_FOLDER, f)) and f.endswith('.json'))


def get_search_metadata_gmeta(dataset):
    with open('{0}/{1}.json'.format(DATASETS_FOLDER, dataset)) as f:
        data = json.load(f)
        return data['gmeta']


def update_or_create_datasets(datasets):
    for dataset_id in datasets:
        try:
            print("\nProcessing dataset: %s" % dataset_id)
            print('     Getting gmeta')
            gmeta = get_search_metadata_gmeta(dataset_id)
            print('     Loading gmeta')
            dataset = gmeta_serializer.load(gmeta)
            print('     Save dataset')
            save_or_update(dataset)
        # break
        except UnicodeEncodeError as ex:
            print(" -------> Error loading dataset: %s" % dataset_id)
            print("---\n%s\n---" % ex)
            logger.error(ex)


def save_or_update(dataset):
    try:
        db_dataset = Dataset.objects.get(dataset_id=dataset.dataset_id)
        db_dataset.search_gmeta = dataset.search_gmeta
        db_dataset.detailed_gmeta = dataset.detailed_gmeta
        db_dataset.title = dataset.title
        db_dataset.description = dataset.description
        db_dataset.save()

        print(" > Dataset %s - updated." % dataset)
    except Dataset.DoesNotExist:
        dataset.save()
        print(" > Dataset %s - created." % dataset)

def run():
    print("Loading datasets from folder %s " % DATASETS_FOLDER)

    datasets = get_dataset_list()
    # print('Datasets found: %s' % len(datasets))

    print("Updating datasets:")
    update_or_create_datasets(datasets)

    print("Done!")
