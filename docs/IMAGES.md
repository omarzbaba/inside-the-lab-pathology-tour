# Generating the photoreal station scenes

The tour shows a polished SVG scene for every station out of the box. To replace those with
**photorealistic renders**, generate one image per station into `assets/stations/`.

The site automatically uses `assets/stations/<station-id>.png` (or `.jpg` / `.webp`) when it
exists, and falls back to the SVG scene when it doesn't — so you can add images one at a time.

Station IDs: `accessioning, grossing, histology, frozen, signout, ihc, cytology, neuropath,
molecular, micro, core_clinical, autopsy`.

## Option A — use the included script (recommended)

1. Get an OpenRouter API key: https://openrouter.ai/keys
2. Put it in a `.env` file in the project root (this file is git‑ignored, never committed):

   ```bash
   echo 'OPENROUTER_API_KEY=sk-or-your-key-here' > .env
   ```

3. Generate all twelve (or pass IDs to do specific ones):

   ```bash
   bash scripts/generate-stations.sh
   bash scripts/generate-stations.sh histology molecular
   ```

The script uses photoreal prompts tuned for each station, with **no people and no faces** —
appropriate for a public site. Output lands in `assets/stations/`.

> Cost: generating 12 images is a small one‑time OpenRouter charge (a few cents to ~$1
> depending on the model). The default model is `flux.2-pro`; override with
> `IMAGE_MODEL=google/gemini-3.1-flash-image-preview bash scripts/generate-stations.sh`.

## Option B — bring your own images

Drop any image named `<station-id>.jpg` (or `.png`/`.webp`) into `assets/stations/`.
Recommended size ~1280×880, landscape. Keep files reasonably small (< ~400 KB) for fast
mobile loading.

## Tips

- Keep imagery neutral and equipment‑focused; avoid recognizable people for a public repo.
- After adding images, hard‑refresh the page (the JSON is fetched with `no-cache`, images
  are normal browser cache).
