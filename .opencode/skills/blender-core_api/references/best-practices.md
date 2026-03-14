# Best Practices

Concise reference for writing efficient, correct Blender Python scripts.

## Key Principles

1. **Access data via `bpy.data`, not by instantiating types** -- Blender owns all data-blocks.
2. **Context is read-only** -- use `bpy.data` or API functions to change state.
3. **Use `temp_override`** to run operators outside their normal context.
4. **Use `foreach_get`/`foreach_set`** for bulk property access -- orders of magnitude faster than loops.
5. **Register classes before referencing them** in properties; unregister in reverse order.
6. **Avoid `bpy.context` at import time** -- it is not yet available during module loading.
7. **Keep operator `execute()` thin** -- delegate logic to plain utility functions.
8. **Use list comprehensions** over manual loops for filtering Blender collections.
9. **Time your code** during development to catch performance regressions early.

## Table of Contents

- [Data Access Patterns](#data-access-patterns)
  - [Accessing Data-Blocks](#accessing-data-blocks)
  - [Creating and Removing Data](#creating-and-removing-data)
  - [Custom Properties](#custom-properties)
  - [Context vs Data](#context-vs-data)
- [Context Override (temp_override)](#context-override-temp_override)
  - [Why Operators Need Context](#why-operators-need-context)
  - [Using temp_override](#using-temp_override)
- [Performance](#performance)
  - [foreach_get / foreach_set](#foreach_get--foreach_set)
  - [Dependency Graph (depsgraph)](#dependency-graph-depsgraph)
  - [List Manipulation](#list-manipulation)
  - [String Operations](#string-operations)
  - [Error Handling in Loops](#error-handling-in-loops)
  - [Timing Your Code](#timing-your-code)
- [Script Organization](#script-organization)
  - [Module vs Direct Execution](#module-vs-direct-execution)
  - [Style Conventions](#style-conventions)
  - [Enum vs String Quoting](#enum-vs-string-quoting)
- [Registration Patterns](#registration-patterns)
  - [Module Registration](#module-registration)
  - [Class Registration Order](#class-registration-order)
  - [Property Groups with Dependencies](#property-groups-with-dependencies)
  - [Dynamic Class Definition](#dynamic-class-definition)

---

## Data Access Patterns

### Accessing Data-Blocks

All Blender data lives in `bpy.data`. You cannot create data outside this database. Access collections by name (stable) or index (may change).

**Why it matters:** Blender manages data lifetime (save, load, undo). Accessing by name is reliable across sessions; indices shift when objects are added/removed.

```python
import bpy

# Access by name (preferred -- stable across operations)
cube = bpy.data.objects["Cube"]

# Access by index (fragile -- order can change)
first_obj = bpy.data.objects[0]

# Iterate all meshes
for mesh in bpy.data.meshes:
    print(mesh.name)
```

### Creating and Removing Data

You cannot instantiate Blender types directly (`bpy.types.Mesh()` raises `TypeError`). Use collection methods instead.

**Why it matters:** Blender must track all data for undo, save/load, and memory management.

```python
import bpy

# Create
mesh = bpy.data.meshes.new(name="MyMesh")
obj = bpy.data.objects.new("MyObj", mesh)
bpy.context.collection.objects.link(obj)

# Remove
bpy.data.objects.remove(obj)
bpy.data.meshes.remove(mesh)
```

### Custom Properties

Any ID data-block supports arbitrary custom properties (int, float, string, dict, arrays).

**Why it matters:** Custom properties persist in .blend files, can be animated with keyframes, and work in driver expressions.

```python
import bpy

obj = bpy.context.object
obj["my_prop"] = 42
obj["settings"] = {"speed": 1.5, "label": "fast"}

# Safe access with fallback
val = obj.get("missing_key", "default_value")

# Clean up
del obj["my_prop"]
```

### Context vs Data

`bpy.context` gives the current user state (active object, selection, mode). It is **read-only** -- you cannot assign to it directly.

**Why it matters:** Scripts that depend on context break when run from the wrong editor or mode. Prefer `bpy.data` for direct access when possible.

```python
import bpy

# WRONG -- raises AttributeError
# bpy.context.active_object = some_obj

# CORRECT -- set active through view layer
bpy.context.view_layer.objects.active = bpy.data.objects["Cube"]

# Read selection (read-only convenience)
selected = bpy.context.selected_objects
```

---

## Context Override (temp_override)

### Why Operators Need Context

Operators (`bpy.ops.*`) check a `poll()` function before running. If the context is wrong (wrong mode, wrong editor area), the operator raises `RuntimeError`.

**Why it matters:** Scripts that call operators from timers, background tasks, or non-3D-Viewport contexts will fail without a context override.

```python
import bpy

# Check poll before calling to avoid exceptions
if bpy.ops.view3d.render_border.poll():
    bpy.ops.view3d.render_border()
```

### Using temp_override

`context.temp_override()` lets you run operators with a substituted context. This is the modern replacement for the deprecated dictionary override.

**Why it matters:** Allows calling viewport operators from scripts running outside the 3D Viewport, or operating on a specific object/area.

```python
import bpy

# Override the active object for an operator call
obj = bpy.data.objects["Cube"]
with bpy.context.temp_override(active_object=obj):
    bpy.ops.object.transform_apply(
        location=True, rotation=True, scale=True
    )
```

```python
import bpy

# Override to target a specific 3D Viewport area
for area in bpy.context.screen.areas:
    if area.type == 'VIEW_3D':
        with bpy.context.temp_override(area=area):
            bpy.ops.view3d.camera_to_view()
        break
```

---

## Performance

### foreach_get / foreach_set

`foreach_get` and `foreach_set` transfer bulk data between Blender C arrays and flat Python/NumPy arrays in a single call.

**Why it matters:** Looping over thousands of vertices in Python is 10-100x slower than a single `foreach_get` call because it avoids per-element Python-to-C overhead.

```python
import bpy
import numpy as np

mesh = bpy.context.object.data
n = len(mesh.vertices)

# Fast: read all vertex positions into a NumPy array
coords = np.empty(n * 3, dtype=np.float64)
mesh.vertices.foreach_get("co", coords)
coords = coords.reshape(n, 3)

# Modify and write back
coords[:, 2] += 0.5  # shift Z
mesh.vertices.foreach_set("co", coords.ravel())
mesh.update()
```

### Dependency Graph (depsgraph)

The dependency graph (`depsgraph`) provides evaluated (final) object data after modifiers, constraints, and drivers.

**Why it matters:** Reading `object.data` gives the original mesh. To get the mesh after a Subdivision Surface or Array modifier, you must use the evaluated object.

```python
import bpy

depsgraph = bpy.context.evaluated_depsgraph_get()
obj = bpy.context.object
obj_eval = obj.evaluated_get(depsgraph)
mesh_eval = obj_eval.to_mesh()

print(f"Evaluated verts: {len(mesh_eval.vertices)}")

# Clean up temporary mesh
obj_eval.to_mesh_clear()
```

### List Manipulation

Prefer list comprehensions over in-place removal loops. Avoid `list.remove()` (searches entire list) -- use `list.pop(index)` when you must remove by position.

**Why it matters:** `list.remove()` is O(n) per call. Rebuilding a list via comprehension is faster and clearer for filtering.

```python
import bpy

mesh = bpy.context.object.data

# SLOW: remove triangles one by one
# for p in reversed(mesh.polygons):
#     if len(p.vertices) == 3: ...

# FAST: build filtered list with comprehension
quads_and_ngons = [
    p for p in mesh.polygons if len(p.vertices) != 3
]
```

### String Operations

Use `str.join()` or format strings instead of concatenation (`+`) in loops. Use `startswith()`/`endswith()` instead of slicing.

**Why it matters:** String concatenation in a loop creates a new string object every iteration. `join()` allocates once.

```python
# SLOW
output = ""
for name in names:
    output += name + "\n"

# FAST
output = "\n".join(names)

# Prefer startswith over slicing
if line.startswith("vert "):
    process(line)
```

### Error Handling in Loops

Avoid `try/except` inside tight loops. Use `if` checks instead.

**Why it matters:** Python sets up an exception frame for every `try` block. In a loop running thousands of times, the overhead is significant.

```python
# SLOW in a hot loop
for item in large_list:
    try:
        val = item.some_attr
    except AttributeError:
        val = None

# FAST
for item in large_list:
    val = getattr(item, "some_attr", None)
```

### Timing Your Code

Wrap sections with `time.time()` to catch performance regressions during development.

**Why it matters:** Small changes can cause large slowdowns in Blender scripts that process thousands of data-blocks.

```python
import time

start = time.time()

# ... your code ...

print(f"Elapsed: {time.time() - start:.4f} sec")
```

---

## Script Organization

### Module vs Direct Execution

Prefer importing scripts as modules over direct execution. When scripts are imported, their classes remain accessible via the module, making unregistration straightforward.

**Why it matters:** Directly executed scripts leave classes in Blender with no module reference, making cleanup and reloading difficult.

```python
# At the bottom of your module:
if __name__ == "__main__":
    register()
# This lets the script work both as a module (import)
# and when run directly in the text editor.
```

### Style Conventions

Follow PEP 8 with Blender-specific additions:

- `PascalCase` for classes, `snake_case` for functions/variables
- 4-space indentation, no tabs
- Explicit imports only (no wildcard `*`)
- Prefix Blender class attributes with `bl_`

### Enum vs String Quoting

Use **single quotes** for Blender enum values and **double quotes** for user-facing strings. This is a Blender convention that distinguishes fixed API identifiers from free-form text.

**Why it matters:** Consistency across the codebase makes scripts easier to read and review.

```python
import bpy

# Single quotes for enums (fixed API values)
bpy.context.scene.render.image_settings.file_format = 'PNG'

# Double quotes for strings (user-facing text)
bpy.context.scene.render.filepath = "//render_output"
```

---

## Registration Patterns

### Module Registration

Every Blender module must define `register()` and `unregister()` functions. These are the only entry points Blender calls.

**Why it matters:** Registration at import time makes it impossible to distinguish "import for code reuse" from "load into Blender." Explicit register/unregister enables toggling addons and reloading scripts at runtime.

```python
import bpy

class MY_OT_example(bpy.types.Operator):
    bl_idname = "my.example"
    bl_label = "Example"

    def execute(self, context):
        return {'FINISHED'}

def register():
    bpy.utils.register_class(MY_OT_example)

def unregister():
    bpy.utils.unregister_class(MY_OT_example)
```

### Class Registration Order

Register dependency classes (PropertyGroups) **before** the classes that reference them. Unregister in **reverse** order.

**Why it matters:** A `PointerProperty(type=MyGroup)` fails if `MyGroup` is not yet registered. Reverse unregistration avoids dangling references.

```python
import bpy

class SubProps(bpy.types.PropertyGroup):
    value: bpy.props.FloatProperty()

class MainProps(bpy.types.PropertyGroup):
    sub: bpy.props.PointerProperty(type=SubProps)

def register():
    bpy.utils.register_class(SubProps)       # dependency first
    bpy.utils.register_class(MainProps)
    bpy.types.Object.my_props = bpy.props.PointerProperty(type=MainProps)

def unregister():
    del bpy.types.Object.my_props            # mirror order
    bpy.utils.unregister_class(MainProps)
    bpy.utils.unregister_class(SubProps)
```

### Property Groups with Dependencies

Attach custom property groups to existing Blender types via `PointerProperty` in `register()` and clean up with `del` in `unregister()`.

**Why it matters:** Leaking registered properties pollutes the Blender type system and can cause crashes or data corruption on reload.

```python
import bpy

class MatSettings(bpy.types.PropertyGroup):
    roughness: bpy.props.FloatProperty(default=0.5)

def register():
    bpy.utils.register_class(MatSettings)
    bpy.types.Material.my_settings = bpy.props.PointerProperty(
        type=MatSettings
    )

def unregister():
    del bpy.types.Material.my_settings
    bpy.utils.unregister_class(MatSettings)
```

### Dynamic Class Definition

Use Python's `type()` builtin to create operator classes at runtime when the set of operators is data-driven.

**Why it matters:** Useful for plugin systems or external shader definitions where the number of operators is not known at code-writing time.

```python
import bpy

def make_operator(index):
    def execute(self, context):
        print(f"Running operator {index}")
        return {'FINISHED'}

    return type(
        f"DynOp{index}",
        (bpy.types.Operator,),
        {
            "bl_idname": f"object.dyn_op_{index}",
            "bl_label": f"Dynamic Op {index}",
            "execute": execute,
        },
    )

# Register a batch of dynamic operators
for i in range(5):
    bpy.utils.register_class(make_operator(i))
```

---

## Quick Reference Table

| Anti-Pattern | Best Practice |
|---|---|
| `bpy.types.Mesh()` | `bpy.data.meshes.new("Name")` |
| `bpy.context.active_object = obj` | `bpy.context.view_layer.objects.active = obj` |
| Loop over vertices with `for v in mesh.vertices` | `mesh.vertices.foreach_get("co", flat_array)` |
| `bpy.ops.x()` from wrong context | `with bpy.context.temp_override(area=area):` |
| `try/except` in tight loops | `if` checks or `getattr(obj, attr, default)` |
| String concatenation in loops | `"\n".join(items)` |
| Wildcard imports `from bpy import *` | `import bpy` (explicit) |
| Register at module level | Register inside `register()` function |
| `eval(string)` for number parsing | `float(string)` or `int(string)` |
