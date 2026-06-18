#!/usr/bin/env python3
"""
Procedurally build a 3D model of the Henry Ford Pathology department in Blender
from the recovered floor-plan data (reference/rooms.json), then render it.

Run headless:
  /Applications/Blender.app/Contents/MacOS/Blender --background \
      --python blender/build_lab.py -- \
      --rooms reference/rooms.json --out blender/renders/overview.png \
      --engine EEVEE --samples 64 --view overview

Axes: floorplan x -> Blender X, floorplan z -> Blender -Y, height -> Z. 1 unit = 1 m.
"""
import bpy, bmesh, json, sys, os, math, argparse

# ----------------------------- args -----------------------------
argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
ap = argparse.ArgumentParser()
ap.add_argument("--rooms", required=True)
ap.add_argument("--out", required=True)
ap.add_argument("--engine", default="EEVEE", choices=["EEVEE", "CYCLES"])
ap.add_argument("--samples", type=int, default=64)
ap.add_argument("--res", type=int, default=1600)
ap.add_argument("--view", default="overview")   # overview | <roomId>
ap.add_argument("--save-blend", default="")
args = ap.parse_args(argv)

ROOMS = json.load(open(args.rooms))

# ----------------------------- palette -----------------------------
# Muted, realistic dept tints (wayfinding without candy colors)
DEPT = {
    "core_lab":  (0.16, 0.45, 0.85), "bb":      (0.85, 0.22, 0.28),
    "autopsy":   (0.42, 0.47, 0.56), "cytopath":(0.10, 0.62, 0.56),
    "gross":     (0.10, 0.52, 0.74), "histology":(0.50, 0.30, 0.80),
    "ihc":       (0.88, 0.35, 0.58), "molec":   (0.93, 0.62, 0.18),
    "micro":     (0.25, 0.68, 0.32), "hla":     (0.30, 0.42, 0.82),
    "special":   (0.62, 0.46, 0.24), "quality": (0.62, 0.62, 0.20),
    "sp_office": (0.36, 0.46, 0.66), "chair":   (0.60, 0.42, 0.30),
    "lab_cs":    (0.30, 0.56, 0.66), "coag":    (0.80, 0.30, 0.36),
    "corridor":  (0.82, 0.83, 0.86),
}
WALL_H = {"corridor": 0.15, "sp_office": 2.6, "chair": 2.6}   # default below
DEF_WALL_H = 2.2

def clear_scene():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete()
    for c in (bpy.data.meshes, bpy.data.materials, bpy.data.lights, bpy.data.cameras):
        for b in list(c):
            c.remove(b)

def mat(name, rgb, rough=0.6, metal=0.0, emit=0.0):
    m = bpy.data.materials.new(name); m.use_nodes = True
    bsdf = m.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (*rgb, 1)
    bsdf.inputs["Roughness"].default_value = rough
    bsdf.inputs["Metallic"].default_value = metal
    if emit and "Emission Color" in bsdf.inputs:
        bsdf.inputs["Emission Color"].default_value = (*rgb, 1)
        bsdf.inputs["Emission Strength"].default_value = emit
    return m

def box(name, cx, cy, sx, sy, z0, z1, material):
    bpy.ops.mesh.primitive_cube_add(size=1, location=(cx, cy, (z0 + z1) / 2))
    o = bpy.context.active_object; o.name = name
    o.scale = (sx / 2, sy / 2, (z1 - z0) / 2)
    bpy.ops.object.transform_apply(scale=True)
    o.data.materials.append(material)
    return o

# floorplan -> blender helpers
def fx(x): return float(x)
def fy(z): return -float(z)

# ----------------------------- build -----------------------------
clear_scene()

xs = [r["x1"] for r in ROOMS] + [r["x2"] for r in ROOMS]
zs = [r["z1"] for r in ROOMS] + [r["z2"] for r in ROOMS]
minx, maxx, minz, maxz = min(xs), max(xs), min(zs), max(zs)
cx_all, cy_all = (minx + maxx) / 2, -(minz + maxz) / 2
span = max(maxx - minx, maxz - minz)

# ground slab (epoxy lab floor)
floor_mat = mat("Floor", (0.86, 0.87, 0.89), rough=0.35)
box("GroundSlab", cx_all, cy_all, (maxx - minx) + 8, (maxz - minz) + 8, -0.2, 0.0, floor_mat)

mats = {d: mat(f"dept_{d}", c, rough=0.5) for d, c in DEPT.items()}
wall_mat = mat("Wall", (0.92, 0.93, 0.95), rough=0.7)
equip_mat = mat("Equip", (0.72, 0.74, 0.78), rough=0.55, metal=0.1)
accent_mat = mat("Accent", (0.20, 0.45, 0.95), rough=0.4, emit=2.0)

for r in ROOMS:
    x1, z1, x2, z2 = r["x1"], r["z1"], r["x2"], r["z2"]
    cx, cy = (fx(x1) + fx(x2)) / 2, (fy(z1) + fy(z2)) / 2
    sx, sy = abs(fx(x2) - fx(x1)), abs(fy(z2) - fy(z1))
    if sx < 0.2 or sy < 0.2:
        continue
    dept = r["dept"]
    # Clean "extruded pad" map style: one rounded colored block per room.
    if dept == "corridor":
        box(f"corr_{r['id']}", cx, cy, sx * 0.99, sy * 0.99, 0.0, 0.10, mats["corridor"])
        continue
    h = 0.55 + (0.45 if min(sx, sy) > 6 else 0.0)   # bigger rooms slightly taller
    o = box(f"room_{r['id']}", cx, cy, sx * 0.9, sy * 0.9, 0.10, h, mats.get(dept, wall_mat))
    # soft bevel for a premium look
    mod = o.modifiers.new("bev", "BEVEL"); mod.width = 0.12; mod.segments = 3
    # subtle equipment hint on larger lab rooms (light, not metal)
    if min(sx, sy) > 7:
        box(f"eq_{r['id']}", cx, cy, sx * 0.45, min(1.0, sy * 0.18), h, h + 0.5, equip_mat)

# ----------------------------- lighting / world -----------------------------
world = bpy.data.worlds.new("W"); bpy.context.scene.world = world
world.use_nodes = True
bg = world.node_tree.nodes["Background"]
bg.inputs[0].default_value = (0.58, 0.67, 0.80, 1)   # soft sky
bg.inputs[1].default_value = 0.35                     # lower ambient -> more contrast

bpy.ops.object.light_add(type="SUN", location=(cx_all + 30, cy_all - 30, 80))
sun = bpy.context.active_object.data; sun.energy = 3.5; sun.angle = math.radians(2)
bpy.context.active_object.rotation_euler = (math.radians(45), math.radians(15), math.radians(35))

for dx, dy in [(-1, -1), (1, 1)]:
    bpy.ops.object.light_add(type="AREA",
        location=(cx_all + dx * span * 0.4, cy_all + dy * span * 0.4, 40))
    a = bpy.context.active_object.data; a.energy = 3500; a.size = 30

# ----------------------------- camera -----------------------------
bpy.ops.object.camera_add()
cam = bpy.context.active_object
scene = bpy.context.scene
scene.camera = cam

if args.view == "overview":
    d = span * 0.92
    cam.location = (cx_all + d * 0.62, cy_all - d * 0.62, d * 0.72)
    cam.data.lens = 52
else:
    room = next((r for r in ROOMS if r["id"] == args.view), None) or ROOMS[0]
    rx = (fx(room["x1"]) + fx(room["x2"])) / 2
    ry = (fy(room["z1"]) + fy(room["z2"])) / 2
    cam.location = (rx + 14, ry - 14, 16)
    cam.data.lens = 35
# aim at target
tx, ty, tz = (cx_all, cy_all, 0) if args.view == "overview" else (rx, ry, 1.2)
import mathutils
dirv = mathutils.Vector((tx, ty, tz)) - cam.location
cam.rotation_euler = dirv.to_track_quat('-Z', 'Y').to_euler()

# ----------------------------- render -----------------------------
scene.render.resolution_x = args.res
scene.render.resolution_y = int(args.res * 0.625)
scene.render.film_transparent = False
try: scene.view_settings.exposure = -0.7
except Exception: pass
scene.render.filepath = os.path.abspath(args.out)
os.makedirs(os.path.dirname(scene.render.filepath), exist_ok=True)

# engine (Blender 5.x EEVEE id fallback)
if args.engine == "CYCLES":
    scene.render.engine = "CYCLES"
    try:
        scene.cycles.device = "GPU"
        prefs = bpy.context.preferences.addons["cycles"].preferences
        prefs.compute_device_type = "METAL"
        prefs.get_devices()
        for d in prefs.devices: d.use = True
    except Exception as e:
        print("GPU setup note:", e)
    scene.cycles.samples = args.samples
    scene.cycles.use_denoising = True
else:
    for eng in ("BLENDER_EEVEE_NEXT", "BLENDER_EEVEE"):
        try: scene.render.engine = eng; break
        except Exception: continue
    try: scene.eevee.taa_render_samples = args.samples
    except Exception: pass

if args.save_blend:
    bpy.ops.wm.save_as_mainfile(filepath=os.path.abspath(args.save_blend))

print(f"Rendering {args.view} with {scene.render.engine} -> {scene.render.filepath}")
bpy.ops.render.render(write_still=True)
print("DONE", scene.render.filepath)
