---
created:
---
---
## Prijsvraag

Air Traffic Control The Netherlands (LVNL) has asked the VSV 'Leonardo da Vinci' to host a competition among TU Delft Aerospace students. The competition consists of one question. The team that answers it correctly will win entrance and transport to and from the Airspace World Conference in Geneva. The question is as follows: ‘**What is the maximum number of take-offs and landings (added up) that Schiphol handled within one hour in 2023?**’. Every team shall consist of two persons (who have a VSV membership). The link to fill in your answer is in the link in the bio. Deadline is February 15th at 17:00! Good luck!!

[Answer form](https://forms.office.com/e/7Bh8RAvJQp) 

Dear student, Air Traffic Control The Netherlands (LVNL) has asked the VSV 'Leonardo da Vinci' to host a competition among TU Delft Aerospace students. The competition consists of one question. The team that answers it correctly will win the following prize:  
  
- Two tickets to **Airspace World Geneva** for one day on either March 20th or March 21st (this is yet to be determined)  
- Two plane tickets from Amsterdam to Geneva. Flying to Geneva in the morning and coming back to Amsterdam the same evening.  
- Pocket money for that day  
- A short meeting with Michiel Van Dorst, CEO of Air Traffic Control the Nehterlands (and member of honor of the VSV)  
  
Each team should consist of two students, both should be a member of the VSV. If more than one team answers the question correctly, the winning team will be randomly selected.

---
## Data:
Mogelijke bronnen waar we data vandaan kunnen halen.

  - [ADS-B exchange](https://www.adsbexchange.com/products/historical-data/) (per 5 sec) paid. Alleen data van eerste van iedere maand. Aanvraag ingediend om alle data van 2023 te krijgen.
  - [CBS Vliegbewegingen](https://www.cbs.nl/nl-nl/visualisaties/verkeer-en-vervoer/verkeer/vliegbewegingen) (per maand) Eig waardeloos
  - [OpenSky](https://opensky-network.org/data/impala) Lijkt de meeste potentie te hebben. Gratis data? Account maken lukt vooralsnog niet.
  - [Dutch Plane Spotters](https://schiphol.dutchplanespotters.nl/?date=2023-11-01) Alleen commerciele vluchten


#### ADS-B data
Opgeslagen in JSON bestanden, zoals hieronder. Voorbeeld van 1 Januari 2023 `000000Z.json.gz`, Met header van tijd, hoeveel heid messages? daarna 2 vliegtuig toestellen getoond, waarbij de ene veel mee info heeft dan de andere.
 
```
{ "now" : 1672531199.532,
  "messages" : 2826785130,
  "aircraft" : [
{"hex":"873334","type":"adsc","r":"JA933A","t":"B789","alt_baro":39996,"track":260.65,"lat":49.067001,"lon":-179.533081,"nic":0,"rc":0,"seen_pos":1324.543,"mlat":[],"tisb":[],"messages":38831796,"seen":1324.5,"rssi":-49.5},
{"hex":"a73d45","type":"adsb_icao","flight":"ASA184  ","r":"N566AS","t":"B738","alt_baro":7825,"alt_geom":6600,"gs":254.6,"track":235.56,"baro_rate":-1216,"squawk":"5724","emergency":"none","category":"A3","lat":52.195160,"lon":-176.141915,"nic":8,"rc":186,"seen_pos":0.297,"version":2,"nic_baro":1,"nac_p":9,"nac_v":1,"sil":3,"sil_type":"perhour","gva":2,"sda":2,"alert":0,"spi":0,"mlat":[],"tisb":[],"messages":44268988,"seen":0.2,"rssi":-3.9},
```


---
## Structuur:

Probleem: 5256000 tijdstappen, kaulo veel data

1) Verkrijg data
	1) [Zie Data hierboven](#data)
2) Data analyse
	1) Data cleaning and preprocessing
		- Ervoor zorgen dat de data clean is (bijv. geen ontbrekende waarden, juiste formaten).
	2) Data parsing
		- Convert time naar een format dat leesbaar is voor Python (zoals datetime) en zorg ervoor dat de tijdzones consistent zijn.
	3) Analysis
		- Bereken het aantal starts en landingen voor elk uur. (wat telt als landing en hoe detecteer je die)
	4) Finding maximum
		- Hoogste aantal landingen per uur


### Tools:
[traffic](https://github.com/xoolive/traffic) A toolbox for processing and analyzing air traffic data in python
