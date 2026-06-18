# Inside the Lab — A Student's Tour of Pathology

An interactive, mobile‑friendly walkthrough that introduces high‑school students to a
hospital **Pathology & Laboratory Medicine** department. Students follow a real sample on
its journey through the lab and learn — in plain language — what happens at every station.

> **Unofficial educational orientation.** Built for visiting high‑school students using
> public information about Henry Ford Health's Pathology & Laboratory Medicine department.
> This is **not** an official Henry Ford Health publication.

## ✨ Features

- **Guided walkthrough** — auto‑walk or step through 12 lab stations at your own pace.
- **Interactive floor‑plan map** — tap any room to jump straight to it.
- **High‑school‑level content** — every station has a hook, a plain‑English explanation,
  a real‑world analogy, key points, the tests done there, and a "Did you know?" fact.
- **Photoreal station scenes** — drop rendered images into `assets/stations/` (see below);
  polished SVG scenes show automatically until then.
- **Feedback survey** — embed a Google Form so students can share what they think.
- **Fast, dependency‑free** — plain HTML/CSS/JS. Works great on phones and computers.
- **Accessible** — keyboard navigation, focus states, and `prefers-reduced-motion` support.

## 🗂 Project structure

```
.
├── index.html            # page shell
├── css/styles.css        # design system + layout
├── js/app.js             # walkthrough engine (renders everything from data)
├── data/stations.json    # ALL content lives here — edit this to change the tour
├── assets/
│   ├── stations/         # photoreal renders: <station-id>.jpg|png|webp
│   ├── icons/guide.svg   # the neutral lab-coat guide figure
│   └── map/
├── scripts/generate-stations.sh   # batch-generate photoreal station images
├── docs/
│   ├── IMAGES.md         # how to generate the photoreal scenes
│   └── SURVEY-SETUP.md   # how to wire up the Google Form (2 minutes)
└── .github/workflows/pages.yml    # auto-deploy to GitHub Pages
```

## ✏️ Editing the content

All text lives in [`data/stations.json`](data/stations.json). Change a station's wording,
add a fact, or reorder stops there — no code changes needed.

## 🖼 Adding the photoreal images

See [`docs/IMAGES.md`](docs/IMAGES.md). In short: set an OpenRouter API key, run
`scripts/generate-stations.sh`, and the renders drop into `assets/stations/`.

## 📝 Adding the feedback survey

See [`docs/SURVEY-SETUP.md`](docs/SURVEY-SETUP.md). Create a Google Form, paste its embed
URL into the `survey.embedUrl` field in `data/stations.json`, and it appears on the page.

## 🚀 Running locally

```bash
python3 -m http.server 8000   # then open http://localhost:8000
```

(A plain double‑click won't work — browsers block the data file over `file://`.)

## 📄 License

Code is released under the [MIT License](LICENSE). Henry Ford Health names and marks belong
to their respective owners and are used here only to describe the department for education.
