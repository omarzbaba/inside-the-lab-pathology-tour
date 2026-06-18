#!/usr/bin/env python3
"""
Translate the recovered interactive 3D lab map (medical-student level) into a
high-school-friendly version. ONLY swaps text content (subtitle / overview /
tests / methods) and a couple of UI labels — all 3D geometry and interactivity
is left untouched.

  python3 tools/translate_to_hs.py
  -> writes tour.html
"""
import re, os

SRC = "reference/original-3d-floorplan.html"
OUT = "index.html"
SURVEY_URL = ""   # paste the Google Form share/embed URL here to switch the Feedback button on

# High-school content keyed by stop id. Keep it accurate but simple + friendly.
HS = {
 "accessioning": {
  "subtitle": "Where every sample checks in",
  "overview": "This is the front door for every tissue sample. When a doctor removes tissue during surgery, it comes here first. Each sample is scanned and given its own barcode, like a boarding pass, so it can never be mixed up with anyone else.",
  "tests": ["Logging in every sample","Giving each one a barcode ID","Double-checking the patient","Sending it next door to grossing"],
  "methods": ["Barcode scanners","A computer tracking system","Tubes that shoot samples in","Careful chain-of-custody records"]},
 "grossing": {
  "subtitle": "Looking at tissue with the naked eye",
  "overview": "Right next door, scientists examine the tissue without a microscope. They measure it, describe it, take photos, and cut tiny pieces to turn into slides. Their notes become part of the diagnosis.",
  "tests": ["Examining tumors removed in surgery","Checking the edges to see if a cancer was fully removed","Sampling lymph nodes","Photographing each specimen"],
  "methods": ["Stainless-steel cutting stations","Special inks to mark the edges","Tiny cassettes to hold the pieces","Voice dictation into the computer"]},
 "molecular": {
  "subtitle": "Reading the DNA",
  "overview": "Here, DNA and RNA do the talking. Machines read the genetic code inside cells to find the exact change that is driving a disease, which helps doctors pick a medicine aimed right at it.",
  "tests": ["Finding the gene changes behind a cancer","Matching patients to targeted medicines","Checking for inherited risks","Reading a tumor's genetic fingerprint"],
  "methods": ["DNA sequencing machines","PCR machines that copy DNA","FISH (glowing DNA markers)","Powerful analysis computers"]},
 "hist-process": {
  "subtitle": "Turning tissue into wax blocks",
  "overview": "Tissue is too soft and wet to slice thin, so overnight machines soak it in wax. By morning, each piece is a solid wax block, ready to be sliced paper-thin.",
  "tests": ["Preparing almost every surgery sample","Fast runs for tiny biopsies"],
  "methods": ["Automated tissue processors","Wax (paraffin) embedding","Overnight processing"]},
 "hist-microtomy": {
  "subtitle": "Wax blocks into glass slides",
  "overview": "A machine called a microtome shaves the wax block into ribbons thinner than a hair. The slices float on warm water and are lifted onto glass slides.",
  "tests": ["Making the standard pink-and-purple slides","Extra-deep slices to find tiny clues","Re-cuts for special tests"],
  "methods": ["A microtome (super-precise slicer)","Warm water baths","Specially coated glass slides"]},
 "hist-collation": {
  "subtitle": "Coloring and finishing the slides",
  "overview": "The last step in the slide lab. Slides are dipped in dyes so the cells show up, sealed with a thin glass cover, matched to their paperwork, and sent to the pathologist.",
  "tests": ["The classic pink-and-purple (H&E) stain","Special stains that reveal germs or fibers","Matching every slide to the right case"],
  "methods": ["Automated staining machines","Coverslipping machines","Careful sorting by case"]},
 "scanning": {
  "subtitle": "Turning glass slides into digital images",
  "overview": "Scanners photograph entire slides at very high zoom, making huge digital images. Pathologists can then read them on a computer, share them with experts anywhere, and even get help from AI.",
  "tests": ["Getting expert second opinions from far away","Sharing cases between hospitals","AI helping to count cells","Building teaching libraries"],
  "methods": ["Whole-slide scanners","Giant digital image files","Telepathology (pathology over the internet)"]},
 "ihc": {
  "subtitle": "Using antibodies to reveal clues",
  "overview": "Some cells look alike under a regular stain. Antibody stains attach to one specific protein and add color only where it is, helping identify exactly what kind of cell or cancer it is.",
  "tests": ["Figuring out the exact type of a cancer","Finding where a cancer started","Guiding which targeted medicine to use","Telling apart kinds of lymphoma"],
  "methods": ["Antibodies that find one protein","Automated staining robots","Color tags you can see under the microscope"]},
 "micro": {
  "subtitle": "Hunting germs",
  "overview": "On the way to the core lab we pass Microbiology, where the team grows and identifies the bacteria, viruses, and fungi that make people sick, and tests which medicine will beat them.",
  "tests": ["Blood and urine cultures","Strep and stomach-bug tests","Tests for viruses like HIV and hepatitis","Respiratory virus panels"],
  "methods": ["Biosafety cabinets (safe work hoods)","Incubators that grow microbes","A machine that IDs germs (MALDI-TOF)","Automated culture systems"]},
 "core-overview": {
  "subtitle": "The 24/7 high-speed lab",
  "overview": "This is the biggest room in the department, and it never closes. A conveyor belt, like an airport baggage system, carries thousands of blood tubes to machines that run most of the hospital's everyday tests.",
  "tests": ["Everyday blood chemistry","Blood cell counts","Heart-attack markers","Thyroid, pregnancy, and more"],
  "methods": ["A robotic conveyor track","Rows of automated analyzers","Open day and night"]},
 "core-inlet": {
  "subtitle": "Where blood tubes arrive and get prepped",
  "overview": "Tubes drop in here and get scanned, spun very fast to separate the liquid from the cells, uncapped, and split into smaller portions so several machines can test them at once.",
  "tests": ["Checking in and scanning each tube","Spinning to separate the blood","Removing caps for the machines","Splitting samples for many tests"],
  "methods": ["High-speed centrifuges (spinners)","An automatic decapper","A robot that splits samples"]},
 "core-heme-coag": {
  "subtitle": "Blood counts and clotting tests",
  "overview": "Machines here count your red cells, white cells, and platelets, and measure how fast your blood clots, which is important for people on blood thinners.",
  "tests": ["Complete blood count (CBC)","Clotting-time tests","Young red blood cell counts","Flagging unusual cells for a human to check"],
  "methods": ["Cell-counting analyzers","Clot-detection machines","Expert manual review"]},
 "core-imm-chem": {
  "subtitle": "Hormones, heart markers, and chemistry",
  "overview": "These analyzers measure hormones, heart-attack markers, tumor markers, and the basic chemicals in your blood like sodium, sugar, and cholesterol.",
  "tests": ["Thyroid and other hormones","Heart-attack markers","Blood sugar, salts, and cholesterol","Liver tests"],
  "methods": ["Immunoassay analyzers","Chemistry analyzers","Light-based measurements"]},
 "core-outlet": {
  "subtitle": "Capping and storing samples",
  "overview": "After testing, tubes get re-capped to stay clean and are stored cold in case a doctor needs an extra test later, like a giant, well-organized refrigerator.",
  "tests": ["Adding extra tests later","Re-running important results","Finding samples to send out","Quality checks"],
  "methods": ["An automatic recapper","Refrigerated storage","Barcode retrieval"]},
 "surgpath": {
  "subtitle": "Where the diagnosis is made",
  "overview": "This is the answer at the end of the journey. In their offices, pathologists study the glass slides under a microscope (or on a big screen) and write the report that tells your doctor exactly what is going on.",
  "tests": ["Reading biopsies","Working up surgery samples","Sizing up (staging) cancers","Getting expert second opinions"],
  "methods": ["Microscopes","Digital pathology screens","16 individual sign-out offices"]},
 "transfusion": {
  "subtitle": "Keeping blood transfusions safe",
  "overview": "The blood bank types and matches donated blood so it is safe to give to patients, and double-checks every unit before a transfusion.",
  "tests": ["Finding your blood type","Checking for antibodies","Matching donor blood to the patient","Working up transfusion reactions"],
  "methods": ["Blood-typing tests","Crossmatching","Refrigerated blood storage"]},
}

def esc_sq(s):  # for single-quoted JS strings
    return s.replace("\\", "\\\\").replace("'", "\\'")
def esc_dq(s):  # for double-quoted JS strings
    return s.replace("\\", "\\\\").replace('"', '\\"')

html = open(SRC, encoding="utf-8").read()

# locate TOUR_STOPS array
s = html.index("const TOUR_STOPS")
arr0 = html.index("[", s)
arr1 = html.index("\n];", arr0)
head, body, tail = html[:arr0+1], html[arr0+1:arr1], html[arr1:]

# split body into per-stop blocks by id position
ids = [(m.start(), m.group(1)) for m in re.finditer(r"id:'([\w-]+)'", body)]
pieces = []
pieces.append(body[:ids[0][0]])
for k, (pos, sid) in enumerate(ids):
    end = ids[k+1][0] if k+1 < len(ids) else len(body)
    block = body[pos:end]
    hs = HS.get(sid)
    if hs:
        block = re.sub(r"subtitle:'(?:[^'\\]|\\.)*'", "subtitle:'%s'" % esc_sq(hs["subtitle"]), block, count=1)
        block = re.sub(r'overview:"(?:[^"\\]|\\.)*"', 'overview:"%s"' % esc_dq(hs["overview"]), block, count=1, flags=re.S)
        tests = ",".join("'%s'" % esc_sq(t) for t in hs["tests"])
        methods = ",".join("'%s'" % esc_sq(t) for t in hs["methods"])
        block = re.sub(r"tests:\[(?:[^\[\]])*\]", "tests:[%s]" % tests, block, count=1, flags=re.S)
        block = re.sub(r"methods:\[(?:[^\[\]])*\]", "methods:[%s]" % methods, block, count=1, flags=re.S)
    pieces.append(block)
html = head + "".join(pieces) + tail

# relabel panel headers + intro for a younger audience
html = html.replace(">Common tests<", ">What they do here<")
html = html.replace(">Methods &amp; instruments<", ">Tools they use<")
html = html.replace(
  "A guided sequence through the department, following the journey of a specimen from intake to final diagnosis.",
  "Follow a real sample on its journey through the lab — tap a stop or use the arrows. Each room shows what happens there in plain language.")
# friendly page title
html = html.replace("<title>Henry Ford Pathology · 3D Floor Plan</title>",
                    "<title>Inside the Lab · 3D Tour for Students</title>")

# inject a small disclaimer + a feedback button (independent of the map's layout)
fb_attr = ' target="_blank" rel="noopener"' if SURVEY_URL else ''
fb_href = SURVEY_URL or '#'
inject = """
<style>
#hs-credit{position:fixed;left:50%;transform:translateX(-50%);bottom:8px;z-index:99999;font:11px/1.4 system-ui,-apple-system,sans-serif;color:rgba(255,255,255,.4);max-width:60ch;text-align:center;pointer-events:none}
#hs-fb{position:fixed;right:14px;bottom:12px;z-index:99999;font:600 13px system-ui,sans-serif;background:#2f6fed;color:#fff;padding:9px 15px;border-radius:999px;text-decoration:none;box-shadow:0 6px 18px rgba(0,0,0,.4);transition:transform .15s ease}
#hs-fb:hover{transform:translateY(-2px)}
@media(max-width:720px){#hs-credit{display:none}#hs-fb{bottom:10px;right:10px;padding:8px 13px}}
</style>
<div id="hs-credit">Unofficial educational orientation for high‑school students · facts from public Henry Ford Health information · not an official Henry Ford Health publication.</div>
<a id="hs-fb" href="__HREF__"__ATTR__>\U0001F4AC Feedback</a>
"""
inject = inject.replace("__HREF__", fb_href).replace("__ATTR__", fb_attr)
html = html.replace("</body>", inject + "</body>")

open(OUT, "w", encoding="utf-8").write(html)
n = sum(1 for _, sid in ids if sid in HS)
print("wrote %s  (%d/%d stops translated)" % (OUT, n, len(ids)))
