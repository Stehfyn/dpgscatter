import pandas as pd
import dearpygui.dearpygui as dpg
from utils import save_item

def on_file_dialog_cancel():
    print("user cancel")

class App:
    def __init__(self):
        self.setup_dpg()
        self.setup_variables()
        self.setup_window()
        with dpg.font_registry():
        # first argument ids the path to the .ttf or .otf file
            default_font = dpg.add_font("./assets/fonts/BrixSansRegular.otf", 20)
        dpg.bind_font(default_font)

    def run(self):
        dpg.set_primary_window("Primary Window", True)
        dpg.show_viewport()

        while dpg.is_dearpygui_running():
            jobs = dpg.get_callback_queue() # retrieves and clears queue
            dpg.run_callbacks(jobs)

            #anything you want to do every frame
            window_width = dpg.get_item_width("Primary Window")
            window_width -= dpg.get_item_pos("listbox_x")[0]*2
            dpg.set_item_width("listbox_x", window_width/2)
            dpg.set_item_width("listbox_y", window_width/2)

            dpg.render_dearpygui_frame()

    def __enter__(self):
        return self
    
    def __exit__(self, et, ev, etb):
        dpg.destroy_context()
        return True
    
    def setup_dpg(self):
        dpg.create_context()
        dpg.create_viewport(title='dpgscatter', width=1000, height=800)
        self.set_icon()
        dpg.setup_dearpygui()
        
    def setup_variables(self):
        #self.files is dict() where key is filename str, and value is filepath str {"example.csv":"C:\dev\example.csv"}
        self.files = {}
        self.filenames = []

        self.columns = []

        self.plot_types = ["Scatter"] # Something to extend later
        self.plot_views = {}
        self.plots = {}
        self.plot_axes = {}

        self.current_plot_view = self.plot_types[0]

        self.current_csv_df = {}
        self.current_x = ""
        self.current_y = ""

        self.output_file = "default"
        self.output_ext = ".png"
        self.output_file += self.output_ext

    def setup_window(self):
        dpg.push_container_stack(dpg.add_window(tag="Primary Window"))
        with dpg.theme(tag="plottheme") as variable_theme:
            with dpg.theme_component(dpg.mvAll):
                dpg.add_theme_color(dpg.mvPlotCol_Line, (255, 255, 255, 255), tag="plotcolor",category=dpg.mvThemeCat_Plots)
                dpg.add_theme_color(dpg.mvPlotCol_MarkerOutline, (255,0,0,255), tag="legendcolor",category=dpg.mvThemeCat_Plots)
                
            self.theme = variable_theme

        self.setup_input_menu()
        self.setup_plot_view()

        dpg.pop_container_stack()
        self.setup_file_dialog()

    def setup_input_menu(self):
        
        window_width = dpg.get_item_width("Primary Window")

        with dpg.group(horizontal=True):
            dpg.add_text("Files:")
            dpg.add_button(label="Load", callback=lambda: dpg.show_item("file_dialog_id"))
            
        self.listbox_files = dpg.add_listbox(self.filenames, num_items=len(self.filenames), tag="listbox_files", callback=self.on_listbox_files_clicked, width=-1)

        with dpg.group(horizontal=True):
            self.label_x = dpg.add_text("X:", tag="label_x")
            dpg.add_listbox(self.columns, num_items=len(self.columns), tag="listbox_x", callback=self.on_listbox_x_clicked)
            self.label_y = dpg.add_text("Y:", tag="label_y")
            dpg.add_listbox(self.columns, num_items=len(self.columns), tag="listbox_y", callback=self.on_listbox_y_clicked)

        with dpg.group(horizontal=True):
            dpg.add_button(tag="Save Button", label="Save", callback=save_item, user_data=("Scatter Plot", self.output_file))
            dpg.add_input_text(track_offset=0.5, callback=self.on_input_text_ok, width=400)
            dpg.add_combo([".png"],callback=self.on_combo_ok, width=100, default_value=".png")
            dpg.add_colormap_slider(width=-1, callback=self.color_picker_callback)
            dpg.bind_colormap(dpg.last_item(), dpg.mvPlotColormap_Plasma)
        #dpg.add_radio_button(self.plot_types, tag="radio_buttons", show=True, callback=self.on_radio_button_clicked, horizontal=True)

    def color_picker_callback(self, sender, user_data):
        user_data = dpg.sample_colormap(dpg.mvPlotColormap_Plasma, user_data)
        dpg.set_value("plotcolor", tuple([255*x for x in user_data]))
        dpg.set_value("legendcolor", tuple([255*x for x in user_data]))
    
    def setup_plot_view(self):
    
        with dpg.tree_node(label="Scatter Plot View", show=False, default_open=True) as scatterplotview:
            self.plot_views.update({"Scatter":scatterplotview})

            with dpg.plot(tag="Scatter Plot", label="Scatter Plot", height=400, width=-1) as scatterplot:
                self.plots.update({"Scatter":scatterplot})
                dpg.bind_item_theme(dpg.last_item(), "plottheme")

                xaxis = dpg.add_plot_axis(dpg.mvXAxis, label="x", tag="Scatter_x")
                self.plot_axes.update({"Scatter_x":xaxis})
                with dpg.plot_axis(dpg.mvYAxis, label="y", tag="Scatter_y") as yaxis:
                    dpg.add_scatter_series([],[], tag="Scatter Plot Data", label="ff")
                    self.plot_axes.update({"Scatter_y":yaxis})

        """ TODO: Implement Histogram
        with dpg.tree_node(label="Histogram Plot View", show=False, default_open=True) as histogramplotview:
            self.plot_views.update({"Histogram":histogramplotview})

            with dpg.plot(tag="Histogram Plot", label="Histogram Plot", height=400, width=-1) as histogramplot:
                self.plots.update({"Histogram":histogramplot})
                dpg.bind_item_theme(dpg.last_item(), self.theme)

                dpg.add_plot_legend()
                xaxis = dpg.add_plot_axis(dpg.mvXAxis, label="x", tag="Histogram_x")
                self.plot_axes.update({"Histogram_x":xaxis})

                with dpg.plot_axis(dpg.mvYAxis, label="y", tag="Histogram_y") as yaxis:
                    dpg.add_scatter_series([],[], tag="Histogram Plot Data", label="0.5 + 0.5 * sin(x)")
                    self.plot_axes.update({"Histogram_y":yaxis})
        """
        dpg.configure_item(self.plot_views[self.current_plot_view], show=True)

    def setup_file_dialog(self):
        with dpg.file_dialog(directory_selector=False, show=False, callback=self.on_file_dialog_ok, cancel_callback=on_file_dialog_cancel, tag="file_dialog_id", width=800, height=600, modal=True):
            dpg.add_file_extension(".csv", color=(123, 255, 132, 255))

    def on_input_text_ok(self, sender, user_data):
        self.output_file = user_data + self.output_ext
        dpg.configure_item("Save Button", user_data=("Scatter Plot", self.output_file))
        
    def on_combo_ok(self, sender, user_data):
        self.output_ext = user_data

    def on_file_dialog_ok(self, sender, user_data):
        if len(user_data.get("selections")) != 0:
            print(user_data["selections"])

            for key, value in user_data["selections"].items():
                if key not in self.files.keys():
                    self.files.update({key:value})
                    self.filenames.append(key)

            dpg.configure_item("listbox_files", items=self.filenames, num_items=len(self.filenames))
            self.on_listbox_files_clicked(sender, self.filenames[-1])

    def on_listbox_files_clicked(self, sender, user_data):
        #user_data here will be the filename selected, use it as a key to self.files to get the filepath
        filename: str = user_data
        self.current_csv_df = pd.read_csv(self.files[filename], sep= ',')

        #clear columns by assigning it an empty list
        self.columns = []

        for key in self.current_csv_df.keys():
            self.columns.append(key)

        dpg.configure_item("listbox_x", items=self.columns, num_items=len(self.columns))
        dpg.configure_item("listbox_y", items=self.columns, num_items=len(self.columns))

    def on_listbox_x_clicked(self, sender, user_data):
        self.current_x = user_data
        self.update_plot_view_values()

    def on_listbox_y_clicked(self, sender, user_data):
        self.current_y = user_data
        self.update_plot_view_values()

    def on_radio_button_clicked(self, sender, user_data):
        dpg.configure_item(self.plot_views[self.current_plot_view], show=False)
        dpg.configure_item(self.plot_views[user_data], show=True)
        self.current_plot_view = user_data
        self.update_plot_view_values()

    def update_plot_view_values(self):
        print(self.current_plot_view + " Plot Data")
        
        #pygui wants floats so lets give em floats
        float_x = []
        float_y = []

        for x in self.current_csv_df.get(self.current_x):
            float_x.append(float(x))
        
        for y in self.current_csv_df.get(self.current_y):
            float_y.append(float(y))
        
        dpg.fit_axis_data(self.plot_axes[self.current_plot_view + "_x"])
        dpg.fit_axis_data(self.plot_axes[self.current_plot_view + "_y"])

        dpg.set_value(self.current_plot_view + " Plot Data", [float_x, float_y])

    def set_icon(self):
        dpg.set_viewport_small_icon("./assets/images/ucsd.ico")
        dpg.set_viewport_large_icon("./assets/images/ucsd.ico")

def main():
    app = App()
    with app:
        app.run()

if __name__ == "__main__":
    main()