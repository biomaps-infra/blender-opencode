# Handlers and Timers Reference

## Table of Contents

- [Handler System Overview](#handler-system-overview)
- [All Handler Lists](#all-handler-lists)
- [The @persistent Decorator](#the-persistent-decorator)
- [Handler Registration Pattern](#handler-registration-pattern)
- [Timer System](#timer-system)
- [Timer Return Values](#timer-return-values)
- [bpy.app Key Attributes](#bypapp-key-attributes)
- [Common Patterns](#common-patterns)

---

## Handler System Overview

`bpy.app.handlers` provides callback lists that fire at specific application events. Each handler list is a Python `list`; append a function to subscribe, remove it to unsubscribe. Handler functions receive arguments depending on the event (typically the scene and/or depsgraph).

**Key rules:**
- Handlers are **cleared when a new file is loaded** unless marked `@persistent`.
- During rendering, `frame_change_pre/post` run on a **separate thread** from the viewport. Lock the interface (`RenderSettings.use_lock_interface`) if a handler modifies viewport data.
- Never access `bpy.context` in ways that assume a specific UI state inside handlers.

---

## All Handler Lists

### Animation & Playback

| Handler | Fires when |
|---|---|
| `animation_playback_pre` | Starting animation playback. Args: (scene, depsgraph) |
| `animation_playback_post` | Ending animation playback. Args: (scene, depsgraph) |
| `frame_change_pre` | After frame change, **before** data is evaluated for the new frame. Args: (scene, depsgraph) |
| `frame_change_post` | After frame change, **after** data has been evaluated for the new frame. Args: (scene, depsgraph) |

### Dependency Graph

| Handler | Fires when |
|---|---|
| `depsgraph_update_pre` | Before depsgraph evaluation. Args: (scene, depsgraph) |
| `depsgraph_update_post` | After depsgraph evaluation. Args: (scene, depsgraph) |

### File Load

| Handler | Fires when |
|---|---|
| `load_pre` | Before loading a blend file. Args: (filepath,) |
| `load_post` | After loading a blend file. Args: (filepath,) |
| `load_post_fail` | After failing to load a blend file. Args: (filepath,) |
| `load_factory_startup_post` | After loading factory startup |
| `load_factory_preferences_post` | After loading factory preferences |

### File Save

| Handler | Fires when |
|---|---|
| `save_pre` | Before saving a blend file. Args: (filepath,) |
| `save_post` | After saving a blend file. Args: (filepath,) |
| `save_post_fail` | After failing to save a blend file. Args: (filepath,) |

### Render

| Handler | Fires when |
|---|---|
| `render_init` | On initialization of a render job. Args: (scene,) |
| `render_pre` | Before a render |
| `render_post` | After a render |
| `render_complete` | On completion of a render job. Args: (scene,) |
| `render_cancel` | On cancellation of a render job. Args: (scene,) |
| `render_write` | Directly after writing a render frame |
| `render_stats` | On printing render statistics. Args: (stats_string,) |

### Compositing

| Handler | Fires when |
|---|---|
| `composite_pre` | Before a compositing background job. Args: (scene,) |
| `composite_post` | After a compositing background job. Args: (scene,) |
| `composite_cancel` | On cancelling a compositing background job. Args: (scene,) |

### Undo / Redo

| Handler | Fires when |
|---|---|
| `undo_pre` | Before loading an undo step |
| `undo_post` | After loading an undo step |
| `redo_pre` | Before loading a redo step |
| `redo_post` | After loading a redo step |

### Bake

| Handler | Fires when |
|---|---|
| `object_bake_pre` | Before starting a bake job. Args: (object,) |
| `object_bake_complete` | On completing a bake job. Args: (object,) |
| `object_bake_cancel` | On cancelling a bake job. Args: (object,) |

### Other

| Handler | Fires when |
|---|---|
| `annotation_pre` | Before drawing an annotation. Args: (annotation, depsgraph) |
| `annotation_post` | After drawing an annotation. Args: (annotation, depsgraph) |
| `blend_import_pre` | Before linking/appending data. Args: (BlendImportContext,) |
| `blend_import_post` | After linking/appending data. Args: (BlendImportContext,) |
| `translation_update_post` | On translation settings update |
| `version_update` | On ending versioning code |
| `xr_session_start_pre` | Before starting an XR session |

---

## The @persistent Decorator

By default, all handlers are **removed** when a new blend file is loaded. Use `@persistent` to keep a handler active across file loads. This is essential for addon handlers.

```python
from bpy.app.handlers import persistent

@persistent
def my_load_handler(dummy):
    print("File loaded:", bpy.data.filepath)

# Without @persistent, this handler would be removed on File > Open
bpy.app.handlers.load_post.append(my_load_handler)
```

**When to use:** Always use `@persistent` for handlers registered by addons. Omit it only for handlers meant to be file-specific (e.g., registered by a script inside a blend file).

---

## Handler Registration Pattern

Register handlers in `register()` and unregister in `unregister()` to follow addon conventions. Always guard against duplicate registration.

```python
import bpy
from bpy.app.handlers import persistent

@persistent
def on_frame_change(scene, depsgraph):
    obj = scene.objects.get("Cube")
    if obj:
        obj.location.z = scene.frame_current * 0.1

def register():
    bpy.app.handlers.frame_change_post.append(on_frame_change)

def unregister():
    if on_frame_change in bpy.app.handlers.frame_change_post:
        bpy.app.handlers.frame_change_post.remove(on_frame_change)
```

**Handler function signatures vary by event:**
- Most animation/depsgraph handlers: `def handler(scene, depsgraph)`
- File load/save handlers: `def handler(filepath)`
- Render handlers: `def handler(scene)` (some take no args)
- Undo/redo handlers: `def handler(scene)` (no documented args)

---

## Timer System

`bpy.app.timers` runs deferred or periodic functions on the main thread.

### bpy.app.timers.register

```python
bpy.app.timers.register(function, *, first_interval=0, persistent=False)
```

| Parameter | Type | Description |
|---|---|---|
| `function` | `Callable[[], float \| None]` | Function to call (no arguments) |
| `first_interval` | `float` | Seconds before first call (default: 0 = next evaluation) |
| `persistent` | `bool` | Survive file loads (default: False) |

### bpy.app.timers.unregister

```python
bpy.app.timers.unregister(function)
```

Removes the timer. Raises `ValueError` if not registered.

### bpy.app.timers.is_registered

```python
bpy.app.timers.is_registered(function) -> bool
```

Returns `True` if the function is currently registered as a timer.

---

## Timer Return Values

The registered function must return `float` or `None`:

| Return value | Behavior |
|---|---|
| `None` | Timer stops (unregistered automatically) |
| `float` (e.g. `2.0`) | Timer fires again after that many seconds |

```python
import bpy

def repeating_task():
    print("Tick")
    return 1.0  # repeat every 1 second

bpy.app.timers.register(repeating_task)
```

```python
import bpy

def one_shot():
    print("Runs once after 3 seconds")
    return None  # stops the timer

bpy.app.timers.register(one_shot, first_interval=3.0)
```

Use `functools.partial` to pass arguments to timer functions:

```python
import bpy, functools

def greet(name):
    print(f"Hello, {name}")

bpy.app.timers.register(functools.partial(greet, "World"), first_interval=1.0)
```

---

## bpy.app Key Attributes

| Attribute | Type | Description |
|---|---|---|
| `bpy.app.version` | `tuple[int,int,int]` | Blender version, e.g. `(4, 3, 1)` |
| `bpy.app.version_string` | `str` | Version formatted as string |
| `bpy.app.version_file` | `tuple[int,int,int]` | File format version (for compatibility checks) |
| `bpy.app.version_cycle` | `str` | Release status: `alpha`, `beta`, `rc`, `release` |
| `bpy.app.binary_path` | `str` | Path to the Blender executable |
| `bpy.app.background` | `bool` | `True` when running with `-b` (no UI) |
| `bpy.app.factory_startup` | `bool` | `True` when running with `--factory-startup` |
| `bpy.app.debug` | `bool` | `True` when started with `--debug` |
| `bpy.app.tempdir` | `str` | Blender's temp directory |
| `bpy.app.driver_namespace` | `dict` | Namespace dict for drivers (reset on file load) |
| `bpy.app.online_access` | `bool` | Whether internet access is allowed |

### Utility Methods

- `bpy.app.is_job_running(job_type: str) -> bool` — check if a background job is active
- `bpy.app.memory_usage_undo() -> int` — undo stack memory usage in bytes

---

## Common Patterns

### Auto-save Reminder on File Change

```python
import bpy
from bpy.app.handlers import persistent

@persistent
def save_reminder(filepath):
    print(f"Loaded: {filepath}. Remember to save your work!")

def register():
    bpy.app.handlers.load_post.append(save_reminder)

def unregister():
    if save_reminder in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.remove(save_reminder)
```

### Frame-Change Callback (Drive Object from Frame)

```python
import bpy
from bpy.app.handlers import persistent

@persistent
def drive_from_frame(scene, depsgraph):
    obj = bpy.data.objects.get("Cube")
    if obj:
        obj.location.z = scene.frame_current * 0.05

def register():
    bpy.app.handlers.frame_change_post.append(drive_from_frame)
```

### Deferred Initialization with Timer

Use a timer to defer work that requires full Blender context after startup:

```python
import bpy

def deferred_init():
    # Context is fully available here
    bpy.context.scene.render.engine = 'CYCLES'
    print("Deferred init complete")
    return None  # run once

def register():
    bpy.app.timers.register(deferred_init, first_interval=0.1)
```

### Periodic Background Task

```python
import bpy

_running = False

def poll_external_data():
    if not _running:
        return None  # stop
    # ... check external resource ...
    print("Polling...")
    return 5.0  # check every 5 seconds

def register():
    global _running
    _running = True
    bpy.app.timers.register(poll_external_data, first_interval=1.0)

def unregister():
    global _running
    _running = False
```

### Version-Gated Feature

```python
import bpy

if bpy.app.version >= (4, 0, 0):
    # Use Blender 4.x API
    pass
else:
    # Fallback for older versions
    pass
```
