# Adding a 360° photo tour

`pano.html` plays **real 360° photographs** of each lab section (drag to look around, click
hotspots to move between rooms) — the same idea as the 3DVista tour, built on the free
open‑source **Pannellum** viewer. Until you add photos, it shows a friendly "add photos" screen.

## 1. Shoot the photos

- Use a 360 camera (Ricoh Theta, Insta360) or phone panorama. You need **equirectangular**
  images (the wide 2:1 "unwrapped sphere" format every 360 camera exports).
- One photo per section. Stand in a spot that shows the key equipment.
- **No patients, no staff faces, nothing identifiable** — this site is public.
- Keep each file reasonably sized (~2–6 MB, e.g. 4096×2048) so it loads fast on phones.

## 2. Drop them in + name them

Put the files in `assets/pano/` and add each filename to the matching scene in
`assets/pano/tour.json`:

```json
"surgpath": { "title": "Surgical Pathology", "blurb": "Diagnosing disease in tissue",
              "panorama": "surgpath.jpg", "hotSpots": [] }
```

Scenes with an empty `"panorama"` are skipped, so you can add rooms one at a time. The viewer
**auto‑links** each section to the next/previous one in the `order` list — no setup needed.

## 3. (Optional) custom hotspots

Add clickable bubbles inside `hotSpots`. `pitch`/`yaw` are degrees (up/down, left/right) — aim
them at things in your photo:

```json
"hotSpots": [
  { "type": "info",  "text": "This is the microtome", "pitch": -5, "yaw": 30 },
  { "type": "scene", "sceneId": "cyto", "text": "Walk to Cytology", "pitch": -8, "yaw": 120 }
]
```

## 4. See it / link it

Open `pano.html`. Once photos are in, tell me and I'll add a prominent **"Take the 360° photo
tour"** button on the welcome screen so students can switch between the 3D map and the real‑photo
walk‑through.

## Getting files to me

OneDrive cloud‑only files time out when I read them — right‑click → **"Always keep on this
device"** and place them in `assets/pano/`, then let me know.
