from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk

class CustomToolbar(NavigationToolbar2Tk):
    def __init__(
        self,
        canvas,
        parent,
        on_export_magnitude=None,
        on_export_components=None,
        on_export_distribution=None,
        on_export_animation=None
    ):
        self.toolitems = list(NavigationToolbar2Tk.toolitems)

        if on_export_magnitude:
            self.toolitems.append((
                "Export Magnitude",
                "Export the data to a CSV file",
                "qt4_editor_options",
                "handle_export_magnitude"
            ))

        if on_export_components:
            self.toolitems.append((
                "Export Components",
                "Export the data to a CSV file",
                "qt4_editor_options",
                "handle_export_components"
            ))

        if on_export_distribution:
            self.toolitems.append((
                "Export Distribution",
                "Export the data to a CSV file",
                "qt4_editor_options",
                "handle_export_distribution"
            ))

        if on_export_animation:
            self.toolitems.append((
                "Export Animation",
                "Export the animation to an MP4 file",
                "qt4_editor_options",
                "handle_export_animation"
            ))

        super().__init__(canvas, parent)

        self.on_export_magnitude = on_export_magnitude
        self.on_export_components = on_export_components
        self.on_export_distribution = on_export_distribution
        self.on_export_animation = on_export_animation

    def handle_export_magnitude(self):
        if self.on_export_magnitude:
            self.on_export_magnitude()

    def handle_export_components(self):
        if self.on_export_components:
            self.on_export_components()

    def handle_export_distribution(self):
        if self.on_export_distribution:
            self.on_export_distribution()

    def handle_export_animation(self):
        if self.on_export_animation:
            self.on_export_animation()