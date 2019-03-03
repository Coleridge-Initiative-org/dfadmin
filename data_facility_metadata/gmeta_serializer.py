from data_facility_admin.models import Dataset
from collections import namedtuple
import json

import logging

logger = logging.getLogger(__name__)

FieldMapping = namedtuple('FieldMapping', ['dataset', 'gmeta'])
DIRECT_FIELD_MAPPINGS = [
    FieldMapping('title', 'title'),
    FieldMapping('description', 'description'),
    FieldMapping('dataset_id', 'dataset_id'),
    FieldMapping('version', 'dataset_version'),
    FieldMapping('dataset_citation', 'dataset_citation'),
    # FieldMapping('keywords', 'keywords'),
]


def load(search_gmeta, detailed_gmeta=None):
    """
    Loads a DFAdmin datateset from a gmeta dictionary (JSON).

    :param search_gmeta: inpuot JSON to create a dataset with.
    :return:
    """
    # print('Gmeta: \n %s' % json.dumps(search_gmeta, indent=4))
    dataset = Dataset()
    # The first key on gmeta is the item id. Gmeta is prepared to return a list of metadata.
    # So we need to get the first in this case.
    gmeta_data = search_gmeta[0][search_gmeta[0].keys()[0]]


    mimetype = gmeta_data['mimetype']
    content = gmeta_data['content']

    # Load fields with direct Mapping
    for field_mapping in DIRECT_FIELD_MAPPINGS:
        try:
            value = content[field_mapping.gmeta]
            # logger.debug('Dataset field "{0}" from gmeta field "{1}" = {2}'.format(field_mapping.dataset,
            #                                                                        field_mapping.gmeta,
            #                                                                        value))
            setattr(dataset, field_mapping.dataset, value)
        except UnicodeEncodeError as ex:
            setattr(dataset, field_mapping.dataset, value.encode('ascii', 'ignore'))


    # Add other fields that need nested entities


    dataset.search_gmeta = search_gmeta
    dataset.detailed_gmeta = detailed_gmeta
    return dataset
