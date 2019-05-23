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
from data_facility_admin import metadata_serializer

DATASETS_SEARCH_META_FOLDER = 'data/datasets/search_metadata'
DATASETS_DETAIL_META_FOLDER = 'data/datasets/detailed_metadata'

import logging
logger = logging.getLogger(__name__)


def get_dataset_list():
    return (f.rstrip('.json') for f in listdir(DATASETS_SEARCH_META_FOLDER) if
            isfile(join(DATASETS_SEARCH_META_FOLDER, f)) and f.endswith('.json'))


def get_search_metadata_gmeta(dataset):
    with open('{0}/{1}.json'.format(DATASETS_SEARCH_META_FOLDER, dataset)) as f:
        data = json.load(f)
        return data['gmeta']


def get_detailed_metadata_gmeta(dataset):
    filename = '{0}/{1}.json'.format(DATASETS_DETAIL_META_FOLDER, dataset)
    try:
        print('===> %s' %filename)
        with open(filename) as f:
            data = json.load(f)
            print(' Detailed gmeta found!')
            return data['gmeta']

    except IOError as ex:
        print('File not found: %s' % filename)
    except Exception as ex:
        raise ex
        print('Detailed metadata for dataset %s not found' % dataset)
        return None


def update_or_create_datasets(datasets):
    for dataset_id in sorted(datasets):
        # if dataset_id not in ['dataset-adrf-000005']: continue
        try:
            print("\nProcessing dataset: %s" % dataset_id)
            print('     Getting gmeta')
            search_gmeta = get_search_metadata_gmeta(dataset_id)
            detailed_gmeta = get_detailed_metadata_gmeta(dataset_id)
            print('     Loading gmeta')
            dataset = metadata_serializer.load(search_gmeta, detailed_gmeta=detailed_gmeta)
            print('     Save dataset')

            save_or_update(dataset)
        # break
        except UnicodeEncodeError as ex:
            print(" -------> Error loading dataset: %s" % dataset_id)
            print("---\n%s\n---" % ex)
            logger.error(ex)


def save_or_update(dataset):
    # fields_to_update = ['data_provider', 'name', 'description',
    #                     'data_classification', 'search_gmeta', 'detailed_gmeta',
    #                     'version', 'dataset_citation', 'category',
    #                     ]
    fields_to_update = (mapping.dataset for mapping in metadata_serializer.DIRECT_FIELD_MAPPINGS)
    fields_to_update.remove('dataset_id')
    fields_to_update += ['search_gmeta', 'detailed_gmeta']
    try:
        db_dataset = Dataset.objects.get(dataset_id=dataset.dataset_id)
        for attr in fields_to_update:
            print('     Updating attr: ' + attr)
            value = getattr(dataset, attr, None)
            setattr(db_dataset, attr, value)
        db_dataset.available = False
        db_dataset.save()

        print(" > Dataset %s - updated." % dataset.dataset_id)

    except Dataset.DoesNotExist:
        db_dataset.available = False
        dataset.save()
        print(" > Dataset %s - created." % dataset.dataset_id)


def run():
    print("Loading datasets from folder %s " % DATASETS_SEARCH_META_FOLDER)

    datasets = get_dataset_list()
    # print('Datasets found: %s' % len(datasets))

    print("Updating datasets:")
    update_or_create_datasets(datasets)

    print("Done!")
