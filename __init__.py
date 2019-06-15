bl_info = {
        "name": "batches",
        "blender": (2,80,0),
        "category":"util"
        }
from pathlib import Path
import bpy
from .which import which

from subprocess import Popen,PIPE
from pathlib import Path

def gmic_batch_op(gmic_exe_path,gmic_command_string,inputdir,outputdir,glob_pat="*.png"):
    for n,fpath in enumerate(Path(inputdir).glob(glob_pat)):
        pad = "%04d" % n
        outname = str(Path(outputdir) / (fpath.stem + pad + fpath.suffix))
        cmd = [gmic_exe_path,str(fpath),*gmic_command_string.split(),outname]
        print(cmd,end="-->")
        proc = Popen(cmd,stdout=PIPE,stderr=PIPE)
        out,err = proc.communicate()
        if err:
            print("!",err)
        print("output: ",out)

def _(c=None,r=[]):
    if c:
        r.append(c)
        return c
    return r

@_
class BGT_UL_job_listitem(bpy.types.UIList):
    def draw_item(self,context,layout,data,item,icon,ac_data,ac_prop):
        layout.label(text=item.name)
        layout.label(text=item.command.text)

@_
class BGT_UL_cmd_listitem(bpy.types.UIList):
    def draw_item(self,context,layout,data,item,icon,ac_data,ac_prop):
        layout.label(text=item.name)
        layout.label(text=item.text)

@_
class Executable(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty()
    path: bpy.props.StringProperty(subtype="FILE_PATH")

@_
class Command(bpy.types.PropertyGroup):
    binx: bpy.props.PointerProperty(type=Executable)
    name: bpy.props.StringProperty(default="cmd")
    text: bpy.props.StringProperty(default="+norm +ge[-1] 30% +pixelsort[0] +,xy,[1],[2] output[3]")

@_
class InputDir(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(default="input dir")
    path: bpy.props.StringProperty(default="g:\\Frames\\sqb",subtype="DIR_PATH")
@_
class OutputDir(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(default="output dir")
    path: bpy.props.StringProperty(default=str(Path.home()/"Desktop"),subtype="DIR_PATH")

@_
class Batch(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(default="batch job")
    inputdir: bpy.props.PointerProperty(type=InputDir)
    outputdir : bpy.props.PointerProperty(type=OutputDir)
    command : bpy.props.PointerProperty(type=Command)

@_
class Batches(bpy.types.PropertyGroup):
    jobs : bpy.props.CollectionProperty(type=Batch)
    jobs_i : bpy.props.IntProperty(min=-1,default=-1)

@_
class BGT_OT_do_batch(bpy.types.Operator):
    bl_idname = "batches.do_batch"
    bl_label = "do batch"
    job_index: bpy.props.IntProperty()
    @classmethod
    def poll(self,context):
        return True
    def execute(self,context):
        prefs = context.preferences.addons[__package__].preferences
        wm = context.window_manager
        t = wm.batches
        j = t.jobs[self.job_index]
        g = prefs.gmic
        cmd = j.command.text
        ipath = j.inputdir.path
        opath = j.outputdir.path
        gmic_batch_op(prefs.gmic,cmd,ipath,opath)
        return {"FINISHED"}

@_
class BGT_OT_add_job(bpy.types.Operator):
    bl_idname = "batches.add_job"
    bl_label = "add job"
    def execute(self,context):
        batches = context.window_manager.batches
        new = batches.jobs.add()
        new.name = "foo"
        return {"FINISHED"}
@_
class BGT_PT_main_panel(bpy.types.Panel):
    bl_label = "batch"
    bl_space_type = "CLIP_EDITOR"
    bl_region_type = "UI"
    bl_category = "batch"
    def draw(self,context):
        op = self.layout.operator("batches.do_batch")
        op.job_index = 0


@_
class BGT_PT_jobs(bpy.types.Panel):
    bl_label = "jobs"
    bl_space_type = "CLIP_EDITOR"
    bl_region_type = "UI"
    bl_category = "batch"
    bl_parent_id = "BGT_PT_main_panel"
    bl_order = 1
    def draw(self,context):
        wm = context.window_manager
        b = wm.batches
        self.layout.template_list("BGT_UL_job_listitem","",b,"jobs",b,"jobs_i")
        self.layout.operator("batches.add_job")


@_
class BGT_PT_info(bpy.types.Panel):
    bl_label = "info"
    bl_space_type = "CLIP_EDITOR"
    bl_region_type = "UI"
    bl_category = "batch"
    bl_parent_id = "BGT_PT_main_panel"
    bl_order = 2
    def draw(self,context):
        prefs = context.preferences.addons[__package__].preferences
        if prefs.gmic:
            self.layout.label(text=prefs.gmic)


@_
class BatchgmicSettings(bpy.types.AddonPreferences):
    bl_idname = __package__
    gmic: bpy.props.StringProperty(subtype="FILE_PATH",default=which("gmic.exe"))
    def draw(self,context):
        self.layout.prop(self,"gmic")


def register():
    list(map(bpy.utils.register_class,_()))
    bpy.types.WindowManager.batches = bpy.props.PointerProperty(type=Batches)
    t = bpy.context.window_manager.batches.jobs.add()


def unregister():
    list(map(bpy.utils.unregister_class,_()))

