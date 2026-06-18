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
FEEDBACK_EMAIL = "omar.z.baba@gmail.com"   # responses are emailed here via FormSubmit

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

# CRITICAL for mobile: the original has no viewport meta, so phones render it at
# ~980px (desktop) and zoom out. Add it so device-width + the media query apply.
if 'name="viewport"' not in html:
    html = html.replace('<meta charset="UTF-8" />',
        '<meta charset="UTF-8" />\n<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover" />', 1)

# inject disclaimer + mobile layout + an on-site feedback form (FormSubmit-backed)
def opts(name, values):
    cells = "".join(
        '<label><input type="radio" name="%s" value="%s"><span>%s</span></label>' % (name, v, v)
        for v in values)
    return '<div class="hs-opts">%s</div>' % cells

inject = """
<style>
#hs-credit{position:fixed;left:50%;transform:translateX(-50%);bottom:8px;z-index:99990;font:11px/1.4 system-ui,-apple-system,sans-serif;color:rgba(255,255,255,.4);max-width:60ch;text-align:center;pointer-events:none}
#hs-fb{position:fixed;right:14px;bottom:12px;z-index:99991;border:0;cursor:pointer;display:inline-flex;align-items:center;gap:6px;font:600 13px system-ui,sans-serif;background:#2f6fed;color:#fff;padding:10px 16px;border-radius:999px;box-shadow:0 6px 18px rgba(0,0,0,.4);transition:transform .15s ease}
#hs-fb:hover{transform:translateY(-2px)}
#hs-modal{position:fixed;inset:0;z-index:100000;background:rgba(5,10,25,.72);backdrop-filter:blur(4px);display:flex;align-items:center;justify-content:center;padding:18px}
#hs-modal[hidden]{display:none}
.hs-card{background:#fff;color:#0f172a;width:min(560px,100%);max-height:90vh;overflow:auto;border-radius:18px;padding:24px 22px;box-shadow:0 30px 80px rgba(0,0,0,.5);font-family:system-ui,-apple-system,sans-serif}
.hs-card h2{margin:0 0 4px;font-size:22px;font-weight:700}
.hs-card .sub{margin:0 0 16px;color:#475569;font-size:14px}
.hs-field{margin-bottom:14px}
.hs-field .q{display:block;font-weight:600;font-size:14px;margin-bottom:6px}
.hs-field input[type=text],.hs-field textarea{width:100%;border:1px solid #cbd5e1;border-radius:10px;padding:10px 12px;font:inherit;font-size:14px;box-sizing:border-box}
.hs-field textarea{min-height:70px;resize:vertical}
.hs-opts{display:flex;flex-wrap:wrap;gap:6px}
.hs-opts label{font-size:13px;border:1px solid #cbd5e1;border-radius:999px;padding:6px 12px;cursor:pointer;user-select:none}
.hs-opts input{position:absolute;opacity:0;width:0;height:0}
.hs-opts label:has(input:checked){background:#2f6fed;color:#fff;border-color:#2f6fed}
.hs-opts input:focus-visible + span{outline:2px solid #2f6fed;outline-offset:2px;border-radius:4px}
.hs-actions{display:flex;gap:12px;align-items:center;margin-top:18px;flex-wrap:wrap}
.hs-submit{background:#2f6fed;color:#fff;border:0;border-radius:999px;padding:11px 22px;font:600 14px system-ui;cursor:pointer}
.hs-cancel{background:none;border:0;color:#475569;cursor:pointer;font:14px system-ui}
.hs-status{font-size:13px;color:#475569}
.hs-thanks{text-align:center;padding:18px 6px}
.hs-thanks h2{font-size:22px;margin-bottom:8px}
.hs-thanks p{color:#475569;font-size:15px;margin-bottom:16px}
@media(max-width:768px){
  #hs-credit{display:none}
  #hs-fb{bottom:10px;right:10px;padding:9px 14px;font-size:12px}
  body{flex-direction:column!important}
  #sidebar{width:100%!important;height:40vh!important;max-height:40vh!important;border-right:none!important;border-bottom:1px solid rgba(255,255,255,.14)!important}
  .sidebar-header{padding:12px 16px 8px!important}
  .sidebar-title{font-size:21px!important}
  .sidebar-subtitle{display:none!important}
  .room-list{padding:6px 0 10px!important}
  #canvas-host{flex:1 1 auto!important;min-height:58vh!important}
  #tour-panel{width:100%!important;height:100%!important;max-height:100%!important;overflow-y:auto!important}
  .hs-card{max-height:94vh}
}
</style>
<div id="hs-credit">Unofficial educational orientation for high‑school students · facts from public Henry Ford Health information · not an official Henry Ford Health publication.</div>
<button id="hs-fb" type="button">\U0001F4AC Feedback</button>
<div id="hs-modal" hidden role="dialog" aria-modal="true" aria-label="Tour feedback">
  <div class="hs-card">
    <form id="hs-form" novalidate>
      <h2>Tell us what you think</h2>
      <p class="sub">A few quick questions — it helps us make this better. Thanks!</p>
      <input type="text" name="_honey" tabindex="-1" autocomplete="off" style="display:none">
      <input type="hidden" name="_subject" value="New Lab Tour feedback \U0001F389">
      <input type="hidden" name="_template" value="table">
      <input type="hidden" name="_captcha" value="false">
      <div class="hs-field"><span class="q">Your name (optional)</span><input type="text" name="Name" autocomplete="off"></div>
      <div class="hs-field"><span class="q">How much did you enjoy the tour?</span>__ENJOY__</div>
      <div class="hs-field"><span class="q">Which station was most interesting?</span><input type="text" name="Most interesting station" autocomplete="off"></div>
      <div class="hs-field"><span class="q">How easy was it to understand?</span>__CLARITY__</div>
      <div class="hs-field"><span class="q">One thing you learned today</span><textarea name="Learned"></textarea></div>
      <div class="hs-field"><span class="q">Any questions or comments for the team?</span><textarea name="Comments"></textarea></div>
      <div class="hs-field"><span class="q">Could you see yourself in science or medicine?</span>__CAREER__</div>
      <div class="hs-actions"><button type="submit" class="hs-submit">Send feedback</button><button type="button" class="hs-cancel">Cancel</button><span class="hs-status"></span></div>
    </form>
    <div class="hs-thanks" hidden><h2>Thank you! \U0001F389</h2><p>Your feedback was sent to the workshop team.</p><button type="button" class="hs-cancel hs-submit">Close</button></div>
  </div>
</div>
<script>
(function(){
  var btn=document.getElementById('hs-fb'),modal=document.getElementById('hs-modal');
  if(!btn||!modal)return;
  var panel=document.getElementById('tour-panel');
  function sync(){btn.style.display=(panel&&panel.classList.contains('show'))?'none':'inline-flex';}
  if(panel&&window.MutationObserver){new MutationObserver(sync).observe(panel,{attributes:true,attributeFilter:['class']});}
  sync();
  function close(){modal.hidden=true;}
  btn.addEventListener('click',function(){modal.hidden=false;});
  modal.addEventListener('click',function(e){if(e.target===modal)close();});
  Array.prototype.forEach.call(modal.querySelectorAll('.hs-cancel'),function(b){b.addEventListener('click',close);});
  document.addEventListener('keydown',function(e){if(e.key==='Escape'&&!modal.hidden)close();});
  var form=document.getElementById('hs-form'),status=form.querySelector('.hs-status');
  form.addEventListener('submit',function(e){
    e.preventDefault();status.textContent='Sending…';
    var data={};new FormData(form).forEach(function(v,k){if(k!=='_honey')data[k]=v;});
    fetch('https://formsubmit.co/ajax/__EMAIL__',{method:'POST',headers:{'Content-Type':'application/json','Accept':'application/json'},body:JSON.stringify(data)})
      .then(function(r){return r.json();})
      .then(function(){form.style.display='none';modal.querySelector('.hs-thanks').hidden=false;})
      .catch(function(){status.textContent='Could not send — please check your connection and try again.';});
  });
})();
</script>
"""
inject = (inject
          .replace("__ENJOY__", opts("Enjoyment", ["Loved it", "Liked it", "It was OK", "Not really"]))
          .replace("__CLARITY__", opts("Clarity", ["Very easy", "Easy", "A bit hard", "Hard"]))
          .replace("__CAREER__", opts("Career interest", ["Yes", "Maybe", "Not sure", "No"]))
          .replace("__EMAIL__", FEEDBACK_EMAIL))
html = html.replace("</body>", inject + "</body>")

open(OUT, "w", encoding="utf-8").write(html)
n = sum(1 for _, sid in ids if sid in HS)
print("wrote %s  (%d/%d stops translated)" % (OUT, n, len(ids)))
