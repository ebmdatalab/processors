# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import pytest
import processors.base.helpers as helpers
import processors.pubmed.processor as processor
import processors.pubmed.extractors as extractors_module


class TestProcessUnregisteredTrials(object):
    def test_creates_unregistred_trial_if_no_registry_ids(self, conn, pubmed_record):
        pubmed_attrs = conn['warehouse']['pubmed'].find_one(pmid=pubmed_record)
        pubmed_attrs['registry_ids'] = None
        conn['warehouse']['pubmed'].update(pubmed_attrs, ['pmid'])
        identifiers = {'pubmed': ('PUBMED%s' % pubmed_record)}
        processor.process({}, conn)

        trial = helpers.find_trial_by_identifiers(conn, identifiers)
        assert trial is not None


    def test_creates_document_if_trial_found_from_registry_ids(self, conn,
        pubmed_record, record, trial, results_document_category):

        pubmed_attrs = conn['warehouse']['pubmed'].find_one(pmid=pubmed_record)
        record_attrs = conn['database']['records'].find_one(id=record)
        identifiers = {'isrctn': 'ISRCTN31181395'}
        pubmed_attrs['registry_ids'] = [identifiers]
        record_attrs.update({
            'identifiers': identifiers,
            'trial_id': trial,
        })
        conn['warehouse']['pubmed'].update(pubmed_attrs, ['pmid'])
        conn['database']['records'].update(record_attrs, ['id'])
        processor.process({}, conn)

        doc = conn['database']['documents'].find_one(
            source_url=pubmed_attrs['meta_source']
        )
        assert doc is not None


    def test_doesnt_create_document_if_trial_not_found_from_registry_ids(self, conn,
        pubmed_record):

        pubmed_attrs = conn['warehouse']['pubmed'].find_one(pmid=pubmed_record)
        pubmed_attrs['registry_ids'] = [{'isrctn': 'ISRCTN31181395'}]
        conn['warehouse']['pubmed'].update(pubmed_attrs, ['pmid'])
        processor.process({}, conn)

        doc = conn['database']['documents'].find_one(
            source_url=pubmed_attrs['meta_source']
        )
        assert doc is None


    def test_deletes_unregistered_trial_record_if_registry_ids_added(self, conn,
        pubmed_record, record):

        record_attrs = conn['database']['records'].find_one(id=record)
        record_attrs.update({
            'identifiers': {'pubmed': ('PUBMED%s' % pubmed_record)},
        })
        conn['database']['records'].update(record_attrs, ['id'])

        processor.process({}, conn)

        assert conn['database']['records'].find_one(id=record) is None


@pytest.fixture
def results_document_category(conn, document_category):
    extractors = helpers.get_variables(
        extractors_module, lambda x: x.startswith('extract_')
    )
    doc_category_id = extractors['extract_document_category'](None)
    doc_category_attrs = conn['database']['document_categories'].find_one(id=document_category)
    doc_category_attrs['id'] = doc_category_id
    conn['database']['document_categories'].update(doc_category_attrs, ['name', 'group'])
