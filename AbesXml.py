import os
import re
# external imports
import requests
import logging
import xml.etree.ElementTree as ET
# internal import
from mail import mail
import logs
from datetime import datetime


class AbesXml(object):
    """
    AbesXml
    =======
    A set of function wich handle data returned by service 'Sudoc in Xml' 
    http://documentation.abes.fr/sudoc/manuels/administration/aidewebservices/index.html#SudocMarcXML
    On init take a PPN (sudoc identifier) in argument
    ex : https://www.sudoc.fr/178565946.xml   
"""

    def __init__(self,ppn,service='AbesXml'):
        self.logger = logging.getLogger(service)
        self.endpoint = "https://www.sudoc.fr"
        self.service = service
        self.ppn = ppn
        if not(re.search("^\d{8}[\dxX]$", ppn)):
            self.status = "Error"
            self.logger.error("{} :: XmlAbes_Init :: PPN invalide".format(ppn))
            self.error_msg = "PPN invalide"
        else:
            url =  '{}/{}.xml'.format(self.endpoint, self.ppn)
            r = requests.get(url)
            try:
                r.raise_for_status()  
            except requests.exceptions.HTTPError:
                self.status = 'Error'
                self.logger.error("{} :: XmlAbes_Init :: HTTP Status: {} || Method: {} || URL: {} || Response: {}".format(ppn, r.status_code, r.request.method, r.url, r.text))
                self.error_msg = "PPN inconnu ou service indisponible"
            else:
                self.record = r.content.decode('utf-8')
                self.status = 'Succes'
                self.logger.debug("{} :: AbesXml :: Notice trouvées".format(ppn))

    @property
    
    def get_record(self):
        """
        Return the entire record
        
        Returns:
            string -- the record in unimarc_xml 
        """
        return self.record
    
    def get_init_status(self):
        """Return the init status
        """
        return self.status

    def get_error_msg(self):
        if self.error_msg is not None:
            return self.error_msg
        else:
            return "Pas de message d'erreur"

    def get_title_info(self):
        key_title = ''
        root = ET.fromstring(self.record)
        for subfield in root.find("./datafield[@tag='200']").getchildren():
            if subfield.attrib['code'] in ('a','d','e','h','i','v') :
                key_title = key_title + " " +subfield.text
        return key_title
  
    def get_dates_pub(self):
        root = ET.fromstring(self.record)
        zone_100 = None
        date_type = None
        date_1 = None
        date_2 = None
        if root.find("./datafield[@tag='100']/subfield[@code='a']") != None :
            zone_100 = root.find("./datafield[@tag='100']/subfield[@code='a']").text
            date_type = zone_100[8:9]
            date_1 = zone_100[9:13]
            date_2 = zone_100[13:17]
        return zone_100,date_type,date_1,date_2
   
    def get_leader(self):
        root = ET.fromstring(self.record)
        return root.find("./leader").text
    
    def get_ppn_autre_support(self):
        root = ET.fromstring(self.record)
        ppn_list = []
        for ppn in root.findall("./datafield[@tag='452']/subfield[@code='0']"):
            ppn_list.append(ppn.text)
        return ppn_list

    def get_editeurs(self):
        root = ET.fromstring(self.record)
        ed_list = []
        for ed in root.findall("./datafield[@tag='214']/subfield[@code='c']"):
            ed_list.append(ed.text)
        for ed in root.findall("./datafield[@tag='210']/subfield[@code='c']"):
            ed_list.append(ed.text)
        return ed_list