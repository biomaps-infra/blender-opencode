# Math and Spatial Reference

Blender 5.0 `mathutils` module — vectors, matrices, rotations, spatial queries, and noise.

> All classes accept tuples/lists anywhere a Vector is expected.

## Table of Contents

- [Vector](#vector)
- [Matrix](#matrix)
- [Euler](#euler)
- [Quaternion](#quaternion)
- [Color](#color)
- [mathutils.geometry](#mathutilsgeometry)
- [BVHTree](#bvhtree)
- [KDTree](#kdtree)
- [Noise](#noise)
- [Common Transform Recipes](#common-transform-recipes)

---

## Vector

`mathutils.Vector(seq)` — 2D, 3D, or 4D vector.

### Construction

```python
from mathutils import Vector

v3 = Vector((1.0, 2.0, 3.0))       # 3D
v2 = Vector((1.0, 2.0))             # 2D
v4 = Vector((1.0, 2.0, 3.0, 1.0))  # 4D
v_fill = Vector.Fill(3, 1.0)        # (1, 1, 1)
```

### Arithmetic

```python
a + b           # component-wise add/subtract
a * 2.0         # scalar multiply
a @ b           # dot product (vectors)
matrix @ vec    # matrix-vector transform
quat @ vec      # quaternion rotation of vector
-a              # negate
```

### Key Methods

| Method / Property | Returns | Description |
|---|---|---|
| `v.normalized()` | `Vector` | Unit-length copy |
| `v.length` / `v.length_squared` | `float` | Length / squared length |
| `v.dot(other)` | `float` | Dot product |
| `v.cross(other)` | `Vector` | Cross product (3D), float (2D) |
| `v.angle(other, fallback)` | `float` | Angle in radians |
| `v.lerp(other, factor)` | `Vector` | Linear interpolation |
| `v.slerp(other, factor)` | `Vector` | Spherical interpolation |
| `v.project(other)` | `Vector` | Projection onto other |
| `v.reflect(mirror)` | `Vector` | Reflection across normal |
| `v.rotation_difference(other)` | `Quaternion` | Rotation between vectors (3D) |
| `v.to_track_quat(track, up)` | `Quaternion` | Tracking rotation |
| `v.rotate(euler\|quat\|mat)` | `None` | In-place rotation |
| `v.to_2d()` / `to_3d()` / `to_4d()` | `Vector` | Resize copy |
| `v.xyz`, `v.xy`, `v.xz` | `Vector` | Swizzle access |
| `v.copy()` / `v.freeze()` | `Vector` | Copy / make hashable |

---

## Matrix

`mathutils.Matrix(rows)` — 2x2 to 4x4 matrix. Default is 4x4 identity.

### Construction (Class Methods)

```python
from mathutils import Matrix
from math import radians

Matrix.Identity(4)                              # 4x4 identity
Matrix.Translation(Vector((1, 2, 3)))           # 4x4 translation
Matrix.Rotation(radians(45), 4, 'Z')            # 4x4 rotation around Z
Matrix.Scale(2.0, 4)                            # 4x4 uniform scale
Matrix.Scale(2.0, 4, Vector((0, 0, 1)))         # scale along axis
Matrix.Diagonal(Vector((1, 2, 3, 1)))           # diagonal matrix
Matrix.LocRotScale(loc, rot, scale)             # combined TRS (any can be None)
```

### Key Methods

| Method / Property | Returns | Description |
|---|---|---|
| `m.decompose()` | `(Vector, Quaternion, Vector)` | Extract loc, rot, scale |
| `m.inverted(fallback)` | `Matrix` | Inverse copy |
| `m.inverted_safe()` | `Matrix` | Inverse, never errors |
| `m.transposed()` | `Matrix` | Transposed copy |
| `m.normalized()` | `Matrix` | Column-normalized copy |
| `m.determinant()` | `float` | Determinant |
| `m.to_euler(order, compat)` | `Euler` | Rotation as Euler |
| `m.to_quaternion()` | `Quaternion` | Rotation as Quaternion |
| `m.to_scale()` | `Vector` | Scale component |
| `m.to_translation()` | `Vector` | Translation (4x4) |
| `m.to_3x3()` / `to_4x4()` | `Matrix` | Resize copy |
| `m.lerp(other, factor)` | `Matrix` | Polar decomposition interp |
| `m.translation` | `Vector` | Translation (read/write) |
| `m.is_identity` / `m.is_negative` | `bool` | State checks |
| `m @ other` | `Matrix` | Composition |
| `m @ vec` | `Vector` | Transform vector |

```python
# Build matrix from object's TRS
if obj.rotation_mode == 'QUATERNION':
    mat = Matrix.LocRotScale(obj.location, obj.rotation_quaternion, obj.scale)
else:
    mat = Matrix.LocRotScale(obj.location, obj.rotation_euler, obj.scale)
```

---

## Euler

`mathutils.Euler(angles=(0,0,0), order='XYZ')` — rotation in radians.

```python
from mathutils import Euler
from math import radians
eul = Euler((0.0, radians(45), 0.0), 'XYZ')
```

| Method / Property | Returns | Description |
|---|---|---|
| `e.to_matrix()` | `Matrix` (3x3) | Rotation matrix |
| `e.to_quaternion()` | `Quaternion` | Quaternion rotation |
| `e.rotate(other)` | `None` | Compose with Euler/Quat/Matrix |
| `e.rotate_axis(axis, angle)` | `None` | Rotate around single axis |
| `e.make_compatible(other)` | `None` | Fix for smooth interpolation |
| `e.order` | `str` | `'XYZ'`, `'XZY'`, `'YXZ'`, `'YZX'`, `'ZXY'`, `'ZYX'` |
| `e.x`, `e.y`, `e.z` | `float` | Axis angles in radians |

```python
# Euler to 4x4 transform
mat = Matrix.Translation((2, 3, 4)) @ eul.to_matrix().to_4x4()
```

---

## Quaternion

`mathutils.Quaternion(seq=(1,0,0,0), angle=0.0)` — rotation quaternion.

### Construction

```python
from mathutils import Quaternion
from math import radians

q = Quaternion()                                  # identity
q = Quaternion((1.0, 0.0, 0.0, 0.0))             # (w, x, y, z)
q = Quaternion((0, 1, 0), radians(90))            # axis + angle
q = Quaternion(exponential_map_vec)                # from 3D exp map
```

### Key Methods

| Method / Property | Returns | Description |
|---|---|---|
| `q.rotation_difference(other)` | `Quaternion` | Delta rotation |
| `q.slerp(other, factor)` | `Quaternion` | Spherical interpolation |
| `q.to_euler(order, compat)` | `Euler` | Convert to Euler |
| `q.to_matrix()` | `Matrix` (3x3) | Rotation matrix |
| `q.to_axis_angle()` | `(Vector, float)` | Axis and angle |
| `q.to_exponential_map()` | `Vector` (3D) | For averaging rotations |
| `q.to_swing_twist(axis)` | `(Quaternion, float)` | Decompose rotation |
| `q.normalized()` / `q.inverted()` | `Quaternion` | Unit / inverse |
| `q.conjugated()` | `Quaternion` | Conjugate |
| `q.make_compatible(other)` | `None` | Fix sign for interpolation |
| `q @ other_quat` / `q @ vec` | `Quat`/`Vec` | Compose / rotate |
| `q.angle` / `q.axis` | `float`/`Vector` | Angle and axis |
| `q.w`, `q.x`, `q.y`, `q.z` | `float` | Components |

```python
# Interpolate two rotations
q_mid = q_start.slerp(q_end, 0.5)

# Average rotations via exponential map
exp_avg = (q1.to_exponential_map() + q2.to_exponential_map()) / 2.0
q_avg = Quaternion(exp_avg)
```

---

## Color

`mathutils.Color(rgb=(0,0,0))` — RGB color, values 0-1. Most Blender API colors are scene-linear.

```python
from mathutils import Color
col = Color((1.0, 0.0, 0.0))   # red
col.r, col.g, col.b             # RGB components
col.h, col.s, col.v             # HSV components (read/write)
col.s *= 0.5                    # desaturate
```

### Color Space Conversions (5.0)

Methods on `Color` instances. Pattern: `col.from_{source}_to_{target}()`.

**sRGB:** `from_srgb_to_scene_linear()`, `from_scene_linear_to_srgb()`
**Rec.709:** `from_rec709_linear_to_scene_linear()`, `from_scene_linear_to_rec709_linear()`
**Rec.2020:** `from_rec2020_linear_to_scene_linear()`, `from_scene_linear_to_rec2020_linear()`
**ACES2065-1:** `from_aces_to_scene_linear()`, `from_scene_linear_to_aces()`
**ACEScg:** `from_acescg_to_scene_linear()`, `from_scene_linear_to_acescg()`
**CIE XYZ D65:** `from_xyz_d65_to_scene_linear()`, `from_scene_linear_to_xyz_d65()`

---

## mathutils.geometry

Utility functions for computational geometry.

### Intersection Functions

| Function | Signature | Returns |
|---|---|---|
| `intersect_ray_tri` | `(v1, v2, v3, ray, orig, clip=True)` | `Vector \| None` |
| `intersect_line_line` | `(v1, v2, v3, v4)` | `(Vector, Vector) \| None` |
| `intersect_line_plane` | `(line_a, line_b, plane_co, plane_no)` | `Vector \| None` |
| `intersect_line_line_2d` | `(A1, A2, B1, B2)` | `Vector \| None` (segments) |
| `intersect_line_sphere` | `(line_a, line_b, center, radius, clip)` | `(Vec\|None, Vec\|None)` |
| `intersect_plane_plane` | `(a_co, a_no, b_co, b_no)` | `(Vector, Vector) \| (None, None)` |
| `intersect_point_line` | `(pt, line_p1, line_p2)` | `(Vector, float)` |
| `intersect_point_tri` | `(pt, t1, t2, t3)` | `Vector \| None` |

### Measurement & Utility

| Function | Signature | Returns |
|---|---|---|
| `distance_point_to_plane` | `(pt, plane_co, plane_no)` | `float` (signed) |
| `area_tri` | `(v1, v2, v3)` | `float` |
| `volume_tetrahedron` | `(v1, v2, v3, v4)` | `float` |
| `normal` | `(*vectors)` | `Vector` (polygon normal) |
| `closest_point_on_tri` | `(pt, t1, t2, t3)` | `Vector` |
| `tessellate_polygon` | `(polylines)` | `list[(int,int,int)]` |
| `convex_hull_2d` | `(points)` | `list[int]` (indices) |
| `interpolate_bezier` | `(k1, h1, h2, k2, res)` | `list[Vector]` |
| `barycentric_transform` | `(pt, a1,a2,a3, b1,b2,b3)` | `Vector` |
| `delaunay_2d_cdt` | `(verts, edges, faces, type, eps)` | 6-tuple |

---

## BVHTree

`mathutils.bvhtree.BVHTree` — bounding volume hierarchy for fast spatial queries.

### Construction

```python
from mathutils.bvhtree import BVHTree

depsgraph = bpy.context.evaluated_depsgraph_get()
bvh = BVHTree.FromObject(obj, depsgraph)            # from scene object
bvh = BVHTree.FromBMesh(bm, epsilon=0.0)            # from BMesh
bvh = BVHTree.FromPolygons(verts, polys)             # from raw geometry
```

### Methods

| Method | Returns |
|---|---|
| `ray_cast(origin, direction, distance)` | `(location, normal, index, distance)` or all `None` |
| `find_nearest(origin, distance)` | `(location, normal, index, distance)` or all `None` |
| `find_nearest_range(origin, distance)` | `list[(location, normal, index, distance)]` |
| `overlap(other_tree)` | `list[(index_a, index_b)]` |

```python
loc, normal, index, dist = bvh.ray_cast(origin, direction)
if loc:
    print(f"Hit face {index} at {loc}")
```

---

## KDTree

`mathutils.kdtree.KDTree(size)` — 3D k-d tree for nearest-neighbor queries.

```python
import mathutils

kd = mathutils.kdtree.KDTree(len(mesh.vertices))
for i, v in enumerate(mesh.vertices):
    kd.insert(v.co, i)
kd.balance()  # MUST call before any find

co, index, dist = kd.find((0, 0, 0))                       # nearest point
results = kd.find_n((0, 0, 0), 10)                          # nearest N
results = kd.find_range((0, 0, 0), 0.5)                     # within radius
co, index, dist = kd.find((0, 0, 0), filter=lambda i: i>0)  # with filter
```

| Method | Signature | Returns |
|---|---|---|
| `insert` | `(co, index)` | `None` |
| `balance` | `()` | `None` — required after all inserts |
| `find` | `(co, filter=None)` | `(Vector, int, float)` |
| `find_n` | `(co, n)` | `list[(Vector, int, float)]` |
| `find_range` | `(co, radius)` | `list[(Vector, int, float)]` |

---

## Noise

`mathutils.noise` — procedural noise functions.

**Noise basis options:** `'BLENDER'`, `'PERLIN_ORIGINAL'`, `'PERLIN_NEW'`, `'VORONOI_F1'`, `'VORONOI_F2'`, `'VORONOI_F3'`, `'VORONOI_F4'`, `'VORONOI_F2F1'`, `'VORONOI_CRACKLE'`, `'CELLNOISE'`

```python
from mathutils import noise

noise.seed_set(42)
val = noise.random()                            # float in [0, 1)
vec = noise.random_unit_vector(size=3)          # random unit vector
val = noise.noise(pos, noise_basis='PERLIN_ORIGINAL')
val = noise.cell(pos)                           # cell noise (constant per cell)
val = noise.fractal(pos, H=1.0, lacunarity=2.0, octaves=8)
val = noise.turbulence(pos, octaves=4, hard=False,
                       amplitude_scale=0.5, frequency_scale=2.0)
result = noise.voronoi(pos, distance_metric='DISTANCE')
```

| Function | Extra Params | Description |
|---|---|---|
| `fractal` | `H, lacunarity, octaves` | fBm noise |
| `multi_fractal` | `H, lacunarity, octaves` | Multifractal |
| `hetero_terrain` | `H, lacunarity, octaves, offset` | Heterogeneous terrain |
| `hybrid_multi_fractal` | `H, lacunarity, octaves, offset, gain` | Hybrid multifractal |
| `ridged_multi_fractal` | `H, lacunarity, octaves, offset, gain` | Ridged multifractal |
| `variable_lacunarity` | `distortion, noise_type1, noise_type2` | Distorted noise |
| `turbulence` / `turbulence_vector` | `octaves, hard` | Turbulence scalar/vector |

---

## Common Transform Recipes

### Transform Chain: Translation @ Rotation @ Scale

```python
from mathutils import Matrix, Vector
from math import radians

mat = Matrix.Translation(Vector((1, 2, 3))) \
    @ Matrix.Rotation(radians(45), 4, 'Z') \
    @ Matrix.Scale(2.0, 4)
```

### World to Local Space

```python
world_point = Vector((10, 5, 3))
local_point = obj.matrix_world.inverted() @ world_point
```

### Local Axis Movement

```python
# Move 5 units along object's local X
obj.matrix_world = obj.matrix_world @ Matrix.Translation(Vector((5, 0, 0)))
```

### Decompose and Recompose

```python
loc, rot, sca = obj.matrix_world.decompose()
loc.z += 1.0
obj.matrix_world = Matrix.LocRotScale(loc, rot, sca)
```

### Parent-Relative Transform

```python
if obj.parent:
    local_mat = obj.parent.matrix_world.inverted() @ obj.matrix_world
else:
    local_mat = obj.matrix_world.copy()
```

### Look-At / Track-To

```python
direction = (target.location - obj.location).normalized()
obj.rotation_euler = direction.to_track_quat('Z', 'Y').to_euler()
```

### Interpolate Transforms

```python
mat_mid = mat_a.lerp(mat_b, factor=0.5)            # matrix interp
q_mid = q_a.slerp(q_b, 0.5)                        # rotation interp
```

### BVHTree Ray Cast from Camera

```python
bvh = BVHTree.FromObject(obj, bpy.context.evaluated_depsgraph_get())
cam = bpy.context.scene.camera
origin = cam.matrix_world.translation
direction = cam.matrix_world.to_quaternion() @ Vector((0, 0, -1))
hit, normal, idx, dist = bvh.ray_cast(origin, direction)
```
