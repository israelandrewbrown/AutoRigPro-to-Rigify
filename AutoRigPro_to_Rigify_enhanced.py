import bpy
from bpy.types import Operator, Panel, PropertyGroup
from bpy.props import PointerProperty, BoolProperty
import mathutils

# Addon Info
bl_info = {
    "name": "AutoRigPro-To-Rigify",
    "blender": (4,0),
    "category": "Rigging",
    "version": (2,0),
    "author": "Israel-Andrew-Brown_Jamaica",
    "description": "To Make Rigify Rig Bones Align With AutoRigPro.",
}

# Bone mapping dictionary: Rigify bone → Auto-Rig Pro bone
bone_mapping = {
    # Legs - Left
    "thigh.L": "thigh_ref.l",
    "shin.L": "leg_ref.l",
    "foot.L": "foot_ref.l",
    "toe.L": "toes_ref.l",
    "heel.02.L": "foot_heel_ref.l",
    # Legs - Right
    "thigh.R": "thigh_ref.r",
    "shin.R": "leg_ref.r",
    "foot.R": "foot_ref.r",
    "toe.R": "toes_ref.r",
    "heel.02.R": "foot_heel_ref.r",
    # Torso / Spine
    "spine": "root_ref.x",
    "spine.001": "spine_01_ref.x",
    "spine.002": "spine_02_ref.x",
    "spine.003": "spine_03_ref.x",
    # "spine.004": special handling - no direct mapping
    "spine.005": "neck_ref.x",
    "spine.006": "head_ref.x",
    # Shoulder & Arms - Left
    "shoulder.L": "shoulder_ref.l",
    "upper_arm.L": "arm_ref.l",
    "forearm.L": "forearm_ref.l",
    "hand.L": "hand_ref.l",
    # Left Fingers
    "palm.01.L": "index1_base_ref.l",
    "f_index.01.L": "index1_ref.l",
    "f_index.02.L": "index2_ref.l",
    "f_index.03.L": "index3_ref.l",
    "thumb.01.L": "thumb1_ref.l",
    "thumb.02.L": "thumb2_ref.l",
    "thumb.03.L": "thumb3_ref.l",
    "palm.02.L": "middle1_base_ref.l",
    "f_middle.01.L": "middle1_ref.l",
    "f_middle.02.L": "middle2_ref.l",
    "f_middle.03.L": "middle3_ref.l",
    "palm.03.L": "ring1_base_ref.l",
    "f_ring.01.L": "ring1_ref.l",
    "f_ring.02.L": "ring2_ref.l",
    "f_ring.03.L": "ring3_ref.l",
    "palm.04.L": "pinky1_base_ref.l",
    "f_pinky.01.L": "pinky1_ref.l",
    "f_pinky.02.L": "pinky2_ref.l",
    "f_pinky.03.L": "pinky3_ref.l",
    # Shoulder & Arms - Right
    "shoulder.R": "shoulder_ref.r",
    "upper_arm.R": "arm_ref.r",
    "forearm.R": "forearm_ref.r",
    "hand.R": "hand_ref.r",
    # Right Fingers
    "palm.01.R": "index1_base_ref.r",
    "f_index.01.R": "index1_ref.r",
    "f_index.02.R": "index2_ref.r",
    "f_index.03.R": "index3_ref.r",
    "thumb.01.R": "thumb1_ref.r",
    "thumb.02.R": "thumb2_ref.r",
    "thumb.03.R": "thumb3_ref.r",
    "palm.02.R": "middle1_base_ref.r",
    "f_middle.01.R": "middle1_ref.r",
    "f_middle.02.R": "middle2_ref.r",
    "f_middle.03.R": "middle3_ref.r",
    "palm.03.R": "ring1_base_ref.r",
    "f_ring.01.R": "ring1_ref.r",
    "f_ring.02.R": "ring2_ref.r",
    "f_ring.03.R": "ring3_ref.r",
    "palm.04.R": "pinky1_base_ref.r",
    "f_pinky.01.R": "pinky1_ref.r",
    "f_pinky.02.R": "pinky2_ref.r",
    "f_pinky.03.R": "pinky3_ref.r",
    # Others
    "breast.L": "",
    "breast.R": "",
    "pelvis.L": "",
    "pelvis.R": "",
    # "root": "root_ref.x", # Commented out as per new mapping
}

# Face bones that can be deleted
face_bones = [
    # Core Head/Face
    "face",
    "jaw",          # Main jaw bone
    "jaw.L",        # Left jaw helper
    "jaw.L.001",    # Left jaw additional
    "jaw.L.002",    # New (extends jaw.L hierarchy)
    "jaw.R",        # Right jaw helper
    "jaw.R.001",    # Right jaw additional
    
    # Chin
    "chin",         # Main chin bone
    "chin.001",     # Chin additional
    "chin.002",     # New (extends chin hierarchy)
    "chin.R",       # Right chin helper
    "chin.L",       # Left chin helper
    "chin.L.001",   # New (extends chin.L)
    
    # Cheeks
    "cheek.T.L",    # Top-left cheek
    "cheek.T.L.001",
    "cheek.T.R",    # Top-right cheek
    "cheek.T.R.001",
    "cheek.B.R",    # Bottom-right cheek
    "cheek.B.R.001",
    "cheek.B.L",    # Bottom-left cheek
    "cheek.B.L.001",
    "cheek.B.L.002", # New (extends cheek.B.L)
    "cheek.B.L.003", # New (extends cheek.B.L further)
    
    # Nose
    "nose",         # Main nose bone
    "nose.L",       # Left nostril/nose helper
    "nose.L.001",
    "nose.R",       # Right nostril/nose helper
    "nose.R.001",
    "nose.001",     # Additional nose bones
    "nose.002",
    "nose.003",
    "nose.004",
    
    # Lips
    "lip.T.L",      # Top-left lip
    "lip.T.L.001",
    "lip.B.L",      # Bottom-left lip
    "lip.B.L.001",
    "lip.T.R",      # Top-right lip
    "lip.T.R.001",
    "lip.B.R",      # Bottom-right lip
    "lip.B.R.001",
    
    # Eyes
    "eye.L",        # Left eye (controller)
    "eye.R",        # Right eye (controller)
    "lid.T.L",      # Top-left eyelid
    "lid.T.L.001",
    "lid.T.L.002",
    "lid.T.L.003",
    "lid.B.L",      # Bottom-left eyelid
    "lid.B.L.001",
    "lid.B.L.002",
    "lid.B.L.003",
    "lid.B.L.004",  # New (extends bottom-left eyelid)
    "lid.T.R",      # Top-right eyelid
    "lid.T.R.001",
    "lid.T.R.002",
    "lid.T.R.003",
    "lid.B.R",      # Bottom-right eyelid
    "lid.B.R.001",
    "lid.B.R.002",
    "lid.B.R.003",
    "lid.B.R.004",  # New (matches left side)
    
    # Brows
    "brow.B.L",     # Bottom-left brow
    "brow.B.L.001",
    "brow.B.L.002",
    "brow.B.L.003",
    "brow.B.R",     # Bottom-right brow
    "brow.B.R.001",
    "brow.B.R.002",
    "brow.B.R.003",
    "brow.B.R.004", # New (extends brow.B.R)
    "brow.T.L",     # Top-left brow
    "brow.T.L.001",
    "brow.T.L.002",
    "brow.T.L.003",
    "brow.T.L.004", # New (extends brow.T.L)
    "brow.T.L.005", # New
    "brow.T.L.006", # New
    "brow.T.L.007", # New (deep hierarchy)
    "brow.T.R",     # Top-right brow
    "brow.T.R.001",
    "brow.T.R.002",
    "brow.T.R.003",
    "brow.T.R.004", # New (matches left side)
    
    # Ears
    "ear.L",        # Left ear root
    "ear.L.001",
    "ear.L.002",
    "ear.L.003",
    "ear.L.004",
    "ear.L.005",    # New (extends ear.L)
    "ear.R",        # Right ear root
    "ear.R.001",
    "ear.R.002",
    "ear.R.003",
    "ear.R.004",
    "ear.R.005",    # New (matches left side)
    
    # Forehead/Temples
    "forehead.L",
    "forehead.L.001",
    "forehead.L.002",
    "forehead.R",
    "forehead.R.001",
    "forehead.R.002",
    "temple.L",
    "temple.R",
    
    # Teeth/Tongue
    "teeth.T",      # Upper teeth
    "teeth.B",      # Lower teeth
    "tongue",       # Tongue root
    "tongue.001",   # Tongue mid
    "tongue.002",   # Tongue tip
    "tongue.003"    # New (extends tongue hierarchy)
]

# Property group to store rig selections and settings
class RigSelectionProperties(PropertyGroup):
    auto_rig: PointerProperty(
        name="Target Rig (AutoRig Pro)",
        type=bpy.types.Object,
        description="Select the Auto-Rig Pro armature",
        poll=lambda self, obj: obj.type == 'ARMATURE'
    )
    rigify_rig: PointerProperty(
        name="Rigify Rig",
        type=bpy.types.Object,
        description="Select the Rigify metarig",
        poll=lambda self, obj: obj.type == 'ARMATURE'
    )
    keep_face_bones: BoolProperty(
        name="Keep Face Bones",
        description="Keep face bones in the rigify rig, otherwise delete them",
        default=False
    )
    selected_mesh: PointerProperty(
        name="Selected Mesh",
        type=bpy.types.Object,
        description="Select the mesh to be parented to the rig",
        poll=lambda self, obj: obj.type == 'MESH'
    )
    rig_controls: PointerProperty(
        name="Rig Controls",
        type=bpy.types.Object,
        description="Select the rig with control bones (generated rigify rig)",
        poll=lambda self, obj: obj.type == 'ARMATURE'
    )

# Operator to add basic human metarig
class OBJECT_OT_AddMetarig(Operator):
    bl_idname = "object.add_metarig"
    bl_label = "Add Human Metarig"
    bl_description = "Add a basic human metarig for rigify"

    def execute(self, context):
        # Add basic human metarig
        try:
            bpy.ops.object.armature_human_metarig_add()
            self.report({'INFO'}, "Human metarig added successfully")
        except:
            # Fallback if rigify addon is not enabled
            self.report({'ERROR'}, "Rigify addon must be enabled to add metarig")
            return {'CANCELLED'}
        
        return {'FINISHED'}

# Operator to handle face bones (keep or delete)
class OBJECT_OT_HandleFaceBones(Operator):
    bl_idname = "object.handle_face_bones"
    bl_label = "Process Face Bones"
    bl_description = "Keep or delete face bones based on selection"

    def execute(self, context):
        props = context.scene.rig_selection_props
        rigify_rig = props.rigify_rig

        if not rigify_rig:
            self.report({'ERROR'}, "Please select a Rigify rig")
            return {'CANCELLED'}

        if rigify_rig.type != 'ARMATURE':
            self.report({'ERROR'}, "Selected object must be an armature")
            return {'CANCELLED'}

        if not props.keep_face_bones:
            # Delete face bones
            bpy.context.view_layer.objects.active = rigify_rig
            bpy.ops.object.mode_set(mode='EDIT')
            
            deleted_count = 0
            for bone_name in face_bones:
                bone = rigify_rig.data.edit_bones.get(bone_name)
                if bone:
                    rigify_rig.data.edit_bones.remove(bone)
                    deleted_count += 1
            
            bpy.ops.object.mode_set(mode='OBJECT')
            self.report({'INFO'}, f"Deleted {deleted_count} face bones")
        else:
            self.report({'INFO'}, "Face bones kept in the rig")

        return {'FINISHED'}

# Operator to align Rigify metarig to Auto-Rig Pro rig in object mode
class OBJECT_OT_AlignRigs(Operator):
    bl_idname = "object.align_rigs"
    bl_label = "Align"
    bl_description = "Align Rigify metarig to Auto-Rig Pro rig in object mode"

    def execute(self, context):
        props = context.scene.rig_selection_props
        auto_rig = props.auto_rig
        rigify_rig = props.rigify_rig

        if not auto_rig or not rigify_rig:
            self.report({'ERROR'}, "Please select both Auto-Rig Pro and Rigify metarig")
            return {'CANCELLED'}

        if auto_rig.type != 'ARMATURE' or rigify_rig.type != 'ARMATURE':
            self.report({'ERROR'}, "Selected objects must be armatures")
            return {'CANCELLED'}

        # Deselect all objects
        bpy.ops.object.select_all(action='DESELECT')

        # Select Auto-Rig Pro rig and set cursor to its origin
        auto_rig.select_set(True)
        bpy.context.view_layer.objects.active = auto_rig
        bpy.ops.view3d.snap_cursor_to_selected()

        # Select Rigify metarig and snap it to cursor
        auto_rig.select_set(False)
        rigify_rig.select_set(True)
        bpy.context.view_layer.objects.active = rigify_rig
        bpy.ops.view3d.snap_selected_to_cursor(use_offset=False)

        # Copy rotation and scale from Auto-Rig Pro to Rigify metarig
        rigify_rig.rotation_euler = auto_rig.rotation_euler
        rigify_rig.scale = auto_rig.scale

        self.report({'INFO'}, "Rigify metarig aligned to Auto-Rig Pro rig")
        return {'FINISHED'}

# Operator to align Rigify bones to Auto-Rig Pro bones
class OBJECT_OT_AlignBones(Operator):
    bl_idname = "object.align_bones"
    bl_label = "Align Bones"
    bl_description = "Align Rigify bones head and tail to Auto-Rig Pro bones"

    def execute(self, context):
        props = context.scene.rig_selection_props
        auto_rig = props.auto_rig
        rigify_rig = props.rigify_rig

        if not auto_rig or not rigify_rig:
            self.report({'ERROR'}, "Please select both Auto-Rig Pro and Rigify metarig")
            return {'CANCELLED'}

        if auto_rig.type != 'ARMATURE' or rigify_rig.type != 'ARMATURE':
            self.report({'ERROR'}, "Selected objects must be armatures")
            return {'CANCELLED'}

        # Ensure we're in object mode first
        if bpy.context.mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')
            
        # Get world space bone head and tail positions from Auto-Rig Pro
        auto_rig_bone_positions = {}
        
        # Enter edit mode on Auto-Rig Pro to get exact positions
        bpy.context.view_layer.objects.active = auto_rig
        bpy.ops.object.mode_set(mode='EDIT')
        
        for rigify_bone_name, auto_rig_bone_name in bone_mapping.items():
            if not auto_rig_bone_name:  # Skip empty mappings
                continue
                
            # Get Auto-Rig Pro edit bone
            auto_edit_bone = auto_rig.data.edit_bones.get(auto_rig_bone_name)
            if not auto_edit_bone:
                continue
                
            # Store world space head and tail positions
            head_world = auto_rig.matrix_world @ auto_edit_bone.head
            tail_world = auto_rig.matrix_world @ auto_edit_bone.tail
            
            auto_rig_bone_positions[rigify_bone_name] = {
                'head': head_world,
                'tail': tail_world
            }
        
        # Return to object mode
        bpy.ops.object.mode_set(mode='OBJECT')
        
        # Now enter edit mode on Rigify to apply the positions
        bpy.context.view_layer.objects.active = rigify_rig
        bpy.ops.object.mode_set(mode='EDIT')
        
        for rigify_bone_name, positions in auto_rig_bone_positions.items():
            rigify_edit_bone = rigify_rig.data.edit_bones.get(rigify_bone_name)
            if not rigify_edit_bone:
                self.report({'WARNING'}, f"Rigify bone '{rigify_bone_name}' not found")
                continue
                
            # Convert world positions to Rigify local space
            head_local = rigify_rig.matrix_world.inverted() @ positions['head']
            tail_local = rigify_rig.matrix_world.inverted() @ positions['tail']
            
            # Set the head and tail positions
            rigify_edit_bone.head = head_local
            rigify_edit_bone.tail = tail_local
            
        # Special handling for spine.004 bone (between spine.003 and spine.005)
        spine004_bone = rigify_rig.data.edit_bones.get("spine.004")
        spine003_bone = rigify_rig.data.edit_bones.get("spine.003")
        spine005_bone = rigify_rig.data.edit_bones.get("spine.005")
        
        if spine004_bone and spine003_bone and spine005_bone:
            # First, make sure spine.005 and spine.006 are positioned properly
            # Move them up on the Z axis by 0.3 units
            spine005_bone.head.z += 0.045
            spine005_bone.tail.z += 0.01
            
            if rigify_rig.data.edit_bones.get("spine.006"):
                spine006_bone = rigify_rig.data.edit_bones.get("spine.006")
                spine006_bone.head.z += 0.005
                spine006_bone.tail.z += 0.005
            
            # Now position spine.004's head at spine.003's tail
            spine004_bone.head = spine003_bone.tail.copy()
            
            # Position spine.004's tail to be in line with spine.005's head
            # This creates a connection between spine.003 and spine.005
            spine004_bone.tail = spine005_bone.head.copy()
            
            self.report({'INFO'}, "Special spine.004 bone positioned between spine.003 and spine.005")
        
        # Return to object mode
        bpy.ops.object.mode_set(mode='OBJECT')

        self.report({'INFO'}, "Rigify bones aligned to Auto-Rig Pro bones - head and tail positions matched")
        return {'FINISHED'}

# Operator to apply all transforms
class OBJECT_OT_ApplyTransforms(Operator):
    bl_idname = "object.apply_transforms"
    bl_label = "Apply All Transforms"
    bl_description = "Apply all transforms (Location, Rotation, Scale) to the selected rig"

    def execute(self, context):
        props = context.scene.rig_selection_props
        rigify_rig = props.rigify_rig

        if not rigify_rig:
            self.report({'ERROR'}, "Please select a Rigify rig")
            return {'CANCELLED'}

        # Select the rigify rig
        bpy.ops.object.select_all(action='DESELECT')
        rigify_rig.select_set(True)
        bpy.context.view_layer.objects.active = rigify_rig

        # Apply all transforms
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
        
        self.report({'INFO'}, "All transforms applied to Rigify rig")
        return {'FINISHED'}

# Operator to generate rigify rig
class OBJECT_OT_GenerateRig(Operator):
    bl_idname = "object.generate_rig"
    bl_label = "Generate Rig"
    bl_description = "Generate the final rigify rig from the metarig"

    def execute(self, context):
        props = context.scene.rig_selection_props
        rigify_rig = props.rigify_rig

        if not rigify_rig:
            self.report({'ERROR'}, "Please select a Rigify metarig")
            return {'CANCELLED'}

        if rigify_rig.type != 'ARMATURE':
            self.report({'ERROR'}, "Selected object must be an armature")
            return {'CANCELLED'}

        # Select the rigify metarig
        bpy.ops.object.select_all(action='DESELECT')
        rigify_rig.select_set(True)
        bpy.context.view_layer.objects.active = rigify_rig

        # Generate the rigify rig
        try:
            bpy.ops.pose.rigify_generate()
            self.report({'INFO'}, "Rigify rig generated successfully!")
        except Exception as e:
            self.report({'ERROR'}, f"Failed to generate rig: {str(e)}")
            return {'CANCELLED'}

        return {'FINISHED'}

# Operator to parent mesh to rig with automatic weights
class OBJECT_OT_ParentWithWeights(Operator):
    bl_idname = "object.parent_with_weights"
    bl_label = "Parent with Automatic Weights"
    bl_description = "Parent selected mesh to rig with automatic weights (Ctrl+P)"

    def execute(self, context):
        props = context.scene.rig_selection_props
        mesh_obj = props.selected_mesh
        rig_obj = props.rig_controls

        if not mesh_obj or not rig_obj:
            self.report({'ERROR'}, "Please select both mesh and rig controls")
            return {'CANCELLED'}

        if mesh_obj.type != 'MESH':
            self.report({'ERROR'}, "Selected object must be a mesh")
            return {'CANCELLED'}

        if rig_obj.type != 'ARMATURE':
            self.report({'ERROR'}, "Rig controls must be an armature")
            return {'CANCELLED'}

        # Ensure we're in object mode
        if bpy.context.mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')

        # Deselect all objects
        bpy.ops.object.select_all(action='DESELECT')

        # Select mesh first, then rig (rig needs to be active)
        mesh_obj.select_set(True)
        rig_obj.select_set(True)
        bpy.context.view_layer.objects.active = rig_obj

        # Parent with automatic weights
        try:
            bpy.ops.object.parent_set(type='ARMATURE_AUTO')
            self.report({'INFO'}, f"Mesh '{mesh_obj.name}' parented to rig '{rig_obj.name}' with automatic weights")
        except Exception as e:
            self.report({'ERROR'}, f"Failed to parent with automatic weights: {str(e)}")
            return {'CANCELLED'}

        return {'FINISHED'}

# Panel in the 3D View N-panel
class VIEW3D_PT_AutoRigToRigify(Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Tool'
    bl_label = 'AutoRig To Rigify'

    def draw(self, context):
        layout = self.layout
        props = context.scene.rig_selection_props

        # Shelf One: Target rig selection
        box = layout.box()
        box.label(text="1. Rig Selection", icon='ARMATURE_DATA')
        box.prop(props, "auto_rig", icon='OUTLINER_OB_ARMATURE')
        box.prop(props, "rigify_rig", icon='OUTLINER_OB_ARMATURE')

        # Shelf Two: Add armature
        box = layout.box()
        box.label(text="2. Add Metarig", icon='ADD')
        box.operator("object.add_metarig", text="Add Human Metarig", icon='ARMATURE_DATA')

        # Shelf Three: Face bones option
        box = layout.box()
        box.label(text="3. Face Bones", icon='FACE_MAPS')
        box.prop(props, "keep_face_bones")
        box.operator("object.handle_face_bones", text="Process Face Bones", icon='CHECKMARK')

        # Shelf Four: Align pelvis bones
        box = layout.box()
        box.label(text="4. Align Pelvis Bones", icon='CON_LOCLIKE')
        box.operator("object.align_rigs", text="Align Rigs", icon='SNAP_ON')
        box.operator("object.align_bones", text="Align Bones", icon='BONE_DATA')
        box.label(text="Don't forget to save! (Ctrl+S)", icon='FILE_TICK')

        # Shelf Five: Apply transforms
        box = layout.box()
        box.label(text="5. Apply Transforms", icon='OBJECT_ORIGIN')
        box.operator("object.apply_transforms", text="Apply All Transforms", icon='CHECKMARK')

        # Shelf Six: Generate rig
        box = layout.box()
        box.label(text="6. Generate Final Rig", icon='ARMATURE_DATA')
        box.operator("object.generate_rig", text="Generate Rig", icon='PLAY')

        # Shelf Seven: Parent mesh to rig
        box = layout.box()
        box.label(text="7. Parent Mesh to Rig", icon='CONSTRAINT_BONE')
        box.prop(props, "selected_mesh", icon='OUTLINER_OB_MESH')
        box.prop(props, "rig_controls", icon='OUTLINER_OB_ARMATURE')
        box.operator("object.parent_with_weights", text="Ctrl+P Parent with Automatic Weights", icon='LINKED')

# Register classes
classes = (
    RigSelectionProperties,
    OBJECT_OT_AddMetarig,
    OBJECT_OT_HandleFaceBones,
    OBJECT_OT_AlignRigs,
    OBJECT_OT_AlignBones,
    OBJECT_OT_ApplyTransforms,
    OBJECT_OT_GenerateRig,
    OBJECT_OT_ParentWithWeights,
    VIEW3D_PT_AutoRigToRigify,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.rig_selection_props = PointerProperty(type=RigSelectionProperties)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.rig_selection_props

if __name__ == "__main__":
    register()
