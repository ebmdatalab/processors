# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from .. import base


# Module API

def extract_source(record):
    source = {
        'id': 'jprn',
        'name': 'UMIN',
        'type': 'register',
    }
    return source


def extract_trial(record):

    # Get identifiers
    identifiers = base.helpers.clean_dict({
        'jprn': record['unique_trial_number'],
    })

    # Get public title
    public_title = base.helpers.get_optimal_title(
        record['title_of_the_study'],
        record['official_scientific_title_of_the_study'],
        record['unique_trial_number'])

    # Get recruitment status
    statuses = {
        'Completed': 'complete',
        'Enrolling by invitation(outpatients are not recruited publicly)': 'recruiting',
        'Main results already published': 'complete',
        'No longer recruiting': 'complete',
        'Open public recruiting(outpatients can be recruited publicly)': 'complete',
        'Preinitiation': 'pending',
        'Recruiting': 'recruiting',
        'Suspended': 'suspended',
        'Terminated': 'other',
    }
    recruitment_status = statuses[record['recruitment_status']]

    # Get gender
    gender = None
    if record['gender'] == 'Male and Female':
        gender = 'both'
    elif record['gender'] == 'Male':
        gender = 'male'
    elif record['gender'] == 'Female':
        gender = 'female'

    # Get has_published_results
    has_published_results = False
    if record['publication_of_results'] in ['Published', 'partially published']:
        has_published_results = True

    trial = {
        'primary_register': 'UMIN',
        'primary_id': record['unique_trial_number'],
        'identifiers': identifiers,
        'registration_date': record['date_of_registration'],
        'public_title': public_title,
        'brief_summary': record['narrative_objectives1'],
        'scientific_title': record['official_scientific_title_of_the_study'],
        'description': record['narrative_objectives1'],
        'recruitment_status': recruitment_status,
        'eligibility_criteria': {
            'inclusion': record['key_inclusion_criteria'],
            'exclusion': record['key_exclusion_criteria'],
        },
        'target_sample_size': record['target_sample_size'],
        'first_enrollment_date': record['anticipated_trial_start_date'],
        'study_type': record['study_type'],
        'study_design': record['basic_design'],
        'study_phase': record['developmental_phase'],
        'primary_outcomes': record['primary_outcomes'] or [],
        'secondary_outcomes': record['key_secondary_outcomes'] or [],
        'gender': gender,
        'has_published_results': has_published_results,
    }
    return trial


def extract_conditions(record):
    conditions = [record['condition']]
    return conditions


def extract_interventions(record):
    interventions = []
    return interventions


def extract_locations(record):
    locations = []
    return locations


def extract_organisations(record):
    organisations = []
    organisations.append({
        'name': record['name_of_primary_sponsor'],
        # ---
        'trial_role': 'primary_sponsor',
    })
    organisations.append({
        'name': record['source_of_funding'],
        # ---
        'trial_role': 'funder',
    })
    return organisations


def extract_persons(record):
    persons = []
    if record['research_name_of_lead_principal_investigator']:
        persons.append({
            'name': record['research_name_of_lead_principal_investigator'],
            'phones': [],
            # ---
            'trial_id': record['unique_trial_number'],
            'trial_role': 'principal_investigator',
        })
    if record['public_name_of_contact_person']:
        persons.append({
            'name': record['public_name_of_contact_person'],
            'phones': [],
            # ---
            'trial_id': record['unique_trial_number'],
            'trial_role': 'public_queries',
        })
    return persons