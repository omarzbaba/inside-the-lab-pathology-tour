#!/usr/bin/env bash
# Batch-generate photoreal station scenes for the lab tour.
#
# Setup (one time):
#   echo 'OPENROUTER_API_KEY=sk-or-...' > .env          # in the project root
# Run:
#   bash scripts/generate-stations.sh                    # all stations
#   bash scripts/generate-stations.sh histology micro    # just these
#
# Output: assets/stations/<id>.png  (the site picks these up automatically)

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
GEN="$HOME/.claude/skills/generate-image/scripts/generate_image.py"
OUT="$ROOT/assets/stations"
MODEL="${IMAGE_MODEL:-black-forest-labs/flux.2-pro}"   # photoreal; override with env if desired
mkdir -p "$OUT"

# Load API key from .env if present
if [ -f "$ROOT/.env" ]; then set -a; . "$ROOT/.env"; set +a; fi
if [ -z "${OPENROUTER_API_KEY:-}" ]; then
  echo "ERROR: OPENROUTER_API_KEY not set. Put it in $ROOT/.env (see docs/IMAGES.md)." >&2
  exit 1
fi

STYLE="ultra photorealistic, professional medical photography, bright clean clinical lighting, modern hospital laboratory, cinematic wide angle, shallow depth of field, NO people, no faces, no text overlays, 16:11"

declare -A PROMPTS=(
  [accessioning]="Hospital laboratory specimen receiving and accessioning area: white benches, barcode label printers, computer workstations, racks of labeled specimen tubes and containers. $STYLE"
  [grossing]="Surgical pathology grossing station: stainless-steel dissection bench with downdraft ventilation, cutting board, measuring rulers, specimen cassettes and containers. $STYLE"
  [histology]="Histology laboratory: automated tissue processor and embedding center, a microtome with paraffin wax blocks, racks of pink and purple H&E stained glass slides. $STYLE"
  [frozen]="Frozen section room: a cryostat machine, glass slides, a small microscope, cold sterile stainless-steel surfaces, intraoperative rapid-diagnosis setup. $STYLE"
  [signout]="Pathologist sign-out office: a binocular microscope on a desk beside a large high-resolution digital pathology monitor displaying magnified tissue, trays of glass slides, warm focused light. $STYLE"
  [ihc]="Immunohistochemistry laboratory: automated immunostainer instruments, reagent bottles, slides with brown and blue antibody stains, robotic staining platform. $STYLE"
  [cytology]="Cytology laboratory: microscope with cytology slides, liquid-based Pap-test sample vials, a slide preparation station, tidy modern bench. $STYLE"
  [neuropath]="Neuropathology laboratory: microscope with brain tissue slides, an anatomical brain model on the bench, deep-blue accent lighting, scientific atmosphere. $STYLE"
  [molecular]="Molecular pathology and genomics laboratory: next-generation DNA sequencing machines, PCR thermocyclers, robotic liquid handlers, glowing screens with DNA sequence data, high-tech precision diagnostics. $STYLE"
  [micro]="Clinical microbiology laboratory: petri dishes with bacterial cultures on agar, incubators, a biosafety cabinet, automated identification instruments. $STYLE"
  [core_clinical]="High-throughput clinical chemistry and hematology core lab: a large automated analyzer track system conveying blood sample tubes, robotic automation line, blood-bank refrigerators in the background. $STYLE"
  [autopsy]="Clean, dignified, non-graphic hospital autopsy suite: an empty stainless-steel examination table and neatly arranged instruments in a bright sterile respectful room. No bodies. $STYLE"
)

IDS=("$@")
if [ ${#IDS[@]} -eq 0 ]; then IDS=("${!PROMPTS[@]}"); fi

for id in "${IDS[@]}"; do
  p="${PROMPTS[$id]:-}"
  if [ -z "$p" ]; then echo "skip: unknown station '$id'"; continue; fi
  echo "→ generating $id ..."
  python3 "$GEN" "$p" --model "$MODEL" --output "$OUT/$id.png"
done

echo "Done. Images in $OUT"
