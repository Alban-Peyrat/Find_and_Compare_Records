import fcr_classes as fcr
import api.koha.Koha_API_PublicBiblio as Koha_API_PublicBiblio
import os

es = fcr.Execution_Settings(os.path.dirname(__file__))
es.load_env_values()
rec = fcr.Original_Record({})
# koha_record = Koha_API_PublicBiblio.Koha_API_PublicBiblio("514854", es.origin_url, service=es.service, format="application/marcxml+xml")
koha_record = Koha_API_PublicBiblio.Koha_API_PublicBiblio("75969", es.origin_url, service=es.service, format="application/marcxml+xml")

rec.get_origin_database_data(es.processing, koha_record.record_parsed, fcr.Databases.KOHA_PUBLIC_BIBLIO, es)
print(rec.origin_database_data.ude.get_contents_notes())