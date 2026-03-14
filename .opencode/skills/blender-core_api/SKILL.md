---
name: blender-core_api
description: Blender 5.0 Python API reference for scripting with bpy. Use this skill whenever writing Blender Python scripts, addons, or automation — including mesh/bmesh manipulation, materials and shader nodes, geometry nodes, modifiers, constraints, operators, mathutils, handlers/timers, import/export, and avoiding common pitfalls. Consult this skill for any bpy.types, bpy.ops, bpy.data, bpy.context, bpy.props, bpy.app, bmesh, mathutils, or bpy_extras question. Also use when the user mentions Blender scripting, 3D modeling automation, procedural generation in Blender, or Python-based Blender workflows.
metadata:
    skill-author: Biomaps
---

# Blender 5.0 Python API

This skill provides distilled API reference for Blender 5.0's Python API (`bpy` module and friends). It covers the most-used parts of the API across 11 domain reference files, loaded on demand.

**Target**: Blender 4.x/5.0 embedded Python 3.11+

## Domain Router

Read the reference file(s) matching the user's task. If the task spans multiple domains, read multiple files.

| Domain | Reference File | When to Read |
|--------|---------------|--------------|
| Pitfalls & crashes | `references/gotchas-and-pitfalls.md` | Stale refs, threading, undo/redo bugs, mode errors |
| Best practices | `references/best-practices.md` | Performance, code organization, data access patterns |
| Core API | `references/core-api.md` | bpy.context, bpy.data, bpy.props, bpy.utils, bpy.msgbus |
| Mesh & BMesh | `references/mesh-and-bmesh.md` | Mesh creation/editing, bmesh ops, vertex/edge/face data |
| Materials & Nodes | `references/materials-and-nodes.md` | Shader nodes, materials, node trees, Principled BSDF |
| Geometry Nodes | `references/geometry-nodes.md` | Geometry node trees, NodesModifier, procedural geometry |
| Modifiers & Constraints | `references/modifiers-and-constraints.md` | Adding/configuring modifiers and constraints |
| Operators | `references/operators-reference.md` | bpy.ops.* calls, operator parameters |
| Math & Spatial | `references/math-and-spatial.md` | Vector, Matrix, Euler, Quaternion, BVHTree, KDTree |
| Handlers & Timers | `references/handlers-and-timers.md` | bpy.app.handlers, bpy.app.timers, @persistent |
| Import/Export & Utils | `references/import-export.md` | File I/O, bpy_extras, view3d_utils |

**Always read `gotchas-and-pitfalls.md`** when the task involves modifying Blender data, especially mesh data, collections, or anything involving undo/redo.

**Read `best-practices.md`** when writing substantial scripts (>20 lines) — it has performance patterns and registration conventions that prevent common mistakes.

## Top 10 Universal Rules

These apply to ALL Blender Python code. Memorize them.

1. **Never hold stale references.** After undo/redo, adding/removing items from collections, or calling operators that modify data, all previous `bpy.types` references may be invalidated. Re-fetch from `bpy.data` or `bpy.context`.

2. **No threading.** Blender's Python API is not thread-safe. Never call `bpy.*` from a thread. Use `bpy.app.timers` for deferred work.

3. **Don't access `bpy.context` at import time.** Module-level code runs before the context exists. Access context only inside functions (operators, handlers, etc.).

4. **Use `temp_override` for operator context.**
```python
with bpy.context.temp_override(active_object=obj, selected_objects=[obj]):
    bpy.ops.object.delete()
```

5. **Call `view_layer.update()` before reading transforms.** `matrix_world` is stale until the depsgraph updates.
```python
bpy.context.view_layer.update()
mat = obj.matrix_world
```

6. **Use `foreach_get`/`foreach_set` for bulk data.** 10-100x faster than Python loops.
```python
import numpy as np
coords = np.empty(len(mesh.vertices) * 3, dtype=np.float64)
mesh.vertices.foreach_get("co", coords)
```

7. **Never instantiate `bpy.types` directly.** Always use factory methods:
   - Objects: `bpy.data.objects.new(name, data)`
   - Meshes: `bpy.data.meshes.new(name)`
   - Materials: `bpy.data.materials.new(name)`
   - Nodes: `node_tree.nodes.new('ShaderNodeXxx')`

8. **Mode matters for mesh access.** Switch to OBJECT mode before accessing `mesh.vertices`; switch to EDIT mode before using `bmesh.from_edit_mesh()`.
```python
bpy.ops.object.mode_set(mode='OBJECT')
```

9. **Free BMesh when done.** Call `bm.free()` after `bm.to_mesh(mesh)`, or use `bm = bmesh.from_edit_mesh(mesh)` (no free needed, call `bmesh.update_edit_mesh(mesh)` instead).

10. **Operators return `{'FINISHED'}` or `{'CANCELLED'}`.** Always check the return value. Operators need correct context — if they fail silently, the context is probably wrong.

## Execution Context: GUI vs Headless

Blender Python scripts run in two primary contexts. **Always determine the target context before generating code that touches UI or viewport features.**

| Context | How it runs | Detection |
|---------|------------|-----------|
| **GUI** | Interactive Blender (full UI, viewports) | `bpy.app.background == False` |
| **Headless** | `blender --background --python script.py` | `bpy.app.background == True` |

**Detection snippet**:
```python
import bpy
HEADLESS = bpy.app.background
```

### Headless-compatible (works in both modes)

| Category | Operations |
|----------|-----------|
| **All `bpy.data.*`** | Creating/reading/modifying objects, meshes, materials, node trees, images, etc. |
| **`bpy.ops.render.render()`** | Full render to file (`write_still=True` or `animation=True`) |
| **Import/Export operators** | `import_scene.fbx`, `export_scene.gltf`, `wm.obj_import`, `wm.stl_export`, etc. |
| **`bpy.ops.object.*`** (most) | `delete`, `join`, `duplicate`, `convert`, `mode_set`, `modifier_add/apply`, `shade_smooth` |
| **`bpy.ops.mesh.*`** | All edit-mode mesh ops (with `temp_override`) |
| **Mesh & BMesh** | All `bpy.data.meshes`, `bmesh` operations |
| **Materials & nodes** | Creating/modifying shader nodes, node trees, materials |
| **Geometry Nodes** | Creating/modifying GN trees, NodesModifier |
| **Modifiers & constraints** | Adding, configuring, applying |
| **Handlers & timers** | `bpy.app.handlers`, `bpy.app.timers` |
| **mathutils** | `Vector`, `Matrix`, `Euler`, `Quaternion`, `BVHTree`, `KDTree` |
| **Keyframe insertion** | `obj.keyframe_insert()`, `scene.frame_set()` |
| **File ops** | `wm.save_mainfile`, `wm.open_mainfile` |

### GUI-only (fails or no-ops headless)

| Category | Operations | Why |
|----------|-----------|-----|
| **`bpy.context.area/region/screen/space_data`** | All are `None` in background | No UI areas exist |
| **`bpy.ops.view3d.*`** | `camera_to_view`, `snap_*`, `view_all`, `view_selected` | Requires active viewport |
| **`bpy.ops.screen.*`** | `animation_play`, `screenshot_area`, `frame_jump` | Requires screen context |
| **`bpy.ops.node.*`** | `add_node`, `link_make`, `group_make` | Requires node editor area |
| **`bpy.ops.render.opengl()`** | Viewport snapshot | Captures viewport buffer (doesn't exist) |
| **Interactive modal operators** | `loop_cut_and_slide`, `knife_project`, transform gizmos | Require user interaction |
| **`bpy_extras.view3d_utils`** | `region_2d_to_*`, `location_3d_to_region_2d` | Require region/rv3d |

### Headless workarounds

```python
# Instead of bpy.ops.view3d.camera_to_view(), set camera transform directly:
cam = bpy.data.objects["Camera"]
cam.location = (10, -10, 5)
cam.rotation_euler = (1.1, 0, 0.78)

# Instead of bpy.ops.render.opengl(), use full render:
bpy.ops.render.render(write_still=True)

# Instead of bpy.ops.node.add_node(), create nodes via API:
node = node_tree.nodes.new('ShaderNodeBsdfPrincipled')

# Instead of bpy.ops.node.link_make(), link via API:
node_tree.links.new(from_socket, to_socket)

# Finding a VIEW_3D area for temp_override (only works in GUI):
def get_view3d_override():
    if bpy.app.background:
        return None  # No areas in background mode
    for window in bpy.context.window_manager.windows:
        for area in window.screen.areas:
            if area.type == 'VIEW_3D':
                region = next(r for r in area.regions if r.type == 'WINDOW')
                return {"window": window, "area": area, "region": region}
    return None
```

## Quick Recipes

### Create an object with mesh data
```python
import bpy
mesh = bpy.data.meshes.new("MyMesh")
verts = [(0,0,0), (1,0,0), (1,1,0), (0,1,0)]
faces = [(0,1,2,3)]
mesh.from_pydata(verts, [], faces)
mesh.update()
obj = bpy.data.objects.new("MyObj", mesh)
bpy.context.collection.objects.link(obj)
```

### BMesh edit workflow
```python
import bpy, bmesh
bm = bmesh.new()
bm.from_mesh(obj.data)
# ... manipulate bm ...
bm.to_mesh(obj.data)
obj.data.update()
bm.free()
```

### Create a material with Principled BSDF
```python
mat = bpy.data.materials.new("MyMat")
# In Blender 5.0, use_nodes is always True (deprecated). In 4.x, call mat.use_nodes = True
nodes = mat.node_tree.nodes
bsdf = nodes.get("Principled BSDF")
bsdf.inputs["Base Color"].default_value = (0.8, 0.1, 0.1, 1.0)
bsdf.inputs["Metallic"].default_value = 0.9
bsdf.inputs["Roughness"].default_value = 0.2
obj.data.materials.append(mat)
```

### Add and configure a modifier
```python
obj = bpy.context.active_object
mod = obj.modifiers.new("MySub", 'SUBSURF')
mod.levels = 2
mod.render_levels = 3
# Apply: bpy.ops.object.modifier_apply(modifier="MySub")
```

### Add a constraint
```python
obj = bpy.context.active_object
con = obj.constraints.new('COPY_LOCATION')
con.target = bpy.data.objects["Target"]
con.influence = 0.5
```

### Register a handler
```python
import bpy
from bpy.app.handlers import persistent

@persistent
def my_handler(scene):
    print("Frame:", scene.frame_current)

def register():
    bpy.app.handlers.frame_change_post.append(my_handler)

def unregister():
    bpy.app.handlers.frame_change_post.remove(my_handler)
```

### Timer for deferred work
```python
import bpy
def my_timer():
    print("Running deferred task")
    return None  # None = don't repeat; return float = repeat interval

bpy.app.timers.register(my_timer, first_interval=0.5)
```

### Batch transform with foreach_get/set
```python
import bpy, numpy as np
mesh = bpy.context.active_object.data
n = len(mesh.vertices)
co = np.empty(n * 3, dtype=np.float64)
mesh.vertices.foreach_get("co", co)
co = co.reshape(n, 3)
co[:, 2] += 1.0  # move all vertices up by 1
mesh.vertices.foreach_set("co", co.ravel())
mesh.update()
```

### Import/Export
```python
import bpy
# Import FBX
bpy.ops.import_scene.fbx(filepath="/path/to/model.fbx")

# Export glTF
bpy.ops.export_scene.gltf(filepath="/path/to/out.glb", export_format='GLB')

# Export OBJ (Blender 4.x+)
bpy.ops.wm.obj_export(filepath="/path/to/out.obj")
```

### Keyframe insertion
```python
obj = bpy.context.active_object
obj.location = (1.0, 2.0, 3.0)
obj.keyframe_insert(data_path="location", frame=1)
obj.location = (4.0, 5.0, 6.0)
obj.keyframe_insert(data_path="location", frame=24)
```

### Context override for operators
```python
import bpy
# Select specific objects and run operator on them
with bpy.context.temp_override(
    active_object=obj,
    selected_objects=[obj, other_obj],
    object=obj
):
    bpy.ops.object.join()
```

## Blender 5.0 New Features

- **Slot-based action system**: `Action` now has layers, strips, and slots. Use `ActionSlot` to bind animation data.
- **InlineShaderNodes**: New node type for inline shader definitions.
- **NodeSocketBundle / NodeSocketClosure**: New socket types for bundled and closure-based data passing in node trees.
- **GeometryAttributeConstraint**: Constraint driven by geometry node attributes.
- **Color class color space conversions**: `Color` now supports ACES, Rec.2020, and other color space conversions.

## Key Type Hierarchies

```
bpy_struct
├── ID (has .name, .users, .use_fake_user)
│   ├── Object (has .data, .matrix_world, .modifiers, .constraints)
│   ├── Mesh (has .vertices, .edges, .polygons, .loops)
│   ├── Material (has .node_tree, .use_nodes)
│   ├── Scene (has .frame_current, .render, .world)
│   ├── Collection (has .objects, .children)
│   ├── NodeTree (has .nodes, .links)
│   ├── Action (has .layers, .slots - NEW in 5.0)
│   ├── Image, Camera, Light, Armature, Curve, ...
│   └── World, Text, Library, ...
├── Modifier (has .type, .show_viewport, .show_render)
├── Constraint (has .type, .target, .influence)
├── Node (has .inputs, .outputs, .location, .bl_idname)
├── NodeSocket (has .default_value, .is_linked)
├── NodeLink (has .from_node, .to_node, .from_socket, .to_socket)
├── Operator (has .bl_idname, .bl_label, .execute(), .invoke())
├── Panel (has .bl_idname, .bl_label, .bl_space_type, .draw())
├── PropertyGroup (for custom properties)
└── UILayout (has .row(), .column(), .prop(), .operator(), .label())
```

## Object Type → Data Block Mapping

| Object Type | `obj.type` | Data Block Type | Create With |
|-------------|-----------|-----------------|-------------|
| Mesh | `'MESH'` | `Mesh` | `bpy.data.meshes.new()` |
| Curve | `'CURVE'` | `Curve` | `bpy.data.curves.new(type='CURVE')` |
| Surface | `'SURFACE'` | `SurfaceCurve` | `bpy.data.curves.new(type='SURFACE')` |
| Text | `'FONT'` | `TextCurve` | `bpy.data.curves.new(type='FONT')` |
| Armature | `'ARMATURE'` | `Armature` | `bpy.data.armatures.new()` |
| Lattice | `'LATTICE'` | `Lattice` | `bpy.data.lattices.new()` |
| Empty | `'EMPTY'` | `None` | `bpy.data.objects.new(name, None)` |
| Camera | `'CAMERA'` | `Camera` | `bpy.data.cameras.new()` |
| Light | `'LIGHT'` | `Light` | `bpy.data.lights.new(type=...)` |

## Common Enum Values

**Object modes**: `'OBJECT'`, `'EDIT'`, `'SCULPT'`, `'VERTEX_PAINT'`, `'WEIGHT_PAINT'`, `'TEXTURE_PAINT'`, `'POSE'`

**Light types**: `'POINT'`, `'SUN'`, `'SPOT'`, `'AREA'`

**Space types**: `'VIEW_3D'`, `'PROPERTIES'`, `'OUTLINER'`, `'NODE_EDITOR'`, `'TEXT_EDITOR'`, `'IMAGE_EDITOR'`, `'GRAPH_EDITOR'`, `'DOPESHEET_EDITOR'`, `'NLA_EDITOR'`, `'SEQUENCE_EDITOR'`, `'PREFERENCES'`

**Region types**: `'WINDOW'`, `'HEADER'`, `'TOOLS'`, `'UI'`, `'TOOL_PROPS'`

**Render engines**: `'BLENDER_EEVEE_NEXT'`, `'CYCLES'`, `'BLENDER_WORKBENCH'`

**Keymap context**: `'INVOKE_DEFAULT'`, `'INVOKE_REGION_WIN'`, `'EXEC_DEFAULT'`
