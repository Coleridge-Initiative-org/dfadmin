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


def create_or_get_file(dataset, file_name):
    ff = FileFormat.objects.get(name='csv')
    try:
        data_file = File.objects.get(name=file_name, dataset=dataset)
    except File.DoesNotExist:
        data_file = File(name=file_name, dataset=dataset)
    data_file.format = ff
    data_file.save()


def create_or_get_data_provider(data_owner):
    try:
        dp = DataProvider.objects.get(name=data_owner)
    except DataProvider.DoesNotExist:
        dp = DataProvider(name=data_owner)
        dp.save()
    return dp


def import_from_adrf_csv(file_name):

    headers = None

    with open(file_name) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        for row in csv_reader:
            print row
            if not headers:
                headers = {val: idx for idx, val in enumerate(row)}
            else:
                adrf_id = row[headers['adrf_id']]
                try:
                    dataset = Dataset.objects.get(dataset_id=adrf_id)
                except Dataset.DoesNotExist:
                    dataset = Dataset(dataset_id=adrf_id)
                dataset.name = row[headers['title']]
                dataset.description = row[headers['description']]
                dataset.source_archive = row[headers['source_archive']]
                dataset.version = row[headers['dataset_version']]
                dataset.public = True
                dataset.save()

                if row[headers['filenames']]:
                    for data_file in row[headers['filenames']].split(','):
                        create_or_get_file(dataset, data_file)

                if row[headers['data_steward']]:
                    steward_name = row[headers['data_steward']].split()
                    try:
                        u = User.objects.get(first_name=steward_name[0], last_name=steward_name[1])
                    except User.DoesNotExist:
                        u = User(first_name=steward_name[0], last_name=steward_name[1])
                        u.save()
                    try:
                        ds = DataSteward(user=u, dataset=dataset, start_date=timezone.now())
                        ds.save()
                    except:
                        pass
                if row[headers['data_provider']]:
                    dp = create_or_get_data_provider(row[headers['data_provider']])
                    dataset.data_provider = dp
                # dataset.save()





def grab_nyc_open_data_datasets():
    source_api = 'http://api.us.socrata.com/api/catalog/v1'
    response = urllib.urlopen(source_api)
    data = json.loads(response.read())['results']
    for d in data:
        if d['resource']['type'] == 'dataset':
            dataset = d['resource']
            print('Processing dataset %s' % dataset['id'])
            
            try:
                ds = Dataset.objects.get(dataset_id=dataset['id'])
            except Dataset.DoesNotExist:
                ds = Dataset(name=dataset['name'], dataset_id=dataset['id'], description=dataset['description'])

            if d['classification']['domain_metadata']:
                data_owner = [e['value']
                              for e in d['classification']['domain_metadata']
                              if e['key'] == 'Data-Owner_Owner']
                if data_owner:
                    dp = create_or_get_data_provider(data_owner)
                    ds.data_provider = dp
            ds.source_archive = 'NYC Open Data'
            ds.source_url = ['permalink']
            ds.public = True
            ds.save()

            try:
                dt = DataTable.objects.get(dataset=ds, name=ds.name)
            except DataTable.DoesNotExist:
                dt = DataTable(dataset=ds, name=ds.name)
                dt.save()

            columns_name = dataset['columns_name']
            columns_field_name = dataset['columns_field_name']
            columns_datatype = dataset['columns_datatype']
            columns_description = dataset['columns_description']
            for i in range(len(columns_name)):
                try:
                    v = Variable.objects.get(name=columns_name[i], data_table=dt)
                except Variable.DoesNotExist:
                    v = Variable(name=columns_name[i], data_table=dt)
                v.description = columns_description[i]
                v.provided_type = columns_datatype[i]
                v.save()

            create_or_get_file(ds, '{}.csv'.format(ds.dataset_id))

    print(Dataset.objects.count())


@transaction.atomic
def run():
    print('Loading Datasets from CSV')
    import_from_adrf_csv('ADRF_Dataset_Metadata-supplementary-datasets-20181220.csv')
    return

    print('Loading random Datasets')
    grab_nyc_open_data_datasets()

    print('Creating Storage Types')
    try:
        s3 = StorageType.objects.get(name='S3')
    except StorageType.DoesNotExist:
        s3 = StorageType(name='S3')
        s3.save()
    try:
        pg = StorageType.objects.get(name='PG')
    except StorageType.DoesNotExist:
        pg = StorageType(name='PG')
        pg.save()

    print('Creating Data Stores')
    try:
        db = DataStore.objects.get(name='Postgres', host='db.adrf.info')
    except DataStore.DoesNotExist:
        db = DataStore(name='Postgres', host='db.adrf.info', description='test', type=pg)
        db.save()
    try:
        central_store = DataStore.objects.get(name='Central Store', host='centralstore.s3.amazonaws.com')
    except DataStore.DoesNotExist:
        central_store = DataStore(name='Central Store',
                                  host='centralstore.s3.amazonaws.com',
                                  type=s3)
    central_store.save()

    h9gi = Dataset.objects.get(dataset_id='h9gi-nx95')

    print('Creating Data Table')
    if PhysicalDataTable.objects.count() == 0:
        dt = DataTable(name='Collisions', dataset=h9gi)
        dt.save()

        PhysicalDataTable(logical_data_table=dt,
                          path=h9gi.dataset_id + '.collisions',
                          data_store=db).save()
        PhysicalDataTable(logical_data_table=dt,
                          path=h9gi.dataset_id + '/collisions.csv',
                          data_store=central_store).save()

    if User.objects.count() < 100:
        print('Creating users')
        UserFactory.create_batch(100)

    if Project.objects.count() < 100:
        print('Creating projects')
        ProjectFactory.create_batch(100)

    print("Initial data loaded with success.")
