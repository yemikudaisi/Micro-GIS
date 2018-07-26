from zoomtool import ZoomTool
from pantool import PanTool
import utils

types = utils.enum(
    ZOOM_IN_TOOL = "ZoomInTool",
    ZOOM_OUT_TOOL = "ZoomOutTool",
    ZOOM_ENVELOPE_TOOL = "ZoomEnvelopeTool",
    ZOOM_EXETENT_TOOL = "ZoomExtentTool",
    PAN_TOOL = "PanTool")

def validateToolType(type):
    if type not in (types.ZOOM_IN_TOOL, types.ZOOM_OUT_TOOL,types.ZOOM_ENVELOPE_TOOL,types.ZOOM_EXTENT_TOOL,types.PAN_TOOL):
        raise ValueError('map tool not valid')

__all__ = ['pantool', 'zoomtool']