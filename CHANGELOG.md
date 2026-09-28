# Changelog

## 1.2.0b1

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

- **MQTT error fallback option:** the "MQTT error sensor as second source" field has been
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
  `name`- und `description`-Felder in `services.yaml`. Ein optionaler `entry_id`-Parameter
  wählt die Ziel-Instanz, wenn mehrere Jupiter-Integrationen eingerichtet sind; ohne ihn
  funktioniert der Dienst wie bisher für Einzel-Instanz-Setups.
- **CI-Workflow:** GitHub Actions führt die volle Testsuite auf Python 3.11 und 3.12
  parallel bei jedem Push und Pull-Request aus (pyflakes + pytest).
- **Dependabot:** wöchentliche Prüfung auf GitHub-Actions-Versions-Updates.
- **Testabdeckung:** 70 Tests in 10 Dateien, inkl. Diagnostics, Service-Helpers und
  TCP-Reconnect-Szenarien.

#### Entfernt

- **MQTT-Fehlercode-Fallback:** das Feld „MQTT-Fehlersensor als zweite Quelle" wurde aus
  den Integrationsoptionen entfernt. Fehlercodes werden ausschließlich per Modbus gelesen.

---

## 1.1.0

- Energiezähler: PV Energie, Batterie geladen/entladen
- Status- und Diagnose-Entitäten entfernt
- TCP-Reconnect-Logik verbessert

## 1.0.1

- Bugfix: Setup-Fehler (NameError entry)

## 1.0.0

- Erste stabile Version
