#    Copyright (C) 2025 Israel Andrew Brown
#    Created by Israel Andrew Brown
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  
#
#    See the GNU General Public License for more details.
#    You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.

import bpy
from bpy.types import Operator, Panel, PropertyGroup, UIList
from bpy.props import PointerProperty, BoolProperty, CollectionProperty, IntProperty, StringProperty
import mathutils

# Addon Info
bl_info = {
    "name": "AutoRigPro-To-Rigify",
    "blender": (4, 0, 0),
    "category": "Rigging",
    "version": (2, 1, 0),
    "author": "Israel-Andrew-Brown_Jamaica",
    "description": "To Make Rigify Rig Bones Align With AutoRigPro. Includes multi-mesh parenting.",
    "location": "View3D > Sidebar > Tool Tab",
    "warning": "",
    "doc_url": "",
    "tracker_url": "",
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
}

# Face bones that can be deleted
face_bones = [
    "face", "jaw", "jaw.L", "jaw.L.001", "jaw.L.002", "jaw.R", "jaw.R.001",
    "chin", "chin.001", "chin.002", "chin.R", "chin.L", "chin.L.001",
    "cheek.T.L", "cheek.T.L.001", "cheek.T.R", "cheek.T.R.001", "cheek.B.R",
    "cheek.B.R.001", "cheek.B.L", "cheek.B.L.001", "cheek.B.L.002", "cheek.B.L.003",
    "nose", "nose.L", "nose.L.001", "nose.R", "nose.R.001", "nose.001", "nose.002",
    "nose.003", "nose.004", "lip.T.L", "lip.T.L.001", "lip.B.L", "lip.B.L.001",
    "lip.T.R", "lip.T.R.001", "lip.B.R", "lip.B.R.001", "eye.L", "eye.R",
    "lid.T.L", "lid.T.L.001", "lid.T.L.002", "lid.T.L.003", "lid.B.L", "lid.B.L.001",
    "lid.B.L.002", "lid.B.L.003", "lid.B.L.004", "lid.T.R", "lid.T.R.001",
    "lid.T.R.002", "lid.T.R.003", "lid.B.R", "lid.B.R.001", "lid.B.R.002",
    "lid.B.R.003", "lid.B.R.004", "brow.B.L", "brow.B.L.001", "brow.B.L.002",
    "brow.B.L.003", "brow.B.R", "brow.B.R.001", "brow.B.R.002", "brow.B.R.003",
    "brow.B.R.004", "brow.T.L", "brow.T.L.001", "brow.T.L.002", "brow.T.L.003",
    "brow.T.L.004", "brow.T.L.005", "brow.T.L.006", "brow.T.L.007", "brow.T.R",
    "brow.T.R.001", "brow.T.R.002", "brow.T.R.003", "brow.T.R.004", "ear.L",
    "ear.L.001", "ear.L.002", "ear.L.003", "ear.L.004", "ear.L.005", "ear.R",
    "ear.R.001", "ear.R.002", "ear.R.003", "ear.R.004", "ear.R.005", "forehead.L",
    "forehead.L.001", "forehead.L.002", "forehead.R", "forehead.R.001",
    "forehead.R.002", "temple.L", "temple.R", "teeth.T", "teeth.B", "tongue",
    "tongue.001", "tongue.002", "tongue.003"
]

# PropertyGroup for mesh items in the list
class MeshObjectItem(PropertyGroup):
    obj: PointerProperty(
        name="Mesh Object",
        type=bpy.types.Object,
        poll=lambda self, obj: obj.type == 'MESH'
    )

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
    # List of meshes to parent
    meshes_to_parent: CollectionProperty(type=MeshObjectItem)
    # Index for the UI list of meshes
    active_mesh_index: IntProperty(name="Active Mesh Index")

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
        try:
            bpy.ops.object.armature_human_metarig_add()
            self.report({'INFO'}, "Human metarig added successfully")
        except:
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

        bpy.ops.object.select_all(action='DESELECT')
        auto_rig.select_set(True)
        context.view_layer.objects.active = auto_rig
        bpy.ops.view3d.snap_cursor_to_selected()

        auto_rig.select_set(False)
        rigify_rig.select_set(True)
        context.view_layer.objects.active = rigify_rig
        bpy.ops.view3d.snap_selected_to_cursor(use_offset=False)

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

        if bpy.context.mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')
        
        auto_rig_bone_positions = {}
        
        context.view_layer.objects.active = auto_rig
        bpy.ops.object.mode_set(mode='EDIT')
        
        for rigify_bone_name, auto_rig_bone_name in bone_mapping.items():
            if not auto_rig_bone_name: 
                continue
            auto_edit_bone = auto_rig.data.edit_bones.get(auto_rig_bone_name)
            if not auto_edit_bone: 
                continue
            
            head_world = auto_rig.matrix_world @ auto_edit_bone.head
            tail_world = auto_rig.matrix_world @ auto_edit_bone.tail
            auto_rig_bone_positions[rigify_bone_name] = {'head': head_world, 'tail': tail_world}
        
        bpy.ops.object.mode_set(mode='OBJECT')
        
        context.view_layer.objects.active = rigify_rig
        bpy.ops.object.mode_set(mode='EDIT')
        
        for rigify_bone_name, positions in auto_rig_bone_positions.items():
            rigify_edit_bone = rigify_rig.data.edit_bones.get(rigify_bone_name)
            if not rigify_edit_bone:
                self.report({'WARNING'}, f"Rigify bone '{rigify_bone_name}' not found")
                continue
            
            head_local = rigify_rig.matrix_world.inverted() @ positions['head']
            tail_local = rigify_rig.matrix_world.inverted() @ positions['tail']
            rigify_edit_bone.head = head_local
            rigify_edit_bone.tail = tail_local
            
        spine004_bone = rigify_rig.data.edit_bones.get("spine.004")
        spine003_bone = rigify_rig.data.edit_bones.get("spine.003")
        spine005_bone = rigify_rig.data.edit_bones.get("spine.005")
        
        if spine004_bone and spine003_bone and spine005_bone:
            spine005_bone.head.z += 0.045
            spine005_bone.tail.z += 0.01
            
            if rigify_rig.data.edit_bones.get("spine.006"):
                spine006_bone = rigify_rig.data.edit_bones.get("spine.006")
                spine006_bone.head.z += 0.005
                spine006_bone.tail.z += 0.005
            
            spine004_bone.head = spine003_bone.tail.copy()
            spine004_bone.tail = spine005_bone.head.copy()
            self.report({'INFO'}, "Special spine.004 bone positioned")
        
        bpy.ops.object.mode_set(mode='OBJECT')
        self.report({'INFO'}, "Rigify bones aligned to Auto-Rig Pro bones")
        return {'FINISHED'}

# Operator to apply all transforms
class OBJECT_OT_ApplyTransforms(Operator):
    bl_idname = "object.apply_transforms"
    bl_label = "Apply All Transforms"
    bl_description = "Apply all transforms to the selected rig"

    def execute(self, context):
        props = context.scene.rig_selection_props
        rigify_rig = props.rigify_rig

        if not rigify_rig:
            self.report({'ERROR'}, "Please select a Rigify rig")
            return {'CANCELLED'}

        bpy.ops.object.select_all(action='DESELECT')
        rigify_rig.select_set(True)
        context.view_layer.objects.active = rigify_rig
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

        bpy.ops.object.select_all(action='DESELECT')
        rigify_rig.select_set(True)
        context.view_layer.objects.active = rigify_rig

        try:
            bpy.ops.pose.rigify_generate()
            self.report({'INFO'}, "Rigify rig generated successfully!")
        except Exception as e:
            self.report({'ERROR'}, f"Failed to generate rig: {str(e)}")
            return {'CANCELLED'}
        return {'FINISHED'}

# Operators to manage the list of meshes to parent
class MESH_OT_AddSelectedToParentList(Operator):
    bl_idname = "mesh.add_selected_to_parent_list"
    bl_label = "Add Selected Meshes"
    bl_description = "Add selected mesh objects in the 3D View to the parenting list"

    def execute(self, context):
        props = context.scene.rig_selection_props
        selected_meshes = [obj for obj in context.selected_objects if obj.type == 'MESH']

        if not selected_meshes:
            self.report({'WARNING'}, "No mesh objects selected in the 3D View")
            return {'CANCELLED'}

        current_mesh_pointers = {item.obj for item in props.meshes_to_parent if item.obj}

        added_count = 0
        for mesh_obj in selected_meshes:
            if mesh_obj not in current_mesh_pointers:
                new_item = props.meshes_to_parent.add()
                new_item.obj = mesh_obj
                added_count += 1
        
        if added_count > 0:
            self.report({'INFO'}, f"Added {added_count} mesh(es) to the list")
        else:
            self.report({'INFO'}, "Selected mesh(es) already in the list or no new meshes selected")
        return {'FINISHED'}

class MESH_OT_RemoveSelectedFromParentList(Operator):
    bl_idname = "mesh.remove_selected_from_parent_list"
    bl_label = "Remove Selected Mesh"
    bl_description = "Remove the selected mesh from the parenting list"

    def execute(self, context):
        props = context.scene.rig_selection_props
        if not props.meshes_to_parent:
            self.report({'WARNING'}, "List is empty")
            return {'CANCELLED'}
        
        index = props.active_mesh_index
        if index < 0 or index >= len(props.meshes_to_parent):
            self.report({'WARNING'}, "No mesh selected in the list or index out of bounds")
            return {'CANCELLED'}

        removed_mesh_name = props.meshes_to_parent[index].obj.name if props.meshes_to_parent[index].obj else "Unnamed"
        props.meshes_to_parent.remove(index)
        
        # Adjust active index if needed
        if props.active_mesh_index >= len(props.meshes_to_parent) and len(props.meshes_to_parent) > 0:
            props.active_mesh_index = len(props.meshes_to_parent) - 1
        elif not props.meshes_to_parent:
            props.active_mesh_index = 0

        self.report({'INFO'}, f"Removed '{removed_mesh_name}' from the list")
        return {'FINISHED'}

class MESH_OT_ClearParentList(Operator):
    bl_idname = "mesh.clear_parent_list"
    bl_label = "Clear List"
    bl_description = "Clear all meshes from the parenting list"

    def execute(self, context):
        props = context.scene.rig_selection_props
        if not props.meshes_to_parent:
            self.report({'INFO'}, "List is already empty")
            return {'CANCELLED'}
        
        count = len(props.meshes_to_parent)
        props.meshes_to_parent.clear()
        props.active_mesh_index = 0
        self.report({'INFO'}, f"Cleared {count} mesh(es) from the list")
        return {'FINISHED'}

# Operator to parent mesh to rig with automatic weights
class OBJECT_OT_ParentWithWeights(Operator):
    bl_idname = "object.parent_with_weights"
    bl_label = "Parent Meshes with Automatic Weights"
    bl_description = "Parent meshes in the list to rig with automatic weights (Ctrl+P)"

    def execute(self, context):
        props = context.scene.rig_selection_props
        meshes_to_parent_items = props.meshes_to_parent
        rig_obj = props.rig_controls

        if not meshes_to_parent_items:
            self.report({'ERROR'}, "No meshes in the list to parent.")
            return {'CANCELLED'}
        
        if not rig_obj:
            self.report({'ERROR'}, "Please select rig controls (generated Rigify rig)")
            return {'CANCELLED'}

        if rig_obj.type != 'ARMATURE':
            self.report({'ERROR'}, "Rig controls must be an armature")
            return {'CANCELLED'}

        if bpy.context.mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')

        parented_count = 0
        failed_count = 0

        for item in meshes_to_parent_items:
            mesh_obj = item.obj
            if not mesh_obj:
                self.report({'WARNING'}, f"Skipping an empty item in the mesh list.")
                failed_count += 1
                continue
            
            if mesh_obj.name not in context.scene.objects:
                self.report({'WARNING'}, f"Mesh '{mesh_obj.name}' not found in scene. Skipping.")
                failed_count += 1
                continue

            if mesh_obj.type != 'MESH':
                self.report({'WARNING'}, f"Object '{mesh_obj.name}' is not a mesh. Skipping.")
                failed_count += 1
                continue
            
            # Deselect all objects
            bpy.ops.object.select_all(action='DESELECT')

            # Select mesh first, then rig (rig needs to be active)
            mesh_obj.select_set(True)
            rig_obj.select_set(True)
            context.view_layer.objects.active = rig_obj

            try:
                bpy.ops.object.parent_set(type='ARMATURE_AUTO')
                self.report({'INFO'}, f"Mesh '{mesh_obj.name}' parented to rig '{rig_obj.name}' with automatic weights")
                parented_count += 1
            except Exception as e:
                self.report({'ERROR'}, f"Failed to parent '{mesh_obj.name}': {str(e)}")
                failed_count += 1
        
        if parented_count > 0:
            self.report({'INFO'}, f"Successfully parented {parented_count} mesh(es).")
        if failed_count > 0:
            self.report({'WARNING'}, f"Failed to parent or skipped {failed_count} mesh(es). Check console for details.")
        if parented_count == 0 and failed_count == 0:  # Should not happen if list is not empty
            self.report({'WARNING'}, "No meshes were processed.")

        # Clear selection after operation
        bpy.ops.object.select_all(action='DESELECT')
        if rig_obj:  # Attempt to re-select the rig controls if it exists
            try:
                rig_obj.select_set(True)
                context.view_layer.objects.active = rig_obj
            except ReferenceError:  # rig_obj might have been deleted or is invalid
                pass

        return {'FINISHED'}

# UIList class for displaying mesh items
class MESH_UL_MeshParentList(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        # 'item' is the MeshObjectItem type
        # 'data' is the RigSelectionProperties instance
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            if item.obj:
                layout.prop(item.obj, "name", text="", emboss=False, icon_value=icon)
            else:
                layout.label(text="<Empty Slot>", icon='QUESTION')
        elif self.layout_type == 'GRID':
            layout.alignment = 'CENTER'
            layout.label(text="", icon_value=icon)

# Panel in the 3D View N-panel
class VIEW3D_PT_AutoRigToRigify(Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Tool'  # Changed from 'AutoRig To Rigify' to 'Tool' and set label
    bl_label = 'ARP to Rigify'  # Shorter label for the tab

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

        # Shelf Four: Alignment operations
        box = layout.box()
        box.label(text="4. Alignment", icon='SNAP_ON')
        box.operator("object.align_rigs", text="Align Rigs", icon='SNAP_FACE')
        box.operator("object.align_bones", text="Align Bones", icon='BONE_DATA')
        box.operator("object.apply_transforms", text="Apply Transforms", icon='CHECKMARK')

        # Shelf Five: Generate rig
        box = layout.box()
        box.label(text="5. Generate Rig", icon='MODIFIER_ON')
        box.operator("object.generate_rig", text="Generate Rigify Rig", icon='ARMATURE_DATA')

        # Shelf Six: Mesh parenting
        box = layout.box()
        box.label(text="6. Mesh Parenting", icon='MESH_DATA')
        box.prop(props, "rig_controls", icon='OUTLINER_OB_ARMATURE')
        
        # Mesh list UI
        row = box.row()
        row.template_list("MESH_UL_MeshParentList", "", props, "meshes_to_parent", props, "active_mesh_index")
        
        # List management buttons
        col = row.column(align=True)
        col.operator("mesh.add_selected_to_parent_list", text="", icon='ADD')
        col.operator("mesh.remove_selected_from_parent_list", text="", icon='REMOVE')
        col.operator("mesh.clear_parent_list", text="", icon='TRASH')
        
        # Parent operation
        box.operator("object.parent_with_weights", text="Parent Meshes", icon='CONSTRAINT_BONE')

# Registration
classes = [
    MeshObjectItem,
    RigSelectionProperties,
    OBJECT_OT_AddMetarig,
    OBJECT_OT_HandleFaceBones,
    OBJECT_OT_AlignRigs,
    OBJECT_OT_AlignBones,
    OBJECT_OT_ApplyTransforms,
    OBJECT_OT_GenerateRig,
    MESH_OT_AddSelectedToParentList,
    MESH_OT_RemoveSelectedFromParentList,
    MESH_OT_ClearParentList,
    OBJECT_OT_ParentWithWeights,
    MESH_UL_MeshParentList,
    VIEW3D_PT_AutoRigToRigify,
]

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
