import datetime
import re
import requests
from robot.api import logger
from robot.api.deco import keyword
from QWeb.internal import window
from urllib.parse import urlparse, parse_qs, urlencode

class QForceACN():
    ROBOT_LIBRARY_DOC_FORMAT = 'reST'

    """
    This library was created to extend the ``QForce`` library provided with Copado Robotic Testing.
    """

    def __init__(self):
        self.access_token = None
        self.loginUrl = None
        self.namespace = 'vlocity_cmt'

    @keyword(name="Authenticate", tags=['REST API'])
    def authenticate(self, client_id, client_secret, username, password, loginUrl):
        r"""Authenticates to Salesforce REST API and sets access token which will be used in all subsequent calls.
        When combining this library with the QForce library, please ensure you prepend the keyword with ``QForceACN.``

        Example
        --------
        .. code:: robotframework

            QForceACN.Authenticate     ${client_id}   ${client_secret}   myusername@test.com    ${password}    ${loginUrl}

        Parameters
        ----------

        ``client_id`` : str
            Consumer key of a connected app
        ``client_secret`` : str
            Consumer secret of a connected app
        ``username`` : str
            Your Salesforce username
        ``password`` : str
            Your Salesforce password
        ``loginUrl`` : str
            The url used for Salesforce login, defaults to https://login.salesforce.com

        Raises
        ------
        ``ConnectionError``
            Authentication call was not successful.
        ``KeyError``
            Reply did not contain expected data.
        """
        # Set up the request data
        data = {
            'grant_type': 'password',
            'client_id': client_id,
            'client_secret': client_secret,
            'username': username,
            'password': password
        }

        self.loginUrl = loginUrl.split('.com',1)[0] + '.com'
        tokenUrl = self.loginUrl + '/services/oauth2/token'

        # Make the request
        response = requests.post(tokenUrl, data=data)

        # Extract the access token from the response
        self.access_token = response.json()['access_token']

    @keyword(name="Revoke", tags=['REST API'])
    def revoke(self):
        r"""Revokes authentication token. You need to call Authenticate again to continue using the Salesforce REST API keywords.
        When combining this library with the QForce library, please ensure you prepend the keyword with ``QForceACN.``

        Example
        --------
        .. code:: robotframework

            QForceACN.Authenticate     ${client_id}   ${client_secret}   myusername@test.com    ${password}    ${loginUrl}
            # do API things
            QForceACN.Revoke
        """

        # Reset the access_token
        self.access_token = None

    @keyword(name="Execute Integration Procedure", tags=['OmniStudio', 'REST API'])
    def execute_integration_procedure(self, type_subtype, json=None, **params):
        r"""Executes an OmniStudio Integration Procedure via the Salesforce REST API and returns a JSON string for further processing.

        Example
        --------
        .. code:: robotframework

            ${params}=   Create Dictionary    key1=value1    key2=value2    key3=value3
            ${result}=   Execute Integration Procedure     Application_GrantMgmt    params=&{params}

            ${json}      Load Json From File    testfile.json
            ${result}=   Execute Integration Procedure     Application_GrantMgmt    json=${json}

        Parameters
        ----------

        ``type_subtype`` : str
            Type and Subtype of the integration procedure you would like to run, concatenated with an underscore (e.g. Type_SubType)
        ``json`` : str
            A json-formatted string to pass into the integration procedure
        ``params`` : dict
            A dictionary of key-value pairs related to the input parameters to pass into the integration procedure
        """
        # Set up the request headers
        headers = {
            'Authorization': 'Bearer ' + self.access_token,
            'Content-Type': 'application/json'
        }

        # Build the request
        requestUrl = self.loginUrl
        requestUrl += '/services/apexrest/'
        requestUrl += self.namespace
        requestUrl += '/v1/integrationprocedure/'
        requestUrl += type_subtype
        if params != None:
            requestUrl += '?' + urlencode(params)

        logger.info(requestUrl)

        # Make the request
        response = requests.get(requestUrl, json=json, headers=headers)

        # Extract the data from the response
        return response.json()

    @keyword(name="Execute DataRaptor", tags=['OmniStudio', 'REST API'])
    def execute_dataraptor(self, bundleName, **params):
        r"""Executes an OmniStudio DataRaptor via the Salesforce REST API and returns a JSON string for further processing.

        Example
        --------
        .. code:: robotframework
        
            ${params}=   Create Dictionary    key1=value1    key2=value2    key3=value3
            ${result}=   Execute DataRaptor     LookupAccounts    &{params}

        Parameters
        ----------

        ``bundleName`` : str
            Bundle name of the DataRaptor you would like to run
        ``params`` : dict
            A dictionary of key-value pairs related to the input parameters to pass into the DataRaptor
        """
        # Set up the request headers
        headers = {
            'Authorization': 'Bearer ' + self.access_token,
            'Content-Type': 'application/json'
        }

        # Build the request
        requestUrl = self.loginUrl
        requestUrl += '/services/apexrest/'
        requestUrl += self.namespace
        requestUrl += '/v2/DataRaptor/'
        requestUrl += bundleName
        requestUrl += '?' + urlencode(params)

        logger.info(requestUrl)

        # Make the request
        response = requests.get(requestUrl, headers=headers)

        # Extract the data from the response
        return response.json()
    
    @keyword(name="Execute Calculation Procedure", tags=['OmniStudio', 'REST API'])
    def execute_calculation_procedure(self, configName, effectiveDate=None, **params):
        r"""Executes an OmniStudio Calculation Procedure via the Salesforce REST API and returns a JSON string for further processing.

        Example
        --------
        .. code:: robotframework

            ${datetime}=    Convert Date    2023-06-11 10:07:42    datetime
            ${params}=   Create Dictionary    key1=value1    key2=value2    key3=value3
            ${result}=   Execute Calculation Procedure     CalcTax    ${datetime}    &{params}

        Parameters
        ----------

        ``configName`` : str
            Calculation procedure name
        ``effectiveDate`` : datetime, optional
            Effective datetime to get the right version of the calculation procedure and matrix
        ``params`` : dict
            A dictionary of key-value pairs related to the input parameters to pass into the calculation procedure
        """
        # Set up the request headers
        headers = {
            'Authorization': 'Bearer ' + self.access_token,
            'Content-Type': 'application/json'
        }

        if(effectiveDate != None and isinstance(effectiveDate, datetime.datetime)):
            params['effectiveDate'] = effectiveDate.strftime("%Y-%m-%d %H:%M:%S")

        # Build the request
        requestUrl = self.loginUrl
        requestUrl += '/services/apexrest/'
        requestUrl += self.namespace
        requestUrl += '/v1/calculate/'
        requestUrl += configName
        requestUrl += '?' + urlencode(params)

        logger.info(requestUrl)

        # Make the request
        response = requests.get(requestUrl, headers=headers)

        # Extract the data from the response
        return response.json()

    @keyword(name="Get Vlocity Namespace", tags=['OmniStudio'])
    def get_vlocity_namespace(self):
        r"""Returns the configured Vlocity namespace used for OmniStudio API calls.  By default, the namespace is vlocity_cmt.

        Example
        --------
        .. code:: robotframework
        
            ${namespace}=   Get Vlocity Namespace
        """
        return self.namespace
    
    @keyword(name="Set Vlocity Namespace", tags=['OmniStudio'])
    def set_vlocity_namespace(self, namespace):
        r"""Sets the Vlocity namespace to be used for OmniStudio API calls.

        Example
        --------
        .. code:: robotframework
        
            Set Vlocity Namespace    vlocity_cmt

        Parameters
        ----------

        ``namespace`` : str
            Namespace you would like to set.  By default, the namespace is vlocity_cmt.
        """
        self.namespace = namespace

    @keyword(name="Get Record Id", tags=['UI'])
    def get_record_id(self):
        r"""Returns the Salesforce record id (either 15- or 18-char) found in URL of current page.

        Example
        --------
        .. code-block:: robotframework

            ${recordId}=    Get Record Id

        Parameters
        ----------
        None

        Raises
        ------
        ValueError
            Record id not found in URL
        """

        url = urlparse(window.get_url())
        # Find record ID from URL
        search_params = parse_qs(url.query)

        # Salesforce Classic and Console
        if url.hostname.endswith(".salesforce.com"):
            match = re.search(r"\/([a-zA-Z0-9]{3}|[a-zA-Z0-9]{15}|[a-zA-Z0-9]{18})(?:\/|$)", url.path)
            if match:
                res = match.group(1)
                if "0000" in res or len(res) == 3:
                    return match.group(1)

        # Lightning Experience and Salesforce1
        if url.hostname.endswith(".lightning.force.com"):
            match = None

            if url.path == "/one/one.app":
                # Pre URL change: https://docs.releasenotes.salesforce.com/en-us/spring18/release-notes/rn_general_enhanced_urls_cruc.htm
                match = re.search(r"\/sObject\/([a-zA-Z0-9]+)(?:\/|$)", url.fragment)
            else:
                match = re.search(r"\/lightning\/[r|o]\/[a-zA-Z0-9_]+\/([a-zA-Z0-9]+)", url.path)

            if match:
                return match.group(1)

        # Visualforce
        id_param = search_params.get("id")
        if id_param:
            return id_param[0]

        # Visualforce page that does not follow standard Visualforce naming
        for p in search_params.values():
            if re.match(r"^([a-zA-Z0-9]{3}|[a-zA-Z0-9]{15}|[a-zA-Z0-9]{18})$", p[0]) and "0000" in p[0]:
                return p[0]

        raise Exception("No Record Id found in current window URL.")