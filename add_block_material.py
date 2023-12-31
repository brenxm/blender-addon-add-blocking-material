# Blocking Material
# Adds a material to a mesh that has no existing material in their slots. 
# Default keymap Ctrl + Alt + shift + 9

bl_info = {
    "name": "Add blocking material",
    "blender": (4, 0, 0),
    "category": "Object",
    "author": 'Bryan Mina',
    "version": (1, 0),
    "location": 'SpaceBar Search -> Add block material',
    "description": 'Add a blocking material to selected objects WITHOUT a material. if no selected objects, it will apply to all meshes that has no material'
    }
    

import bpy
import colorsys
import random

class BlockingMaterial(bpy.types.Operator):
    bl_idname = 'object.add_blocking_material'
    bl_label = 'Add block material'
    bl_options = {"REGISTER", "UNDO"}
    
    color: bpy.props.IntProperty(name='Color Seed', min=1, max = 1000, default = 1)
    saturation: bpy.props.FloatProperty(name='Saturation', default=0.65, min=0.1, max=1.0)
    value: bpy.props.FloatProperty(name='Value', default=0.5, min=0.1, max=1.0)
    
    def __init__(self):
        self.mat_seed_map = {}
    
    
    def execute(self, context):
        self._clean_up_mat()
        
        scene_objects = [obj for obj in context.scene.objects if obj.type == 'MESH']
        
        selected_objects = [obj for obj in scene_objects if obj.select_get()]
        
        # Handle if user has objects selected
        if selected_objects:
            for obj in selected_objects:
                # Check if there is a material -> Check if has Block Material -> Edit
                if obj.material_slots:
                    if 'BlockMaterial' in obj.material_slots[0].material.name:
                        self._modify_mat(obj)
                
                
                # Handle new material if object has no existing materials
                else:
                    self._generate_material(obj)
                
                    
        # Handle if no selected objects
        else:
             for obj in [obj for obj in scene_objects if not obj.material_slots]:
                 self._generate_material(obj)
                
    
        # Ensure user to view the material if user in 'SOLID' mode, change to 'MATERIAL' preview
        if bpy.context.space_data.shading.type == 'SOLID':
            bpy.context.space_data.shading.type = 'MATERIAL'
        
        #self._clean_up_mat()
        return {'FINISHED'}
    
    def _generate_material(self, obj):
                    
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
            bpy.data.materials[new_material.name].node_tree.nodes["Principled BSDF"].inputs[0].default_value = (*rgb_color, 1)
            
            # Apply new material to obj
            obj.data.materials.append(new_material)
            
    def _modify_mat(self, obj):
        
        material = obj.material_slots[0].material
        
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
        bpy.data.materials[material.name].node_tree.nodes["Principled BSDF"].inputs[0].default_value = (*rgb_color, 1)
        
    
                
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
    
    # Handle keymaps
    wm = bpy.context.window_manager
    km = wm.keyconfigs.addon.keymaps.new(name='Object Mode', space_type='EMPTY')
    
    kmi = km.keymap_items.new(BlockingMaterial.bl_idname, 'NINE', 'PRESS', ctrl=True, shift=True, alt=True)

    
    add_on_keymaps.append((km, kmi))
    
def unregister():
    bpy.utils.unregister_class(BlockingMaterial)
        

                   
# For testing purposes
if __name__ == '__main__':
    register()