# coding: utf-8

from __future__ import absolute_import

from flask import json
from six import BytesIO

from swagger_server.models.decision_tree import DecisionTree  # noqa: E501
from swagger_server.models.guidance import Guidance  # noqa: E501
from swagger_server.models.object import Object  # noqa: E501
from swagger_server.test import BaseTestCase


class TestDosingModelController(BaseTestCase):
    """DosingModelController integration test stubs"""

    def test_get_decision_tree(self):
        """Test case for get_decision_tree

        Get decision tree
        """
        response = self.client.open(
            '/krobasky/PDS-API-Plugin/1.0.0/decisionTree',
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_get_guidance(self):
        """Test case for get_guidance

        get guidance
        """
        response = self.client.open(
            '/krobasky/PDS-API-Plugin/1.0.0/guidance/{pluginId}/{model}'.format(plugin_id='plugin_id_example', model='model_example'),
            method='POST')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_get_patient_data(self):
        """Test case for get_patient_data

        Get patient data
        """
        body = Object()
        response = self.client.open(
            '/krobasky/PDS-API-Plugin/1.0.0/patient/{patientId}'.format(patient_id='patient_id_example'),
            method='POST',
            data=json.dumps(body),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    import unittest
    unittest.main()
