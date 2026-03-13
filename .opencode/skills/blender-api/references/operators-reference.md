# Operators Reference

Blender 5.0 Python API — most-used operators across all categories.

## Table of Contents

- [Operator Calling Conventions](#operator-calling-conventions)
- [Object Ops](#object-ops)
- [Mesh Ops](#mesh-ops)
- [Transform Ops](#transform-ops)
- [Render Ops](#render-ops)
- [Import/Export Ops](#importexport-ops)
- [UV Ops](#uv-ops)
- [WM (File) Ops](#wm-file-ops)
- [Animation Ops](#animation-ops)
- [Screen Ops](#screen-ops)
- [View3D / Curve / Node Highlights](#view3d--curve--node-highlights)

---

## Operator Calling Conventions

All operators live under `bpy.ops.<category>.<name>()`. They return a set: `{'FINISHED'}`, `{'CANCELLED'}`, or `{'RUNNING_MODAL'}`.

**Context requirement** — most operators need a valid context (correct mode, selection, area type). In scripts running outside the UI, use `temp_override`:

```python
import bpy

# temp_override pattern (Blender 3.2+)
with bpy.context.temp_override(active_object=obj, selected_objects=[obj]):
    bpy.ops.object.delete()

# Override with a specific area/region (needed for viewport ops)
window = bpy.context.window_manager.windows[0]
area = [a for a in window.screen.areas if a.type == 'VIEW_3D'][0]
region = [r for r in area.regions if r.type == 'WINDOW'][0]
with bpy.context.temp_override(window=window, area=area, region=region):
    bpy.ops.view3d.camera_to_view()
```

**Key rules:**
- Keyword-only args after `***` — always pass parameters by name
- Avoid operators when direct data API is available (faster, no context needed)
- `bpy.ops.object.mode_set()` before operators that require a specific mode

---

## Object Ops

### Adding Objects

```python
bpy.ops.object.add(type='EMPTY', radius=1.0, location=(0,0,0), rotation=(0,0,0), align='WORLD')
# type: 'EMPTY', 'MESH', 'CURVE', 'SURFACE', 'META', 'FONT', 'ARMATURE', 'LATTICE', 'LIGHT', 'CAMERA', etc.

bpy.ops.object.armature_add(radius=1.0, location=(0,0,0))
```

### Selection

```python
bpy.ops.object.select_all(action='TOGGLE')    # 'SELECT', 'DESELECT', 'INVERT', 'TOGGLE'
bpy.ops.object.select_by_type(type='MESH', extend=False)  # Object Type Items
```

### Delete / Join / Duplicate

```python
bpy.ops.object.delete(use_global=False, confirm=True)
bpy.ops.object.join()                          # selected → active object
bpy.ops.object.duplicate(linked=False)         # linked=True shares data
bpy.ops.object.duplicate_move()                # duplicate + translate
```

### Convert

```python
bpy.ops.object.convert(target='MESH', keep_original=False)
# target: 'MESH', 'CURVE', 'POINTCLOUD', 'CURVES', 'GREASEPENCIL'
```

### Mode Set

```python
bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
# mode: 'OBJECT', 'EDIT', 'SCULPT', 'VERTEX_PAINT', 'WEIGHT_PAINT', 'TEXTURE_PAINT', 'POSE'

bpy.ops.object.mode_set_with_submode(mode='EDIT', mesh_select_mode={'VERT'})
# mesh_select_mode: {'VERT'}, {'EDGE'}, {'FACE'} or combinations
```

### Parenting

```python
bpy.ops.object.parent_set(type='OBJECT', keep_transform=False)
# type: 'OBJECT', 'ARMATURE', 'ARMATURE_AUTO', 'BONE', 'CURVE', 'LATTICE', 'VERTEX', etc.

bpy.ops.object.parent_clear(type='CLEAR')      # 'CLEAR', 'CLEAR_KEEP_TRANSFORM', 'CLEAR_INVERSE'
```

### Origin

```python
bpy.ops.object.origin_set(type='GEOMETRY_ORIGIN', center='MEDIAN')
# type: 'GEOMETRY_ORIGIN', 'ORIGIN_GEOMETRY', 'ORIGIN_CURSOR', 'ORIGIN_CENTER_OF_MASS', 'ORIGIN_CENTER_OF_VOLUME'
```

### Shading

```python
bpy.ops.object.shade_smooth(keep_sharp_edges=True)
bpy.ops.object.shade_flat(keep_sharp_edges=True)
bpy.ops.object.shade_smooth_by_angle(angle=0.523599, keep_sharp_edges=True)  # angle in radians
```

### Modifiers (via operators)

```python
bpy.ops.object.modifier_add(type='SUBSURF')   # Object Modifier Type Items
bpy.ops.object.modifier_apply(modifier="Subdivision")
bpy.ops.object.modifier_remove(modifier="Subdivision")
```

---

## Mesh Ops

All mesh ops require **Edit Mode** (`bpy.ops.object.mode_set(mode='EDIT')`).

### Primitives (Object Mode)

```python
bpy.ops.mesh.primitive_cube_add(size=2.0, location=(0,0,0), rotation=(0,0,0))
bpy.ops.mesh.primitive_plane_add(size=2.0, location=(0,0,0))
bpy.ops.mesh.primitive_uv_sphere_add(segments=32, ring_count=16, radius=1.0)
bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=1.0)
bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=1.0, depth=2.0)
bpy.ops.mesh.primitive_cone_add(vertices=32, radius1=1.0, radius2=0.0, depth=2.0)
bpy.ops.mesh.primitive_torus_add(major_radius=1.0, minor_radius=0.25, major_segments=48, minor_segments=12)
bpy.ops.mesh.primitive_circle_add(vertices=32, radius=1.0, fill_type='NOTHING')  # 'NOTHING','NGON','TRIFAN'
bpy.ops.mesh.primitive_grid_add(x_subdivisions=10, y_subdivisions=10, size=2.0)
bpy.ops.mesh.primitive_monkey_add(size=2.0)
```

### Selection (Edit Mode)

```python
bpy.ops.mesh.select_all(action='TOGGLE')       # 'SELECT', 'DESELECT', 'INVERT', 'TOGGLE'
```

### Editing

```python
bpy.ops.mesh.extrude_region_move()              # extrude + translate
bpy.ops.mesh.subdivide(number_cuts=1, smoothness=0.0)
bpy.ops.mesh.merge(type='CENTER', uvs=False)   # 'CENTER', 'CURSOR', 'COLLAPSE', 'FIRST', 'LAST'
bpy.ops.mesh.separate(type='SELECTED')          # 'SELECTED', 'MATERIAL', 'LOOSE'
bpy.ops.mesh.delete(type='VERT')               # 'VERT', 'EDGE', 'FACE', 'EDGE_FACE', 'ONLY_FACE'
bpy.ops.mesh.fill(use_beauty=True)
bpy.ops.mesh.fill_grid(span=1, offset=0)
```

### Bevel & Knife

```python
bpy.ops.mesh.bevel(offset=0.1, segments=1, profile=0.5, affect='EDGES')
# affect: 'EDGES' or 'VERTICES'; offset_type: 'OFFSET','WIDTH','DEPTH','PERCENT','ABSOLUTE'

bpy.ops.mesh.knife_project(cut_through=False)   # project knife from view
```

### Loop & Normals

```python
bpy.ops.mesh.loop_cut_and_slide()               # interactive — use loopcut_slide for scripting
bpy.ops.mesh.normals_make_consistent(inside=False)
```

---

## Transform Ops

Work in both Object and Edit Mode on selected elements.

```python
bpy.ops.transform.translate(value=(x, y, z), orient_type='GLOBAL', constraint_axis=(False,False,False))
bpy.ops.transform.rotate(value=angle, orient_axis='Z', orient_type='GLOBAL')  # value in radians
bpy.ops.transform.resize(value=(sx, sy, sz), orient_type='GLOBAL')
bpy.ops.transform.mirror(orient_type='GLOBAL', constraint_axis=(True,False,False))  # mirror along X
```

**Common parameters** (shared across transform ops):
- `orient_type` — `'GLOBAL'`, `'LOCAL'`, `'NORMAL'`, `'GIMBAL'`, `'VIEW'`, `'CURSOR'`
- `constraint_axis` — `(bool, bool, bool)` to lock axes
- `mirror` — `bool` mirror editing
- `snap` — `bool` enable snapping
- `use_proportional_edit`, `proportional_edit_falloff`, `proportional_size`

### Direct data alternative (faster, no context needed)

```python
obj.location += mathutils.Vector((1, 0, 0))
obj.rotation_euler.z += 0.5
obj.scale *= 2.0
```

---

## Render Ops

```python
bpy.ops.render.render(write_still=False)                    # [HEADLESS-OK] render single frame
bpy.ops.render.render(animation=True)                       # [HEADLESS-OK] render animation range
bpy.ops.render.render(animation=True, frame_start=1, frame_end=100)
bpy.ops.render.render(write_still=True, layer='', scene='') # [HEADLESS-OK] write to output path

bpy.ops.render.opengl(animation=False, write_still=False)   # [GUI-ONLY] viewport snapshot
bpy.ops.render.view_show()                                   # [GUI-ONLY] toggle render viewer
bpy.ops.render.view_cancel()                                 # [GUI-ONLY] close render viewer
```

> **`render.opengl()` is GUI-ONLY** — it captures the viewport buffer, which doesn't exist in `--background` mode. Use `render.render(write_still=True)` for headless renders.

**Typical headless render:**

```python
import bpy
scn = bpy.context.scene
scn.render.filepath = "/tmp/output.png"
scn.render.resolution_x = 1920
scn.render.resolution_y = 1080
bpy.ops.render.render(write_still=True)
```

---

## Import/Export Ops

### FBX

```python
# Import
bpy.ops.import_scene.fbx(filepath="/path/to/file.fbx", global_scale=1.0, use_anim=True,
    use_custom_normals=True, axis_forward='-Z', axis_up='Y')

# Export
bpy.ops.export_scene.fbx(filepath="/path/to/file.fbx", use_selection=False,
    global_scale=1.0, apply_unit_scale=True, use_mesh_modifiers=True,
    bake_anim=True, path_mode='AUTO', axis_forward='-Z', axis_up='Y',
    object_types={'ARMATURE','CAMERA','EMPTY','LIGHT','MESH','OTHER'})
```

### glTF 2.0

```python
# Import
bpy.ops.import_scene.gltf(filepath="/path/to/file.glb", import_pack_images=True,
    merge_vertices=False, import_shading='NORMALS')

# Export (format auto-detected from extension: .glb=binary, .gltf=JSON)
bpy.ops.export_scene.gltf(filepath="/path/to/file.glb", export_format='GLB',
    export_texcoords=True, export_normals=True, export_materials='EXPORT',
    export_animations=True, export_yup=True, use_selection=False)
# export_format: 'GLB' (binary), 'GLTF_SEPARATE' (JSON + bins), 'GLTF_EMBEDDED'
```

### OBJ (built-in via wm)

```python
# Import
bpy.ops.wm.obj_import(filepath="/path/to/file.obj", global_scale=1.0,
    forward_axis='NEGATIVE_Z', up_axis='Y')

# Export
bpy.ops.wm.obj_export(filepath="/path/to/file.obj", export_selected_objects=False,
    export_uv=True, export_normals=True, export_materials=True,
    forward_axis='NEGATIVE_Z', up_axis='Y', apply_modifiers=True)
```

### STL (built-in via wm)

```python
# Import
bpy.ops.wm.stl_import(filepath="/path/to/file.stl", global_scale=1.0,
    forward_axis='Y', up_axis='Z')

# Export
bpy.ops.wm.stl_export(filepath="/path/to/file.stl", export_selected_objects=False,
    global_scale=1.0, ascii_format=False, apply_modifiers=True,
    forward_axis='Y', up_axis='Z')
```

---

## UV Ops

All UV ops require **Edit Mode** and usually an active UV map.

```python
bpy.ops.uv.unwrap(method='CONFORMAL', fill_holes=False, margin=0.001)
# method: 'CONFORMAL' (preserves angles), 'ANGLE_BASED' (preserves area)

bpy.ops.uv.smart_project(angle_limit=1.15192, island_margin=0.0, correct_aspect=True,
    scale_to_bounds=False)

bpy.ops.uv.cube_project(cube_size=1.0, correct_aspect=True)

bpy.ops.uv.pack_islands(rotate=True, margin=0.001, scale=True)
```

---

## WM (File) Ops

```python
bpy.ops.wm.open_mainfile(filepath="/path/to/file.blend", load_ui=True)
bpy.ops.wm.save_mainfile(filepath="/path/to/file.blend", compress=False, relative_remap=False)
bpy.ops.wm.save_as_mainfile(filepath="/path/to/new.blend", compress=False, copy=False)
bpy.ops.wm.read_homefile(use_factory_startup=False, use_empty=False)
```

---

## Animation Ops

```python
bpy.ops.anim.keyframe_insert(type='DEFAULT')    # insert keyframe on active channels
bpy.ops.anim.keyframe_delete(type='DEFAULT')    # delete keyframe on active channels
bpy.ops.anim.change_frame(frame=24.0)           # jump to frame

# Playback
bpy.ops.screen.animation_play(reverse=False, sync=False)
bpy.ops.screen.animation_cancel(restore_frame=True)
```

**Direct data alternative (preferred for scripting):**

```python
obj.keyframe_insert(data_path="location", frame=1)
obj.keyframe_insert(data_path="rotation_euler", frame=1)
obj.keyframe_delete(data_path="location", frame=1)
bpy.context.scene.frame_set(24)
```

---

## Screen Ops [GUI-ONLY]

> **[GUI-ONLY]** All `screen.*` operators require an active screen/window context and do not work in `--background` mode. For headless frame control, use `bpy.context.scene.frame_set(N)`.

```python
bpy.ops.screen.animation_play(reverse=False, sync=False)       # [GUI-ONLY]
bpy.ops.screen.animation_cancel(restore_frame=True)            # [GUI-ONLY]
bpy.ops.screen.frame_jump(end=False)                           # [GUI-ONLY]
bpy.ops.screen.screenshot_area(filepath="/tmp/screenshot.png") # [GUI-ONLY]
```

---

## View3D / Curve / Node Highlights

### View3D [GUI-ONLY]

> **[GUI-ONLY]** All `view3d.*` operators require an active 3D Viewport. They do not work in `--background` mode. For headless camera positioning, set `camera.location` and `camera.rotation_euler` directly.

```python
bpy.ops.view3d.camera_to_view()                  # [GUI-ONLY] align active camera to current view
bpy.ops.view3d.snap_cursor_to_center()            # [GUI-ONLY] cursor → world origin
bpy.ops.view3d.snap_cursor_to_selected()          # [GUI-ONLY] cursor → selection
bpy.ops.view3d.snap_selected_to_cursor(use_offset=False)  # [GUI-ONLY]
bpy.ops.view3d.view_all(center=False)             # [GUI-ONLY] frame all objects
bpy.ops.view3d.view_selected(use_all_regions=False)  # [GUI-ONLY] frame selected
```

### Curve (Edit Mode)

```python
bpy.ops.curve.primitive_bezier_curve_add(radius=1.0, location=(0,0,0))
bpy.ops.curve.primitive_bezier_circle_add(radius=1.0, location=(0,0,0))
bpy.ops.curve.primitive_nurbs_curve_add(radius=1.0)
bpy.ops.curve.primitive_nurbs_circle_add(radius=1.0)
bpy.ops.curve.subdivide()
bpy.ops.curve.handle_type_set(type='AUTO')      # 'AUTO', 'VECTOR', 'ALIGNED', 'FREE_ALIGN'
bpy.ops.curve.extrude_move()                     # extrude curve points
```

### Node [GUI-ONLY]

> **[GUI-ONLY]** All `node.*` operators require an active Node Editor area. For headless node manipulation, use the direct API: `node_tree.nodes.new()`, `node_tree.links.new()`, etc.

```python
bpy.ops.node.add_node(type='ShaderNodeBsdfPrincipled', use_transform=True)  # [GUI-ONLY]
bpy.ops.node.link_make(replace=False)             # [GUI-ONLY] — use node_tree.links.new() instead
bpy.ops.node.group_make()                         # [GUI-ONLY] selected nodes → group
bpy.ops.node.group_ungroup()                      # [GUI-ONLY]
bpy.ops.node.select_all(action='SELECT')          # [GUI-ONLY]
bpy.ops.node.delete()                             # [GUI-ONLY]
```

### Material

```python
bpy.ops.material.new()
bpy.ops.material.copy()
bpy.ops.material.paste()
```
