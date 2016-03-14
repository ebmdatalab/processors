# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import os
import time
import dataset

from ..helpers import upsert


def map_data():

    wh = dataset.connect(os.environ['OPENTRIALS_WAREHOUSE_URL'])
    db = dataset.connect(os.environ['OPENTRIALS_DATABASE_URL'])


    # source

    source_id = upsert(db['sources'], ['name', 'type'], {
        'name': 'actrn',
        'type': 'register',
        'data': {},
    })


    for item in wh['actrn']:


        # Log mapping

        print('Mapped: %s' % item['trial_id'])
        time.sleep(0.1)
