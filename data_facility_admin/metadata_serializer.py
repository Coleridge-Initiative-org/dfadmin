from data_facility_admin.models import Dataset, DataProvider
from collections import namedtuple
import json

import logging

logger = logging.getLogger(__name__)



DATA_CLASSIFICATION_MAPPING = {
    'Public': Dataset.DATA_CLASSIFICATION_GREEN,
    'Restricted': Dataset.DATA_CLASSIFICATION_RESTRICTED_GREEN,
    '?': Dataset.DATA_CLASSIFICATION_YELLOW,
    '??': Dataset.DATA_CLASSIFICATION_RED,
}
DATA_PROVIDER_KEY = 'data_provider'


def __get_classification_model(gmeta_classification):
    if gmeta_classification in DATA_CLASSIFICATION_MAPPING:
        return DATA_CLASSIFICATION_MAPPING[gmeta_classification]
    return None


def __get_data_provider(data_provider_name):
    logger.debug('Data Provider: %s' % data_provider_name)

    try:
        return DataProvider.objects.get(name=data_provider_name)
    except DataProvider.DoesNotExist:
        logger.info('Created Data Provider: %s' % data_provider_name)
        dp = DataProvider(name=data_provider_name)
        dp.save()
        return dp


FieldMapping = namedtuple('FieldMapping', ['dataset', 'gmeta', 'mapping'])
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
    if detailed_gmeta:
        detailed_gmeta_data = detailed_gmeta[0][search_gmeta[0].keys()[0]]
        detailed_content = detailed_gmeta_data['content']
    else:
        detailed_content = None

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

        except UnicodeEncodeError as ex:
            setattr(dataset, field_mapping.dataset, value.encode('ascii', 'ignore'))

    # Add other fields that need nested entities
    dataset.data_classification = __get_classification_model(search_content['data_classification'])
    dataset.data_provider = __get_data_provider(search_content[DATA_PROVIDER_KEY])

    dataset.search_gmeta = search_content
    dataset.detailed_gmeta = detailed_gmeta
    return dataset


def dumps(dataset):
    """
    Generate a metadata representation of the dataset.

    :param dataset:
    :return:
    """
    metadata = dataset.search_gmeta.copy()
    for field_mapping in DIRECT_FIELD_MAPPINGS:
        value = getattr(dataset, field_mapping.dataset, None)
        metadata[field_mapping.gmeta] = value
    return metadata

