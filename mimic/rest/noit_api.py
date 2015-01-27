# -*- test-case-name: mimic.test.test_noit -*-
"""
Defines get token, impersonation
"""
import xmltodict
import json
from twisted.web.server import Request
from mimic.rest.mimicapp import MimicApp
from mimic.canned_responses.noit import (create_check, get_check, get_checks,
                                         delete_check, test_check)


### TO DO:
# Convert responses to XML
# Include all check type to the metrics in the fixtures
# Fixture to populate as per test check request
# Move away from using dict for the templates
# add tests
# Include errors such as 500s on create check


Request.defaultContentType = 'application/xml'


class NoitApi(object):

    """
    Rest endpoints for mocked Noit api.
    """

    app = MimicApp()

    def __init__(self, core):
        """
        :param MimicCore core: The core to which this NoitApi will be
            communicating.
        """
        self.core = core

    def validate_check_payload(self, request):
        """
        Validate the check request payload and returns the response code
        """
        content = str(request.content.read())
        payload = xmltodict.parse(content)
        attributes = ["name", "module", "target", "period", "timeout",
                      "filterset"]
        for each in attributes:
            if not payload["check"]["attributes"].get(each):
                return 404, None
        return 200, payload["check"]["attributes"]


    @app.route('/checks/test', methods=['POST'])
    def test_check(self, request):
        """
        Validates the check xml and returns ????
        """
        response = self.validate_check_payload(request)
        if (response[0] == 200):
            # request.setHeader("content-type", "application/xml")
            response_body = test_check(response[1]["module"])
            return json.dumps(response_body)
        request.setResponseCode(response[0])
        return

    @app.route('/checks/set/<check_id>', methods=['PUT'])
    def set_check(self, request, check_id):
        """
        Creates a check for the given check_id. If the check_id already exists, then
        it updates that check.
        TBD: Include error 400 and 500s. Module cannot be updated (test against noit service
            to see the response code expected)
        """
        # validate check_id is a uuid ?? does noit fail if not?

        response = self.validate_check_payload(request)
        request.setResponseCode(response[0])
        if (response[0] == 200):
            # construct xml response
            return create_check(response[1], check_id)
        return

    @app.route('/check/show/<check_id>', methods=['GET'])
    def get_checks(self, request, check_id):
        """
        Return the current configuration and state of the specified check.
        """
        # request.setHeader("content-type", "application/xml")
        return json.dumps(get_check(check_id))

    @app.route('/checks', methods=['GET'])
    def get_all_checks(self, request):
        """
        Return the current configuration and state of all checks.
        """
        # request.setHeader("content-type", "application/xml")
        return json.dumps(get_checks())


    @app.route('/checks/delete/<check_id>', methods=['DELETE'])
    def delete_checks(self, request, check_id):
        """
        Delete the specified check and return 204 response code
        """
        response_code = delete_check(check_id) or  200
        request.setResponseCode(response_code)
        request.setHeader("content-type", "application/xml")
        return
