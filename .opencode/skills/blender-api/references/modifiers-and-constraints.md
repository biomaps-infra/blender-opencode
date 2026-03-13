# Modifiers and Constraints Reference

> Blender 5.0 Python API -- `bpy.types.Modifier`, `bpy.types.Constraint`, and related types.

## Table of Contents

- [Adding Modifiers](#adding-modifiers)
- [Modifier Type Enum Values](#modifier-type-enum-values)
- [Key Modifiers](#key-modifiers)
  - [SubsurfModifier](#subsurfmodifier)
  - [ArrayModifier](#arraymodifier)
  - [BooleanModifier](#booleanmodifier)
  - [MirrorModifier](#mirrormodifier)
  - [SolidifyModifier](#solidifymodifier)
  - [BevelModifier](#bevelmodifier)
  - [ShrinkwrapModifier](#shrinkwrapmodifier)
  - [DecimateModifier](#decimatemodifier)
- [Base Modifier Properties](#base-modifier-properties)
- [Applying Modifiers](#applying-modifiers)
- [Modifier Stack Order](#modifier-stack-order)
- [Adding Constraints](#adding-constraints)
- [Constraint Type Enum Values](#constraint-type-enum-values)
- [Key Constraints](#key-constraints)
  - [CopyLocationConstraint](#copylocationconstraint)
  - [CopyRotationConstraint](#copyrotationconstraint)
  - [TrackToConstraint](#tracktoconstraint)
  - [LimitLocationConstraint](#limitlocationconstraint)
- [Base Constraint Properties](#base-constraint-properties)
- [Common Patterns](#common-patterns)

---

## Adding Modifiers

Use `obj.modifiers.new(name, type)` to add modifiers. Returns the new `Modifier` subclass instance.

```python
import bpy

obj = bpy.context.active_object
mod = obj.modifiers.new(name="MySubsurf", type='SUBSURF')
mod.levels = 2
```

**ObjectModifiers methods:**

| Method | Signature | Description |
|--------|-----------|-------------|
| `new` | `new(name: str, type: str) -> Modifier` | Add a new modifier |
| `remove` | `remove(modifier: Modifier)` | Remove a modifier |
| `active` | property | Get/set the active modifier |

---

## Modifier Type Enum Values

### Generate
| Type String | Class | Description |
|-------------|-------|-------------|
| `'ARRAY'` | `ArrayModifier` | Array duplication |
| `'BEVEL'` | `BevelModifier` | Bevel edges/vertices |
| `'BOOLEAN'` | `BooleanModifier` | Boolean operations |
| `'BUILD'` | `BuildModifier` | Animate face appearance |
| `'DECIMATE'` | `DecimateModifier` | Reduce polygon count |
| `'MASK'` | `MaskModifier` | Hide vertices by group |
| `'MIRROR'` | `MirrorModifier` | Mirror geometry |
| `'MULTIRES'` | `MultiresModifier` | Multi-resolution sculpt |
| `'REMESH'` | `RemeshModifier` | Remesh topology |
| `'SCREW'` | `ScrewModifier` | Lathe/screw profile |
| `'SKIN'` | `SkinModifier` | Generate skin mesh |
| `'SOLIDIFY'` | `SolidifyModifier` | Add thickness |
| `'SUBSURF'` | `SubsurfModifier` | Subdivision surface |
| `'TRIANGULATE'` | `TriangulateModifier` | Triangulate faces |
| `'WELD'` | `WeldModifier` | Merge by distance |
| `'WIREFRAME'` | `WireframeModifier` | Wireframe mesh |

### Deform
| Type String | Class | Description |
|-------------|-------|-------------|
| `'ARMATURE'` | `ArmatureModifier` | Skeletal deform |
| `'CAST'` | `CastModifier` | Cast to shape |
| `'CURVE'` | `CurveModifier` | Deform along curve |
| `'DISPLACE'` | `DisplaceModifier` | Texture displacement |
| `'HOOK'` | `HookModifier` | Hook to object |
| `'LAPLACIANDEFORM'` | `LaplacianDeformModifier` | Laplacian deform |
| `'LAPLACIANSMOOTH'` | `LaplacianSmoothModifier` | Laplacian smooth |
| `'LATTICE'` | `LatticeModifier` | Lattice deform |
| `'MESH_DEFORM'` | `MeshDeformModifier` | Mesh cage deform |
| `'SHRINKWRAP'` | `ShrinkwrapModifier` | Project onto target |
| `'SIMPLE_DEFORM'` | `SimpleDeformModifier` | Twist/bend/taper |
| `'SMOOTH'` | `SmoothModifier` | Smooth vertices |
| `'SURFACE_DEFORM'` | `SurfaceDeformModifier` | Bind to surface |
| `'WARP'` | `WarpModifier` | Warp using objects |
| `'WAVE'` | `WaveModifier` | Wave deformation |

### Physics
| Type String | Description |
|-------------|-------------|
| `'CLOTH'` | Cloth simulation |
| `'COLLISION'` | Collision detection |
| `'DYNAMIC_PAINT'` | Dynamic paint |
| `'FLUID'` | Fluid simulation |
| `'PARTICLE_SYSTEM'` | Particle system |
| `'SOFT_BODY'` | Soft body physics |

### Other
| Type String | Description |
|-------------|-------------|
| `'DATA_TRANSFER'` | Transfer mesh data |
| `'NORMAL_EDIT'` | Edit normals |
| `'WEIGHTED_NORMAL'` | Weighted normals |
| `'UV_PROJECT'` | UV projection |
| `'UV_WARP'` | UV warp |
| `'NODES'` | Geometry Nodes |

---

## Key Modifiers

### SubsurfModifier

Type string: `'SUBSURF'`

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `levels` | `int` [0, 11] | `1` | Viewport subdivision levels |
| `render_levels` | `int` [0, 11] | `2` | Render subdivision levels |
| `subdivision_type` | `enum` `'CATMULL_CLARK'`, `'SIMPLE'` | `'CATMULL_CLARK'` | Subdivision algorithm |
| `use_creases` | `bool` | `True` | Use crease data for sharpening |
| `uv_smooth` | `enum` | `'PRESERVE_BOUNDARIES'` | UV smoothing mode |

```python
mod = obj.modifiers.new("Subdiv", 'SUBSURF')
mod.levels = 2
mod.render_levels = 3
mod.subdivision_type = 'CATMULL_CLARK'
```

### ArrayModifier

Type string: `'ARRAY'`

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `count` | `int` [1, inf] | `2` | Number of duplicates |
| `fit_type` | `enum` `'FIXED_COUNT'`, `'FIT_LENGTH'`, `'FIT_CURVE'` | `'FIXED_COUNT'` | Length calculation method |
| `relative_offset_displace` | `Vector(3)` | `(1,0,0)` | Relative offset per axis |
| `use_relative_offset` | `bool` | `True` | Use relative offset |
| `use_constant_offset` | `bool` | `False` | Use constant offset |
| `constant_offset_displace` | `Vector(3)` | `(1,0,0)` | Constant offset distance |
| `use_merge_vertices` | `bool` | `False` | Merge adjacent vertices |

```python
mod = obj.modifiers.new("Array", 'ARRAY')
mod.count = 5
mod.relative_offset_displace = (1.0, 0.0, 0.0)
```

### BooleanModifier

Type string: `'BOOLEAN'`

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `operation` | `enum` `'INTERSECT'`, `'UNION'`, `'DIFFERENCE'` | `'DIFFERENCE'` | Boolean operation |
| `object` | `Object` | `None` | Target mesh object |
| `operand_type` | `enum` `'OBJECT'`, `'COLLECTION'` | `'OBJECT'` | Single object or collection |
| `solver` | `enum` `'FLOAT'`, `'EXACT'`, `'MANIFOLD'` | `'EXACT'` | Solver method |
| `collection` | `Collection` | `None` | Collection operand (when `operand_type='COLLECTION'`) |

```python
mod = obj.modifiers.new("Bool", 'BOOLEAN')
mod.operation = 'DIFFERENCE'
mod.object = bpy.data.objects["Cutter"]
mod.solver = 'EXACT'
```

### MirrorModifier

Type string: `'MIRROR'`

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `use_axis` | `bool[3]` | `(True, False, False)` | Mirror per axis (X, Y, Z) |
| `use_clip` | `bool` | `False` | Prevent vertices crossing mirror plane |
| `merge_threshold` | `float` [0, inf] | `0.001` | Merge distance |
| `use_mirror_merge` | `bool` | `True` | Merge mirrored vertices |
| `mirror_object` | `Object` | `None` | Custom mirror center object |

```python
mod = obj.modifiers.new("Mirror", 'MIRROR')
mod.use_axis[0] = True   # Mirror X
mod.use_axis[1] = True   # Mirror Y
mod.use_clip = True
```

### SolidifyModifier

Type string: `'SOLIDIFY'`

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `thickness` | `float` | `0.01` | Shell thickness |
| `offset` | `float` | `-1.0` | Offset from center (-1 = inward, 1 = outward) |
| `solidify_mode` | `enum` `'EXTRUDE'`, `'NON_MANIFOLD'` | `'EXTRUDE'` | Algorithm |
| `use_even_offset` | `bool` | `False` | Maintain thickness at sharp corners |
| `use_rim` | `bool` | `True` | Create rim edge loops |

```python
mod = obj.modifiers.new("Shell", 'SOLIDIFY')
mod.thickness = 0.05
mod.offset = -1.0
```

### BevelModifier

Type string: `'BEVEL'`

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `width` | `float` [0, inf] | `0.1` | Bevel amount |
| `segments` | `int` [1, 1000] | `1` | Segment count |
| `limit_method` | `enum` `'NONE'`, `'ANGLE'`, `'WEIGHT'`, `'VGROUP'` | `'ANGLE'` | Selection method |
| `angle_limit` | `float` [0, pi] | `0.523599` | Angle threshold (radians, ~30 deg) |
| `affect` | `enum` `'VERTICES'`, `'EDGES'` | `'EDGES'` | Bevel edges or vertices |
| `profile` | `float` [0, 1] | `0.5` | Profile shape (0.5 = round) |
| `harden_normals` | `bool` | `False` | Match normals to adjacent faces |

```python
mod = obj.modifiers.new("Bevel", 'BEVEL')
mod.width = 0.02
mod.segments = 3
mod.limit_method = 'ANGLE'
mod.angle_limit = 0.523599  # 30 degrees
```

### ShrinkwrapModifier

Type string: `'SHRINKWRAP'`

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `target` | `Object` | `None` | Target mesh to shrink to |
| `wrap_method` | `enum` | `'NEAREST_SURFACEPOINT'` | Projection method |
| `wrap_mode` | `enum` | `'ON_SURFACE'` | How vertices are constrained |
| `offset` | `float` | `0.0` | Distance from target surface |
| `vertex_group` | `str` | `""` | Limit effect to vertex group |

```python
mod = obj.modifiers.new("Shrinkwrap", 'SHRINKWRAP')
mod.target = bpy.data.objects["TargetMesh"]
mod.wrap_method = 'NEAREST_SURFACEPOINT'
mod.offset = 0.01
```

### DecimateModifier

Type string: `'DECIMATE'`

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `decimate_type` | `enum` `'COLLAPSE'`, `'UNSUBDIV'`, `'DISSOLVE'` | `'COLLAPSE'` | Decimation algorithm |
| `ratio` | `float` [0, 1] | `1.0` | Triangle ratio (collapse only) |
| `iterations` | `int` [0, 32767] | `0` | Un-subdivide iterations |
| `angle_limit` | `float` [0, pi] | `0.087` | Dissolve angle threshold |
| `face_count` | `int` (readonly) | -- | Resulting face count |

```python
mod = obj.modifiers.new("Decimate", 'DECIMATE')
mod.decimate_type = 'COLLAPSE'
mod.ratio = 0.5
```

---

## Base Modifier Properties

All modifiers inherit from `Modifier`:

| Property | Type | Description |
|----------|------|-------------|
| `name` | `str` | Modifier name |
| `type` | `enum` (readonly) | Modifier type string |
| `show_viewport` | `bool` | Display in viewport |
| `show_render` | `bool` | Use during render |
| `show_in_editmode` | `bool` | Display in edit mode |
| `show_on_cage` | `bool` | Adjust edit cage |
| `is_active` | `bool` | Active modifier in stack |

---

## Applying Modifiers

```python
import bpy

obj = bpy.context.active_object

# Apply by name (object must be active and selected)
bpy.ops.object.modifier_apply(modifier="MySubsurf")

# Apply all modifiers
for mod in obj.modifiers:
    bpy.ops.object.modifier_apply(modifier=mod.name)
```

**Note:** `modifier_apply` is a context operator -- the object must be the active object and in Object mode.

---

## Modifier Stack Order

Modifiers evaluate top-to-bottom. Use `ObjectModifiers.move()` or the operator to reorder:

```python
# Move modifier to a different position (by index)
obj = bpy.context.active_object
# Move from index 2 to index 0 (top of stack)
bpy.ops.object.modifier_move_to_index(modifier="Bevel", index=0)
```

Typical order: Mirror -> Array -> Bevel -> Subsurf -> Solidify

---

## Adding Constraints

Use `obj.constraints.new(type)` to add constraints. Returns the new `Constraint` subclass.

```python
import bpy

obj = bpy.context.active_object
con = obj.constraints.new('COPY_LOCATION')
con.target = bpy.data.objects["Target"]
```

**ObjectConstraints methods:**

| Method | Signature | Description |
|--------|-----------|-------------|
| `new` | `new(type: str) -> Constraint` | Add a new constraint |
| `remove` | `remove(constraint: Constraint)` | Remove a constraint |
| `clear` | `clear()` | Remove all constraints |
| `move` | `move(from_index: int, to_index: int)` | Reorder constraints |
| `copy` | `copy(constraint: Constraint) -> Constraint` | Copy a constraint |
| `active` | property | Get/set active constraint |

---

## Constraint Type Enum Values

| Type String | Class | Description |
|-------------|-------|-------------|
| `'COPY_LOCATION'` | `CopyLocationConstraint` | Copy target location |
| `'COPY_ROTATION'` | `CopyRotationConstraint` | Copy target rotation |
| `'COPY_SCALE'` | `CopyScaleConstraint` | Copy target scale |
| `'COPY_TRANSFORMS'` | `CopyTransformsConstraint` | Copy all transforms |
| `'TRACK_TO'` | `TrackToConstraint` | Aim at target |
| `'DAMPED_TRACK'` | `DampedTrackConstraint` | Damped aim at target |
| `'LOCKED_TRACK'` | `LockedTrackConstraint` | Locked aim at target |
| `'LIMIT_LOCATION'` | `LimitLocationConstraint` | Clamp location |
| `'LIMIT_ROTATION'` | `LimitRotationConstraint` | Clamp rotation |
| `'LIMIT_SCALE'` | `LimitScaleConstraint` | Clamp scale |
| `'LIMIT_DISTANCE'` | `LimitDistanceConstraint` | Limit distance to target |
| `'CHILD_OF'` | `ChildOfConstraint` | Parent-like constraint |
| `'FLOOR'` | `FloorConstraint` | Floor collision |
| `'FOLLOW_PATH'` | `FollowPathConstraint` | Follow curve path |
| `'CLAMP_TO'` | `ClampToConstraint` | Clamp to curve |
| `'STRETCH_TO'` | `StretchToConstraint` | Stretch toward target |
| `'MAINTAIN_VOLUME'` | `MaintainVolumeConstraint` | Preserve volume |
| `'TRANSFORM'` | `TransformConstraint` | Map transforms |
| `'PIVOT'` | `PivotConstraint` | Pivot point constraint |
| `'SHRINKWRAP'` | `ShrinkwrapConstraint` | Shrinkwrap to surface |
| `'ARMATURE'` | `ArmatureConstraint` | Multi-bone influence |
| `'IK'` | `KinematicConstraint` | Inverse kinematics |
| `'SPLINE_IK'` | `SplineIKConstraint` | Spline IK |

---

## Key Constraints

### CopyLocationConstraint

Type string: `'COPY_LOCATION'`

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `target` | `Object` | `None` | Target object |
| `subtarget` | `str` | `""` | Bone or vertex group name |
| `use_x` / `use_y` / `use_z` | `bool` | `True` | Copy per axis |
| `invert_x` / `invert_y` / `invert_z` | `bool` | `False` | Invert per axis |
| `use_offset` | `bool` | `False` | Add to existing location |

### CopyRotationConstraint

Type string: `'COPY_ROTATION'`

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `target` | `Object` | `None` | Target object |
| `subtarget` | `str` | `""` | Bone or vertex group name |
| `use_x` / `use_y` / `use_z` | `bool` | `True` | Copy per axis |
| `mix_mode` | `enum` `'REPLACE'`, `'ADD'`, `'BEFORE'`, `'AFTER'` | `'REPLACE'` | Combine method |
| `invert_x` / `invert_y` / `invert_z` | `bool` | `False` | Invert per axis |

### TrackToConstraint

Type string: `'TRACK_TO'`

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `target` | `Object` | `None` | Target to aim at |
| `subtarget` | `str` | `""` | Bone or vertex group name |
| `track_axis` | `enum` `'TRACK_X'`..`'TRACK_NEGATIVE_Z'` | `'TRACK_X'` | Axis pointing at target |
| `up_axis` | `enum` `'UP_X'`, `'UP_Y'`, `'UP_Z'` | `'UP_X'` | Upward axis |
| `use_target_z` | `bool` | `False` | Use target Z as up |

### LimitLocationConstraint

Type string: `'LIMIT_LOCATION'`

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `use_min_x` / `use_max_x` | `bool` | `False` | Enable min/max X clamping |
| `min_x` / `max_x` | `float` | `0.0` | Min/max X bounds |
| `use_min_y` / `use_max_y` | `bool` | `False` | Enable min/max Y clamping |
| `min_y` / `max_y` | `float` | `0.0` | Min/max Y bounds |
| `use_min_z` / `use_max_z` | `bool` | `False` | Enable min/max Z clamping |
| `use_transform_limit` | `bool` | `False` | Also affect transform tools |

---

## Base Constraint Properties

All constraints inherit from `Constraint`:

| Property | Type | Description |
|----------|------|-------------|
| `name` | `str` | Constraint name |
| `type` | `enum` (readonly) | Constraint type string |
| `influence` | `float` [0, 1] | Blend factor (0 = off, 1 = full) |
| `mute` | `bool` | Disable constraint |
| `enabled` | `bool` | Use constraint results |
| `owner_space` | `enum` `'WORLD'`, `'LOCAL'`, `'POSE'`, `'CUSTOM'` | Owner evaluation space |
| `target_space` | `enum` `'WORLD'`, `'LOCAL'`, `'POSE'`, `'CUSTOM'` | Target evaluation space |

---

## Common Patterns

### Mirror + Subdivision Surface

Standard hard-surface modeling stack: model one side, mirror, then smooth.

```python
import bpy

obj = bpy.context.active_object
mirror = obj.modifiers.new("Mirror", 'MIRROR')
mirror.use_axis[0] = True
mirror.use_clip = True

subsurf = obj.modifiers.new("Subsurf", 'SUBSURF')
subsurf.levels = 2
subsurf.render_levels = 3
```

### Boolean Workflow

Cut shapes from a mesh using a cutter object.

```python
import bpy

obj = bpy.context.active_object
cutter = bpy.data.objects["Cutter"]

bool_mod = obj.modifiers.new("Cut", 'BOOLEAN')
bool_mod.operation = 'DIFFERENCE'
bool_mod.object = cutter
bool_mod.solver = 'EXACT'

# Hide cutter in viewport
cutter.hide_set(True)
```

### Constraint Chain -- Follow with Limits

Make an object follow a target but clamp its location range.

```python
import bpy

follower = bpy.data.objects["Follower"]
target = bpy.data.objects["Leader"]

# Copy location from target
loc = follower.constraints.new('COPY_LOCATION')
loc.target = target
loc.influence = 0.5  # Lag behind

# Limit to a bounding box
limit = follower.constraints.new('LIMIT_LOCATION')
limit.use_min_x = True
limit.use_max_x = True
limit.min_x = -5.0
limit.max_x = 5.0
limit.owner_space = 'WORLD'
```

### Track-To Camera Rig

Point a camera at a target object.

```python
import bpy

cam = bpy.data.objects["Camera"]
target = bpy.data.objects["LookAt"]

track = cam.constraints.new('TRACK_TO')
track.target = target
track.track_axis = 'TRACK_NEGATIVE_Z'
track.up_axis = 'UP_Y'
```

### Remove All Modifiers

```python
obj = bpy.context.active_object
obj.modifiers.clear()
```

### Iterate and Configure Modifiers

```python
for mod in obj.modifiers:
    if mod.type == 'SUBSURF':
        mod.levels = 1
    mod.show_viewport = True
```
