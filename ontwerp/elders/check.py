"""Fase 0 'Elders': datacheck Open Raadsinformatie (ORI) en CVDR per gemeente.

Bewust buiten src/ (geen pijplijncode, valt niet onder het codeslot).
Gebruik: python ontwerp/elders/check.py > ontwerp/elders/check.json
"""
import json, re, sys, time, urllib.parse, urllib.request

ORI = "https://api.openraadsinformatie.nl/v1/elastic/"
SRU = "https://zoekservice.overheid.nl/sru/Search?"
GEM = {  # ORI-indexnaam: naam in CVDR (dcterms.creator)
    "rotterdam": "Rotterdam", "amsterdam": "Amsterdam", "den_haag": "'s-Gravenhage",
    "utrecht": "Utrecht", "eindhoven": "Eindhoven", "tilburg": "Tilburg",
    "groningen": "Groningen", "schiedam": "Schiedam", "dordrecht": "Dordrecht",
    "vlaardingen": "Vlaardingen",
}
ONDERWERP = {
    "deelvervoer": "deelscooter* OR deelvervoer OR deelmobiliteit",
    "parkeren": "parkeervergunning OR parkeertarief OR parkeertarieven OR \"betaald parkeren\"",
    "handhaving": "boa OR boa's OR handhavers",
}


def haal(req, n=4):
    for i in range(n):
        try:
            return urllib.request.urlopen(req, timeout=90).read()
        except OSError:
            if i == n - 1:
                raise
            time.sleep(2 ** (i + 1))


def ori(idx, body):
    r = urllib.request.Request(ORI + idx + "/_search", data=json.dumps(body).encode(),
                               headers={"Content-Type": "application/json"})
    return json.loads(haal(r))


def tel(idx, query):
    return ori(idx, {"size": 0, "track_total_hits": True, "query": query})["hits"]["total"]["value"]


def sinds(d):
    return {"range": {"last_discussed_at": {"gte": d}}}


def cvdr(gem, titel):
    cql = f'dcterms.creator="{gem}" and dcterms.title any "{titel}" and overheidrg.inwerkingtredingDatum>="2024-01-01"'
    x = haal(SRU + urllib.parse.urlencode(
        {"query": cql, "x-connection": "cvdr", "maximumRecords": 50,
         "version": "1.2", "operation": "searchRetrieve"})).decode()
    d = sorted(re.findall(r"inwerkingtredingDatum[^>]*>(.*?)<", x))
    return {"n": int(re.search(r"numberOfRecords>(\d+)", x).group(1)), "nieuwste": d[-1] if d else None}


def main():
    uit = {}
    for g, cg in GEM.items():
        idx = f"ori_{g}_2*"
        a = ori(idx, {"size": 0, "aggs": {
            "t": {"terms": {"field": "@type", "size": 20}},
            "v": {"filter": {"term": {"@type": "Meeting"}}, "aggs": {
                "mx": {"max": {"field": "start_date"}},
                "j": {"date_histogram": {"field": "start_date", "calendar_interval": "year", "format": "yyyy"}}}}}})["aggregations"]
        mo = {"term": {"@type": "MediaObject"}}
        motie = {"match": {"name": "motie"}}
        r = {
            "types": {b["key"]: b["doc_count"] for b in a["t"]["buckets"]},
            "laatste_vergadering": a["v"]["mx"].get("value_as_string"),
            "vergaderingen_per_jaar": {b["key_as_string"]: b["doc_count"] for b in a["v"]["j"]["buckets"] if b["key_as_string"] >= "2018"},
            "documenten_met_tekst": tel(idx, {"bool": {"must": [mo, {"exists": {"field": "text"}}]}}),
            "motie_in_naam_sinds_2022": tel(idx, {"bool": {"must": [mo, motie, sinds("2022-01-01")]}}),
        }
        for k, t in ONDERWERP.items():
            qs = {"query_string": {"query": t, "fields": ["name", "text"]}}
            r["docs_" + k] = tel(idx, {"bool": {"must": [qs, sinds("2022-01-01")]}})
            r["moties_" + k] = tel(idx, {"bool": {"must": [motie, qs, sinds("2022-01-01")]}})
        r["cvdr"] = {t: cvdr(cg, t) for t in ["parkeerbelastingen", "parkeerverordening", "plaatselijke verordening"]}
        uit[g] = r
        print(g, file=sys.stderr, flush=True)
    json.dump(uit, sys.stdout, ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
