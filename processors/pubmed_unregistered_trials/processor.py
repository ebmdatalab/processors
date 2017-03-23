# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import json
import logging
from sqlalchemy import exc as sqlalchemy_exceptions
from .. import base
from . import extractors as extractors_module
from ..pubmed_publications import extractors as related_extractors_module
logger = logging.getLogger(__name__)


def process(conf, conn):
    extractors = base.helpers.get_variables(
        extractors_module, lambda x: x.startswith('extract_')
    )
    related_extractors = base.helpers.get_variables(
        related_extractors_module, lambda x: x.startswith('extract_')
    )
    source = related_extractors['extract_source'](None)
    source_id = base.writers.write_source(conn, source)

    for record in base.helpers.iter_rows(conn, 'warehouse', 'pubmed', orderby='meta_id'):
        publication = related_extractors['extract_publication'](record)
        unregistered_trial = extractors['extract_trial'](record)
        conn['database'].begin()
        try:

            # Create/Update unregistered trial from the publication
            if not publication['registry_ids']:
                trial_id, is_primary = base.writers.write_trial(
                    conn, unregistered_trial, source_id, record['meta_id']
                )
                base.writers.write_record(
                    conn, record, source_id, trial_id, unregistered_trial, is_primary
                )

            # Publication is not/no longer an unregistered trial but a results document
            else:
                delete_record = "DELETE FROM records WHERE identifiers @> '%s'"
                delete_record = delete_record % json.dumps(unregistered_trial['identifiers'])
                conn['database'].query(delete_record)
                for identifiers in publication['registry_ids']:
                    trial = base.helpers.find_trial_by_identifiers(
                        conn, identifiers=identifiers
                    )
                    if trial:
                        doc_category_id = extractors['extract_document_category'](record)
                        document = extractors['extract_document'](record)
                        document.update({
                            'source_id': source_id,
                            'document_category_id': doc_category_id,
                        })
                        document_id = base.writers.write_document(conn, document)
                        base.writers.write_trial_relationship(
                            conn, 'document', document, document_id, trial['id']
                        )
        except sqlalchemy_exceptions.DBAPIError:
            conn['database'].rollback()
            base.config.SENTRY.captureException(extra={
                'record': record,
            })
            logger.debug('Couldn\'t process unregistered trial from PubMed record: %s',
                record['meta_id']
            )
        else:
            conn['database'].commit()
