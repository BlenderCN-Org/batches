bl_info = {
        "name": "batchgmic",
        "blender": (2,80,0),
        "category":"util"
        }
from pathlib import Path as _p
import bpy
from .which import which
from .batch_operation import gmic_batch_op


def _(c=None,r=[]):
    if c:
        r.append(c)
        return c
    return r

@_
class BGT_UL_job_listitem(bpy.types.UIList):
    def draw_item(self,context,layout,data,item,icon,ac_data,ac_prop):
        layout.label(text=item.name)
        layout.label(text=item.gmiccommand.title)


@_
class GmicCommand(bpy.types.PropertyGroup):
    title: bpy.props.StringProperty(default="gmic command")
    command: bpy.props.StringProperty(default="+norm +ge[-1] 30% +pixelsort[0] +,xy,[1],[2] output[3]")


@_
class InputDir(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(default="input dir")
    path: bpy.props.StringProperty(default="g:\\Frames\\seqb",subtype="DIR_PATH")
@_
class OutputDir(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(default="output dir")
    path: bpy.props.StringProperty(default=str(_p.home()/"Desktop"),subtype="DIR_PATH")


@_
class Batch(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(default="batch job")
    inputdir: bpy.props.PointerProperty(type=InputDir)
    infiles : bpy.props.StringProperty()
    outputdir : bpy.props.PointerProperty(type=OutputDir)
    gmiccommand : bpy.props.PointerProperty(type=GmicCommand)


@_
class BGTSession(bpy.types.PropertyGroup):
    jobs : bpy.props.CollectionProperty(type=Batch)
    jobs_i : bpy.props.IntProperty(min=-1,default=-1)


@_
class BGT_OT_do_batch(bpy.types.Operator):
    bl_idname = "bgt.do_batch"
    bl_label = "do batch"
    job_index: bpy.props.IntProperty()
    @classmethod
    def poll(self,context):
        return True
    def execute(self,context):
        prefs = context.preferences.addons[__package__].preferences
        wm = context.window_manager
        t = wm.bgt
        j = t.jobs[self.job_index]
        cmd = j.gmiccommand.command
        ipath = j.inputdir.path
        opath = j.outputdir.path
        print("cmd,ipath,opath:",cmd,ipath,opath)
        gmic_batch_op(prefs.gmic,cmd,ipath,opath)
        print("j:",j)
        print("t:",t)
        return {"FINISHED"}

@_
class BGT_PT_main_panel(bpy.types.Panel):
    bl_label = "batch"
    bl_space_type = "CLIP_EDITOR"
    bl_region_type = "UI"
    bl_category = "batch"
    def draw(self,context):
        op = self.layout.operator("bgt.do_batch")
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
        b = wm.bgt
        self.layout.template_list("BGT_UL_job_listitem","",b,"jobs",b,"jobs_i")


@_
class BGT_PT_gmic(bpy.types.Panel):
    bl_label = "gmic"
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
    bpy.types.WindowManager.bgt = bpy.props.PointerProperty(type=BGTSession)
    t = bpy.context.window_manager.bgt.jobs.add()


def unregister():
    list(map(bpy.utils.unregister_class,_()))

