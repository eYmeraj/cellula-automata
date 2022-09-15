
import bpy
import os

# File to use in blender

# https://docs.blender.org/api/current/info_quickstart.html
# https://blender.stackexchange.com/questions/79665/can-i-use-objects-custom-properties-inside-cycles-materials/93621#93621

time_frame = 0
time_scale = 2

iteration_max = 100
rule_passes = 10


def init():
    # clear
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.select_by_type(type='MESH')
    bpy.ops.object.delete()
    for item in bpy.data.meshes:
        bpy.data.meshes.remove(item)
        
    bpy.context.scene.frame_end = iteration_max
    
    for iteration in range(1,iteration_max):
        print(" =========== ITERATION {} ==========".format(iteration))
        for passes in range(1,rule_passes):
            project_path = 'your project path'
            file_loc = project_path + 'out/ca_p' + str(passes) + '_i' + str(iteration) + '.obj'
            if os.path.exists(file_loc):
                imported_object = bpy.ops.import_scene.obj(filepath=file_loc)
                ob = bpy.context.selected_objects[0] ####<--Fix
                ob.pass_index = passes; # set state for node to process
                ob["iteration"] = str(iteration)
                bpy.context.scene.frame_current = iteration + 1
                ob.hide_render = True
                ob.keyframe_insert("hide_render")
                 
                bpy.context.scene.frame_current = iteration
                ob.hide_render = False
                ob.keyframe_insert("hide_render")
                 
                bpy.context.scene.frame_current = iteration - 1
                ob.hide_render = True
                ob.keyframe_insert("hide_render")
                
                bpy.context.scene.frame_current = iteration + 1
                ob.hide_viewport = True
                ob.keyframe_insert("hide_viewport")
                 
                bpy.context.scene.frame_current = iteration
                ob.hide_viewport = False
                ob.keyframe_insert("hide_viewport")
                 
                bpy.context.scene.frame_current = iteration - 1
                ob.hide_viewport = True
                ob.keyframe_insert("hide_viewport")

init()