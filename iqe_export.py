# Inter-Quake Export
#
# TODO: generalize vertex array output logic
# TODO: multiple vertex color layers
# TODO: multiple texture coordinate layers
#

bl_info = {
	"name": "Export Inter-Quake Model (.iqe)",
	"description": "Export Inter-Quake Model.",
	"author": "Tor Andersson",
	"version": (2012, 12, 2),
	"blender": (2, 6, 4),
	"location": "File > Export > Inter-Quake Model",
	"wiki_url": "http://github.com/ccxvii/asstools",
	"category": "Import-Export",
}

import bpy, math, struct, os, sys

from bpy.props import *
from bpy_extras.io_utils import ExportHelper
from mathutils import Matrix, Quaternion, Vector

def gather_attributes(attributes, vertex_groups, bones):
	for g in vertex_groups:
		if not g.name in bones:
			if g.name.endswith('.x'): name, count = g.name[:-2], 1
			elif g.name.endswith('.y'): name, count = g.name[:-2], 2
			elif g.name.endswith('.z'): name, count = g.name[:-2], 3
			elif g.name.endswith('.w'): name, count = g.name[:-2], 4
			else: name, count = g.name, 1
			if name in attributes:
				attributes[name] = max(count, attributes[name])
			else:
				attributes[name] = count

def export_attributes(file, attributes):
	list = []
	if len(attributes):
		file.write("\n")
	for name in attributes:
		count = attributes[name]
		file.write("vertexarray custom%d ubyte %d \"%s\"\n" % (len(list), count, name))
		list.append((name, count))
	return list

def make_attribute(groups, vertex_groups, attribute):
	name, count = attribute
	x, y, z, w = 0, 0, 0, 0
	for g in groups:
		if count == 1 and vertex_groups[g.group].name == name: x = g.weight
		if count >= 1 and vertex_groups[g.group].name == name + ".x": x = g.weight
		if count >= 2 and vertex_groups[g.group].name == name + ".y": y = g.weight
		if count >= 3 and vertex_groups[g.group].name == name + ".z": z = g.weight
		if count >= 4 and vertex_groups[g.group].name == name + ".w": w = g.weight
	if count == 1: return (x,)
	if count == 2: return x, y
	if count == 3: return x, y, z
	return x, y, z, w

def make_blend(groups, vertex_groups, bones):
	vb = []
	for g in groups:
		n = vertex_groups[g.group].name
		if n in bones:
			vb += [ bones[n], g.weight ]
	return tuple(vb)

def export_mesh_data(file, mesh, mesh_name, vertex_groups, bones, attributes):
	print("exporting mesh:", mesh_name)

	texcoords = mesh.tessface_uv_textures.active
	colors = mesh.tessface_vertex_colors.active

	out = {}
	for face in mesh.tessfaces:
		fm = face.material_index
		if not fm in out:
			out[fm] = []
		out[fm].append(face)

	for fm in out.keys():
		vertex_map = {}
		vertex_list = []
		face_list = []

		for face in out[fm]:
			ft = texcoords and texcoords.data[face.index]
			fc = colors and colors.data[face.index]
			ft = ft and [ft.uv1, ft.uv2, ft.uv3, ft.uv4]
			fc = fc and [fc.color1, fc.color2, fc.color3, fc.color4]
			f = []
			for i, v in enumerate(face.vertices):
				vp = tuple(mesh.vertices[v].co)
				vn = tuple(mesh.vertices[v].normal) if face.use_smooth else tuple(face.normal)
				vt = ft and tuple(ft[i])
				vc = fc and tuple(fc[i])
				vb = bones and make_blend(mesh.vertices[v].groups, vertex_groups, bones)
				v0 = len(attributes) > 0 and make_attribute(mesh.vertices[v].groups, vertex_groups, attributes[0])
				v1 = len(attributes) > 1 and make_attribute(mesh.vertices[v].groups, vertex_groups, attributes[1])
				v2 = len(attributes) > 2 and make_attribute(mesh.vertices[v].groups, vertex_groups, attributes[2])
				v3 = len(attributes) > 3 and make_attribute(mesh.vertices[v].groups, vertex_groups, attributes[3])
				v4 = len(attributes) > 4 and make_attribute(mesh.vertices[v].groups, vertex_groups, attributes[4])
				v5 = len(attributes) > 5 and make_attribute(mesh.vertices[v].groups, vertex_groups, attributes[5])
				v6 = len(attributes) > 6 and make_attribute(mesh.vertices[v].groups, vertex_groups, attributes[6])
				v7 = len(attributes) > 7 and make_attribute(mesh.vertices[v].groups, vertex_groups, attributes[7])
				v8 = len(attributes) > 8 and make_attribute(mesh.vertices[v].groups, vertex_groups, attributes[8])
				v9 = len(attributes) > 9 and make_attribute(mesh.vertices[v].groups, vertex_groups, attributes[9])
				v = vp, vn, vt, vc, vb, v0, v1, v2, v3, v4, v5, v6, v7, v8, v9
				if v not in vertex_map:
					vertex_map[v] = len(vertex_list)
					vertex_list.append(v)
				f.append(vertex_map[v])
			face_list.append(f)

		file.write("\n")
		file.write("mesh \"%s\"\n" % mesh_name)
		file.write("material \"%s\"\n" % mesh.materials[fm].name)
		for vp, vn, vt, vc, vb, v0, v1, v2, v3, v4, v5, v6, v7, v8, v9 in vertex_list:
			file.write("vp %.9g %.9g %.9g\n" % vp)
			file.write("vn %.9g %.9g %.9g\n" % vn)
			if vt: file.write("vt %.9g %.9g\n" % (vt[0], 1.0 - vt[1]))
			if vc: file.write("vc %.9g %.9g %.9g\n" % vc)
			if vb: file.write("vb %s\n" % " ".join("%.9g" % x for x in vb))
			if v0: file.write("v0 %s\n" % " ".join("%.9g" % x for x in v0))
			if v1: file.write("v1 %s\n" % " ".join("%.9g" % x for x in v1))
			if v2: file.write("v2 %s\n" % " ".join("%.9g" % x for x in v2))
			if v3: file.write("v3 %s\n" % " ".join("%.9g" % x for x in v3))
			if v4: file.write("v4 %s\n" % " ".join("%.9g" % x for x in v4))
			if v5: file.write("v5 %s\n" % " ".join("%.9g" % x for x in v5))
			if v6: file.write("v6 %s\n" % " ".join("%.9g" % x for x in v6))
			if v7: file.write("v7 %s\n" % " ".join("%.9g" % x for x in v7))
			if v8: file.write("v8 %s\n" % " ".join("%.9g" % x for x in v8))
			if v9: file.write("v9 %s\n" % " ".join("%.9g" % x for x in v9))
		for f in face_list:
			if len(f) == 3:
				file.write("fm %d %d %d\n" % (f[2], f[1], f[0]))
			else:
				file.write("fm %d %d %d %d\n" % (f[3], f[2], f[1], f[0]))

def write_pose(file, t, r, s):
	if abs(s.x - 1.0) > 0.001 or abs(s.y - 1.0) > 0.001 or abs(s.z - 1.0) > 0.001:
		file.write("pq %.9g %.9g %.9g %.9g %.9g %.9g %.9g %.9g %.9g %.9g\n" %
			(t.x, t.y, t.z, r.x, r.y, r.z, r.w, s.x, s.y, s.z))
	else:
		file.write("pq %.9g %.9g %.9g %.9g %.9g %.9g %.9g\n" %
			(t.x, t.y, t.z, r.x, r.y, r.z, r.w))

def export_armature(file, amt):
	print("exporting armature:", amt.name)

	bone_map = {}
	bone_list = []

	file.write("\n")
	for bone in amt.bones:
		if not bone in bone_map:
			bone_map[bone.name] = len(bone_list)
			bone_list.append(bone)
		parent = bone_map[bone.parent.name] if bone.parent else -1
		file.write("joint \"%s\" %d\n" % (bone.name, parent))

	file.write("\n")
	for bone in amt.bones:
		matrix = bone.matrix_local
		if bone.parent:
			matrix = bone.parent.matrix_local.inverted() * bone.matrix_local
		t, r, s = matrix.decompose()
		write_pose(file, t, r, s)

	return bone_map

def export_frame(file, amt, bones):
	print("...")

def export_action(file, scene, obj, bones, amt, action):
	print("exporting action:", action.name, action)
	file.write("\n")
	file.write("animation \"%s\"\n" % action.name)
	startframe = int(action.frame_range[0])
	endframe = int(action.frame_range[1])
	for time in range(startframe, endframe+1):
		scene.frame_set(time)
		file.write("\n")
		file.write("frame %d\n" % time)
		export_frame(file, amt, bones)

def export_armature_actions(file, scene, obj, bones):
	old_action = obj.animation_data.action
	for action in bpy.data.actions:
		obj.animation_data.action = action
		export_action(file, scene, obj, bones, obj.data, action)
	obj.animation_data.action = old_action

def export_mesh_object(file, scene, obj, bones=None, attributes=None):
	# temporarily disable armature modifiers
	amtmods = []
	for mod in obj.modifiers:
		if mod.type == 'ARMATURE':
			amtmods.append((mod, mod.show_viewport))
			mod.show_viewport = False

	mesh = obj.to_mesh(scene, True, 'PREVIEW')
	mesh.calc_tessface()
	export_mesh_data(file, mesh, obj.name, obj.vertex_groups, bones, attributes)
	bpy.data.meshes.remove(mesh)

	# restore armature modifiers
	for mod, show_viewport in amtmods:
		mod.show_viewport = show_viewport

def export_scene(file, scene):
	bones = None
	amtobj = None

	for obj in scene.objects:
		if obj.type == 'ARMATURE':
			amtobj = obj

	if amtobj:
		bones = export_armature(file, amtobj.data)

	attributes = {}
	for obj in scene.objects:
		if obj.type == 'MESH' and obj.find_armature() == amtobj:
			gather_attributes(attributes, obj.vertex_groups, bones)
	attributes = export_attributes(file, attributes)

	for obj in scene.objects:
		if obj.type == 'MESH' and obj.find_armature() == amtobj:
			export_mesh_object(file, scene, obj, bones, attributes)

	if amtobj:
		export_armature_actions(file, scene, amtobj, bones)

def export_iqe(filename):
	file = open(filename, "w")
	file.write("# Inter-Quake Export\n")
	export_scene(file, bpy.context.scene)
	file.close()

#
# Register addon
#

class ExportIQE(bpy.types.Operator, ExportHelper):
	bl_idname = "export.iqe"
	bl_label = "Export IQE"

	filename_ext = ".iqe"

	def execute(self, context):
		export_iqe(self.properties.filepath)
		return {'FINISHED'}

def menu_func(self, context):
	self.layout.operator(ExportIQE.bl_idname, text="Inter-Quake Model (.iqe)")

def register():
	bpy.utils.register_module(__name__)
	bpy.types.INFO_MT_file_export.append(menu_func)

def unregister():
	bpy.utils.unregister_module(__name__)
	bpy.types.INFO_MT_file_export.remove(menu_func)

def batch(output):
	export_iqe(output)

if __name__ == "__main__":
	register()
	if len(sys.argv) > 4 and sys.argv[-2] == '--':
		batch(sys.argv[-1])