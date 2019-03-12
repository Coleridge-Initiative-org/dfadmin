from data_facility_admin.models import Dataset, DataProvider, Category
from collections import namedtuple
import json

import logging

logger = logging.getLogger(__name__)

FieldMapping = namedtuple('FieldMapping', ['dataset', 'gmeta', 'mapping'])
DATA_CLASSIFICATION_MAPPING = [
    FieldMapping(Dataset.DATA_CLASSIFICATION_GREEN, 'Public', None),
    FieldMapping(Dataset.DATA_CLASSIFICATION_RESTRICTED_GREEN, 'Restricted', None),
    FieldMapping(Dataset.DATA_CLASSIFICATION_YELLOW, 'Private', None),
    FieldMapping(Dataset.DATA_CLASSIFICATION_RED, None, None),
]
DATA_PROVIDER_KEY = 'data_provider'
CATEGORY_KEY = 'category'


def data_classification_to_metadata(data_classification=None):
    map = {mapping.dataset: mapping.gmeta for mapping in DATA_CLASSIFICATION_MAPPING}
    # print map
    # print('metadata_data_classification=', metadata_data_classification)
    return map.get(data_classification, Dataset.DATA_CLASSIFICATION_RED)


def data_classification_to_model(data_classification=None):
    map = {mapping.gmeta: mapping.dataset for mapping in DATA_CLASSIFICATION_MAPPING}
    # print map
    # print('data_classification_to_metadata=', data_classification_to_metadata)
    return map.get(data_classification, None)


def __get_classification_model(gmeta_classification):
    return data_classification_to_model(gmeta_classification)


def __get_data_provider(data_provider_name):
    logger.debug('Data Provider: %s' % data_provider_name)

    try:
        return DataProvider.objects.get(name=data_provider_name)
    except DataProvider.DoesNotExist:
        logger.info('Created Data Provider: %s' % data_provider_name)
        dp = DataProvider(name=data_provider_name)
        dp.save()
        return dp

def __get_category(category_name):
    logger.debug('Category: %s' % category_name)

    try:
        return Category.objects.get(name=category_name)
    except Category.DoesNotExist:
        logger.info('Created Category: %s' % category_name)
        o = Category(name=category_name)
        o.save()
        return o


DIRECT_FIELD_MAPPINGS = [
    FieldMapping('name', 'title', None),
    FieldMapping('description', 'description', None),
    FieldMapping('dataset_id', 'dataset_id', None),
    FieldMapping('version', 'dataset_version', None),
    FieldMapping('dataset_citation', 'dataset_citation', None),
    # FieldMapping('data_provider', 'data_provider', __get_data_provider),
    # FieldMapping('keywords', 'keywords'),
]


def load(search_gmeta, detailed_gmeta=None, given_dataset=None):
    """
    Loads a DFAdmin datateset from a gmeta dictionary (JSON).

    :param search_gmeta: inpuot JSON to create a dataset with.
    :return:
    """
    # print('Gmeta: \n %s' % json.dumps(search_gmeta, indent=4))
    dataset = given_dataset if given_dataset else Dataset()
    # The first key on gmeta is the item id. Gmeta is prepared to return a list of metadata.
    # So we need to get the first in this case.
    gmeta_data = search_gmeta[0][search_gmeta[0].keys()[0]]
    if detailed_gmeta is not None:
        detailed_gmeta_data = detailed_gmeta[0][search_gmeta[0].keys()[0]]
        detailed_content = detailed_gmeta_data['content']
    else:
        detailed_content = {}

    mimetype = gmeta_data['mimetype']
    search_content = gmeta_data['content']

    # Load fields with direct Mapping
    for field_mapping in DIRECT_FIELD_MAPPINGS:
        try:
            value = search_content[field_mapping.gmeta]
            #If there is a method to map, call it.

            logger.debug('Dataset field "{0}" from gmeta field "{1}" = {2}'.format(field_mapping.dataset,
                                                                                   field_mapping.gmeta,
                                                                                   value))
            if field_mapping.mapping:
                value = field_mapping.mapping(value)
            # Set attribute on dataset and then remove the field from gmeta to avoid duplicates
            setattr(dataset, field_mapping.dataset, value)
            search_content.pop(field_mapping.gmeta, None)
            detailed_content.pop(field_mapping.gmeta, None)

        except UnicodeEncodeError as ex:
            setattr(dataset, field_mapping.dataset, value.encode('ascii', 'ignore'))

    # Add other fields that need nested entities
    dataset.data_classification = __get_classification_model(search_content['data_classification'])
    dataset.data_provider = __get_data_provider(search_content[DATA_PROVIDER_KEY])
    dataset.category = __get_category(search_content[CATEGORY_KEY])

    dataset.search_gmeta = search_content
    dataset.detailed_gmeta = detailed_content
    return dataset


def dumps(dataset):
    """
    Generate a metadata representation of the dataset.

    :param dataset:
    :return:
    """
    metadata = {}
    if dataset.search_gmeta:
        metadata.update(dataset.search_gmeta)
    for field_mapping in DIRECT_FIELD_MAPPINGS:
        value = getattr(dataset, field_mapping.dataset, None)
        metadata[field_mapping.gmeta] = value
    metadata[DATA_PROVIDER_KEY] = dataset.data_provider.name if dataset.data_provider else None
    return metadata

