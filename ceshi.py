import matplotlib.pyplot as plt
import numpy as np
import dearpygui.dearpygui as dpg
from matplotlib.backends.backend_agg import FigureCanvasAgg

fig = plt.figure(figsize=(11.69, 8.26), dpi=100)
canvas = FigureCanvasAgg(fig)
ax = fig.gca()
canvas.draw()
buf = canvas.buffer_rgba()
image = np.asarray(buf)
image = image.astype(np.float32) / 255

dpg.create_context()

with dpg.texture_registry():
    dpg.add_raw_texture(
        1169, 826, image, format=dpg.mvFormat_Float_rgba, tag="texture_id"
    )

with dpg.window(tag="MatPlotLib"):
    dpg.add_image("texture_id")

dpg.create_viewport(title="a", width=1169, height=826)
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.set_primary_window("MatPlotLib", True)
dpg.start_dearpygui()
dpg.destroy_context()