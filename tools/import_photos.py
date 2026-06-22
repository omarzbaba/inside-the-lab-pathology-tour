#!/usr/bin/env python3
"""Import lab photos into assets/photos/<section>/, optimize them, and write a
manifest the tour reads. Staff confirmed consent (2026-06-22) for the face
photos to appear on the public site; the whiteboard phone-number shot
(Accessioning 5) is still excluded as PII."""
import json, os, subprocess

SRC = os.path.expanduser("~/Downloads/RE_ JVHL Summer Immersion Program-2")
OUT = "assets/photos"

# section id -> [(source filename, caption)]  (only screened, face-free shots)
SAFE = {
  "lss": [
    ("LSS 1.jpg", "Cooler receipt - samples arrive cold"),
    ("LSS 2.jpg", "Integrated receipt station"),
    ("LSS 3.jpg", "Cooler receipt area"),
    ("LSS 4.jpg", "Specimen triage / defects desk"),
    ("Accessioning 1.jpg", "Accessioning workstation"),
    ("Accessioning 2.jpg", "Accessioning bench"),
    ("Accessioning 3.jpg", "Sample check-in"),
    ("Accessioning 4.jpg", "Accessioning area"),
  ],
  "core": [
    ("Core 1.jpg", "Chemistry & immunoassay analyzers"),
    ("Core 4.jpg", "DxU 850m hematology / urinalysis line"),
    ("Core 5.jpg", "Routine chemistry analyzers"),
    ("Core 6.jpg", "Chemistry analyzer"),
    ("Core 2.jpg", "Manual fluids bench"),
    ("Core 3.jpg", "Core lab analyzers"),
  ],
  "molec": [
    ("molecular 4.jpg", "Illumina sequencers"),
    ("molecular 5.jpg", "Genetic analyzer"),
    ("molecular 6.jpg", "Molecular workbench"),
    ("molecular 7.jpg", "Illumina MiSeqDx sequencers"),
    ("molecular 1.jpg", "Molecular DNA analysis bench"),
    ("molecular 2.jpg", "Biosafety cabinet"),
    ("molecular 3.jpg", "Molecular prep bench"),
  ],
  "cyto": [
    ("Cytology 1.jpg", "Specimen prep sink"),
    ("Cytology 2.jpg", "Cytology prep bench & hood"),
    ("Cytology 3.jpg", "Cytology processing bench"),
    ("Cytology 4.jpg", "ThinPrep processing station"),
  ],
  "bloodbank": [
    ("Blood Bank 1.jpg", "Immucor NEO Iris blood-typing analyzer"),
    ("Blood Bank 2.jpg", "Immucor NEO Iris (close-up)"),
    ("Blood Bank 4.jpg", "Helmer blood & plasma storage"),
    ("Blood Bank 3.jpg", "Helmer refrigerated storage"),
  ],
  "surgpath": [
    ("Grossing station.jpg", "Grossing station"),
    ("tissue processor.jpg", "Tissue processors"),
    ("microtome.jpg", "Microtome"),
    ("Processors.jpg", "Histology processors"),
    ("wax cleaning.jpg", "Wax bath / glassware cleaner"),
    ("stainer cover slip.jpg", "Automated stainer & cover-slipper"),
    ("digital scanner.jpg", "Leica Aperio GT 450 slide scanner"),
    ("stained slides.jpg", "Freshly stained slides"),
    ("filed slides file room.jpg", "Slide archive (file room)"),
    ("filed slides file room 2.jpg", "Slide archive (file room)"),
  ],
}

manifest = {}
total = 0
for section, items in SAFE.items():
    d = os.path.join(OUT, section)
    os.makedirs(d, exist_ok=True)
    arr = []
    for i, (src, caption) in enumerate(items, 1):
        sp = os.path.join(SRC, src)
        if not os.path.exists(sp):
            print("MISSING:", sp); continue
        name = "%02d.jpg" % i
        dp = os.path.join(d, name)
        # cap longest side at 1280 and recompress to keep the page light
        subprocess.run(["sips", "-Z", "1280", "-s", "format", "jpeg",
                        "-s", "formatOptions", "68", sp, "--out", dp],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        arr.append({"file": "%s/%s" % (section, name), "caption": caption})
        total += 1
    manifest[section] = arr

with open(os.path.join(OUT, "manifest.json"), "w") as f:
    json.dump(manifest, f, indent=1)
print("imported %d photos across %d sections" % (total, len(manifest)))
