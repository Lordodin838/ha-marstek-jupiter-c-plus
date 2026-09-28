# Changelog

## 1.2.0

### New

- **Battery charge power and battery discharge power:** two new sensors derived from the
  existing *Battery power (calculated)* value. *Charge power* is positive when the battery
  charges (zero otherwise); *discharge power* is positive when the battery discharges (zero
  otherwise). Both report W and carry the `power` device class, so they integrate directly
  into the Energy dashboard without extra helpers.

### Improved

- **Services `register_dump` and `read_register`:** both services now carry full
  `name` and `description` fields in `services.yaml`. An optional `entry_id` parameter
  selects the target instance when more than one Jupiter integration is set up; without
  it the service works as before for single-instance setups.
- **CI workflow:** GitHub Actions runs the full test suite on Python 3.11 and 3.12 in
  parallel on every push and pull request (pyflakes + pytest).
- **Dependabot:** weekly checks for GitHub Actions version updates.
- **Test coverage:** 70 tests across 10 files, including diagnostics, service helpers,
  and TCP reconnect scenarios.

### Removed

- **MQTT error fallback option:** the “MQTT error sensor as second source” field has been
  removed from the integration options. Error codes are read exclusively via Modbus.

---

### Deutsch

#### Neu

- **Batterie Ladeleistung und Batterie Entladeleistung:** zwei neue Sensoren, abgeleitet
  aus dem bestehenden *Batterieleistung (berechnet)*-Wert. *Ladeleistung* ist positiv wenn
  die Batterie lädt (sonst null); *Entladeleistung* ist positiv wenn die Batterie entlädt
  (sonst null). Beide liefern W mit der `power`-Device-Klasse und lassen sich direkt im
  Energie-Dashboard einbinden – keine zusätzlichen Helper nötig.

#### Verbessert

- **Dienste `register_dump` und `read_register`:** beide Dienste haben jetzt vollständige
  `name`- und `description`-Felder in `services.yaml`. Ein optionaler Parameter `entry_id`
  wählt die Ziel-Instanz, wenn mehrere Jupiter-Integrationen eingerichtet sind; ohne ihn
  verhält sich der Dienst wie bisher.
- **CI-Workflow:** GitHub Actions führt die gesamte Test-Suite auf Python 3.11 und 3.12
  parallel aus – bei jedem Push und Pull-Request (pyflakes + pytest).
- **Dependabot:** wöchentliche Prüfung auf neue Versionen der GitHub Actions.
- **Testabdeckung:** 70 Tests in 10 Dateien, darunter Diagnostics, Service-Hilfsfunktionen
  und TCP-Reconnect-Szenarien.

#### Entfernt

- **MQTT-Fehlercode-Fallback:** Das Optionsfeld „MQTT-Fehlersensor als zweite Quelle“
  wurde entfernt. Fehlercodes werden ausschließlich über Modbus gelesen.

---

## 1.1.0

### New

- **Energy counters for the Energy dashboard:** *PV energy*, *Battery
  charged* and *Battery discharged* (kWh). The integration accumulates
  them itself from the 10 s power values, so Riemann integral helpers are
  no longer needed. Only freshly read values are counted; outages longer
  than 60 s are not extrapolated. The counters survive restarts.
- **Error code as a repair issue:** when the device reports an error code,
  Home Assistant shows it under *Settings → Repairs* with the plain-text
  description, and the integration fires the event
  `marstek_jupiter_error`. The issue disappears when the code returns
  to 0.
- **Release workflow:** a release is created in one step
  (*Actions → Release*); it checks the version in `manifest.json` and
  takes the release notes from this file.
- **English README** as the main page (shown by HACS), German in
  `README.de.md`. Both reorganised for the HACS view on a phone.

### Removed

- The entities *Diagnostic 0x0012*, *Diagnostic 0x0023* and
  *Status 0x1000–0x1003, 0x1009, 0x100A*. The registers are still read
  and can be inspected with `read_register` or `register_dump`. Their
  old registry entries are removed automatically on the first start.

### Upgrade notes

- Restart Home Assistant after updating.
- To keep the history of existing Riemann helpers in the Energy
  dashboard, give the new counters the helpers' entity IDs (delete the
  helper first, then rename the new entity).

---

### Deutsch

#### Neu

- **Energiezähler fürs Energie-Dashboard:** *PV Energie*, *Batterie
  geladen* und *Batterie entladen* (kWh), von der Integration selbst aus
  den 10-s-Leistungswerten aufsummiert – Riemann-Helfer sind nicht mehr
  nötig. Gezählt wird nur, was frisch gelesen wurde; Ausfälle über 60 s
  werden nicht hochgerechnet. Der Stand überlebt Neustarts.
- **Fehlercode als Reparatur-Meldung:** Meldet das Gerät einen
  Fehlercode, erscheint er mit Klartext unter *Einstellungen →
  Reparaturen*, zusätzlich feuert das Ereignis `marstek_jupiter_error`.
  Steht der Code wieder auf 0, verschwindet die Meldung.
- **Release-Workflow:** Ein Release ist ein Schritt (*Actions → Release*)
  und prüft die Version in `manifest.json`.
- **README auf Englisch** als Hauptseite, Deutsch in `README.de.md`.

#### Entfernt

- Die Entitäten *Diagnose 0x0012*, *Diagnose 0x0023* und *Status
  0x1000–0x1003, 0x1009, 0x100A*. Die alten Einträge räumt die
  Integration beim ersten Start selbst weg.

## 1.0.1

- **Fix:** entities update again. In 1.0.0 every entity only showed the
  value from when the integration started and then stayed frozen.
- **Fehlerbehebung:** Entitäten aktualisieren sich wieder. In 1.0.0
  blieben alle Werte nach dem Start stehen.

## 1.0.0

- First release: local Modbus TCP integration for the Marstek Jupiter C+
  via Elfin EW11/EE11, block reads, plausibility filter, adoption of
  existing YAML entity IDs, services `register_dump` and `read_register`.
