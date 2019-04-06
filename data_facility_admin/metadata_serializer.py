from data_facility_admin.models import Dataset, DataProvider, Category, Keyword
from collections import namedtuple
import json

import logging

logger = logging.getLogger(__name__)

FieldMapping = namedtuple('FieldMapping', ['dataset', 'gmeta', 'to_model', 'to_json'])
DATA_CLASSIFICATION_MAPPING = [
    FieldMapping(Dataset.DATA_CLASSIFICATION_GREEN, 'Public', None, None),
    FieldMapping(Dataset.DATA_CLASSIFICATION_RESTRICTED_GREEN, 'Restricted', None, None),
    FieldMapping(Dataset.DATA_CLASSIFICATION_YELLOW, 'Private', None, None),
    FieldMapping(Dataset.DATA_CLASSIFICATION_RED, None, None, None),
]
DATA_PROVIDER_KEY = 'data_provider'
CATEGORY_KEY = 'category'


def data_classification_to_metadata(data_classification=None):
    map = {mapping.dataset: mapping.gmeta for mapping in DATA_CLASSIFICATION_MAPPING}
    # print map
    # print('metadata_data_classification=', metadata_data_classification)
    return map.get(data_classification, Dataset.DATA_CLASSIFICATION_RED)


def data_classification_to_model(data_classification=None):
    map = {mapping.gmeta.lower(): mapping.dataset for mapping in DATA_CLASSIFICATION_MAPPING if mapping.gmeta is not None}
    # print map
    value = map.get(data_classification.lower(), None)
    # print('data_classification_to_model(%s)=%s' % (data_classification, map.get(data_classification, None)))

    return value


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


def __name_if_not_none(value):
    logger.debug('Value to get name or None: %s' % value)
    return value.name if value else None


def __to_date(s):
    import datetime
    try:
        if not s: return None
        elif '/' in s:
            return datetime.datetime.strptime(s, "%m/%d/%y").date()
        elif '-' not in s:
            return datetime.datetime.strptime(s, "%Y").date()
        elif len(s.split('-')) == 2:
            return datetime.datetime.strptime(s, "%Y-%m").date()
        elif len(s.split('-')) == 3:
            try:
                return datetime.datetime.strptime(s, "%Y-%d-%m").date()
            except:
                return datetime.datetime.strptime(s, "%Y-%m-%d").date()
    except:
        logger.error('Error translating %s to date.' % s)
        raise
        return None


def __get_year(d):
    return d.year if d is not None else None


def __to_keywords(keywords_list):
    keywords = []
    for keywork in keywords_list:
        try:
            k = Keyword.objects.get(name=keywork)
        except Keyword.DoesNotExist:
            k = Keyword(name=keywork)
            k.save()
        keywords.append(k)
    return keywords


def __keywords_to_list(dataset_keywords):
    return [k.name for k in dataset_keywords.all()] if keywords else []

DATASET_ID_FIELD = 'dataset_id'
DIRECT_FIELD_MAPPINGS = [
    FieldMapping('name', 'title', None, None),
    FieldMapping('description', 'description', None, None),
    FieldMapping(DATASET_ID_FIELD, DATASET_ID_FIELD, None, None),
    FieldMapping('version', 'dataset_version', None, None),
    FieldMapping('dataset_citation', 'dataset_citation', None, None),
    FieldMapping('source_url', 'source_url', None, None),
    FieldMapping('source_archive', 'source_archive', None, None),
    # FieldMapping('keywords', 'keywords', __to_keywords, __keywords_to_list),
    FieldMapping('temporal_coverage_start', 'temporal_coverage_start', __to_date, __get_year),
    FieldMapping('temporal_coverage_end', 'temporal_coverage_end', __to_date, __get_year),
    FieldMapping('category', 'category', __get_category, __name_if_not_none),
    FieldMapping('data_provider', 'data_provider', __get_data_provider, __name_if_not_none),
    FieldMapping('data_classification', 'data_classification',
                 __get_classification_model, data_classification_to_metadata),
    # FieldMapping('keywords', 'keywords'),
]


def load(search_gmeta, detailed_gmeta=None, given_dataset=None):
    """
    Loads a DFAdmin datateset from a gmeta dictionary (JSON).

    :param search_gmeta: inpuot JSON to create a dataset with.
    :return:
    """
    # print('Gmeta: \n %s' % json.dumps(search_gmeta, indent=4))
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

    # Clear duplicates in detailed content and search_content
    for key in search_content:
        del detailed_content[key]

    # Prep dataset if not given.
    if given_dataset:
        dataset = given_dataset
    else:
        try:
            dataset = Dataset.objects.get(dataset_id=search_content[DATASET_ID_FIELD])
        except Dataset.DoesNotExist:
            dataset = Dataset()

    # Load fields with direct Mapping
    for field_mapping in DIRECT_FIELD_MAPPINGS:
        try:
            value = search_content[field_mapping.gmeta]
            # If there is a method to map, call it.

            logger.debug('Dataset field "{0}" from gmeta field "{1}" = {2}'.format(field_mapping.dataset,
                                                                                   field_mapping.gmeta,
                                                                                   value))
            if field_mapping.to_model:
                value = field_mapping.to_model(value)
            # Set attribute on dataset and then remove the field from gmeta to avoid duplicates
            setattr(dataset, field_mapping.dataset, value)
            search_content.pop(field_mapping.gmeta, None)
            detailed_content.pop(field_mapping.gmeta, None)

        except UnicodeEncodeError as ex:
            setattr(dataset, field_mapping.dataset, value.encode('ascii', 'ignore'))

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
        if field_mapping.to_json:
            value = field_mapping.to_json(value)
        metadata[field_mapping.gmeta] = value
    return metadata

