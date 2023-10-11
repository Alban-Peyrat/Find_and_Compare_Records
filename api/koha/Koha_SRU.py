# -*- coding: utf-8 -*- 

# external imports
import logging
import requests
import xml.etree.ElementTree as ET
import urllib.parse

#https://koha-community.org/manual/20.11/fr/html/webservices.html#sru-server
# https://www.loc.gov/standards/sru/sru-1-1.html
# https://www.loc.gov/standards/sru/cql/contextSets/cql-context-set-v1-2.html
# dc.identifier

NS = {
    "zs2.0": "http://docs.oasis-open.org/ns/search-ws/sruResponse",
    "zs1.1": "http://www.loc.gov/zing/srw/",
    "zs1.2": "http://www.loc.gov/zing/srw/",
    "marc": "http://www.loc.gov/MARC21/slim"
    }

class Koha_SRU(object):
    """Koha_API_PublicBiblio
    =======
    A set of function wich handle data returned by Koha API 'getBiblioPublic' 
    https://api.koha-community.org/20.11.html#operation/getBiblioPublic
    On init take as arguments :
    - biblionumber (Koha identifier)
    - Koha server URL
    - [optional] : format (the response format) :
        - "application/marcxml+xml" (default)
        - "application/marc-in-json"
        - "application/marc"
        - "text/plain"
"""

    def __init__(self, query, kohaUrl, service="Koha_SRU", version="1.1", recordSchema="marcxml", operation="searchRetrieve", maximumRecords=100, startRecord=1):
        self.logger = logging.getLogger(service)
        self.endpoint = kohaUrl + "/biblios"
        self.service = service
        self.query = urllib.parse.quote(query)
        self.version = str(version)
        self.recordSchema = str(recordSchema)
        self.operation = operation
        self.maximumRecords = maximumRecords
        self.startRecord = startRecord
        self.url =  '{}?version={}&recordSchema={}&operation={}&query={}&startRecord={}&maximumRecords={}'.format(self.endpoint,
                                            self.version, self.recordSchema, self.operation, self.query,
                                            self.startRecord, self.maximumRecords)
        print(self.url)
        self.payload = {
            
            }
        self.headers = {
            }
        
        try:
            r = requests.get(self.url, headers=self.headers, params=self.payload)
            r.raise_for_status()
        except requests.exceptions.HTTPError:
            self.status = 'Error'
            self.logger.error("{} :: Koha_SRU :: HTTP Status: {} || Method: {} || URL: {} || Response: {}".format(query, r.status_code, r.request.method, r.url, r.text))
            self.error_msg = "Service indisponible"
        except requests.exceptions.RequestException as generic_error:
            self.status = 'Error'
            self.logger.error("{} :: Koha_SRU :: Generic exception || URL: {} || {}".format(query, self.url, generic_error))
            self.error_msg = "Exception générique, voir les logs pour plus de détails"
        else:
            self.result = r.content.decode('utf-8')
            self.status = 'Success'
            self.logger.debug("{} :: Koha_SRU :: Success".format(query))

    def get_result(self):
            """Return the entire result."""
            return self.result

    def get_init_status(self):
        """Return the init status as a string."""
        return self.status

    def get_error_msg(self):
        """Return the error message as a string."""
        if hasattr(self, "error_msg"):
            return self.error_msg
        else:
            return "Pas de message d'erreur"  

    def get_nb_results(self):
        """Returns the number of results as an int."""
        root = ET.fromstring(self.result)
        if root.findall("zs{}:numberOfRecords".format(self.version), NS):
            return root.find("zs{}:numberOfRecords".format(self.version), NS).text
        else: 
            return 0

    def get_records(self):
        """Returns all records as a list"""
        root = ET.fromstring(self.result)
        return root.findall(".//zs{}:record".format(self.version), NS)

    def get_records_id(self):
        """Returns all records as a list of strings"""
        root = ET.fromstring(self.result)
        records = root.findall(".//zs{}:record".format(self.version), NS)

        output = []
        for record in records:
            output.append(record.find(".//marc:controlfield[@tag='001']", NS).text)
        
        return output
