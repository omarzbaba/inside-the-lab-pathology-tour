# Adding real 3D models (or photos) of the lab

The tour can drop **real 3D models** into each room so it looks like a true lab instead of
stylized shapes. Here's exactly what to send and how it gets wired in.

## Option A — real 3D models (best)

Send `.glb` (preferred) or `.gltf` files — one per instrument or piece of furniture, e.g.
`microscope.glb`, `analyzer.glb`, `centrifuge.glb`, `lab-bench.glb`, `biosafety-cabinet.glb`,
`blood-fridge.glb`, `sequencer.glb`.

Good sources (free / licensed): Sketchfab (filter to **Downloadable**), Poly Haven, Quaternius,
or any models your team already owns. Keep each file roughly **under ~5 MB** so it loads fast on
phones.

**Drop them in:** `assets/models/` and list each one in `assets/models/manifest.json`:

```json
[
  { "file": "microscope.glb", "roomId": "surgpath-signout", "scale": 1, "y": 0, "ry": 0 },
  { "file": "analyzer.glb",   "roomId": "core_lab",        "scale": 1.4, "ry": 90 },
  { "file": "biosafety.glb",  "roomId": "micro1",          "scale": 1 }
]
```

Fields: `file` (in assets/models/), `roomId` (which room — see list below), `scale`,
`ry` (Y rotation in degrees), and optional `y`, `dx`, `dz` nudges. **Just send the files — I'll
write the manifest and tune the scale/position/rotation so each model sits right in its room.**

**Room IDs** (the 10 sections): `accession` (Lab Support Services), `lab_cs` (Customer Service),
`gross` (Surgical Pathology), `cytopath` (Cytology), `micro1` (Micro & Serology), `molec1`
(Molecular), `core_lab` (Core Lab), `bb` (Blood Bank), `quality` (Quality), `chair` (Informatics).

## Option B — photos of your actual lab

Send clear, well‑lit photos of each section's key equipment and benches — straight‑on and a 3/4
angle help most. **No patients, no staff faces, no anything identifiable** (this site is public).
I'll either model the equipment from them in Blender (already installed) and export `.glb`, or use
the photos as rich in‑room image panels.

## How to get files to me

OneDrive cloud‑only files time out when I read them, so either:
- right‑click the files → **"Always keep on this device"**, then put them in
  `HFH Pathology Student Tour/assets/models/`, or
- share them any way that lands them in that folder.

Once they're there, tell me and I'll place them, tune them, and redeploy.
