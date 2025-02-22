from manim import *

class GraphYEquals10X(Scene):
    def construct(self):
        # Create axes
        axes = Axes(
            x_range=[-10, 10, 1],
            y_range=[-100, 100, 10],
            axis_config={"color": BLUE}
        )
        labels = axes.get_axis_labels(x_label="x", y_label="y")

        # Define the function
        def func(x):
            return 10 * x

        # Create the graph of the function
        graph = axes.plot(func, color=WHITE)

        # Create the subtitle
        subtitle = Text("Graph of y = 10x", font_size=24).to_edge(UP)

        # Add all elements to the scene
        self.play(Create(axes), Write(labels))
        self.play(Create(graph), Write(subtitle))
        self.wait(2)
