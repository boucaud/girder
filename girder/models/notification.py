#!/usr/bin/env python
# -*- coding: utf-8 -*-

###############################################################################
#  Copyright 2013 Kitware Inc.
#
#  Licensed under the Apache License, Version 2.0 ( the "License" );
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
###############################################################################

import datetime

from .model_base import Model, ValidationException


class ProgressState(object):
    """
    Enum of possible progress states for progress records.
    """
    QUEUED = 'queued'
    ACTIVE = 'active'
    SUCCESS = 'success'
    ERROR = 'error'

    @classmethod
    def isComplete(cls, state):
        return state == cls.SUCCESS or state == cls.ERROR


class Notification(Model):
    """
    This model is used to represent a notification that should be streamed
    to a specific user in some way. Each notification contains a
    type field indicating what kind of notification it is, a userId field
    indicating which user the notification should be sent to, a data field
    representing the payload of the notification, a time field indicating the
    time at which the event happened, and an optional expires field indicating
    at what time the notification should be deleted from the database.
    """
    def initialize(self):
        self.name = 'notification'
        self.ensureIndices(('userId', 'time'))
        self.ensureIndex(('expires', {'expireAfterSeconds': 0}))

    def validate(self, doc):
        """ TODO """
        return doc

    def _createRecord(self, type, data, user, expires=None):
        """
        Helper method to create the notification record that gets saved.
        """
        doc = {
            'type': type,
            'userId': user['_id'],
            'data': data,
            'time': datetime.datetime.now()
        }

        if expires is not None:
            doc['expires'] = expires

        return self.save(doc)

    def createProgressRecord(self, user, title, total,
                             state=ProgressState.ACTIVE, current=0, message=''):
        """
        Create a "progress" type notification that can be updated anytime there
        is progress on some task. Progress records that are not updated for more
        than one hour will be deleted.

        :param title: The title of the task. This should not change over the
        course of the task. (e.g. 'Deleting folder "foo"')
        :type title: str
        :param total: Some numeric value representing the total task length. By
        convention, setting this <= 0 means progress on this task is
        indeterminate.
        :type total: int, long, or float
        :param state: Represents the state of the underlying task execution.
        :type state: ProgressState enum value.
        :param current: Some numeric value representing the current progress
        of the task (relative to total).
        :type current: int, long, or float
        :param message: Message corresponding to the current state of the task.
        :type message: str
        """
        data = {
            'title': title,
            'total': total,
            'current': current,
            'state': state,
            'message': message
        }
        expires = datetime.datetime.now() + datetime.timedelta(hours=1)

        return self._createRecord('progress', data, user, expires)

    def updateProgress(self, record, **kwargs):
        """
        Update an existing progress record.

        :param record: The existing progress record to update.
        :type record: dict
        :param total: Some numeric value representing the total task length. By
        convention, setting this <= 0 means progress on this task is
        indeterminate. Generally this shouldn't change except in cases where
        progress on a task switches between indeterminate and determinate state.
        :type total: int, long, or float
        :param state: Represents the state of the underlying task execution.
        :type state: ProgressState enum value.
        :param current: Some numeric value representing the current progress
        of the task (relative to total).
        :type current: int, long, or float
        :param message: Message corresponding to the current state of the task.
        :type message: str
        """
        for field, value in kwargs:
            if field in ('total', 'current', 'state', 'message'):
                record['data'][field] = value
            else:
                raise Exception('Invalid kwarg: ' + field)

        return self.save(record)
