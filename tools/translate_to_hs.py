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

SRC = "src/tour-base.html"   # editable base (light-theme 3D + walkthrough); reference/ stays pristine
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
pieces.append(body[:ids[0][0]] if ids else body)
for k, (pos, sid) in enumerate(ids):
    end = ids[k+1][0] if k+1 < len(ids) else len(body)
    block = body[pos:end]
    hs = None  # stop content is now authored directly in src/tour-base.html
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
  "The sections you'll rotate through this week — tap a stop or use the arrows to see what each one does before you walk in.")
# friendly page title
html = html.replace("<title>Henry Ford Pathology · 3D Floor Plan</title>",
                    "<title>Lab Tour · Summer Immersion · Henry Ford Pathology</title>")

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
inject += """
<style>
/* ===================== LIGHT THEME OVERRIDE + Henry Ford branding ===================== */
:root{
  --navy-900:#eef3fa!important;--navy-800:#ffffff!important;--navy-700:#e8eef7!important;
  --navy-600:#d8e3f1!important;--navy-500:#c4d5ea!important;--navy-300:#5f7ba6!important;
  --cream:#13233d!important;--text:#13233d!important;--text-dim:#5a6b88!important;
  --accent:#0067a0!important;--accent-warm:#0067a0!important;--border:rgba(14,34,66,.12)!important;
}
body{background:#eef3fa!important;color:#13233d!important}
#sidebar{background:linear-gradient(180deg,#ffffff 0%,#f3f8fd 100%)!important;border-right:1px solid var(--border)!important}
.sidebar-title{color:#13233d!important}
.sidebar-subtitle{color:#5a6b88!important}
.sidebar-eyebrow{color:#0067a0!important}
.room-list,.tour-stop,.tour-stop-title{color:#13233d!important}
.tour-stop-sub{color:#64748b!important}
.tour-stop:hover{background:rgba(0,103,160,.07)!important}
.tour-stop.active{background:rgba(0,103,160,.12)!important;border-left-color:#0067a0!important}
.tour-stop-num{background:#e6eef8!important;color:#0067a0!important}
.tour-stop.active .tour-stop-num{background:#0067a0!important;color:#fff!important}
.tour-controls{border-top:1px solid var(--border)!important}
.tour-ctrl-btn{background:#f0f5fb!important;border:1px solid var(--border)!important;color:#13233d!important}
.tour-ctrl-btn:hover{background:#e3edf8!important}
#tour-panel{background:#ffffff!important;color:#13233d!important;box-shadow:-16px 0 50px rgba(20,40,80,.13)!important}
.tp-header{background:linear-gradient(135deg,#0067a0,#00497a)!important}
.tp-header,.tp-header *{color:#ffffff!important}
.tp-section-h{color:#0067a0!important;border-bottom-color:var(--border)!important}
.tp-overview,.tp-list,.tp-list li,.tp-body{color:#27364f!important}
.tp-footer{background:#f7fafd!important;border-top:1px solid var(--border)!important}
.tp-nav-btn{background:#eef4fb!important;color:#13233d!important;border:1px solid var(--border)!important}
.tp-nav-btn.primary{background:#0067a0!important;color:#fff!important;border-color:#0067a0!important}
#hud-info,#hud-info *{color:#13233d!important;text-shadow:0 1px 3px rgba(255,255,255,.7)!important}
/* animated step-cards in the info panel */
.tp-dots{display:flex;gap:7px;justify-content:center;margin:6px 0 20px}
.tp-dot{width:8px;height:8px;border-radius:50%;background:#cfd8e8;cursor:pointer;transition:all .25s ease;border:0;padding:0}
.tp-dot.on{background:#0067a0;width:22px;border-radius:5px}
.tp-card{opacity:0;transform:translateY(16px);transition:opacity .4s ease,transform .4s ease;text-align:center;padding:10px 6px 4px}
.tp-card.in{opacity:1;transform:none}
.tp-card-ico{font-size:56px;line-height:1;margin-bottom:18px}
.tp-card-text{font-size:18px;line-height:1.55;color:#27364f;max-width:36ch;margin:0 auto}
.tp-card-photo{width:100%;max-width:460px;border-radius:14px;margin:0 auto 16px;display:block;box-shadow:0 10px 28px rgba(20,40,80,.18)}
.tp-card-actions{display:flex;align-items:center;justify-content:space-between;gap:10px;margin-top:28px}
.tp-card-back{background:none;border:0;color:#5a6b88;cursor:pointer;font:600 14px system-ui}
.tp-card-btn{margin-left:auto;background:#0067a0;color:#fff;border:0;border-radius:999px;padding:11px 22px;font:600 15px system-ui;cursor:pointer;transition:transform .15s ease}
.tp-card-btn:hover{transform:translateY(-2px)}
@media(max-width:768px){.tp-card-ico{font-size:48px}.tp-card-text{font-size:17px}}
#loading{background:#eef3fa!important;color:#13233d!important}
/* a small Henry Ford lockup at the very top of the sidebar */
.hs-brandbar{display:flex;align-items:center;gap:10px;padding:14px 22px 0}
.hs-brandbar .m{width:34px;height:34px;border-radius:9px;background:linear-gradient(135deg,#0067a0,#00497a);color:#fff;display:grid;place-items:center;font:700 15px Georgia,serif;flex-shrink:0}
.hs-brandbar .t{line-height:1.12}
.hs-brandbar .t b{display:block;font:600 13px system-ui;color:#0067a0}
.hs-brandbar .t span{font:500 10.5px system-ui;color:#64748b}
/* ===================== WELCOME SCREEN ===================== */
#hs-welcome{position:fixed;inset:0;z-index:100001;background:radial-gradient(120% 120% at 80% 0%,#dbe8f7 0%,#ffffff 55%);display:flex;align-items:center;justify-content:center;padding:24px;transition:opacity .55s ease}
#hs-welcome.hide{opacity:0;pointer-events:none}
.hw-card{max-width:640px;text-align:center;font-family:system-ui,-apple-system,sans-serif;color:#13233d}
.hw-brand{display:inline-flex;align-items:center;gap:13px;margin-bottom:24px}
.hw-mark{width:56px;height:56px;border-radius:14px;background:linear-gradient(135deg,#0067a0,#00497a);color:#fff;display:grid;place-items:center;font:700 23px Georgia,serif;box-shadow:0 12px 28px rgba(0,73,122,.35)}
.hw-bt{text-align:left;line-height:1.15}
.hw-bt b{display:block;font-size:18px;color:#0067a0}
.hw-bt span{font-size:13px;color:#5a6b88}
.hw-card h1{font-family:'Cormorant Garamond',Georgia,serif;font-size:clamp(34px,6vw,54px);font-weight:600;line-height:1.04;margin:6px 0 16px}
.hw-card h1 em{color:#0067a0;font-style:italic}
.hw-card p{font-size:clamp(15px,2.3vw,18px);color:#41526e;line-height:1.55;max-width:50ch;margin:0 auto 28px}
.hw-actions{display:flex;gap:12px;justify-content:center;flex-wrap:wrap}
.hw-btn{font:600 15px system-ui;padding:14px 26px;border-radius:999px;cursor:pointer;border:1px solid transparent;transition:transform .15s ease}
.hw-btn.primary{background:#0067a0;color:#fff;box-shadow:0 12px 28px rgba(0,73,122,.34)}
.hw-btn.primary:hover{transform:translateY(-2px)}
.hw-btn.ghost{background:#fff;color:#13233d;border-color:#cdd8e8}
.hw-btn.ghost:hover{transform:translateY(-2px);border-color:#0067a0}
.hw-note{margin-top:24px;font-size:12px;color:#8493ac}
.hw-brand{flex-direction:column;gap:8px}
.hw-logo{max-width:360px;width:82%;height:auto;display:block}
.hw-dept{font:600 13px system-ui;color:#0067a0;letter-spacing:.02em}
.hs-brandbar{flex-direction:column!important;align-items:flex-start!important;gap:5px!important;padding:16px 22px 6px!important;border-bottom:1px solid var(--border)}
.hs-logo{width:215px;max-width:100%;height:auto}
.hs-dept{font:600 11px system-ui;color:#0067a0;letter-spacing:.01em}
@media(max-width:768px){.hw-card h1{font-size:32px}.hw-brand{margin-bottom:18px}.hw-logo{width:74%}}
</style>
<div id="hs-welcome">
  <div class="hw-card">
    <div class="hw-brand"><img class="hw-logo" src="assets/brand/hfh-logo.png" alt="Henry Ford Health + Michigan State University Health Sciences"><div class="hw-dept">Pathology &amp; Laboratory Medicine</div></div>
    <h1>Welcome to your <em>week in the lab</em></h1>
    <p>You're here for the Medical Laboratory Science Summer Immersion — a week shadowing the scientists who run one of the largest hospital labs in the country. This quick tour previews each section you'll rotate through, so you know what you're looking at before you walk in.</p>
    <div class="hw-actions">
      <button class="hw-btn primary" id="hw-start">▶ Start the guided walkthrough</button>
      <button class="hw-btn ghost" id="hw-explore">Explore on my own</button>
    </div>
    <div class="hw-note">Phase 2 Hospital Shadowing · Henry Ford Detroit · June 22–26, 2026 · with JVHL &amp; Michigan Works.<br>An unofficial educational orientation built with public Henry Ford Health information.</div>
  </div>
</div>
<script>
(function(){
  // Henry Ford lockup at the top of the sidebar
  var sb=document.getElementById('sidebar');
  if(sb){var bar=document.createElement('div');bar.className='hs-brandbar';
    bar.innerHTML='<img class="hs-logo" src="assets/brand/hfh-logo.png" alt="Henry Ford Health + Michigan State University Health Sciences"><div class="hs-dept">Pathology &amp; Laboratory Medicine</div>';
    sb.insertBefore(bar, sb.firstChild);}
  // Welcome screen
  var w=document.getElementById('hs-welcome');if(!w)return;
  function go(walk){w.classList.add('hide');setTimeout(function(){w.style.display='none';},600);
    if(walk&&window.__startWalkthrough){setTimeout(window.__startWalkthrough,650);}}
  var s=document.getElementById('hw-start'),e=document.getElementById('hw-explore');
  if(s)s.addEventListener('click',function(){go(true);});
  if(e)e.addEventListener('click',function(){go(false);});
})();
</script>
"""
html = html.replace("</body>", inject + "</body>")

open(OUT, "w", encoding="utf-8").write(html)
n = sum(1 for _, sid in ids if sid in HS)
print("wrote %s  (%d/%d stops translated)" % (OUT, n, len(ids)))
