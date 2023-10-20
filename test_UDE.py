import fcr_classes as fcr
import json
import xml.etree.ElementTree as ET
import pymarc

# Needs the marc feild 
# generic execution settings
es = fcr.Execution_Settings()
es.get_values_from_env()

# Load records
with open("./test_files/ABESXML.xml", mode="r+", encoding="utf-8") as f:
    ABESXML = ET.fromstring(f.read())
with open("./test_files/KOHA_API_PUBLICBIBLIO_JSON.json", mode="r+", encoding="utf-8") as f:
    KOHA_API_PUBLICBIBLIO_JSON = json.loads(json.load(f))
with open("./test_files/KOHA_API_PUBLICBIBLIO_MARC.mrc", mode="rb") as f:
    marcreader = pymarc.MARCReader(f, to_unicode=True, force_utf8=True)
    for record in marcreader:
        KOHA_API_PUBLICBIBLIO_MARC = record
with open("./test_files/KOHA_API_PUBLICBIBLIO_XML.xml", mode="r+", encoding="utf-8") as f:
    KOHA_API_PUBLICBIBLIO_XML = ET.fromstring(f.read())
with open("./test_files/KOHA_SRU_1_1_XML.xml", mode="r+", encoding="utf-8") as f:
    KOHA_SRU_1_1_XML = ET.fromstring(f.read())
with open("./test_files/KOHA_SRU_1_2_XML.xml", mode="r+", encoding="utf-8") as f:
    KOHA_SRU_1_2_XML = ET.fromstring(f.read())
with open("./test_files/KOHA_SRU_2_0_XML.xml", mode="r+", encoding="utf-8") as f:
    KOHA_SRU_2_0_XML = ET.fromstring(f.read())
with open("./test_files/SUDOC_SRU_PICA_packed_XML.xml", mode="r+", encoding="utf-8") as f:
    SUDOC_SRU_PICA_packed_XML = ET.fromstring(f.read())
with open("./test_files/SUDOC_SRU_PICA_XML_packed_XML.xml", mode="r+", encoding="utf-8") as f:
    SUDOC_SRU_PICA_XML_packed_XML = ET.fromstring(f.read())
with open("./test_files/SUDOC_SRU_UNIMARC_packed_XML.xml", mode="r+", encoding="utf-8") as f:
    SUDOC_SRU_UNIMARC_packed_XML = ET.fromstring(f.read())
with open("./test_files/SUDOC_SRU_UNIMARC_SHORT_packed_XML.xml", mode="r+", encoding="utf-8") as f:
    SUDOC_SRU_UNIMARC_SHORT_packed_XML = ET.fromstring(f.read())

# Get debugging mrac fields mapping
MARC_FIELD_MAPPING_DEBUG_SUDOC_XML = fcr.Marc_Fields_Mapping(es)
MARC_FIELD_MAPPING_DEBUG_SUDOC_XML.force_load_mapping(es, "DEBUG_SUDOC_XML")
MARC_FIELD_MAPPING_DEBUG_SUDOC_PICA = fcr.Marc_Fields_Mapping(es)
MARC_FIELD_MAPPING_DEBUG_SUDOC_PICA.force_load_mapping(es, "DEBUG_SUDOC_PICA")
MARC_FIELD_MAPPING_DEBUG_KOHA = fcr.Marc_Fields_Mapping(es)
MARC_FIELD_MAPPING_DEBUG_KOHA.force_load_mapping(es, "DEBUG_KOHA")
MARC_FIELD_MAPPING_KOHA_ARCHIRES = fcr.Marc_Fields_Mapping(es)
MARC_FIELD_MAPPING_KOHA_ARCHIRES.force_load_mapping(es, "KOHA_ARCHIRES")
MARC_FIELD_MAPPING_SUDOC = fcr.Marc_Fields_Mapping(es)
MARC_FIELD_MAPPING_SUDOC.force_load_mapping(es, "SUDOC")


# Set up universal data extratcor
ude_abexml = fcr.Universal_Data_Extractor(ABESXML, fcr.Databases.ABESXML, is_target_db=True, es=es)
ude_abexml.marc_fields_mapping = MARC_FIELD_MAPPING_DEBUG_SUDOC_XML
ude_koha_api_publicbiblio_json = fcr.Universal_Data_Extractor(KOHA_API_PUBLICBIBLIO_JSON, fcr.Databases.KOHA_PUBLIC_BIBLIO, is_target_db=False, es=es)
ude_koha_api_publicbiblio_json.marc_fields_mapping = MARC_FIELD_MAPPING_DEBUG_KOHA
ude_koha_api_publicbiblio_marc = fcr.Universal_Data_Extractor(KOHA_API_PUBLICBIBLIO_MARC, fcr.Databases.KOHA_PUBLIC_BIBLIO, is_target_db=False, es=es)
ude_koha_api_publicbiblio_marc.marc_fields_mapping = MARC_FIELD_MAPPING_DEBUG_KOHA
ude_koha_api_publicbiblio_xml = fcr.Universal_Data_Extractor(KOHA_API_PUBLICBIBLIO_XML, fcr.Databases.KOHA_PUBLIC_BIBLIO, is_target_db=False, es=es)
ude_koha_api_publicbiblio_xml.marc_fields_mapping = MARC_FIELD_MAPPING_DEBUG_KOHA
ude_koha_sru_1_1_xml = fcr.Universal_Data_Extractor(KOHA_SRU_1_1_XML, fcr.Databases.KOHA_SRU, is_target_db=False, es=es)
ude_koha_sru_1_1_xml.marc_fields_mapping = MARC_FIELD_MAPPING_DEBUG_KOHA
ude_koha_sru_1_2_xml = fcr.Universal_Data_Extractor(KOHA_SRU_1_2_XML, fcr.Databases.KOHA_SRU, is_target_db=False, es=es)
ude_koha_sru_1_2_xml.marc_fields_mapping = MARC_FIELD_MAPPING_DEBUG_KOHA
ude_koha_sru_2_0_xml = fcr.Universal_Data_Extractor(KOHA_SRU_2_0_XML, fcr.Databases.KOHA_SRU, is_target_db=False, es=es)
ude_koha_sru_2_0_xml.marc_fields_mapping = MARC_FIELD_MAPPING_DEBUG_KOHA
ude_sudoc_sru_pica_packed_xml = fcr.Universal_Data_Extractor(SUDOC_SRU_PICA_packed_XML, fcr.Databases.SUDOC_SRU, is_target_db=False, es=es)
ude_sudoc_sru_pica_packed_xml.marc_fields_mapping = MARC_FIELD_MAPPING_DEBUG_SUDOC_PICA
ude_sudoc_sru_pica_xml_packed_xml = fcr.Universal_Data_Extractor(SUDOC_SRU_PICA_XML_packed_XML, fcr.Databases.SUDOC_SRU, is_target_db=False, es=es)
ude_sudoc_sru_pica_xml_packed_xml.marc_fields_mapping = MARC_FIELD_MAPPING_DEBUG_SUDOC_PICA
ude_sudoc_sru_unimarc_packed_xml = fcr.Universal_Data_Extractor(SUDOC_SRU_UNIMARC_packed_XML, fcr.Databases.SUDOC_SRU, is_target_db=False, es=es)
ude_sudoc_sru_unimarc_packed_xml.marc_fields_mapping = MARC_FIELD_MAPPING_DEBUG_SUDOC_XML
ude_sudoc_sru_unimarc_short_packed_xml = fcr.Universal_Data_Extractor(SUDOC_SRU_UNIMARC_SHORT_packed_XML, fcr.Databases.SUDOC_SRU, is_target_db=False, es=es)
ude_sudoc_sru_unimarc_short_packed_xml.marc_fields_mapping = MARC_FIELD_MAPPING_DEBUG_SUDOC_XML

test_universal_data_extractor = {
    "Abes XML":ude_abexml,
    "Koha PublicBiblio JSON":ude_koha_api_publicbiblio_json,
    "Koha PublicBiblio MARC":ude_koha_api_publicbiblio_marc,
    "Koha PublicBiblio XML":ude_koha_api_publicbiblio_xml,
    "Koha SRU 1.1":ude_koha_sru_1_1_xml,
    "Koha SRU 1.2":ude_koha_sru_1_2_xml,
    "Koha SRU 2.0":ude_koha_sru_2_0_xml,
    "Sudoc SRU Pica":ude_sudoc_sru_pica_packed_xml,
    "Sudoc SRU Pica XML":ude_sudoc_sru_pica_xml_packed_xml,
    "Sudoc SRU UNM":ude_sudoc_sru_unimarc_packed_xml,
    "Sudoc SRU UNM short":ude_sudoc_sru_unimarc_short_packed_xml
}

# Abes filter value : 751025206
# Koha filter value : 762122301
filter_value = "762122301"

# TEST THING FINNALLY
# Don't expect much from PICA
for ude in test_universal_data_extractor:
    # Manual mother function tests
    if ude in ["Abes XML", "Sudoc SRU Pica", "Sudoc SRU Pica XML", "Sudoc SRU UNM", "Sudoc SRU UNM short"]:
        filter_value = "751025206"
    else:
        filter_value = "762122301"
    print("\n\n----------", ude, "----------")
    print("Control field (PPN) :", test_universal_data_extractor[ude].extract_data_from_marc_field(test_universal_data_extractor[ude].marc_fields_mapping.ppn))
    print("List of fields (Other DB IDs) :", test_universal_data_extractor[ude].extract_data_from_marc_field(test_universal_data_extractor[ude].marc_fields_mapping.other_database_id))
    print("List of fields with list of subfields (Title) :", test_universal_data_extractor[ude].extract_data_from_marc_field(test_universal_data_extractor[ude].marc_fields_mapping.title))
    print("List of fields with multiple subfields but no precise list (Items) :", test_universal_data_extractor[ude].extract_data_from_marc_field(test_universal_data_extractor[ude].marc_fields_mapping.items))
    print("Coded data positions (General processing dates) :", test_universal_data_extractor[ude].extract_data_from_marc_field(test_universal_data_extractor[ude].marc_fields_mapping.general_processing_data_dates))
    print("Filters (Items barcode) :", test_universal_data_extractor[ude].extract_data_from_marc_field(test_universal_data_extractor[ude].marc_fields_mapping.items_barcode, filter_value))

    # Nammed functions test
    if ude in ["Abes XML", "Sudoc SRU Pica", "Sudoc SRU UNM", "Sudoc SRU UNM short"]:
        test_universal_data_extractor[ude].marc_fields_mapping = MARC_FIELD_MAPPING_SUDOC
    if ude in ["Koha PublicBiblio JSON", "Koha PublicBiblio MARC", "Koha PublicBiblio XML", "Koha SRU 1.1", "Koha SRU 1.2", "Koha SRU 2.0"]:
        test_universal_data_extractor[ude].marc_fields_mapping = MARC_FIELD_MAPPING_KOHA_ARCHIRES
    print("Leader :", test_universal_data_extractor[ude].get_leader())
    print("Other database ID :", test_universal_data_extractor[ude].get_other_database_id("428"))
    print("Title :", test_universal_data_extractor[ude].get_title())
    print("General data processing dates :", test_universal_data_extractor[ude].get_general_processing_data_dates())
    print("Publisher names :", test_universal_data_extractor[ude].get_publishers_name())
    print("PPN :", test_universal_data_extractor[ude].get_ppn())
    print("Edition notes :", test_universal_data_extractor[ude].get_edition_notes())
    print("Publication dates :", test_universal_data_extractor[ude].get_publication_dates())
    print("Physical description :", test_universal_data_extractor[ude].get_physical_description())
    print("Erroneous ISBN :", test_universal_data_extractor[ude].get_erroneous_ISBN())
    print("Other medium IDs :", test_universal_data_extractor[ude].get_other_edition_in_other_medium_bibliographic_id())
    print("Items barcode :", test_universal_data_extractor[ude].get_items_barcode(filter_value))
    print("Items :", test_universal_data_extractor[ude].get_items(filter_value))