# Mesh and BMesh Reference

## Table of Contents

1. [Standard BMesh Workflow](#standard-bmesh-workflow)
2. [BMesh Lifecycle](#bmesh-lifecycle)
3. [BMesh Elements](#bmesh-elements)
4. [BMesh Element Sequences](#bmesh-element-sequences)
5. [CustomData Layers](#customdata-layers)
6. [BMesh Operators (bmesh.ops)](#bmesh-operators)
7. [BMesh Utilities (bmesh.utils)](#bmesh-utilities)
8. [BMesh Geometry (bmesh.geometry)](#bmesh-geometry)
9. [Mesh Data Access (bpy.types.Mesh)](#mesh-data-access)
10. [Mesh Element Types](#mesh-element-types)
11. [Performance: foreach_get/set Pattern](#performance-foreachgetset-pattern)

---

## Standard BMesh Workflow

```python
import bpy, bmesh

# Object-mode workflow: create BMesh, modify, write back
me = bpy.context.object.data
bm = bmesh.new()
bm.from_mesh(me)

for v in bm.verts:
    v.co.z += 0.5

bm.to_mesh(me)
bm.free()
```

```python
# Edit-mode workflow: get existing edit BMesh
obj = bpy.context.edit_object
bm = bmesh.from_edit_mesh(obj.data)

for f in bm.faces:
    if f.select:
        f.smooth = True

bmesh.update_edit_mesh(obj.data)
```

---

## BMesh Lifecycle

### Module Functions

| Function | Description |
|----------|-------------|
| `bmesh.new(use_operators=True)` | Create empty BMesh. Set `use_operators=False` to save memory if not using `bmesh.ops`. |
| `bmesh.from_edit_mesh(mesh)` | Get BMesh from mesh already in edit mode. Returns wrapped BMesh owned by Blender. |
| `bmesh.update_edit_mesh(mesh, loop_triangles=True, destructive=True)` | Update mesh after edit-mode BMesh changes. Set `destructive=True` when geometry added/removed. |

### BMesh Instance Methods

| Method | Description |
|--------|-------------|
| `bm.from_mesh(mesh, face_normals=True, vertex_normals=True, use_shape_key=False, shape_key_index=0)` | Fill BMesh from a `bpy.types.Mesh`. Multiple calls join meshes. |
| `bm.from_object(object, depsgraph, cage=False)` | Fill from evaluated object (applies modifiers). |
| `bm.to_mesh(mesh)` | Write BMesh data into an existing `bpy.types.Mesh`. |
| `bm.free()` | Free BMesh memory immediately. Further access raises exceptions. |
| `bm.copy()` | Return a deep copy of the BMesh. |
| `bm.clear()` | Remove all geometry from the BMesh. |
| `bm.normal_update()` | Recalculate normals for all faces and verts. |
| `bm.transform(matrix, filter=None)` | Transform verts by 4x4 matrix. Filter: `{'SELECT','HIDE','SEAM','SMOOTH','TAG'}`. |
| `bm.select_flush(select)` | Flush selection state up/down. |
| `bm.calc_volume(signed=False)` | Calculate mesh volume from face normals. |

## BMesh Elements

### BMVert

| Attribute | Type | Description |
|-----------|------|-------------|
| `co` | `Vector` | Vertex position (writable) |
| `normal` | `Vector` | Vertex normal (writable) |
| `select` | `bool` | Selection state |
| `hide` | `bool` | Hidden state |
| `tag` | `bool` | Generic script flag |
| `index` | `int` | Index (may be dirty; call `bm.verts.index_update()`) |
| `is_boundary` | `bool` | Connected to boundary edges (read-only) |
| `is_manifold` | `bool` | Manifold vertex (read-only) |
| `is_wire` | `bool` | Not connected to any faces (read-only) |
| `link_edges` | seq of `BMEdge` | Connected edges (read-only) |
| `link_faces` | seq of `BMFace` | Connected faces (read-only) |
| `link_loops` | seq of `BMLoop` | Connected loops (read-only) |

Methods: `select_set(select)`, `hide_set(hide)`, `normal_update()`, `calc_edge_angle(fallback)`, `calc_shell_factor()`.

### BMEdge

| Attribute | Type | Description |
|-----------|------|-------------|
| `verts` | seq of 2 `BMVert` | Edge vertices (read-only) |
| `select` | `bool` | Selection state |
| `hide` | `bool` | Hidden state |
| `seam` | `bool` | UV seam flag |
| `smooth` | `bool` | Smooth shading flag |
| `tag` | `bool` | Generic script flag |
| `index` | `int` | Index |
| `is_boundary` | `bool` | At face boundary (read-only) |
| `is_manifold` | `bool` | Manifold edge (read-only) |
| `is_wire` | `bool` | Not connected to faces (read-only) |
| `is_contiguous` | `bool` | Manifold, same winding (read-only) |
| `link_faces` | seq of `BMFace` | Connected faces (read-only) |
| `link_loops` | seq of `BMLoop` | Connected loops (read-only) |

Methods: `other_vert(vert)`, `calc_length()`, `calc_face_angle(fallback)`, `calc_tangent(loop)`.

### BMFace

| Attribute | Type | Description |
|-----------|------|-------------|
| `normal` | `Vector` | Face normal (writable) |
| `material_index` | `int` | Material slot index |
| `select` | `bool` | Selection state |
| `hide` | `bool` | Hidden state |
| `smooth` | `bool` | Smooth shading |
| `tag` | `bool` | Generic script flag |
| `index` | `int` | Index |
| `verts` | seq of `BMVert` | Face vertices (read-only) |
| `edges` | seq of `BMEdge` | Face edges (read-only) |
| `loops` | seq of `BMLoop` | Face loops/corners (read-only) |

Methods: `calc_area()`, `calc_center_median()`, `calc_center_bounds()`, `calc_perimeter()`, `normal_flip()`, `normal_update()`, `copy(verts=True, edges=True)`.

### BMLoop

Face corner -- accessed via `face.loops`. References one vertex and one edge.

| Attribute | Type | Description |
|-----------|------|-------------|
| `vert` | `BMVert` | The loop's vertex (read-only) |
| `edge` | `BMEdge` | The loop's edge (read-only) |
| `face` | `BMFace` | The loop's face (read-only) |
| `link_loop_next` | `BMLoop` | Next corner in face (read-only) |
| `link_loop_prev` | `BMLoop` | Previous corner in face (read-only) |
| `link_loop_radial_next` | `BMLoop` | Next loop around the edge (read-only) |
| `link_loop_radial_prev` | `BMLoop` | Previous loop around the edge (read-only) |
| `is_convex` | `bool` | Convex corner (read-only) |
| `tag` | `bool` | Generic script flag |

Methods: `calc_angle()`, `calc_normal()`, `calc_tangent()`.

## BMesh Element Sequences

| Sequence | Create | Remove | Lookup |
|----------|--------|--------|--------|
| `bm.verts` (`BMVertSeq`) | `.new(co=(0,0,0))` | `.remove(vert)` | `bm.verts[i]` (after `ensure_lookup_table()`) |
| `bm.edges` (`BMEdgeSeq`) | `.new(verts)` | `.remove(edge)` | `.get(verts, fallback)` - find edge by vert pair |
| `bm.faces` (`BMFaceSeq`) | `.new(verts)` | `.remove(face)` | `.get(verts, fallback)` - find face by verts |

All support: `ensure_lookup_table()`, `index_update()`, `sort(key, reverse)`, `.layers` for custom data.

```python
# Creating geometry manually
bm = bmesh.new()
v1 = bm.verts.new((0, 0, 0))
v2 = bm.verts.new((1, 0, 0))
v3 = bm.verts.new((1, 1, 0))
e = bm.edges.new((v1, v2))
f = bm.faces.new((v1, v2, v3))
bm.faces.ensure_lookup_table()
```

## CustomData Layers

Access custom data through `bm.verts.layers`, `bm.edges.layers`, `bm.faces.layers`, `bm.loops.layers`.

Available layer types per element: `float`, `int`, `bool`, `string`, `float_vector`, `color`, `float_color`.
Vert-specific: `shape`, `deform`, `skin`. Loop-specific: `uv`.

```python
# UV access
uv_lay = bm.loops.layers.uv.active
for face in bm.faces:
    for loop in face.loops:
        uv = loop[uv_lay].uv  # mathutils.Vector 2D
        loop[uv_lay].uv = (0.5, 0.5)
```

```python
# Vertex group (deform) access
dvert_lay = bm.verts.layers.deform.active
group_idx = obj.vertex_groups.active_index
for v in bm.verts:
    v[dvert_lay][group_idx] = 1.0  # set weight
```

```python
# Shape key access
shape_lay = bm.verts.layers.shape["Key.001"]
for v in bm.verts:
    v[shape_lay] = v.co + Vector((0, 0, 1))
```

Layer collections: `.new(name)`, `.remove(layer)`, `.active`, `.get(key)`, `.keys()`, `.verify()`.

## BMesh Operators

All operators take `bm` as first argument and return `dict[str, Any]`.

### Transform

| Operator | Key Parameters |
|----------|---------------|
| `bmesh.ops.translate(bm, vec, verts, space)` | Move verts by offset vector |
| `bmesh.ops.rotate(bm, cent, matrix, verts, space)` | Rotate verts around center |
| `bmesh.ops.scale(bm, vec, verts, space)` | Scale verts by factor |
| `bmesh.ops.transform(bm, matrix, verts, space)` | Apply arbitrary 4x4 matrix |
| `bmesh.ops.mirror(bm, geom, matrix, merge_dist, axis)` | Mirror geometry along axis. Returns `{"geom"}` |

### Extrude

| Operator | Key Parameters |
|----------|---------------|
| `bmesh.ops.extrude_face_region(bm, geom, use_normal_flip)` | Extrude face region (does not move). Returns `{"geom"}` |
| `bmesh.ops.extrude_edge_only(bm, edges)` | Extrude edges into faces. Returns `{"geom"}` |
| `bmesh.ops.extrude_vert_indiv(bm, verts)` | Extrude individual verts as wire edges. Returns `{"verts", "edges"}` |
| `bmesh.ops.extrude_discrete_faces(bm, faces)` | Extrude each face individually. Returns `{"faces"}` |

```python
# Extrude faces and move
ret = bmesh.ops.extrude_face_region(bm, geom=selected_faces)
verts = [e for e in ret["geom"] if isinstance(e, bmesh.types.BMVert)]
bmesh.ops.translate(bm, vec=(0, 0, 1.0), verts=verts)
```

### Subdivide

| Operator | Key Parameters |
|----------|---------------|
| `bmesh.ops.subdivide_edges(bm, edges, cuts, smooth, fractal, use_grid_fill, use_single_edge)` | Subdivide edges with options. Returns `{"geom_inner", "geom_split", "geom"}` |
| `bmesh.ops.subdivide_edgering(bm, edges, cuts, interp_mode, smooth, profile_shape)` | Subdivide edge ring with interpolation |
| `bmesh.ops.bisect_edges(bm, edges, cuts)` | Split edges only (no face changes). Returns `{"geom_split"}` |
| `bmesh.ops.unsubdivide(bm, verts, iterations)` | Reduce grid detail |

### Dissolve

| Operator | Key Parameters |
|----------|---------------|
| `bmesh.ops.dissolve_verts(bm, verts, use_face_split)` | Remove verts, merge faces |
| `bmesh.ops.dissolve_edges(bm, edges, use_verts)` | Remove edges, merge faces. Returns `{"region"}` |
| `bmesh.ops.dissolve_faces(bm, faces, use_verts)` | Merge faces. Returns `{"region"}` |
| `bmesh.ops.dissolve_limit(bm, angle_limit, verts, edges, delimit)` | Dissolve planar faces/colinear edges. `delimit`: `{'NORMAL','MATERIAL','SEAM','SHARP','UV'}` |
| `bmesh.ops.dissolve_degenerate(bm, dist, edges)` | Remove zero-length edges, zero-area faces |

### Fill & Bridge

| Operator | Key Parameters |
|----------|---------------|
| `bmesh.ops.bridge_loops(bm, edges, use_pairs, use_cyclic, twist_offset)` | Bridge two edge loops with faces. Returns `{"faces", "edges"}` |
| `bmesh.ops.grid_fill(bm, edges, mat_nr, use_smooth)` | Fill between 2 edge loops. Returns `{"faces"}` |
| `bmesh.ops.holes_fill(bm, edges, sides)` | Fill boundary holes. Returns `{"faces"}` |
| `bmesh.ops.edgeloop_fill(bm, edges, mat_nr)` | Fill non-overlapping edge loops. Returns `{"faces"}` |
| `bmesh.ops.triangle_fill(bm, edges, use_beauty, use_dissolve)` | Fill with triangles. Returns `{"geom"}` |
| `bmesh.ops.contextual_create(bm, geom, mat_nr)` | F-key equivalent: auto-create faces. Returns `{"faces", "edges"}` |

### Inset & Bevel

| Operator | Key Parameters |
|----------|---------------|
| `bmesh.ops.inset_region(bm, faces, thickness, depth, use_boundary, use_even_offset, use_outset)` | Inset/outset face region. Returns `{"faces"}` |
| `bmesh.ops.inset_individual(bm, faces, thickness, depth, use_even_offset)` | Inset each face individually. Returns `{"faces"}` |
| `bmesh.ops.bevel(bm, geom, offset, offset_type, segments, profile, affect)` | Bevel edges/verts. `affect`: `'VERTICES'` or `'EDGES'`. `offset_type`: `'OFFSET','WIDTH','DEPTH','PERCENT','ABSOLUTE'`. Returns `{"faces","edges","verts"}` |

### Delete & Duplicate

| Operator | Key Parameters |
|----------|---------------|
| `bmesh.ops.delete(bm, geom, context)` | Delete geometry. `context`: `'VERTS','EDGES','FACES_ONLY','EDGES_FACES','FACES','FACES_KEEP_BOUNDARY'` |
| `bmesh.ops.duplicate(bm, geom, dest)` | Duplicate geometry (optionally to another BMesh). Returns `{"geom", "geom_orig"}` |
| `bmesh.ops.split(bm, geom, dest)` | Disconnect and optionally move to another BMesh. Returns `{"geom"}` |

### Other Key Operators

| Operator | Key Parameters |
|----------|---------------|
| `bmesh.ops.spin(bm, geom, cent, axis, angle, steps, dvec)` | Spin/lathe geometry. Returns `{"geom_last"}` |
| `bmesh.ops.triangulate(bm, faces, quad_method, ngon_method)` | Triangulate faces. Returns `{"faces", "edges"}` |
| `bmesh.ops.recalc_face_normals(bm, faces)` | Recalculate outside normals |
| `bmesh.ops.remove_doubles(bm, verts, dist)` | Merge by distance |
| `bmesh.ops.convex_hull(bm, input, use_existing_faces)` | Build convex hull. Returns `{"geom", "geom_interior"}` |
| `bmesh.ops.symmetrize(bm, input, direction, dist)` | Mirror-symmetrize mesh. `direction`: `'-X','-Y','-Z','X','Y','Z'` |
| `bmesh.ops.solidify(bm, geom, thickness)` | Add shell thickness. Returns `{"geom"}` |
| `bmesh.ops.wireframe(bm, faces, thickness, offset)` | Wire-frame copy of faces. Returns `{"faces"}` |
| `bmesh.ops.smooth_vert(bm, verts, factor, use_axis_x/y/z)` | Average-based vertex smooth |
| `bmesh.ops.bisect_plane(bm, geom, plane_co, plane_no, dist, clear_outer, clear_inner)` | Cut mesh with a plane. Returns `{"geom_cut", "geom"}` |

### Primitive Creation

All return `{"verts"}`. All accept optional `matrix` and `calc_uvs` params.

| Operator | Key Parameters |
|----------|---------------|
| `create_cube(bm, size)` | Unit cube |
| `create_circle(bm, segments, radius, cap_ends)` | Circle/disk |
| `create_cone(bm, segments, radius1, radius2, depth, cap_ends)` | Cone/cylinder |
| `create_uvsphere(bm, u_segments, v_segments, radius)` | UV sphere |
| `create_icosphere(bm, subdivisions, radius)` | Ico sphere |
| `create_grid(bm, x_segments, y_segments, size)` | Subdivided plane |

---

## BMesh Utilities

`bmesh.utils` provides low-level topology operations:

| Function | Signature | Description |
|----------|-----------|-------------|
| `edge_split` | `(edge, vert, fac) -> (BMEdge, BMVert)` | Split edge at factor `[0-1]` from vert |
| `edge_rotate` | `(edge, ccw=False) -> BMEdge` | Rotate edge topologically |
| `face_split` | `(face, vert_a, vert_b, coords=(), use_exist=True) -> (BMFace, BMLoop)` | Cut face between two verts |
| `face_split_edgenet` | `(face, edgenet) -> tuple[BMFace, ...]` | Split face by edge network |
| `face_join` | `(faces, remove=True) -> BMFace` | Join faces into one |
| `face_flip` | `(face)` | Flip face normal |
| `face_vert_separate` | `(face, vert) -> BMVert` | Rip vert from face |
| `vert_dissolve` | `(vert) -> bool` | Dissolve vertex |
| `vert_collapse_edge` | `(vert, edge) -> BMEdge` | Collapse vert into edge |
| `vert_collapse_faces` | `(vert, edge, fac, join_faces) -> BMEdge` | Collapse manifold vert |
| `vert_separate` | `(vert, edges) -> tuple[BMVert, ...]` | Separate vert at edges |
| `vert_splice` | `(vert, vert_target)` | Merge vert into target (must not share edge/face) |
| `loop_separate` | `(loop) -> BMVert` | Rip loop corner |

## BMesh Geometry

- `bmesh.geometry.intersect_face_point(face, point) -> bool` -- Test if point projection is inside face.

## Mesh Data Access

`bpy.types.Mesh` stores compact mesh data in object mode via four arrays:

| Collection | Element Type | Description |
|------------|-------------|-------------|
| `mesh.vertices` | `MeshVertex` | 3D positions |
| `mesh.edges` | `MeshEdge` | Pairs of vertex indices |
| `mesh.loops` | `MeshLoop` | Face corners (vertex + edge index) |
| `mesh.polygons` | `MeshPolygon` | Faces referencing loop ranges |

Also: `uv_layers`, `color_attributes`, `vertex_normals`, `polygon_normals`, `corner_normals`, `loop_triangles`, `materials`, `shape_keys`.

### Key Mesh Methods

| Method | Description |
|--------|-------------|
| `from_pydata(vertices, edges, faces, shade_flat=True)` | Build mesh from Python lists |
| `update(calc_edges=False, calc_edges_loose=False)` | Update internal mesh state |
| `calc_loop_triangles()` | Compute tessellation triangles |
| `calc_tangents(uvmap='')` | Compute tangent space |
| `transform(matrix, shape_keys=False)` | Transform all vertices |
| `validate(verbose=False, clean_customdata=True)` | Fix invalid geometry |
| `shade_smooth()` / `shade_flat()` | Set smooth/flat shading |
| `flip_normals()` | Invert all polygon winding |
| `set_sharp_from_angle(angle=pi)` | Mark sharp edges by face angle |
| `clear_geometry()` | Remove all geometry (keeps materials/shape keys) |

## Mesh Element Types

### MeshVertex
`co` (Vector), `normal` (Vector, readonly), `select` (bool), `hide` (bool), `index` (int, readonly), `groups` (vertex group weights, readonly), `undeformed_co` (Vector, readonly).

### MeshEdge
`vertices` (int[2]), `select` (bool), `hide` (bool), `use_seam` (bool), `use_edge_sharp` (bool), `is_loose` (bool, readonly), `index` (int, readonly), `key` (readonly tuple).

### MeshPolygon
`vertices` (int[]), `loop_start` (int), `loop_total` (int, readonly), `material_index` (int), `normal` (Vector, readonly), `center` (Vector, readonly), `area` (float, readonly), `select` (bool), `hide` (bool), `use_smooth` (bool), `loop_indices` (readonly), `edge_keys` (readonly). Method: `flip()`.

### MeshLoop
`vertex_index` (int), `edge_index` (int), `normal` (Vector, readonly), `tangent` (Vector, readonly), `bitangent_sign` (float, readonly), `index` (int, readonly).

## Performance: foreach_get/set Pattern

Use `foreach_get`/`foreach_set` for bulk data access (much faster than per-element loops):

```python
import numpy as np

me = bpy.context.object.data
count = len(me.vertices)

# Read all vertex positions into numpy array
coords = np.empty(count * 3, dtype=np.float64)
me.vertices.foreach_get("co", coords)
coords = coords.reshape((count, 3))

# Modify and write back
coords[:, 2] += 1.0  # shift all Z up
me.vertices.foreach_set("co", coords.ravel())
me.update()
```

Works with any flat attribute: `"co"`, `"normal"`, `"select"`, `"hide"`, `"vertices"`, `"material_index"`, etc.
