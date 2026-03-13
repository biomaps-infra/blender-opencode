# Gotchas and Pitfalls

## Table of Contents

- [Quick Rules](#quick-rules)
- [Stale References & Crashes](#stale-references--crashes)
  - [Collection Re-Allocation](#collection-re-allocation)
  - [Undo/Redo Invalidation](#undoredo-invalidation)
  - [Mode Switching Invalidation](#mode-switching-invalidation)
  - [Array Re-Allocation](#array-re-allocation)
  - [Removing Data](#removing-data)
  - [Collection Iteration Corner Case](#collection-iteration-corner-case)
  - [Data-Block Renaming During Iteration](#data-block-renaming-during-iteration)
- [Stale Data & Deferred Updates](#stale-data--deferred-updates)
  - [Values Not Updated After Setting](#values-not-updated-after-setting)
  - [Data Names May Not Match](#data-names-may-not-match)
  - [Library Name Collisions](#library-name-collisions)
- [Threading](#threading)
- [Operators](#operators)
  - [Poll Failures](#poll-failures)
  - [Operator Limitations](#operator-limitations)
- [Mesh & Mode Access](#mesh--mode-access)
  - [Edit-Mode Data Sync](#edit-mode-data-sync)
  - [Face Access: Polygons vs Loop Triangles vs BMesh](#face-access-polygons-vs-loop-triangles-vs-bmesh)
- [Armatures & Bones](#armatures--bones)
  - [Three Bone Types](#three-bone-types)
  - [Mode Switching With Bones](#mode-switching-with-bones)
- [Headless / Background Mode](#headless--background-mode)
- [File Paths & Encoding](#file-paths--encoding)
  - [Relative Paths](#relative-paths)
  - [Unicode Encoding](#unicode-encoding)

---

## Quick Rules

1. **Never keep references** to Blender data across container modifications, mode switches, or undo/redo. Re-fetch after any mutation.
2. **Use indices or names** (stored by value) instead of direct object references when data may be re-allocated.
3. **Call `view_layer.update()`** after setting properties if you need to read derived values immediately.
4. **Never use Python threads** that outlive the calling script. Use `multiprocessing` for background work.
5. **Always `join()` threads** before returning control to Blender.
6. **Operators need correct context.** Use `bpy.context.temp_override()` when calling operators from scripts.
7. **Edit-Mode mesh data is separate** from `obj.data`. Exit Edit-Mode or use `bmesh.from_edit_mesh()` to access current state.
8. **Three bone types exist**: `EditBone` (Edit-Mode only), `Bone` (read-only transforms), `PoseBone` (animation/constraints). Use the right one.
9. **Convert `//` paths** with `bpy.path.abspath()` before passing to Python's `os`/`sys` modules.
10. **All Blender strings must be UTF-8.** Use `os.fsencode()`/`os.fsdecode()` for file-system paths.
11. **Snapshot iterators** with `[:]` before modifying items that invalidate the iterator.
12. **Never call `sys.exit()`** from addon code — it kills Blender instantly.

---

## Stale References & Crashes

The #1 cause of crashes from Python: holding a reference to Blender data after the underlying C memory has been freed or re-allocated.

### Collection Re-Allocation

Adding items to a collection can re-allocate the entire container, invalidating all existing references.

```python
# WRONG — first_item may point to freed memory
first_item = bpy.context.scene.test_items.add()
for i in range(100):
    bpy.context.scene.test_items.add()
first_item.name = "foobar"  # CRASH
```

```python
# CORRECT — re-fetch after all additions
bpy.context.scene.test_items.add()
for i in range(100):
    bpy.context.scene.test_items.add()
first_item = bpy.context.scene.test_items[0]
first_item.name = "foobar"
```

### Undo/Redo Invalidation

All `bpy.types.ID` instances (Object, Mesh, Scene, etc.) and their sub-data become invalid after undo/redo.

```python
# WRONG — storing a reference across undo
obj = bpy.context.active_object
# ... user performs undo ...
obj.location.x = 1.0  # CRASH or stale data
```

```python
# CORRECT — re-fetch from context after undo
obj = bpy.context.active_object  # always re-fetch
obj.location.x = 1.0
```

**Rule:** In modal operators, re-acquire all data references each time `modal()` is called.

### Mode Switching Invalidation

Switching between Object/Edit mode re-allocates mesh, armature, and curve sub-data.

```python
# WRONG — polygons reference invalid after mode switch
mesh = bpy.context.active_object.data
polygons = mesh.polygons
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.object.mode_set(mode='OBJECT')
print(polygons)  # CRASH
```

```python
# CORRECT — re-fetch sub-data after mode switch
mesh = bpy.context.active_object.data
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.object.mode_set(mode='OBJECT')
polygons = mesh.polygons  # re-fetch
print(polygons)
```

### Array Re-Allocation

Adding points/vertices/edges to existing data re-allocates the underlying array.

```python
# WRONG — point reference stale after add
point = bpy.context.object.data.splines[0].bezier_points[0]
bpy.context.object.data.splines[0].bezier_points.add()
point.co = (1.0, 2.0, 3.0)  # CRASH
```

```python
# CORRECT — add all points at once, or re-fetch after add
spline = bpy.context.object.data.splines[0]
spline.bezier_points.add()
point = spline.bezier_points[0]  # re-fetch
point.co = (1.0, 2.0, 3.0)
```

### Removing Data

After calling `remove()`, the Python wrapper is invalidated. But sub-data references are NOT invalidated.

```python
# WRONG — accessing sub-data of removed mesh
mesh = bpy.data.meshes.new(name="MyMesh")
vertices = mesh.vertices
bpy.data.meshes.remove(mesh)
print(vertices)  # may CRASH (sub-ref not invalidated)
```

```python
# CORRECT — don't access any references after removal
mesh = bpy.data.meshes.new(name="MyMesh")
bpy.data.meshes.remove(mesh)
# mesh.name → raises ReferenceError (safe)
# but sub-data refs like vertices are NOT safe
```

### Collection Iteration Corner Case

Changing `hide_viewport`, `hide_select`, or `hide_render` rebuilds collection caches, breaking active iterators.

```python
# WRONG — modifying during iteration
for obj in bpy.data.collections["Col"].all_objects:
    obj.hide_viewport = True  # CRASH
```

```python
# CORRECT — snapshot to list first
for obj in bpy.data.collections["Col"].all_objects[:]:
    obj.hide_viewport = True
```

### Data-Block Renaming During Iteration

Setting `.name` on data-blocks triggers a re-sort of `bpy.data` collections. Convert iterator to list first.

```python
# WRONG — renaming re-sorts the collection mid-iteration
for obj in bpy.data.objects:
    obj.name = "prefix_" + obj.name  # skips/duplicates

# CORRECT — snapshot first
for obj in list(bpy.data.objects):
    obj.name = "prefix_" + obj.name
```

---

## Stale Data & Deferred Updates

### Values Not Updated After Setting

Blender defers dependency graph evaluation. Setting `location` does not immediately update `matrix_world`.

```python
# WRONG — matrix_world is stale
bpy.context.object.location = (1, 2, 3)
print(bpy.context.object.matrix_world)  # old value
```

```python
# CORRECT — force update
bpy.context.object.location = (1, 2, 3)
bpy.context.view_layer.update()
print(bpy.context.object.matrix_world)  # updated
```

### Data Names May Not Match

Blender may rename data if the name is taken, too long, or empty. Never assume the assigned name stuck.

```python
# WRONG — name may have been modified
bpy.data.meshes.new(name=meshid)
mesh = bpy.data.meshes[meshid]  # KeyError if renamed
```

```python
# CORRECT — store the returned reference
mesh = bpy.data.meshes.new(name=meshid)
# use mesh directly, or keep a mapping:
mesh_map = {}
mesh_map[meshid] = mesh
```

### Library Name Collisions

Local and linked library data can share names. Use tuple lookups to disambiguate.

```python
# Ambiguous — could be local or library
obj = bpy.data.objects["my_obj"]

# Explicit local-only lookup
obj = bpy.data.objects["my_obj", None]

# Explicit library lookup
obj = bpy.data.objects["my_obj", "//my_lib.blend"]
```

---

## Threading

**Python threads are not supported** in Blender's Python integration. Threads that outlive the script cause random crashes.

```python
# WRONG — daemon thread runs after script ends
from threading import Timer

def my_timer():
    t = Timer(0.1, my_timer)
    t.setDaemon(True)
    t.start()
my_timer()  # will eventually crash Blender
```

```python
# CORRECT — threads must join before script returns
import threading

def work(url):
    print(f"Downloading {url}")

threads = [threading.Thread(target=work, args=(u,))
           for u in urls]
for t in threads:
    t.start()
for t in threads:
    t.join()  # block until all done
# Now Blender can safely continue
```

**Alternative:** Use the `multiprocessing` module for true background work independent of Blender.

**Warning:** Some stdlib modules (e.g., `multiprocessing.Queue`) create threads internally.

---

## Operators

### Poll Failures

Operators check context via `poll()` before running. A failed poll raises `RuntimeError`.

```python
# This fails if context is wrong
>>> bpy.ops.action.clean(threshold=0.001)
RuntimeError: Operator bpy.ops.action.clean.poll() failed
```

**How to debug:** Look at how the operator is used in Blender's UI, check what area/mode/selection it expects, or read the operator's `poll()` source.

### Operator Limitations

- Operators use **context**, not arguments, to find data — you can't pass objects directly.
- Return value is only success/cancel status, not the result data.
- Some operators only work in specific editors (Properties, Outliner, etc.).

Use `bpy.context.temp_override()` to set the required context:

```python
# Override context for an operator that needs a specific area
with bpy.context.temp_override(area=target_area):
    bpy.ops.screen.area_split(direction='VERTICAL')
```

**Prefer direct API calls** (`bpy.data`, `bmesh`, etc.) over operators when possible — they are faster, more predictable, and don't depend on UI context.

---

## Mesh & Mode Access

### Edit-Mode Data Sync

In Edit-Mode, `obj.data` (the Mesh) is **out of sync** with the actual edit-mesh. Accessing `mesh.vertices` returns stale data.

```python
# WRONG — reading mesh data while in Edit-Mode
bpy.ops.object.mode_set(mode='EDIT')
verts = bpy.context.object.data.vertices  # stale!
```

**Solutions (pick one):**

```python
# Option 1: Exit Edit-Mode first
bpy.ops.object.mode_set(mode='OBJECT')
verts = bpy.context.object.data.vertices

# Option 2: Use bmesh for edit-mode access
import bmesh
bm = bmesh.from_edit_mesh(bpy.context.object.data)
for v in bm.verts:
    print(v.co)
```

### Face Access: Polygons vs Loop Triangles vs BMesh

| Purpose | `mesh.polygons` | `mesh.loop_triangles` | `bmesh.types.BMFace` |
|---------|------------------|-----------------------|----------------------|
| **Create** | Rigid, all-at-once | Read-only | Best — add one by one |
| **Edit** | Very limited | Don't use | Best |
| **Export** | Good (n-gon) | Good (tri-only formats) | Good (extra overhead) |

**Rule of thumb:** Use `bmesh` for creation/manipulation, `mesh.polygons` for export, `mesh.loop_triangles` only when you need triangulated output.

---

## Armatures & Bones

### Three Bone Types

Blender has **three separate bone data structures**. Using the wrong one is a common source of confusion.

| Type | Access | Mode | Use For |
|------|--------|------|---------|
| `EditBone` | `armature.data.edit_bones` | Edit-Mode only | Create bones, set head/tail/roll, parenting |
| `Bone` | `armature.data.bones` | Object/Pose-Mode | Read transforms (read-only head/tail), toggle `use_deform` |
| `PoseBone` | `armature.pose.bones` | Object/Pose-Mode | Animation, constraints, IK settings |

```python
# EditBone — only in Edit-Mode
bpy.ops.object.mode_set(mode='EDIT')
edit_bone = obj.data.edit_bones["Bone"]
edit_bone.head = (1.0, 2.0, 3.0)  # writable

# Bone — Object/Pose-Mode (head/tail read-only)
bpy.ops.object.mode_set(mode='OBJECT')
bone = obj.data.bones["Bone"]
bone.use_deform = True
tail = bone.tail  # read-only

# PoseBone — animation data, constraints
pose_bone = obj.pose.bones["Bone"]
constraint_name = pose_bone.constraints[0].name
```

**Note:** Pose is on the **Object**, not the Armature — this allows multiple objects to share one armature with different poses.

### Mode Switching With Bones

**Never keep references to edit bones after leaving Edit-Mode.** They point to freed memory.

```python
# WRONG
bpy.ops.object.mode_set(mode='EDIT')
eb = obj.data.edit_bones["Bone"]
bpy.ops.object.mode_set(mode='OBJECT')
print(eb.head)  # CRASH
```

```python
# CORRECT — access edit bones only while in Edit-Mode
bpy.ops.object.mode_set(mode='EDIT')
head = obj.data.edit_bones["Bone"].head.copy()
bpy.ops.object.mode_set(mode='OBJECT')
print(head)  # safe — it's a copy
```

---

## Headless / Background Mode

Running Blender with `--background` or `--background --python script.py` disables the UI. Several API surfaces are unavailable.

### `bpy.context.area` and friends are None

**Cause**: In background mode, there are no windows, screens, or areas. `bpy.context.area`, `bpy.context.region`, `bpy.context.screen`, and `bpy.context.space_data` are all `None`.

**Impact**: Any operator that requires a specific area type (`VIEW_3D`, `NODE_EDITOR`, etc.) will fail with `RuntimeError: Operator poll() failed` because there's no area to provide context.

**Fix**: Use direct API calls instead of operators:
```python
# WRONG headless — no NODE_EDITOR area
bpy.ops.node.add_node(type='ShaderNodeBsdfPrincipled')

# CORRECT headless — direct API
node = mat.node_tree.nodes.new('ShaderNodeBsdfPrincipled')
```

### `render.opengl()` requires a viewport

**Cause**: `bpy.ops.render.opengl()` captures the viewport's framebuffer. No viewport exists in background mode.

**Fix**: Use `bpy.ops.render.render(write_still=True)` for full engine renders (works headless).

### `bpy_extras.view3d_utils` functions fail

**Cause**: Functions like `region_2d_to_vector_3d()`, `region_2d_to_location_3d()`, and `location_3d_to_region_2d()` require `region` and `rv3d` parameters, which are `None` headless.

**Fix**: These have no headless equivalent. Compute projections manually using camera matrices and `mathutils` if needed.

### Interactive modal operators are no-ops

Operators like `bpy.ops.mesh.loop_cut_and_slide()`, `bpy.ops.mesh.knife_project()`, and transform gizmo operators require mouse/keyboard interaction. They cannot run headless.

**Fix**: Use the equivalent non-interactive operations:
```python
# Instead of loop_cut_and_slide (interactive):
bm = bmesh.from_edit_mesh(obj.data)
bmesh.ops.bisect_edges(bm, edges=edges, cuts=1)

# Instead of knife_project (interactive):
# Use bmesh.ops.bisect_plane() or geometry math
```

### Detection pattern

```python
import bpy
if bpy.app.background:
    # Headless mode — avoid viewport ops, use direct API
    pass
```

---

## File Paths & Encoding

### Relative Paths

Blender uses `//` prefix for blend-file-relative paths. Python's `os.path` does not understand this.

```python
# WRONG — Python doesn't understand //
import os
path = os.path.exists(image.filepath)  # fails for // paths
```

```python
# CORRECT — convert first
abs_path = bpy.path.abspath(image.filepath)
os.path.exists(abs_path)

# For linked library data, pass the library
abs_path = bpy.path.abspath(
    image.filepath, library=image.library
)
```

### Unicode Encoding

All Blender strings must be UTF-8. File-system paths may contain non-UTF-8 characters.

```python
# WRONG — may raise UnicodeEncodeError
print(bpy.data.filepath)
```

```python
# CORRECT — use repr() for display
print(repr(bpy.data.filepath))

# CORRECT — convert for assignment to Blender properties
import os
filepath_bytes = os.fsencode(bpy.data.filepath)
filepath_utf8 = filepath_bytes.decode('utf-8', 'replace')
bpy.context.object.name = filepath_utf8
```

**Rules:**
- Always use UTF-8 or convert unknown input to UTF-8
- Use `os.path` functions instead of string manipulation for paths
- Use `os.fsencode()`/`os.fsdecode()` for path encoding
- Use `repr(path)` when displaying paths in UI or console

---

## Cross-References

For MolecularNodes-specific gotchas (invisible molecules, selection confusion, density file issues), see `molecular-nodes/references/gotchas.md`.
