# -*- coding: utf-8 -*- 

import requests
import logging
import xml.etree.ElementTree as ET
import re

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
        self.ppn = str(ppn)
        if not(re.search("^\d{8}[\dxX]$", self.ppn)):
            self.status = "Error"
            self.logger.error("{} :: XmlAbes_Init :: PPN invalide".format(ppn))
            self.error_msg = "PPN invalide"
        else:
            url =  '{}/{}.xml'.format(self.endpoint, self.ppn)
            try:
                r = requests.get(url)
                r.raise_for_status()
            except requests.exceptions.HTTPError:
                self.status = 'Error'
                self.logger.error("{} :: XmlAbes_Init :: HTTP Status: {} || Method: {} || URL: {} || Response: {}".format(ppn, r.status_code, r.request.method, r.url, r.text))
                self.error_msg = "PPN inconnu ou service indisponible"
            except requests.exceptions.RequestException as generic_error:
                self.status = 'Error'
                self.logger.error("{} :: XmlAbes_Init :: Generic exception || URL: {} || {}".format(ppn, url, generic_error))
                self.error_msg = "Exception générique, voir les logs pour plus de détails"
            else:
                self.record = r.content.decode('utf-8')
                self.status = 'Succes'
                self.logger.debug("{} :: AbesXml :: Notice trouvée".format(ppn))

    def get_record(self):
        """Return the entire record as a string in unimarc_xml."""
        return self.record
    
    def get_init_status(self):
        """Return the init status as a string."""
        return self.status

    def get_error_msg(self):
        """Return the error message as a string."""
        if self.error_msg is not None:
            return self.error_msg
        else:
            return "Pas de message d'erreur"

    def get_title_info(self):
        """Return the first 200 field's title content as a string.
        Each subfield is separated by a space."""
        key_title = []
        root = ET.fromstring(self.record)
        for subfield in root.find("./datafield[@tag='200']").findall("./subfield"):
            if subfield.attrib['code'] in ('a','d','e','h','i','v') :
                key_title.append(subfield.text)
        return " ".join(key_title)
  
    def get_dates_pub(self):
        """Return all publication dates in the 100 field.
        Returns a tuple :
         - 100 field
         - date type (pos. 8)
         - 1st publication date (pos. 9-12)
         - 2nd publication date (pos. 13-16)"""
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
        """Return the leader field content as a string."""
        root = ET.fromstring(self.record)
        return root.find("./leader").text
    
    def get_ppn_autre_support(self):
        root = ET.fromstring(self.record)
        ppn_list = []
        for ppn in root.findall("./datafield[@tag='452']/subfield[@code='0']"):
            ppn_list.append(ppn.text)
        return ppn_list

    def get_editeurs(self):
        """Return all publishers in 210/214$c subfields as a list."""
        root = ET.fromstring(self.record)
        ed_list = []
        for ed in root.findall("./datafield[@tag='214']/subfield[@code='c']") + root.findall("./datafield[@tag='210']/subfield[@code='c']"):
            ed_list.append(ed.text)
        return ed_list

    def get_local_system_nb(self, ILN):
        """Return all local system numbers as a list, without duplicates.

        Takes the ILN as argument.
        """
        root = ET.fromstring(self.record)
        local_sys_nb = []
        U035s = root.findall(".//datafield[@tag='035']")

        for U035 in U035s:
            U035iln = U035.find("subfield[@code='1']")
            if U035iln == None:
                continue
            
            if U035iln.text == str(ILN) and not U035.find("subfield[@code='a']").text in local_sys_nb:
                local_sys_nb.append(U035.find("subfield[@code='a']").text)

        return local_sys_nb
    
    def get_library_items(self, RCR):
        """Return all items for the library as a dict of dict, using EPN as key for the first dict.
        
        Takes the RCR as argument.
        EPN dicts :
            - barcode {list of str}
            - all fields {list of str}
        """
        
        root = ET.fromstring(self.record)
        # From Description des données d'exemplaire pour l'échange d'information bibliographique en format UNIMARC - Recommendations - Version 3 - Mai 2022
        item_tags = ["915", "916", "917", "919", "920", "930", "931", "932",
            "955", "956", "957", "958", "990", "991", "992",
            "316", "317", "318", "319", "371",
            "702", "703", "712", "713", "722", "723",
            "856",
            "940", "941"] #Sudoc
        items = {}
        
        # For each field of item_tags
        for tag in item_tags:
            for field in root.findall(".//datafield[@tag='{}']".format(tag)):

                # If the field is linked to an item
                field5 = field.find("subfield[@code='5']")
                if field5 != None:

                    # If the item is from this RCR
                    if field5.text[:9] == RCR:
                        EPN = field5.text[10:]

                        # Creates this EPN if doesn't exist already
                        if not EPN in items:
                            items[EPN] = {"barcodes":[],"fields":[]}

                        # Add barcodes to this EPN
                        if field.attrib["tag"] == "915":
                            for U915 in field.findall("subfield[@code='b']"):
                                items[EPN]["barcodes"].append(U915.text)

                            
                        items[EPN]["fields"].append(str(ET.tostring(field)))
        return items