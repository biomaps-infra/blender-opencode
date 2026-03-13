# Import, Export and Utilities Reference

## Table of Contents

- [Import Operators](#import-operators) (OBJ, FBX, glTF, STL, PLY, Alembic)
- [Export Operators](#export-operators) (OBJ, FBX, glTF, STL, PLY, Alembic)
- [bpy_extras.io_utils](#bpy_extrasio_utils) (ImportHelper, ExportHelper, axis conversion)
- [bpy_extras.view3d_utils](#bpy_extrasview3d_utils) (2D/3D coordinate conversion, ray casting)
- [bpy_extras.object_utils](#bpy_extrasobject_utils) (object_data_add, world_to_camera_view)
- [bpy_extras.mesh_utils](#bpy_extrasmesh_utils) (UV islands, edge loops, tessellation)
- [bpy_extras.image_utils](#bpy_extrasimage_utils) (load_image)
- [bpy_extras.anim_utils](#bpy_extrasanim_utils) (bake_action)
- [Batch Import/Export Patterns](#batch-importexport-patterns)

---

## Import Operators

### OBJ Import — `bpy.ops.wm.obj_import`

```python
bpy.ops.wm.obj_import(
    filepath="/path/to/model.obj",
    global_scale=1.0,
    forward_axis='NEGATIVE_Z',  # 'X','Y','Z','NEGATIVE_X','NEGATIVE_Y','NEGATIVE_Z'
    up_axis='Y',
    use_split_objects=True,
    use_split_groups=False,
    import_vertex_groups=False,
    validate_meshes=True,
)
```

### FBX Import — `bpy.ops.import_scene.fbx`

```python
bpy.ops.import_scene.fbx(
    filepath="/path/to/model.fbx",
    global_scale=1.0,
    use_custom_normals=True,
    use_anim=True,
    use_custom_props=True,
    ignore_leaf_bones=False,
    automatic_bone_orientation=False,
    axis_forward='-Z',  # 'X','Y','Z','-X','-Y','-Z'
    axis_up='Y',
)
```

### glTF Import — `bpy.ops.import_scene.gltf`

```python
bpy.ops.import_scene.gltf(
    filepath="/path/to/model.glb",
    import_pack_images=True,
    merge_vertices=False,
    import_shading='NORMALS',  # 'NORMALS','FLAT','SMOOTH'
    bone_heuristic='BLENDER',  # 'BLENDER','TEMPERANCE','FORTUNE'
    guess_original_bind_pose=True,
    import_scene_extras=True,
)
```

### STL Import — `bpy.ops.wm.stl_import`

```python
bpy.ops.wm.stl_import(
    filepath="/path/to/model.stl",
    global_scale=1.0,
    use_scene_unit=False,
    use_facet_normal=False,
    forward_axis='Y',
    up_axis='Z',
    use_mesh_validate=True,
)
```

### PLY Import — `bpy.ops.wm.ply_import`

```python
bpy.ops.wm.ply_import(
    filepath="/path/to/model.ply",
    global_scale=1.0,
    forward_axis='Y',
    up_axis='Z',
    merge_verts=False,
    import_colors='SRGB',  # 'SRGB','LINEAR','NONE'
    import_attributes=True,
)
```

### Alembic Import — `bpy.ops.wm.alembic_import`

```python
bpy.ops.wm.alembic_import(
    filepath="/path/to/scene.abc",
    scale=1.0,
    set_frame_range=True,
    validate_meshes=False,
    always_add_cache_reader=False,
    is_sequence=False,
)
```

---

## Export Operators

### OBJ Export — `bpy.ops.wm.obj_export`

```python
bpy.ops.wm.obj_export(
    filepath="/path/to/output.obj",
    forward_axis='NEGATIVE_Z',
    up_axis='Y',
    global_scale=1.0,
    apply_modifiers=True,
    export_selected_objects=False,
    export_uv=True,
    export_normals=True,
    export_materials=True,
    export_triangulated_mesh=False,
    export_animation=False,
    path_mode='AUTO',  # 'AUTO','ABSOLUTE','RELATIVE','MATCH','STRIP','COPY'
)
```

### FBX Export — `bpy.ops.export_scene.fbx`

```python
bpy.ops.export_scene.fbx(
    filepath="/path/to/output.fbx",
    use_selection=False,
    global_scale=1.0,
    apply_unit_scale=True,
    object_types={'ARMATURE', 'CAMERA', 'EMPTY', 'LIGHT', 'MESH', 'OTHER'},
    use_mesh_modifiers=True,
    use_triangles=False,
    use_custom_props=False,
    bake_anim=True,
    bake_anim_use_nla_strips=True,
    path_mode='AUTO',
    embed_textures=False,
    axis_forward='-Z',
    axis_up='Y',
)
```

### glTF Export — `bpy.ops.export_scene.gltf`

```python
bpy.ops.export_scene.gltf(
    filepath="/path/to/output.glb",
    export_format='',       # auto-detect from extension (.glb=binary, .gltf=json)
    use_selection=False,
    export_apply=False,     # apply modifiers (prevents shape keys)
    export_animations=True,
    export_materials='EXPORT',  # 'EXPORT','PLACEHOLDER','NONE'
    export_texcoords=True,
    export_normals=True,
    export_yup=True,
    export_extras=False,    # export custom properties
    export_draco_mesh_compression_enable=False,
    export_lights=False,
    export_cameras=False,
)
```

### STL Export — `bpy.ops.wm.stl_export`

```python
bpy.ops.wm.stl_export(
    filepath="/path/to/output.stl",
    ascii_format=False,
    export_selected_objects=False,
    global_scale=1.0,
    use_scene_unit=False,
    forward_axis='Y',
    up_axis='Z',
    apply_modifiers=True,
    use_batch=False,
)
```

### PLY Export — `bpy.ops.wm.ply_export`

```python
bpy.ops.wm.ply_export(
    filepath="/path/to/output.ply",
    forward_axis='Y',
    up_axis='Z',
    global_scale=1.0,
    apply_modifiers=True,
    export_selected_objects=False,
    export_uv=True,
    export_normals=False,
    export_colors='SRGB',  # 'SRGB','LINEAR','NONE'
    export_triangulated_mesh=False,
    ascii_format=False,
)
```

### Alembic Export — `bpy.ops.wm.alembic_export`

```python
bpy.ops.wm.alembic_export(
    filepath="/path/to/output.abc",
    start=-2147483648,  # scene start if default
    end=-2147483648,    # scene end if default
    selected=False,
    uvs=True,
    normals=True,
    vcolors=False,
    face_sets=False,
    global_scale=1.0,
    triangulate=False,
    export_hair=True,
    export_particles=True,
    export_custom_properties=True,
    evaluation_mode='RENDER',  # 'RENDER','VIEWPORT'
)
```

---

## bpy_extras.io_utils

### ImportHelper / ExportHelper Mixins

Use these mixins when creating custom import/export operators. They provide the file browser invocation, `filepath` property, and `check()` method.

```python
import bpy
from bpy_extras.io_utils import ImportHelper, ExportHelper

class IMPORT_OT_custom(bpy.types.Operator, ImportHelper):
    bl_idname = "import_scene.custom"
    bl_label = "Import Custom"
    filename_ext = ".cst"
    filter_glob: bpy.props.StringProperty(default="*.cst", options={'HIDDEN'})

    def execute(self, context):
        # self.filepath is set by ImportHelper
        data = open(self.filepath).read()
        return {'FINISHED'}
```

```python
class EXPORT_OT_custom(bpy.types.Operator, ExportHelper):
    bl_idname = "export_scene.custom"
    bl_label = "Export Custom"
    filename_ext = ".cst"
    filter_glob: bpy.props.StringProperty(default="*.cst", options={'HIDDEN'})

    def execute(self, context):
        with open(self.filepath, 'w') as f:
            f.write("exported data")
        return {'FINISHED'}
```

### Axis Conversion

```python
from bpy_extras.io_utils import axis_conversion, orientation_helper

# Get a rotation matrix to convert from one axis system to another
mat = axis_conversion(from_forward='Y', from_up='Z',
                      to_forward='-Z', to_up='Y')  # returns mathutils.Matrix

# Decorator for import/export classes to add axis properties
@orientation_helper(axis_forward='-Z', axis_up='Y')
class IMPORT_OT_example(bpy.types.Operator, ImportHelper):
    ...
```

### Path Reference (for exporters)

```python
from bpy_extras.io_utils import path_reference, path_reference_copy

copy_set = set()
new_path = path_reference(filepath, base_src, base_dst,
                          mode='AUTO',  # 'AUTO','ABSOLUTE','RELATIVE','MATCH','STRIP','COPY'
                          copy_subdir='textures',
                          copy_set=copy_set)
# After export, copy collected files:
path_reference_copy(copy_set)
```

### Other Utilities

- `create_derived_objects(depsgraph, objects)` — returns dict of object instances (object, matrix) for duplis
- `unpack_list(list_of_tuples)` — flatten tuples for mesh data assignment
- `unique_name(key, name, name_dict)` — generate unique names for export

---

## bpy_extras.view3d_utils

### Function Signatures

```python
region_2d_to_vector_3d(region, rv3d, coord) -> mathutils.Vector
# Returns normalized direction vector from viewport at 2D coord

region_2d_to_origin_3d(region, rv3d, coord, *, clamp=None) -> mathutils.Vector
# Returns 3D origin of view ray from 2D coord

region_2d_to_location_3d(region, rv3d, coord, depth_location) -> mathutils.Vector
# Returns 3D location from 2D coord, aligned to depth_location

location_3d_to_region_2d(region, rv3d, coord, *, default=None) -> mathutils.Vector | None
# Projects 3D world-space location to 2D region coords
```

### Ray Casting Pattern (2D Mouse to 3D World)

```python
from bpy_extras.view3d_utils import region_2d_to_vector_3d, region_2d_to_origin_3d

def mouse_to_world_raycast(context, event):
    region = context.region
    rv3d = context.region_data
    coord = (event.mouse_region_x, event.mouse_region_y)

    origin = region_2d_to_origin_3d(region, rv3d, coord)
    direction = region_2d_to_vector_3d(region, rv3d, coord)

    depsgraph = context.evaluated_depsgraph_get()
    result, location, normal, index, obj, matrix = (
        context.scene.ray_cast(depsgraph, origin, direction)
    )
    return result, location, normal, obj
```

### 3D to 2D Projection

```python
from bpy_extras.view3d_utils import location_3d_to_region_2d

def project_point(context, world_pos):
    region = context.region
    rv3d = context.region_data
    pos_2d = location_3d_to_region_2d(region, rv3d, world_pos)
    return pos_2d  # None if behind camera
```

---

## bpy_extras.object_utils

### object_data_add Pattern

Creates an object from data and adds it to the scene, respecting cursor location/rotation and operator alignment settings.

```python
from bpy_extras.object_utils import object_data_add
import bpy

def create_custom_mesh(self, context):
    mesh = bpy.data.meshes.new("CustomMesh")
    verts = [(0,0,0), (1,0,0), (1,1,0), (0,1,0)]
    faces = [(0,1,2,3)]
    mesh.from_pydata(verts, [], faces)
    obj = object_data_add(context, mesh, operator=self, name="Custom")
    return obj
```

### world_to_camera_view

```python
from bpy_extras.object_utils import world_to_camera_view

# Returns (x, y, z) where x,y in [0,1] = camera frame, z = depth (negative = behind)
ndc = world_to_camera_view(scene, camera_obj, mathutils.Vector((1, 2, 3)))
is_visible = (0 <= ndc.x <= 1 and 0 <= ndc.y <= 1 and ndc.z > 0)
```

### AddObjectHelper Mixin

Provides `align`, `location`, `rotation` properties for add-object operators:

```python
from bpy_extras.object_utils import AddObjectHelper

class MESH_OT_add_custom(bpy.types.Operator, AddObjectHelper):
    bl_idname = "mesh.add_custom"
    bl_label = "Add Custom Mesh"

    def execute(self, context):
        mesh = bpy.data.meshes.new("Custom")
        mesh.from_pydata([(0,0,0),(1,0,0),(0,1,0)], [], [(0,1,2)])
        object_data_add(context, mesh, operator=self)
        return {'FINISHED'}
```

---

## bpy_extras.mesh_utils

| Function | Description |
|---|---|
| `mesh_linked_uv_islands(mesh)` | Returns `list[list[int]]` of polygon indices grouped by UV island |
| `mesh_linked_triangles(mesh)` | Splits mesh into connected triangle groups |
| `edge_face_count(mesh)` | Returns `list[int]` of face-user count per edge |
| `edge_face_count_dict(mesh)` | Returns `dict[tuple[int,int], int]` edge-key to face count |
| `edge_loops_from_edges(mesh, edges=None)` | Returns `list[list[int]]` vertex index loops; closed loops have matching start/end |
| `ngon_tessellate(from_data, indices)` | Tessellates an ngon into triangles; returns `list` of face index lists |
| `triangle_random_points(num_points, loop_triangles)` | Generates random `mathutils.Vector` points on triangles |

```python
import bpy
from bpy_extras.mesh_utils import mesh_linked_uv_islands

mesh = bpy.context.active_object.data
islands = mesh_linked_uv_islands(mesh)  # [[0,1,2], [3,4,5], ...]
print(f"Found {len(islands)} UV islands")
```

---

## bpy_extras.image_utils

### load_image

Flexible image loader with search, placeholder support, and case-insensitive matching.

```python
from bpy_extras.image_utils import load_image

img = load_image(
    "texture.png",
    dirname="/path/to/textures/",
    place_holder=True,     # create placeholder if not found
    recursive=False,       # search subdirs (can be slow)
    check_existing=True,   # reuse already-loaded image
    relpath="/path/to/blend/",  # make path relative to this
)
```

**Parameters:** `imagepath`, `dirname=''`, `place_holder=False`, `recursive=False`, `ncase_cmp=True`, `convert_callback=None`, `verbose=False`, `relpath=None`, `check_existing=False`, `force_reload=False`

**Returns:** `bpy.types.Image | None`

---

## bpy_extras.anim_utils

### bake_action

Bakes animation for objects (useful before export or for constraint/driver baking).

```python
from bpy_extras.anim_utils import bake_action, BakeOptions

options = BakeOptions(
    only_selected=False, do_pose=True, do_object=True,
    do_visual_keying=True, do_constraint_clear=False,
    do_parents_clear=False, do_clean=True,
    do_location=True, do_rotation=True, do_scale=True,
    do_bbone=False, do_custom_props=False,
)
action = bake_action(obj, action=None, frames=range(1, 250), bake_options=options)
```

- `bake_action_objects(object_action_pairs, frames, bake_options)` — batch version for multiple objects

---

## Batch Import/Export Patterns

### Batch Import (multiple files)

```python
import glob
for f in glob.glob("/models/*.obj"):
    bpy.ops.wm.obj_import(filepath=f)
```

### Batch Export (each object to separate file)

```python
import os, bpy

output_dir = "/path/to/export/"
for obj in bpy.context.scene.objects:
    if obj.type != 'MESH':
        continue
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    filepath = os.path.join(output_dir, f"{obj.name}.fbx")
    bpy.ops.export_scene.fbx(filepath=filepath, use_selection=True)
```

### Export Selected to glTF with Draco compression

```python
bpy.ops.export_scene.gltf(
    filepath="/output/compressed.glb",
    use_selection=True,
    export_draco_mesh_compression_enable=True,
    export_draco_mesh_compression_level=6,
    export_apply=True,
)
```

### Operator Module Summary

| Format | Import Operator | Export Operator |
|---|---|---|
| OBJ | `bpy.ops.wm.obj_import()` | `bpy.ops.wm.obj_export()` |
| FBX | `bpy.ops.import_scene.fbx()` | `bpy.ops.export_scene.fbx()` |
| glTF/GLB | `bpy.ops.import_scene.gltf()` | `bpy.ops.export_scene.gltf()` |
| STL | `bpy.ops.wm.stl_import()` | `bpy.ops.wm.stl_export()` |
| PLY | `bpy.ops.wm.ply_import()` | `bpy.ops.wm.ply_export()` |
| Alembic | `bpy.ops.wm.alembic_import()` | `bpy.ops.wm.alembic_export()` |

> **Note:** OBJ, STL, PLY, and Alembic use `bpy.ops.wm.*` (built-in C++ operators). FBX and glTF use `bpy.ops.import_scene.*` / `bpy.ops.export_scene.*` (Python addon operators). Axis enum values differ: built-in operators use `'NEGATIVE_Z'` style; addon operators use `'-Z'` style.
