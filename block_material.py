# Blocking Material
# Adds a material to a mesh that has no existing material in their slots.
# Default keymap Ctrl + Alt + shift + 9

import random
import colorsys
import bpy
bl_info = {
    "name": "Add blocking material",
    "blender": (4, 0, 0),
    "category": "Object",
    "author": 'Bryan Mina',
    "version": (1, 0),
    "location": 'SpaceBar Search -> Add block material or Object -> Add block material',
    "description": 'Add a blocking material to selected objects WITHOUT a material. if no selected objects, it will apply to all meshes that has no material',
    "doc_url": 'https://github.com/brenxm/blender-addon-add-blocking-material/tree/main'
}


class BlockingMaterial(bpy.types.Operator):
    bl_idname = 'object.add_blocking_material'
    bl_label = 'Add block material'
    bl_options = {"REGISTER", "UNDO"}

    color: bpy.props.IntProperty(name='Color Seed', min=1, max=1000, default=1)
    saturation: bpy.props.FloatProperty(
        name='Saturation', default=0.65, min=0.1, max=1.0)
    value: bpy.props.FloatProperty(name='Value', default=0.5, min=0.1, max=1.0)

    def __init__(self):
        self.mat_seed_map = {}

    def execute(self, context):

        self._clean_up_mat()

        if context.mode == 'EDIT_MESH':

            active_obj = context.active_object

            if active_obj:
                new_material = self._generate_material()
                active_obj.data.materials.append(new_material)
                self._modify_mat(new_material)
                context.object.active_material_index = active_obj.data.materials.find(
                    new_material.name)
                bpy.ops.object.material_slot_assign()

        else:
            scene_objects = [
                obj for obj in context.scene.objects if obj.type == 'MESH']

            selected_objects = [
                obj for obj in scene_objects if obj.select_get()]

            # Handle if user has objects selected
            if selected_objects:

                new_material = self._generate_material()

                for obj in selected_objects:
                    bpy.ops.object.select_all(action='DESELECT')
                    context.view_layer.objects.active = obj
                    obj.select_set(True)

                    if obj.material_slots:
                        obj.data.materials.append(new_material)

                        mesh = obj.data
                        # Assigns the newly created material to the obj, essentially overriding the prior material assigned to the obj
                        if mesh:
                            for poly in mesh.polygons:
                                poly.material_index = len(
                                    obj.data.materials) - 1

                    # Handle new material if object has no existing materials
                    else:
                        obj.data.materials.append(new_material)

                # Revert back to selecting all objects
                for obj in selected_objects:
                    context.view_layer.objects.active = obj
                    obj.select_set(True)

            # Handle if no selected objects
            else:
                for obj in scene_objects:
                    if obj.material_slots:
                        if obj.material_slots[0].material == None:
                            obj.material_slots[0].material = self._generate_material(
                            )

                        elif obj.material_slots[0].material.name == 'Material':
                            bpy.data.materials.remove(
                                obj.material_slots[0].material)
                            obj.material_slots[0].material = self._generate_material(
                            )

                    elif not obj.material_slots:
                        obj.data.materials.append(self._generate_material())

        # Ensure user to view the material if user in 'SOLID' mode, change to 'MATERIAL' preview
        if bpy.context.space_data.shading.type == 'SOLID':
            bpy.context.space_data.shading.type = 'MATERIAL'

        # self._clean_up_mat()
        return {'FINISHED'}

    def _generate_material(self):

        new_material = bpy.data.materials.new(f'BlockMaterial')

        # Must enable node to get color node
        new_material.use_nodes = True

        # Generates color seed value for each material being created
        if new_material.name not in self.mat_seed_map:
            self.mat_seed_map[new_material.name] = random.random()

        random.seed(self.mat_seed_map[new_material.name] * self.color)

        # Generate random color using HSV with default saturation input of 0.65 and value input of 0.5
        hsv_color = (
            random.random(),
            self.saturation,
            self.value
        )

        # Convert HSV to RGB
        rgb_color = colorsys.hsv_to_rgb(*hsv_color)

        # Apply generated random color to the new material
        bpy.data.materials[new_material.name].node_tree.nodes["Principled BSDF"].inputs[0].default_value = (
            *rgb_color, 1)

        return new_material

    def _modify_mat(self, mat):

        material = mat

        if material.name not in self.mat_seed_map:
            self.mat_seed_map[material.name] = random.random()

        random.seed(self.mat_seed_map[material.name] * self.color)

        # Generate random color using HSV with default saturation input of 0.65 and value input of 0.5
        hsv_color = (
            random.random(),
            self.saturation,
            self.value
        )

        # Convert HSV to RGB
        rgb_color = colorsys.hsv_to_rgb(*hsv_color)

        # Apply generated random color to the new material
        bpy.data.materials[material.name].node_tree.nodes["Principled BSDF"].inputs[0].default_value = (
            *rgb_color, 1)

    def _clean_up_mat(self):
        for mat in bpy.data.materials[:]:
            if 'BlockMaterial' in mat.name and mat.users == 0:
                bpy.data.materials.remove(mat)


add_on_keymaps = []


def menu_func(self, context):
    self.layout.operator(BlockingMaterial.bl_idname)
    

def register():
    bpy.utils.register_class(BlockingMaterial)
    bpy.types.VIEW3D_MT_object.append(menu_func)
    bpy.types.VIEW3D_MT_edit_mesh_faces.append(menu_func)

    # Handle keymaps
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon

    if kc:
        km = wm.keyconfigs.addon.keymaps.new(
            name='Object Mode', space_type='EMPTY')

        kmi = km.keymap_items.new(
            BlockingMaterial.bl_idname, 'NINE', 'PRESS', ctrl=True, shift=True, alt=True)

        add_on_keymaps.append((km, kmi))

        km = wm.keyconfigs.addon.keymaps.new(
            name='Mesh', space_type='EMPTY')

        kmi = km.keymap_items.new(
            BlockingMaterial.bl_idname, 'NINE', 'PRESS', ctrl=True, shift=True, alt=True)

        add_on_keymaps.append((km, kmi))


def unregister():

    for km, kmi in add_on_keymaps:
        km.keymap_items.remove(kmi)
    add_on_keymaps.clear()

    bpy.utils.unregister_class(BlockingMaterial)
    bpy.types.VIEW3D_MT_object.remove(menu_func)


# For testing purposes
if __name__ == '__main__':
    register()
