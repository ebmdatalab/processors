# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import pytest
from processors.base import helpers
import processors.pubmed.extractors as extractors_module
from processors.base.processors.publication import process_publications


class TestPublicationProcessor(object):
    def test_creates_publication(self, conn, extractors, pubmed_record):
        pubmed_attrs = conn['warehouse']['pubmed'].find_one(pmid=pubmed_record)
        process_publications(conn, 'pubmed', extractors)

        publication = conn['database']['publications'].find_one(
            source_url=pubmed_attrs['meta_source']
        )
        assert publication is not None


    def test_links_publication_to_trial(self, conn, extractors, pubmed_record, trial, record):
        pubmed_attrs = conn['warehouse']['pubmed'].find_one(pmid=pubmed_record)
        record_attrs = conn['database']['records'].find_one(id=record)

        identifier = {'nct': 'NCT00020500'}
        pubmed_attrs['article_title'] = ('This publication is related to %s' % identifier)
        record_attrs.update({
            'trial_id': trial,
            'identifiers': identifier,
        })
        conn['warehouse']['pubmed'].update(pubmed_attrs, ['pmid'])
        conn['database']['records'].update(record_attrs, ['id'])
        process_publications(conn, 'pubmed', extractors)

        trials_publications = conn['database']['trials_publications'].find_one(
            trial_id=trial
        )
        assert trials_publications is not None


@pytest.fixture
def extractors():
    return helpers.get_variables(extractors_module,
        lambda x: x.startswith('extract_'))
