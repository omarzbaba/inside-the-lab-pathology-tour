#!/usr/bin/env python3
"""
Photoreal lab INTERIOR generator. Builds a believable room shell (floor, walls,
ceiling light panels), lab casework, and station-specific instruments, then
renders an eye-level Cycles shot.

Run:
  /Applications/Blender.app/Contents/MacOS/Blender --background \
    --python blender/build_interior.py -- \
    --station histology --out assets/stations/histology.png \
    --samples 160 --res 1280

Room convention: centred at origin. Back wall at +Y, camera at -Y looking +Y.
Floor at Z=0, ceiling ~3.0. 1 unit = 1 m.
"""
import bpy, sys, os, math, argparse, mathutils

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
ap = argparse.ArgumentParser()
ap.add_argument("--station", required=True)
ap.add_argument("--out", required=True)
ap.add_argument("--samples", type=int, default=160)
ap.add_argument("--res", type=int, default=1280)
ap.add_argument("--save-blend", default="")
args = ap.parse_args(argv)

W, D, H = 9.0, 6.5, 3.0   # room width, depth, height

STATION_ACCENT = {
    "accessioning": (0.16, 0.45, 0.85), "grossing": (0.10, 0.52, 0.74),
    "histology": (0.50, 0.30, 0.80), "frozen": (0.06, 0.60, 0.85),
    "signout": (0.30, 0.42, 0.66), "ihc": (0.88, 0.35, 0.58),
    "cytology": (0.10, 0.62, 0.56), "neuropath": (0.55, 0.30, 0.85),
    "molecular": (0.93, 0.62, 0.18), "micro": (0.25, 0.68, 0.32),
    "core_clinical": (0.16, 0.45, 0.85), "autopsy": (0.42, 0.47, 0.56),
}

# ----------------------------- helpers -----------------------------
def clear():
    bpy.ops.object.select_all(action="SELECT"); bpy.ops.object.delete()
    for c in (bpy.data.meshes, bpy.data.materials, bpy.data.lights, bpy.data.cameras):
        for b in list(c): c.remove(b)

def M(name, rgb, rough=0.5, metal=0.0, emit=0.0, trans=0.0, ior=1.45):
    m = bpy.data.materials.new(name); m.use_nodes = True
    b = m.node_tree.nodes.get("Principled BSDF")
    b.inputs["Base Color"].default_value = (*rgb, 1)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    for key in ("Transmission Weight", "Transmission"):
        if key in b.inputs: b.inputs[key].default_value = trans; break
    if "IOR" in b.inputs: b.inputs["IOR"].default_value = ior
    if emit and "Emission Color" in b.inputs:
        b.inputs["Emission Color"].default_value = (*rgb, 1)
        b.inputs["Emission Strength"].default_value = emit
    return m

def cube(name, loc, size, material=None):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    o = bpy.context.active_object; o.name = name
    o.scale = (size[0]/2, size[1]/2, size[2]/2)
    bpy.ops.object.transform_apply(scale=True)
    if material: o.data.materials.append(material)
    return o

def cyl(name, loc, r, h, material=None, verts=32):
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=h, location=loc, vertices=verts)
    o = bpy.context.active_object; o.name = name
    if material: o.data.materials.append(material)
    return o

def bevel(o, w=0.01, seg=2):
    m = o.modifiers.new("b", "BEVEL"); m.width = w; m.segments = seg; return o

# ----------------------------- materials -----------------------------
clear()
mat_floor   = M("floor", (0.045, 0.055, 0.085), rough=0.07)      # dark polished, reflective
mat_wall    = M("wall", (0.06, 0.08, 0.13), rough=0.6)           # deep navy
mat_ceil    = M("ceil", (0.04, 0.05, 0.08), rough=0.8)
mat_panel   = M("panel", (0.95, 0.97, 1.0), emit=18.0)           # bright cool light panels
mat_steel   = M("steel", (0.78, 0.79, 0.82), rough=0.28, metal=1.0)
mat_white   = M("casework", (0.92, 0.93, 0.94), rough=0.4)
mat_counter = M("counter", (0.16, 0.18, 0.22), rough=0.35)       # dark resin top
mat_screen  = M("screen", (0.18, 0.45, 0.85), emit=2.2)
mat_glass   = M("glass", (0.85, 0.92, 0.95), rough=0.05, trans=1.0, ior=1.5)
mat_black   = M("plastic", (0.10, 0.11, 0.13), rough=0.5)
mat_accent  = M("accent", (0.10, 0.45, 0.85), rough=0.4)
mat_status  = M("status", (0.20, 0.95, 0.45), emit=4.0)
mat_red     = M("red", (0.80, 0.16, 0.20), rough=0.45)
mat_amber   = M("amber", (0.95, 0.62, 0.18), emit=3.0)

# ----------------------------- room shell -----------------------------
cube("Floor", (0, 0, -0.05), (W, D, 0.1), mat_floor)
cube("Ceiling", (0, 0, H + 0.05), (W, D, 0.1), mat_ceil)
cube("BackWall", (0, D/2, H/2), (W, 0.12, H), mat_wall)
cube("LeftWall", (-W/2, 0, H/2), (0.12, D, H), mat_wall)
cube("RightWall", (W/2, 0, H/2), (0.12, D, H), mat_wall)
# ceiling light panels (emissive) in a 2x2 grid
for px in (-W*0.22, W*0.22):
    for py in (-D*0.18, D*0.2):
        p = cube(f"panel_{px:.0f}_{py:.0f}", (px, py, H - 0.06), (1.6, 0.9, 0.04), mat_panel)
# baseboard
cube("base_b", (0, D/2 - 0.08, 0.08), (W, 0.04, 0.16), mat_steel)

# ----------------------------- furniture builders -----------------------------
def bench_run(cx, length, depth=0.7, top=0.92):
    """Lab casework along the back wall: base cabinets + dark countertop."""
    y = D/2 - depth/2 - 0.14
    cube(f"cab_{cx:.1f}", (cx, y, top/2), (length, depth, top), mat_white)
    cube(f"top_{cx:.1f}", (cx, y, top + 0.02), (length + 0.04, depth + 0.04, 0.04), mat_counter)
    # drawer seams (thin insets)
    n = max(1, int(length // 0.9))
    for i in range(n):
        dx = cx - length/2 + (i + 0.5) * (length / n)
        cube(f"hndl_{cx:.1f}_{i}", (dx, y - depth/2 + 0.01, top * 0.7), (0.18, 0.02, 0.02), mat_steel)
    return top

def wall_cabinets(cx, length):
    y = D/2 - 0.2
    cube(f"wc_{cx:.1f}", (cx, y, 2.15), (length, 0.34, 0.7), mat_white)

def stool(x, y):
    cyl(f"seat_{x:.1f}", (x, y, 0.55), 0.18, 0.05, mat_black)
    cyl(f"post_{x:.1f}", (x, y, 0.3), 0.03, 0.5, mat_steel)

def monitor(x, y, top, w=0.6):
    cube(f"mon_{x:.1f}", (x, y, top + 0.28), (w, 0.04, 0.34), mat_black)
    cube(f"scr_{x:.1f}", (x, y - 0.03, top + 0.28), (w - 0.05, 0.01, 0.29), mat_screen)
    cyl(f"mst_{x:.1f}", (x, y + 0.05, top + 0.08), 0.04, 0.16, mat_black)

def machine(x, top, w=0.9, d=0.6, h=0.7, screen=True, status=True, col=mat_white):
    cx = x; y = D/2 - 0.45
    o = cube(f"mac_{x:.1f}", (cx, y, top + h/2), (w, d, h), col); bevel(o, 0.02, 2)
    if screen:
        cube(f"macs_{x:.1f}", (cx + w*0.2, y - d/2 + 0.005, top + h*0.6), (w*0.4, 0.01, h*0.4), mat_screen)
    if status:
        for i in range(3):
            cyl(f"led_{x:.1f}_{i}", (cx - w*0.35 + i*0.08, y - d/2 + 0.01, top + h*0.8), 0.015, 0.01,
                [mat_status, mat_amber, mat_red][i])

def microscope(x, top):
    y = D/2 - 0.5
    cube(f"msb_{x:.1f}", (x, y, top + 0.04), (0.34, 0.42, 0.08), mat_black)   # base
    cube(f"msa_{x:.1f}", (x, y + 0.12, top + 0.22), (0.16, 0.12, 0.34), mat_black)  # arm
    cyl(f"mst_{x:.1f}", (x, y - 0.02, top + 0.14), 0.05, 0.16, mat_steel)     # stage post
    cube(f"msstg_{x:.1f}", (x, y - 0.02, top + 0.2), (0.22, 0.22, 0.03), mat_steel)
    # eyepiece tubes toward camera
    eo = cyl(f"mse_{x:.1f}", (x, y - 0.16, top + 0.34), 0.04, 0.18, mat_black)
    eo.rotation_euler = (math.radians(60), 0, 0)
    # objective turret
    cyl(f"mso_{x:.1f}", (x, y - 0.02, top + 0.28), 0.06, 0.06, mat_steel)

def biosafety(x):
    top = 0.85; y = D/2 - 0.5
    cube(f"bsc_{x:.1f}", (x, y, top + 0.55), (1.4, 0.75, 1.1), mat_white)
    cube(f"bscg_{x:.1f}", (x, y - 0.38, top + 0.55), (1.2, 0.02, 0.7), mat_glass)  # sash
    cube(f"bscw_{x:.1f}", (x, y, top), (1.4, 0.75, 0.7), mat_white)  # base
    cube(f"bsci_{x:.1f}", (x, y + 0.2, top + 0.5), (1.2, 0.3, 0.5), mat_steel)  # interior

def fridge_stack(x, red=False):
    col = mat_red if red else mat_white
    for i, h in enumerate([1.0, 0.95]):
        z0 = i * 1.0
        cube(f"frg_{x:.1f}_{i}", (x, D/2 - 0.45, z0 + h/2), (0.9, 0.7, h), col)
        cube(f"frh_{x:.1f}_{i}", (x + 0.4, D/2 - 0.8, z0 + h/2), (0.04, 0.04, h*0.6), mat_steel)

def petri_stacks(x, top):
    y = D/2 - 0.4
    for i in range(4):
        cyl(f"pet_{x:.1f}_{i}", (x - 0.3 + i*0.2, y, top + 0.04 + i*0.005), 0.07, 0.02,
            [mat_red, mat_amber, mat_white, mat_status][i % 4], verts=24)

def long_analyzer(cx, length):
    """Core-lab automation track: long boxy run with covers + sample rack."""
    top = 0.0; y = D/2 - 0.7
    o = cube(f"trk_{cx:.1f}", (cx, y, 0.6), (length, 0.9, 1.2), mat_white); bevel(o, 0.03, 2)
    cube(f"trks_{cx:.1f}", (cx, y - 0.46, 0.85), (length*0.5, 0.01, 0.45), mat_screen)
    for i in range(int(length//0.5)):
        cyl(f"tube_{cx:.1f}_{i}", (cx - length/2 + 0.3 + i*0.5, y - 0.3, 1.25), 0.03, 0.12, mat_red, 16)

# ----------------------------- per-station kit -----------------------------
def build(station):
    sid = station
    if sid in ("core-overview", "core_lab", "core_clinical"):
        long_analyzer(0, 6.0); stool(-2.5, -1.0)
        return "Core Laboratory"
    if sid == "frozen":
        top = bench_run(-1.4, 3.0)
        machine(-1.8, top, w=0.7, h=0.6, col=mat_steel)   # cryostat
        microscope(0.4, top); monitor(2.2, D/2-0.5, top, w=0.7); stool(0.2, -0.9)
        return "Frozen Section Room"
    if sid == "cytology":
        top = bench_run(-1.2, 3.2); microscope(-1.4, top)
        for i in range(5):
            cyl(f"vial_{i}", (0.4 + i*0.18, D/2-0.45, top+0.08), 0.04, 0.16, mat_amber, 16)
        monitor(2.2, D/2-0.5, top, w=0.7); stool(-1.4, -0.9); return "Cytology"
    if sid == "neuropath":
        top = bench_run(-1.2, 3.2); microscope(-1.4, top)
        cyl("brainbase", (0.6, D/2-0.5, top+0.04), 0.12, 0.06, mat_steel)
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.16, location=(0.6, D/2-0.5, top+0.18))
        bpy.context.active_object.data.materials.append(M("brain",(0.86,0.66,0.66),rough=0.6))
        monitor(2.2, D/2-0.5, top, w=0.7); stool(-1.4, -0.9); return "Neuropathology"
    if sid in ("transfusion", "bb", "blood-bank"):
        fridge_stack(-2.6, red=True); fridge_stack(-1.4, red=True)
        top = bench_run(1.6, 3.2); machine(1.4, top, col=mat_white); monitor(2.6, D/2-0.5, top)
        stool(1.2, -0.8); return "Blood Bank / Transfusion"
    if sid in ("micro", "microbiology"):
        biosafety(-2.4)
        top = bench_run(1.8, 3.6); petri_stacks(1.0, top); machine(2.4, top)
        stool(1.4, -0.9); return "Microbiology"
    if sid in ("molecular", "molec"):
        top = bench_run(0, W-1.4)
        machine(-2.6, top, w=1.0, h=0.9, col=mat_white)   # sequencer
        machine(0.0, top, w=0.9, h=0.7)                    # PCR
        monitor(2.4, D/2-0.5, top); stool(-2.6, -0.9); stool(0.2, -0.9)
        return "Molecular Diagnostics"
    if sid in ("ihc",):
        top = bench_run(-1.4, 3.0); machine(-1.4, top, w=1.4, h=0.95, col=mat_white)
        wall_cabinets(1.8, 3.0); monitor(2.2, D/2-0.5, top); stool(-1.4, -0.9)
        return "Immunohistochemistry"
    if sid in ("hist-process", "histology", "hist-microtomy", "hist-collation"):
        top = bench_run(0, W-1.4); wall_cabinets(-2.0, 3.0)
        if sid == "hist-microtomy":
            machine(-1.6, top, w=0.5, h=0.4, screen=False, col=mat_steel)  # microtome
            cyl("wheel", (-1.0, D/2-0.5, top+0.25), 0.18, 0.06, mat_steel)
            cyl("bath", (0.4, D/2-0.5, top+0.06), 0.22, 0.08, mat_steel)
            stool(-1.3, -0.8)
        else:
            machine(-1.8, top, w=0.9, h=0.8, col=mat_white)  # processor
            machine(0.6, top, w=0.9, h=0.6)
            stool(0.4, -0.9)
        monitor(2.4, D/2-0.5, top)
        return "Histology"
    if sid in ("scanning",):
        top = bench_run(-1.6, 3.0); machine(-1.6, top, w=1.0, h=0.7, col=mat_black)  # scanner
        monitor(1.4, D/2-0.5, top, w=0.8); monitor(2.6, D/2-0.5, top, w=0.8)
        stool(1.8, -0.9); return "Slide Scanning"
    if sid in ("surgpath", "sign-out", "sp_office", "signout"):
        # office: desk + scope + monitor + chair
        cube("desk", (0, D/2-0.7, 0.74/2), (2.2, 1.0, 0.74), mat_white)
        cube("desktop", (0, D/2-0.7, 0.76), (2.3, 1.05, 0.04), mat_counter)
        microscope(-0.7, 0.78); monitor(0.7, D/2-0.7, 0.78, w=0.7)
        cube("chair", (0, -0.2, 0.5), (0.5, 0.5, 0.1), mat_black); cyl("cpost",(0,-0.2,0.25),0.04,0.5,mat_steel)
        return "Surgical Pathology Sign-Out"
    if sid in ("grossing", "gross"):
        # stainless grossing station with backsplash + board + faucet
        top = 0.92; y = D/2 - 0.5
        cube("gstn", (0, y, top/2), (3.2, 0.8, top), mat_steel)
        cube("gtop", (0, y, top+0.02), (3.3, 0.85, 0.05), mat_steel)
        cube("gback", (0, D/2-0.16, 1.5), (3.4, 0.06, 1.2), mat_steel)
        cube("board", (0, y-0.1, top+0.07), (0.9, 0.5, 0.04), M("board",(0.85,0.84,0.8),rough=0.6))
        cyl("faucet", (0.9, y+0.1, top+0.25), 0.03, 0.5, mat_steel);
        monitor(-1.2, y, top, w=0.6); stool(0, -0.9)
        return "Grossing"
    if sid in ("accessioning", "accession"):
        top = bench_run(0, W-1.4); wall_cabinets(-1.8, 3.2)
        monitor(-1.6, D/2-0.5, top, w=0.7); monitor(0.0, D/2-0.5, top, w=0.7)
        machine(1.8, top, w=0.5, h=0.3, screen=False, col=mat_black)  # label printer
        stool(-1.6, -0.9); stool(0.0, -0.9)
        return "Accessioning"
    if sid in ("autopsy",):
        # dignified, non-graphic: stainless table + instruments + light
        cube("table", (0, 0.4, 0.9/2), (1.0, 2.4, 0.9), mat_steel)
        cube("ttop", (0, 0.4, 0.92), (1.05, 2.45, 0.04), mat_steel)
        bench_run(2.6, 2.6); cyl("lamp", (0, 0.4, 2.3), 0.25, 0.1, mat_panel)
        return "Autopsy Suite"
    # default generic lab
    top = bench_run(0, W-1.4); machine(-1.6, top); monitor(1.6, D/2-0.5, top); stool(0,-0.9)
    return station

label = build(args.station)

# ----------------------------- accent feature wall -----------------------------
accent = STATION_ACCENT.get(args.station, (0.16, 0.45, 0.85))
mat_acc = M("acc", accent, rough=0.4)
mat_acc_glow = M("accglow", accent, emit=7.0)
# glowing accent signage band high on the back wall
cube("signglow", (-W*0.12, D/2 - 0.06, H - 0.45), (3.4, 0.03, 0.16), mat_acc_glow)
# tall accent light strip on the left wall (identity + side light)
cube("striph", (-W/2 + 0.08, -D*0.15, H*0.55), (0.04, 0.10, H*0.7), mat_acc_glow)
# accent floor inlay stripe leading toward the bench
cube("inlay", (0, -D*0.05, 0.005), (W*0.7, 0.16, 0.02), mat_acc_glow)

# ----------------------------- lighting -----------------------------
world = bpy.data.worlds.new("W"); bpy.context.scene.world = world
world.use_nodes = True
bg = world.node_tree.nodes["Background"]
bg.inputs[0].default_value = (0.10, 0.13, 0.20, 1); bg.inputs[1].default_value = 0.10
# subtle directional key for soft shadows
bpy.ops.object.light_add(type="SUN", location=(-3, -2, H + 4))
sun = bpy.context.active_object; sun.data.energy = 1.6; sun.data.angle = math.radians(10)
sun.data.color = (1.0, 0.97, 0.9)
sun.rotation_euler = (math.radians(52), math.radians(8), math.radians(28))
# soft fill from camera side so foreground isn't crushed
bpy.ops.object.light_add(type="AREA", location=(0, -D/2 - 1, H - 0.9))
fa = bpy.context.active_object; fa.data.energy = 600; fa.data.size = 6
fa.rotation_euler = (math.radians(62), 0, 0)

# ----------------------------- camera -----------------------------
bpy.ops.object.camera_add()
cam = bpy.context.active_object; bpy.context.scene.camera = cam
cam.location = (W*0.32, -D/2 - 0.05, 1.42)
cam.data.lens = 26
target = mathutils.Vector((-0.6, D/2 - 0.6, 1.15))
cam.rotation_euler = (target - cam.location).to_track_quat('-Z', 'Y').to_euler()

# ----------------------------- render -----------------------------
sc = bpy.context.scene
sc.render.engine = "CYCLES"
try:
    sc.cycles.device = "GPU"
    prefs = bpy.context.preferences.addons["cycles"].preferences
    prefs.compute_device_type = "METAL"; prefs.get_devices()
    for d in prefs.devices: d.use = True
except Exception as e:
    print("GPU note:", e)
sc.cycles.samples = args.samples
sc.cycles.use_denoising = True
sc.render.resolution_x = args.res
sc.render.resolution_y = int(args.res * 0.7)
try: sc.view_settings.exposure = 0.4
except Exception: pass
sc.render.filepath = os.path.abspath(args.out)
os.makedirs(os.path.dirname(sc.render.filepath), exist_ok=True)
if args.save_blend:
    bpy.ops.wm.save_as_mainfile(filepath=os.path.abspath(args.save_blend))
print(f"Rendering interior '{label}' -> {sc.render.filepath}")
bpy.ops.render.render(write_still=True)
print("DONE", sc.render.filepath)
