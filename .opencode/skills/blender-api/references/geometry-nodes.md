# Geometry Nodes Reference

> Blender 5.0 Python API -- programmatic creation and manipulation of Geometry Node trees.

## Table of Contents

- [Class Hierarchy](#class-hierarchy)
- [Geometry Node Tree Setup](#geometry-node-tree-setup)
- [Assigning via NodesModifier](#assigning-via-nodesmodifier)
- [Node Creation](#node-creation)
- [Input and Output Nodes](#input-and-output-nodes)
- [Exposing Parameters via Tree Interface](#exposing-parameters-via-tree-interface)
- [Linking Nodes](#linking-nodes)
- [Accessing Modifier Inputs from Python](#accessing-modifier-inputs-from-python)
- [Common Geometry Node Types](#common-geometry-node-types)
- [Complete Workflow Example](#complete-workflow-example)
- [Key Patterns and Tips](#key-patterns-and-tips)

---

## Class Hierarchy

```
NodeTree (ID)
  └── GeometryNodeTree          # tree.type == 'GEOMETRY'

Node (bpy_struct)
  └── NodeInternal
        └── GeometryNode        # base for all geometry nodes
              └── GeometryNodeGroup   # references another node tree

Modifier (bpy_struct)
  └── NodesModifier             # modifier that holds a GeometryNodeTree
```

Key inherited properties from `NodeTree`: `nodes`, `links`, `interface`.
Key inherited properties from `Node`: `inputs`, `outputs`, `location`, `name`, `label`, `mute`.

---

## Geometry Node Tree Setup

Create a new geometry node tree via `bpy.data.node_groups`:

```python
import bpy
tree = bpy.data.node_groups.new("MyGeoNodes", 'GeometryNodeTree')
```

The tree is created empty. You must add Group Input/Output nodes manually.

### GeometryNodeTree Properties

| Property | Type | Description |
|---|---|---|
| `is_modifier` | bool | Tree is used as a geometry modifier |
| `is_tool` | bool | Tree is used as a tool |
| `is_type_mesh` | bool | Tree is used for meshes |
| `is_type_curve` | bool | Tree is used for curves |
| `nodes` | `Nodes` collection | All nodes in the tree |
| `links` | `NodeLinks` collection | All links between nodes |
| `interface` | `NodeTreeInterface` | Input/output socket declarations |

---

## Assigning via NodesModifier

Add a Geometry Nodes modifier to an object and assign the tree:

```python
obj = bpy.context.active_object
mod = obj.modifiers.new("GeoNodes", 'NODES')
mod.node_group = tree
```

### NodesModifier Properties

| Property | Type | Description |
|---|---|---|
| `node_group` | `NodeTree` | The geometry node tree |
| `bake_directory` | str | On-disk bake path |
| `bake_target` | `'PACKED'`/`'DISK'` | Bake storage location |
| `show_viewport` | bool | Show in viewport (inherited) |
| `show_render` | bool | Show in render (inherited) |
| `show_group_selector` | bool | Show node group selector |

---

## Node Creation

Add nodes with `tree.nodes.new(type)` where `type` is the `bl_idname` string:

```python
cube = tree.nodes.new('GeometryNodeMeshPrimitiveCube')
cube.location = (0, 0)
cube.inputs["Size"].default_value = (2.0, 2.0, 2.0)
```

Remove a node:

```python
tree.nodes.remove(cube)
```

### Node Properties (inherited from Node)

| Property | Type | Description |
|---|---|---|
| `inputs` | `NodeInputs` | Input sockets collection |
| `outputs` | `NodeOutputs` | Output sockets collection |
| `location` | Vector(2) | Position in the editor |
| `name` | str | Unique identifier in the tree |
| `label` | str | Custom display label |
| `mute` | bool | Mute/bypass the node |
| `hide` | bool | Collapse the node |
| `width` | float | Node width |

---

## Input and Output Nodes

Every geometry node tree needs Group Input and Group Output nodes to receive and emit geometry:

```python
group_in = tree.nodes.new('NodeGroupInput')
group_out = tree.nodes.new('NodeGroupOutput')
group_in.location = (-300, 0)
group_out.location = (300, 0)
```

These nodes automatically gain sockets that match the tree's `interface` definition.

---

## Exposing Parameters via Tree Interface

Use `tree.interface` to add input/output sockets visible on the modifier panel:

```python
# Add geometry input (required for modifier to work)
tree.interface.new_socket("Geometry", in_out='INPUT', socket_type='NodeSocketGeometry')
tree.interface.new_socket("Geometry", in_out='OUTPUT', socket_type='NodeSocketGeometry')

# Add a user-facing float parameter
tree.interface.new_socket("Scale", in_out='INPUT', socket_type='NodeSocketFloat')
```

### Common Socket Types

| Socket Type String | Data Type |
|---|---|
| `NodeSocketGeometry` | Geometry |
| `NodeSocketFloat` | Float |
| `NodeSocketInt` | Integer |
| `NodeSocketBool` | Boolean |
| `NodeSocketVector` | Vector (3D) |
| `NodeSocketColor` | Color (RGBA) |
| `NodeSocketString` | String |
| `NodeSocketMaterial` | Material |
| `NodeSocketObject` | Object |
| `NodeSocketCollection` | Collection |
| `NodeSocketImage` | Image |

---

## Linking Nodes

Connect output sockets to input sockets with `tree.links.new()`:

```python
# Link by socket index
tree.links.new(group_in.outputs[0], cube.inputs[0])

# Link by socket name
tree.links.new(cube.outputs["Mesh"], group_out.inputs["Geometry"])
```

Remove a link:

```python
tree.links.remove(link)
```

### NodeLink Properties

| Property | Type | Description |
|---|---|---|
| `from_node` | `Node` | Source node (readonly) |
| `from_socket` | `NodeSocket` | Source socket (readonly) |
| `to_node` | `Node` | Target node (readonly) |
| `to_socket` | `NodeSocket` | Target socket (readonly) |
| `is_valid` | bool | Link is valid |
| `is_muted` | bool | Link is muted |

---

## Accessing Modifier Inputs from Python

After exposing inputs via `tree.interface`, set their values through the modifier using identifier-based access:

```python
# The modifier exposes interface sockets as indexed items
# Use the socket identifier from the interface
mod = obj.modifiers["GeoNodes"]

# Set values via the modifier's item interface
# Socket identifiers are auto-generated; find them via:
for item in tree.interface.items_tree:
    if item.item_type == 'SOCKET':
        print(item.name, item.identifier, item.in_out)

# Set input value using the identifier
mod[item.identifier] = 2.5

# For object/collection/material inputs, use _use_attribute suffix pattern
# mod["Socket_2"] = some_object
```

Alternatively, use `default_value` on the Group Input node's sockets:

```python
group_in.outputs["Scale"].default_value = 1.5
```

---

## Common Geometry Node Types

### Mesh Primitives

| `bl_idname` | UI Name |
|---|---|
| `GeometryNodeMeshPrimitiveCube` | Mesh Cube |
| `GeometryNodeMeshPrimitiveCylinder` | Mesh Cylinder |
| `GeometryNodeMeshPrimitiveCone` | Mesh Cone |
| `GeometryNodeMeshPrimitiveUVSphere` | Mesh UV Sphere |
| `GeometryNodeMeshPrimitiveIcoSphere` | Mesh Ico Sphere |
| `GeometryNodeMeshPrimitiveGrid` | Mesh Grid |
| `GeometryNodeMeshPrimitiveLine` | Mesh Line |
| `GeometryNodeMeshPrimitiveCircle` | Mesh Circle |

### Geometry Operations

| `bl_idname` | UI Name |
|---|---|
| `GeometryNodeJoinGeometry` | Join Geometry |
| `GeometryNodeSetPosition` | Set Position |
| `GeometryNodeTransform` | Transform Geometry |
| `GeometryNodeDeleteGeometry` | Delete Geometry |
| `GeometryNodeDuplicateElements` | Duplicate Elements |
| `GeometryNodeMergeByDistance` | Merge by Distance |
| `GeometryNodeBoundBox` | Bounding Box |
| `GeometryNodeConvexHull` | Convex Hull |
| `GeometryNodeGeometryToInstance` | Geometry to Instance |
| `GeometryNodeSeparateGeometry` | Separate Geometry |

### Mesh Operations

| `bl_idname` | UI Name |
|---|---|
| `GeometryNodeExtrudeMesh` | Extrude Mesh |
| `GeometryNodeSubdivisionSurface` | Subdivision Surface |
| `GeometryNodeSubdivideMesh` | Subdivide Mesh |
| `GeometryNodeDualMesh` | Dual Mesh |
| `GeometryNodeFlipFaces` | Flip Faces |
| `GeometryNodeMeshBoolean` | Mesh Boolean |
| `GeometryNodeSetShadeSmooth` | Set Shade Smooth |

### Curve Operations

| `bl_idname` | UI Name |
|---|---|
| `GeometryNodeCurveToMesh` | Curve to Mesh |
| `GeometryNodeCurveToPoints` | Curve to Points |
| `GeometryNodeFillCurve` | Fill Curve |
| `GeometryNodeFilletCurve` | Fillet Curve |
| `GeometryNodeCurvePrimitiveCircle` | Curve Circle |
| `GeometryNodeCurvePrimitiveLine` | Curve Line |

### Instances

| `bl_idname` | UI Name |
|---|---|
| `GeometryNodeInstanceOnPoints` | Instance on Points |
| `GeometryNodeRealizeInstances` | Realize Instances |
| `GeometryNodeRotateInstances` | Rotate Instances |
| `GeometryNodeScaleInstances` | Scale Instances |
| `GeometryNodeTranslateInstances` | Translate Instances |
| `GeometryNodeCollectionInfo` | Collection Info |
| `GeometryNodeObjectInfo` | Object Info |

### Point Distribution

| `bl_idname` | UI Name |
|---|---|
| `GeometryNodeDistributePointsOnFaces` | Distribute Points on Faces |
| `GeometryNodeDistributePointsInVolume` | Distribute Points in Volume |
| `GeometryNodeDistributePointsInGrid` | Distribute Points in Grid |

### Attributes and Fields

| `bl_idname` | UI Name |
|---|---|
| `GeometryNodeAttributeStatistic` | Attribute Statistic |
| `GeometryNodeCaptureAttribute` | Capture Attribute |
| `GeometryNodeStoreNamedAttribute` | Store Named Attribute |
| `GeometryNodeInputNamedAttribute` | Named Attribute |
| `GeometryNodeAttributeDomainSize` | Domain Size |
| `GeometryNodeFieldOnDomain` | Evaluate on Domain |
| `GeometryNodeFieldAtIndex` | Evaluate at Index |
| `GeometryNodeAccumulateField` | Accumulate Field |

### Input Nodes

| `bl_idname` | UI Name |
|---|---|
| `GeometryNodeInputPosition` | Position |
| `GeometryNodeInputNormal` | Normal |
| `GeometryNodeInputIndex` | Index |
| `GeometryNodeInputID` | ID |
| `GeometryNodeInputMeshEdgeVertices` | Edge Vertices |
| `GeometryNodeInputMeshFaceArea` | Face Area |
| `GeometryNodeInputMeshFaceNeighbors` | Face Neighbors |

### Utilities (Math/Logic)

| `bl_idname` | UI Name |
|---|---|
| `ShaderNodeMath` | Math |
| `ShaderNodeVectorMath` | Vector Math |
| `FunctionNodeCompare` | Compare |
| `FunctionNodeBooleanMath` | Boolean Math |
| `ShaderNodeMapRange` | Map Range |
| `ShaderNodeClamp` | Clamp |
| `FunctionNodeRandomValue` | Random Value |
| `GeometryNodeSwitch` | Switch |

> **Note:** Some utility nodes use `ShaderNode*` or `FunctionNode*` prefixes even in geometry node trees.

---

## Complete Workflow Example

Create a scattered-cubes setup from scratch:

```python
import bpy

# 1. Create geometry node tree
tree = bpy.data.node_groups.new("ScatterCubes", 'GeometryNodeTree')

# 2. Define interface (inputs/outputs)
tree.interface.new_socket("Geometry", in_out='INPUT', socket_type='NodeSocketGeometry')
tree.interface.new_socket("Geometry", in_out='OUTPUT', socket_type='NodeSocketGeometry')
tree.interface.new_socket("Density", in_out='INPUT', socket_type='NodeSocketFloat')

# 3. Create nodes
group_in = tree.nodes.new('NodeGroupInput')
group_out = tree.nodes.new('NodeGroupOutput')
scatter = tree.nodes.new('GeometryNodeDistributePointsOnFaces')
cube = tree.nodes.new('GeometryNodeMeshPrimitiveCube')
instance = tree.nodes.new('GeometryNodeInstanceOnPoints')

# 4. Position nodes
group_in.location = (-400, 0)
scatter.location = (-100, 100)
cube.location = (-100, -100)
instance.location = (200, 0)
group_out.location = (450, 0)

# 5. Link nodes
links = tree.links
links.new(group_in.outputs["Geometry"], scatter.inputs["Mesh"])
links.new(group_in.outputs["Density"], scatter.inputs["Density"])
links.new(scatter.outputs["Points"], instance.inputs["Points"])
links.new(cube.outputs["Mesh"], instance.inputs["Instance"])
links.new(instance.outputs["Instances"], group_out.inputs["Geometry"])

# 6. Assign to object via modifier
obj = bpy.context.active_object
mod = obj.modifiers.new("ScatterCubes", 'NODES')
mod.node_group = tree
```

---

## Key Patterns and Tips

**Finding a node by name:**
```python
node = tree.nodes.get("MyNode")  # returns None if missing
```

**Setting enum/mode on a node:**
```python
math = tree.nodes.new('ShaderNodeMath')
math.operation = 'MULTIPLY'
```

**Setting socket defaults by index vs name:**
```python
node.inputs[0].default_value = 1.0        # by index
node.inputs["Value"].default_value = 1.0   # by name
```

**Iterating all links:**
```python
for link in tree.links:
    print(f"{link.from_node.name}:{link.from_socket.name} -> "
          f"{link.to_node.name}:{link.to_socket.name}")
```

**Clearing all nodes in a tree:**
```python
tree.nodes.clear()
```

**Using a node group inside another tree:**
```python
group_node = tree.nodes.new('GeometryNodeGroup')
group_node.node_tree = bpy.data.node_groups["OtherGeoNodes"]
```
