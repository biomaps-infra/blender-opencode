# Materials and Nodes Reference

Blender 5.0 Python API -- shader node trees and node-based material creation.

## Table of Contents

- [Material Basics](#material-basics) -- creating, assigning, removing
- [Node Tree Setup](#node-tree-setup) -- accessing nodes/links, clearing defaults
- [Node Creation Pattern](#node-creation-pattern) -- `nodes.new()`, socket access
- [Linking Nodes](#linking-nodes) -- `links.new()` pattern
- [Key Shader Nodes](#key-shader-nodes) -- Principled BSDF, Image Texture, Mix, Math, Mapping, TexCoord, Normal Map, Noise, Color Ramp
- [Common Recipes](#common-recipes) -- PBR, image-based, procedural

---

## Material Basics

### Creating a Material

```python
import bpy

mat = bpy.data.materials.new(name="MyMaterial")
```

Key `Material` properties:
- `node_tree` -- `NodeTree` (readonly) -- the shader node tree
- `diffuse_color` -- float[4], default `(0.8, 0.8, 0.8, 1.0)`
- `metallic` -- float [0,1] | `roughness` -- float [0,1]
- `surface_render_method` -- `'DITHERED'` | `'BLENDED'`
- `displacement_method` -- `'BUMP'` | `'DISPLACEMENT'` | `'BOTH'`
- `use_backface_culling` -- bool, default False

> `use_nodes` is deprecated in 5.0 (always True). Materials always use nodes.

### Assigning and Removing Materials

```python
obj = bpy.context.active_object
obj.data.materials.append(mat)  # add to material slots
obj.active_material = mat       # set active slot
bpy.data.materials.remove(mat)  # delete material
```

---

## Node Tree Setup

Every material has a `node_tree` (`ShaderNodeTree`) with `.nodes` and `.links` collections.

`ShaderNodeTree` inherits from `NodeTree` and provides:
- `nodes` -- `bpy_prop_collection` of `Node` (readonly)
- `links` -- `bpy_prop_collection` of `NodeLink` (readonly)
- `get_output_node(target)` -- target: `'ALL'` | `'EEVEE'` | `'CYCLES'`

### Clearing Default Nodes

```python
mat = bpy.data.materials.new(name="Custom")
nodes = mat.node_tree.nodes
nodes.clear()  # remove all default nodes
```

### Accessing Existing Nodes

```python
nodes = mat.node_tree.nodes
principled = nodes.get("Principled BSDF")
output = nodes.get("Material Output")
```

---

## Node Creation Pattern

All shader nodes are created via `node_tree.nodes.new(type_string)`:

```python
node = mat.node_tree.nodes.new('ShaderNodeBsdfPrincipled')
node.location = (-300, 0)
node.label = "My Shader"
```

Common `Node` properties: `name`, `label`, `location` (Vector), `inputs`, `outputs`, `mute`, `hide`.

### Accessing Sockets

```python
node.inputs['Base Color'].default_value = (1, 0, 0, 1)  # by name
node.inputs[0].default_value = (1, 0, 0, 1)             # by index
```

`NodeSocket` key properties: `name`, `default_value`, `is_linked` (readonly), `enabled`, `hide`.

---

## Linking Nodes

Links connect an output socket to an input socket:

```python
links = mat.node_tree.links
links.new(node_a.outputs['BSDF'], node_b.inputs['Surface'])
```

**Pattern:** `links.new(from_socket, to_socket)`

`NodeLink` properties: `from_node`, `to_node`, `from_socket`, `to_socket` (all readonly), `is_valid`, `is_muted`.

Remove a link: `links.remove(link)`

---

## Key Shader Nodes

### Principled BSDF

**Type string:** `'ShaderNodeBsdfPrincipled'`

Physically-based surface shader (OpenPBR model).

**Node properties:**
- `distribution` -- `'GGX'` | `'MULTI_GGX'`
- `subsurface_method` -- `'BURLEY'` | `'RANDOM_WALK'` | `'RANDOM_WALK_SKIN'`

**Input sockets:**

| Socket Name | Type | Default |
|---|---|---|
| `Base Color` | RGBA | (0.8, 0.8, 0.8, 1.0) |
| `Metallic` | Float | 0.0 |
| `Roughness` | Float | 0.5 |
| `IOR` | Float | 1.5 |
| `Alpha` | Float | 1.0 |
| `Normal` | Vector | -- |
| `Subsurface Weight` | Float | 0.0 |
| `Subsurface Radius` | Vector | (1.0, 0.2, 0.1) |
| `Subsurface Scale` | Float | 0.05 |
| `Specular IOR Level` | Float | 0.5 |
| `Specular Tint` | RGBA | (1, 1, 1, 1) |
| `Anisotropic` | Float | 0.0 |
| `Anisotropic Rotation` | Float | 0.0 |
| `Tangent` | Vector | -- |
| `Transmission Weight` | Float | 0.0 |
| `Coat Weight` | Float | 0.0 |
| `Coat Roughness` | Float | 0.03 |
| `Coat IOR` | Float | 1.5 |
| `Coat Tint` | RGBA | (1, 1, 1, 1) |
| `Coat Normal` | Vector | -- |
| `Sheen Weight` | Float | 0.0 |
| `Sheen Roughness` | Float | 0.5 |
| `Emission Color` | RGBA | (1, 1, 1, 1) |
| `Emission Strength` | Float | 0.0 |

**Output sockets:** `BSDF`

```python
bsdf = nodes.new('ShaderNodeBsdfPrincipled')
bsdf.inputs['Base Color'].default_value = (0.8, 0.1, 0.1, 1.0)
bsdf.inputs['Roughness'].default_value = 0.4
```

### Material Output

**Type string:** `'ShaderNodeOutputMaterial'`

**Node properties:** `is_active_output` (bool), `target` -- `'ALL'` | `'EEVEE'` | `'CYCLES'`

**Input sockets:** `Surface`, `Volume`, `Displacement`, `Thickness`

### Image Texture

**Type string:** `'ShaderNodeTexImage'`

**Node properties:**
- `image` -- `Image` data-block
- `interpolation` -- `'Linear'` | `'Closest'` | `'Cubic'` | `'Smart'`
- `projection` -- `'FLAT'` | `'BOX'` | `'SPHERE'` | `'TUBE'`
- `extension` -- `'REPEAT'` | `'EXTEND'` | `'CLIP'` | `'MIRROR'`

**Inputs:** `Vector` | **Outputs:** `Color`, `Alpha`

```python
tex = nodes.new('ShaderNodeTexImage')
tex.image = bpy.data.images.load("/path/to/texture.png")
tex.interpolation = 'Linear'
```

### Mix

**Type string:** `'ShaderNodeMix'`

**Node properties:**
- `data_type` -- `'FLOAT'` | `'VECTOR'` | `'RGBA'` | `'ROTATION'`
- `blend_type` -- Ramp Blend Items (default `'MIX'`)
- `clamp_factor` / `clamp_result` -- bool
- `factor_mode` -- `'UNIFORM'` | `'NON_UNIFORM'`

**Input sockets (vary by data_type):** `Factor`, `A`, `B`
**Output sockets:** `Result`

```python
mix = nodes.new('ShaderNodeMix')
mix.data_type = 'RGBA'
mix.inputs['Factor'].default_value = 0.5
```

### Math

**Type string:** `'ShaderNodeMath'`

**Node properties:**
- `operation` -- `'ADD'`, `'SUBTRACT'`, `'MULTIPLY'`, `'DIVIDE'`, `'POWER'`, `'SQRT'`, `'ABSOLUTE'`, `'MINIMUM'`, `'MAXIMUM'`, `'LESS_THAN'`, `'GREATER_THAN'`, `'ROUND'`, `'FLOOR'`, `'CEIL'`, `'FRACT'`, `'MODULO'`, `'SNAP'`, `'SINE'`, `'COSINE'`, `'TANGENT'`, `'ARCTAN2'`, `'RADIANS'`, `'DEGREES'`, `'COMPARE'`, `'MULTIPLY_ADD'`, `'SIGN'`, and more
- `use_clamp` -- bool

**Input sockets:** `Value` (up to 3 depending on operation)
**Output sockets:** `Value`

```python
math = nodes.new('ShaderNodeMath')
math.operation = 'MULTIPLY'
math.inputs[0].default_value = 2.0
math.inputs[1].default_value = 0.5
```

### Mapping

**Type string:** `'ShaderNodeMapping'`

Transform input vectors (translation, rotation, scale).

**Node properties:** `vector_type` -- `'POINT'` | `'TEXTURE'` | `'VECTOR'` | `'NORMAL'`

**Inputs:** `Vector`, `Location`, `Rotation`, `Scale` | **Outputs:** `Vector`

```python
mapping = nodes.new('ShaderNodeMapping')
mapping.vector_type = 'POINT'
mapping.inputs['Scale'].default_value = (2.0, 2.0, 2.0)
```

### Texture Coordinate

**Type string:** `'ShaderNodeTexCoord'`

Provides UV and other coordinate outputs for texture mapping.

**Node properties:** `object` -- `Object` reference, `from_instancer` -- bool

**Inputs:** (none)
**Outputs:** `Generated`, `Normal`, `UV`, `Object`, `Camera`, `Window`, `Reflection`

```python
texcoord = nodes.new('ShaderNodeTexCoord')
links.new(texcoord.outputs['UV'], mapping.inputs['Vector'])
```

### Normal Map

**Type string:** `'ShaderNodeNormalMap'`

Convert RGB normal map image to perturbed normals.

**Node properties:**
- `space` -- `'TANGENT'` | `'OBJECT'` | `'WORLD'` | `'BLENDER_OBJECT'` | `'BLENDER_WORLD'`
- `uv_map` -- string (UV map name)

**Inputs:** `Strength` (Float), `Color` (RGBA) | **Outputs:** `Normal`

```python
nmap = nodes.new('ShaderNodeNormalMap')
nmap.space = 'TANGENT'
links.new(normal_tex.outputs['Color'], nmap.inputs['Color'])
links.new(nmap.outputs['Normal'], bsdf.inputs['Normal'])
```

### Noise Texture

**Type string:** `'ShaderNodeTexNoise'`

Generate fractal Perlin noise.

**Node properties:**
- `noise_dimensions` -- `'1D'` | `'2D'` | `'3D'` | `'4D'`
- `noise_type` -- `'FBM'` | `'MULTIFRACTAL'` | `'RIDGED_MULTIFRACTAL'` | `'HYBRID_MULTIFRACTAL'` | `'HETERO_TERRAIN'`

**Inputs:** `Vector`, `W`, `Scale`, `Detail`, `Roughness`, `Lacunarity`, `Distortion`
**Outputs:** `Fac`, `Color`

```python
noise = nodes.new('ShaderNodeTexNoise')
noise.noise_dimensions = '3D'
noise.inputs['Scale'].default_value = 5.0
noise.inputs['Detail'].default_value = 2.0
```

### Color Ramp (ValToRGB)

**Type string:** `'ShaderNodeValToRGB'`

Map scalar values to colors via a gradient.

**Node properties:** `color_ramp` -- `ColorRamp` (readonly), access stops via `.elements`

**Inputs:** `Fac` (Float [0,1]) | **Outputs:** `Color`, `Alpha`

```python
ramp = nodes.new('ShaderNodeValToRGB')
ramp.color_ramp.elements[0].position = 0.0
ramp.color_ramp.elements[0].color = (0, 0, 0, 1)
ramp.color_ramp.elements[1].position = 1.0
ramp.color_ramp.elements[1].color = (1, 1, 1, 1)
# Add a middle stop
mid = ramp.color_ramp.elements.new(0.5)
mid.color = (1, 0, 0, 1)
```

---

## Common Recipes

### PBR Material Setup

```python
import bpy
mat = bpy.data.materials.new(name="PBR_Material")
nodes = mat.node_tree.nodes
links = mat.node_tree.links
nodes.clear()
output = nodes.new('ShaderNodeOutputMaterial')
bsdf = nodes.new('ShaderNodeBsdfPrincipled')
bsdf.inputs['Base Color'].default_value = (0.8, 0.2, 0.1, 1.0)
bsdf.inputs['Metallic'].default_value = 0.0
bsdf.inputs['Roughness'].default_value = 0.4
links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])
bpy.context.active_object.data.materials.append(mat)
```

### Image-Based Material (with Normal Map)

```python
import bpy
mat = bpy.data.materials.new(name="Textured")
nodes = mat.node_tree.nodes
links = mat.node_tree.links
nodes.clear()
output = nodes.new('ShaderNodeOutputMaterial')
bsdf = nodes.new('ShaderNodeBsdfPrincipled')
tex = nodes.new('ShaderNodeTexImage')
tex.image = bpy.data.images.load("//textures/diffuse.png")
nmap_tex = nodes.new('ShaderNodeTexImage')
nmap_tex.image = bpy.data.images.load("//textures/normal.png")
nmap_tex.image.colorspace_settings.name = 'Non-Color'
nmap = nodes.new('ShaderNodeNormalMap')
links.new(tex.outputs['Color'], bsdf.inputs['Base Color'])
links.new(nmap_tex.outputs['Color'], nmap.inputs['Color'])
links.new(nmap.outputs['Normal'], bsdf.inputs['Normal'])
links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])
```

### Procedural Material (Noise + Color Ramp)

```python
import bpy
mat = bpy.data.materials.new(name="Procedural")
nodes = mat.node_tree.nodes
links = mat.node_tree.links
nodes.clear()
output = nodes.new('ShaderNodeOutputMaterial')
bsdf = nodes.new('ShaderNodeBsdfPrincipled')
noise = nodes.new('ShaderNodeTexNoise')
noise.noise_dimensions = '3D'
noise.inputs['Scale'].default_value = 8.0
ramp = nodes.new('ShaderNodeValToRGB')
ramp.color_ramp.elements[0].color = (0.1, 0.05, 0.02, 1)
ramp.color_ramp.elements[1].color = (0.8, 0.6, 0.3, 1)
coord = nodes.new('ShaderNodeTexCoord')
links.new(coord.outputs['Generated'], noise.inputs['Vector'])
links.new(noise.outputs['Fac'], ramp.inputs['Fac'])
links.new(ramp.outputs['Color'], bsdf.inputs['Base Color'])
links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])
```

### Additional Node Type Strings

| Node | Type String |
|---|---|
| Diffuse BSDF | `ShaderNodeBsdfDiffuse` |
| Glass BSDF | `ShaderNodeBsdfGlass` |
| Transparent BSDF | `ShaderNodeBsdfTransparent` |
| Emission | `ShaderNodeEmission` |
| Mix Shader | `ShaderNodeMixShader` |
| Add Shader | `ShaderNodeAddShader` |
| Separate XYZ | `ShaderNodeSeparateXYZ` |
| Combine XYZ | `ShaderNodeCombineXYZ` |
| RGB Curves | `ShaderNodeRGBCurve` |
| Bump | `ShaderNodeBump` |
| Fresnel | `ShaderNodeFresnel` |
| Voronoi Texture | `ShaderNodeTexVoronoi` |
| Checker Texture | `ShaderNodeTexChecker` |
| Object Info | `ShaderNodeObjectInfo` |
| Geometry | `ShaderNodeNewGeometry` |
