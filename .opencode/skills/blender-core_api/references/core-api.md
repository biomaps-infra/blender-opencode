# Core API Reference

Blender 5.0 Python API — essential modules for scripting and addon development.

## Table of Contents

- [bpy.context — Context Access](#bpycontext--context-access)
- [bpy.data — Blend Data Access](#bpydata--blend-data-access)
- [bpy.props — Property Definitions](#bpyprops--property-definitions)
- [bpy.utils — Utilities](#bpyutils--utilities)
- [bpy.path — Path Utilities](#bpypath--path-utilities)
- [bpy.msgbus — Message Bus](#bpymsgbus--message-bus)

---

## bpy.context — Context Access

All context values are **read-only**. Modify data through `bpy.data` or operators.

### Global Context Attributes (always available)

| Attribute | Type |
|---|---|
| `scene` | `Scene` |
| `view_layer` | `ViewLayer` |
| `collection` | `Collection` |
| `window` | `Window` |
| `window_manager` | `WindowManager` |
| `screen` | `Screen` |
| `workspace` | `WorkSpace` |
| `area` | `Area` |
| `region` | `Region` |
| `space_data` | `Space` (may be None in background mode) |
| `preferences` | `Preferences` |
| `mode` | enum string (e.g. `'OBJECT'`, `'EDIT_MESH'`) |
| `engine` | string |
| `tool_settings` | `ToolSettings` |
| `blend_data` | `BlendData` |

### Screen Context (3D Viewport)

| Attribute | Type |
|---|---|
| `active_object` | `Object` |
| `object` | `Object` |
| `selected_objects` | sequence of `Object` |
| `visible_objects` | sequence of `Object` |
| `edit_object` | `Object` |
| `active_bone` | `EditBone` or `Bone` |
| `active_pose_bone` | `PoseBone` |
| `selected_bones` | sequence of `EditBone` |
| `selected_pose_bones` | sequence of `PoseBone` |

### Buttons Context (Properties Editor)

`material`, `mesh`, `armature`, `camera`, `light`, `brush`, `bone`, `edit_bone`, `pose_bone` — each returns the corresponding `bpy.types.*` or None.

### Other Contexts

`active_node` (`Node`), `selected_nodes` (seq of `Node`), `active_strip` (`Strip`), `selected_strips` (seq of `Strip`), `edit_text` (`Text`), `edit_image` (`Image`).

### Context Temp Override Pattern

```python
import bpy

window = bpy.context.window
screen = window.screen
area = next(a for a in screen.areas if a.type == 'VIEW_3D')
region = next(r for r in area.regions if r.type == 'WINDOW')

with bpy.context.temp_override(window=window, area=area, region=region):
    bpy.ops.view3d.camera_to_view()
```

---

## bpy.data — Blend Data Access

`bpy.data` is the global `BlendData` instance. All blend-file data lives in its collections.

### BlendData Collections

| Collection | Element Type |
|---|---|
| `objects` | `Object` |
| `meshes` | `Mesh` |
| `materials` | `Material` |
| `textures` | `Texture` |
| `images` | `Image` |
| `cameras` | `Camera` |
| `lights` | `Light` |
| `armatures` | `Armature` |
| `curves` | `Curve` |
| `collections` | `Collection` |
| `scenes` | `Scene` |
| `worlds` | `World` |
| `node_groups` | `NodeTree` |
| `texts` | `Text` |
| `actions` | `Action` |
| `particles` | `ParticleSettings` |
| `libraries` | `Library` |

### Collection Methods

Every `bpy.data.<collection>` supports: `.new(name)`, `.remove(datablock)`, `.keys()` / `.values()` / `.items()`, `[name]` or `.get(name)`.

### Creating and Removing Data

```python
import bpy

mesh = bpy.data.meshes.new("MyMesh")
obj = bpy.data.objects.new("MyObject", mesh)
bpy.context.collection.objects.link(obj)

bpy.data.objects.remove(obj)
bpy.data.meshes.remove(mesh)
```

### Iterating and Querying

```python
import bpy

for obj in bpy.data.objects:
    print(obj.name, obj.type)

if "Cube" in bpy.data.meshes:
    mesh = bpy.data.meshes["Cube"]
```

---

## bpy.props — Property Definitions

All parameters must be **keyword arguments**. Assign via annotation (`prop: Type(...)`) or dynamically (`bpy.types.X.prop = Type(...)`).

### Common Keyword Arguments

| Kwarg | Type | Description |
|---|---|---|
| `name` | `str` | UI display name |
| `description` | `str` | Tooltip text |
| `default` | varies | Default value |
| `options` | `set[str]` | `{'ANIMATABLE'}`, `'HIDDEN'`, `'SKIP_SAVE'`, `'LIBRARY_EDITABLE'` |
| `update` | `(self, context)` | Called on value change (not for CollectionProperty) |
| `get` | `(self) -> value` | Custom getter (omit `set` for read-only) |
| `set` | `(self, value)` | Custom setter (requires `get`) |

### Property Type Signatures

```
BoolProperty(*, name='', description='', default=False,
             options={'ANIMATABLE'}, subtype='NONE', update=None, get=None, set=None)

IntProperty(*, name='', description='', default=0, min=-2**31, max=2**31-1,
            soft_min, soft_max, step=1, subtype='NONE', update=None, get=None, set=None)

FloatProperty(*, name='', description='', default=0.0, min, max, soft_min, soft_max,
              step=3, precision=2, subtype='NONE', unit='NONE', update=None, get=None, set=None)

StringProperty(*, name='', description='', default='', maxlen=0, subtype='NONE',
               update=None, get=None, set=None, search=None, search_options={'SUGGESTION'})

EnumProperty(items, *, name='', description='', default=None,
             options={'ANIMATABLE'}, update=None, get=None, set=None)
```

**EnumProperty `items`**: list of `(identifier, name, description)` or `(id, name, desc, icon, number)` tuples. Dynamic: callback `(self, context) -> list` (context may be None). For `ENUM_FLAG`, default must be a set.

### Vector Property Signatures

```
BoolVectorProperty(*, default=(False, False, False), size=3, ...)
IntVectorProperty(*, default=(0, 0, 0), size=3, min, max, ...)
FloatVectorProperty(*, default=(0.0, 0.0, 0.0), size=3, min, max,
                    subtype='NONE', unit='NONE', ...)
```

`size`: int 1-32, or sequence for multi-dimensional arrays.

### Pointer and Collection Properties

```
PointerProperty(type, *, name='', description='', poll=None, update=None)
CollectionProperty(type, *, name='', description='')
RemoveProperty(cls, attr='prop_name')  # Preferred: del cls.prop_name
```

- `PointerProperty.type`: subclass of `PropertyGroup` or `ID`
- `PointerProperty.poll`: `(self, object) -> bool` — filter valid items in UI
- `CollectionProperty.type`: subclass of `PropertyGroup`

### PropertyGroup Example

```python
import bpy

class MySettings(bpy.types.PropertyGroup):
    my_int: bpy.props.IntProperty(default=5)
    my_float: bpy.props.FloatProperty(name="Scale", default=1.0)
    my_string: bpy.props.StringProperty(name="Label")

bpy.utils.register_class(MySettings)
bpy.types.Scene.my_settings = bpy.props.PointerProperty(type=MySettings)
# Access: bpy.context.scene.my_settings.my_int
```

### Dynamic Enum Items

```python
import bpy

def get_items(self, context):
    return [("OPT_A", "Option A", "First option", 0),
            ("OPT_B", "Option B", "Second option", 1)]

# WARNING: keep a reference to prevent callback garbage collection
bpy.types.Scene.my_enum = bpy.props.EnumProperty(items=get_items)
```

### Update Callback

```python
import bpy

def on_change(self, context):
    print("Value changed to", self.my_prop)

bpy.types.Scene.my_prop = bpy.props.FloatProperty(update=on_change)
```

---

## bpy.utils — Utilities

### Class Registration

```python
bpy.utils.register_class(cls)    # Register a Blender type subclass
bpy.utils.unregister_class(cls)  # Unregister a Blender type subclass
```

Accepted types: `Panel`, `UIList`, `Menu`, `Header`, `Operator`, `KeyingSetInfo`, `RenderEngine`, `AssetShelf`, `FileHandler`, `PropertyGroup`, `AddonPreferences`, `NodeTree`, `Node`, `NodeSocket`.

If the class has a `register`/`unregister` classmethod, it is called automatically.

### Batch Registration Factories

```python
# From a tuple of classes
classes = (MyOperator, MyPanel, MyPropertyGroup)
register, unregister = bpy.utils.register_classes_factory(classes)

# From submodule names (register in order, unregister reversed)
register, unregister = bpy.utils.register_submodule_factory(
    __name__, ["operators", "panels", "properties"]
)
```

### Resource and User Paths

```python
bpy.utils.resource_path(type, *, major, minor)
# type: 'USER', 'LOCAL', 'SYSTEM'

bpy.utils.user_resource(resource_type, *, path='', create=False)
# resource_type: 'DATAFILES', 'CONFIG', 'SCRIPTS', 'EXTENSIONS'

bpy.utils.extension_path_user(package, *, path='', create=False)
# Writable directory for an extension
```

### Script Utilities

```python
bpy.utils.script_paths(*, subdir=None)       # Valid script paths
bpy.utils.script_path_user()                  # User script path
bpy.utils.load_scripts(*, reload_scripts=False, refresh_scripts=False)
bpy.utils.modules_from_path(path, loaded_modules)  # Load all modules in path
bpy.utils.execfile(filepath, *, mod=None)     # Execute Python file, return module
```

### Other Utilities

```python
bpy.utils.register_manual_map(manual_hook)
bpy.utils.unregister_manual_map(manual_hook)
bpy.utils.blend_paths(*, absolute=False, packed=False, local=False)
bpy.utils.flip_name(name, *, strip_digits=False)  # "Arm.L" -> "Arm.R"
bpy.utils.escape_identifier(string)    # Escape for animation paths
bpy.utils.smpte_from_frame(frame, *, fps=None, fps_base=None)  # "HH:MM:SS:FF"
bpy.utils.time_from_frame(frame, *, fps=None, fps_base=None)   # timedelta
bpy.utils.preset_paths(subdir)
bpy.utils.register_preset_path(path)
```

---

## bpy.path — Path Utilities

Handles Blender's `//` relative path prefix. Similar scope to `os.path`.

### Key Functions

```python
bpy.path.abspath(path, *, start=None, library=None)  # Resolve "//" to absolute
bpy.path.relpath(path, *, start=None)                 # Absolute to "//" relative
bpy.path.basename(path)              # Like os.path.basename, skips "//"
bpy.path.ensure_ext(filepath, ext, *, case_sensitive=False)
bpy.path.clean_name(name, *, replace='_')  # Replace non-alphanumeric chars
bpy.path.native_pathsep(path)        # Replace separators with os.sep
bpy.path.is_subdir(path, directory)   # Both must be absolute
bpy.path.reduce_dirs(dirs)           # Remove duplicates and nested dirs
bpy.path.module_names(path, *, recursive=False, package='')
# Returns list of (module_name, module_file) tuples
bpy.path.display_name(name, *, has_ext=True, title_case=True)
bpy.path.display_name_from_filepath(name)
```

### Resolving Blend-Relative Paths

```python
import bpy

abs_path = bpy.path.abspath(bpy.data.images["Tex"].filepath)
rel_path = bpy.path.relpath("/home/user/textures/wood.png")
# "//textures/wood.png" if .blend is in /home/user/
```

---

## bpy.msgbus — Message Bus

Subscribe to RNA property change notifications. Triggered by Python API and UI changes. **Not** triggered by viewport dragging or animation playback.

### Key Behaviors

- Callbacks postponed until all operators finish executing
- Each property callback fires only once per update cycle
- All subscriptions cleared on file-load
- Changes from callbacks are not included in undo steps

### Functions

```python
bpy.msgbus.subscribe_rna(key, owner, args, notify, *, options=set())
# key: property instance, Struct type, or (Struct, "prop_name") tuple
# owner: any Python object (compared by identity)
# args: tuple passed to notify callback
# notify: callable(*args)
# options: {'PERSISTENT'} to survive ID remapping

bpy.msgbus.clear_by_owner(owner)    # Remove all subscriptions for owner
bpy.msgbus.publish_rna(key)         # Manually notify (rarely needed)
```

### Subscribe to a Specific Property

```python
import bpy

owner = object()

def on_location_change(*args):
    print("Object moved!", args)

bpy.msgbus.subscribe_rna(
    key=bpy.context.object.location,
    owner=owner, args=(42,), notify=on_location_change,
)
# Cleanup: bpy.msgbus.clear_by_owner(owner)
```

### Subscribe to All Instances of a Type

```python
import bpy

owner = object()
bpy.msgbus.subscribe_rna(
    key=(bpy.types.Object, "location"),
    owner=owner, args=(),
    notify=lambda *_: print("Any object location changed"),
)
```

### Non-Converted Properties

Some properties are converted to Python objects on access. Use `path_resolve` to get the RNA property:

```python
key = bpy.context.object.path_resolve("name", False)
bpy.msgbus.subscribe_rna(key=key, owner=owner, args=(), notify=callback)
```
