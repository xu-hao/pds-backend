import connexion
import six

from swagger_server.models.decision_tree import DecisionTree  # noqa: E501
from swagger_server.models.guidance import Guidance  # noqa: E501
from swagger_server.models.object import Object  # noqa: E501
from swagger_server import util


def get_decision_tree():  # noqa: E501
    """Get decision tree

     # noqa: E501


    :rtype: DecisionTree
    """
    return 'do some magic!'


def get_guidance(plugin_id, model):  # noqa: E501
    """get guidance

    get guidance # noqa: E501

    :param plugin_id: plugin id
    :type plugin_id: str
    :param model: plugin id
    :type model: str

    :rtype: Guidance
    """
    return 'do some magic!'


def get_patient_data(body, patient_id):  # noqa: E501
    """Get patient data

     # noqa: E501

    :param body: keyClinicalProperties
    :type body: dict | bytes
    :param patient_id: 
    :type patient_id: str

    :rtype: object
    """
    if connexion.request.is_json:
        body = Object.from_dict(connexion.request.get_json())  # noqa: E501
    return 'do some magic!'
