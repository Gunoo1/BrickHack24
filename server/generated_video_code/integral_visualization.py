from manim import *

class IntegralVisualization(Scene):
    def construct(self):
        # Define the axes
        axes = Axes(
            x_range=[0, 10, 1],
            y_range=[0, 10, 1],
            axis_config={"color": BLUE}
        )

        # Define the function to be integrated
        func = lambda x: 0.1 * x**2
        graph = axes.plot(func, color=WHITE)

        # Define the area under the curve
        area = axes.get_area(graph, x_range=[2, 8], color=GREY, opacity=0.5)

        # Add labels
        labels = axes.get_axis_labels(x_label="x", y_label="f(x)")

        # Create text for explanation
        explanation = Tex(
            "The integral of a function \\textit{f(x)} ",
            "from \\textit{a} to \\textit{b} ",
            "is the area under the curve ",
            "between \\textit{a} and \\textit{b}.",
            font_size=36
        )
        explanation.to_edge(UP)

        # Create the animations
        self.play(Create(axes), Write(labels))
        self.play(Create(graph), run_time=2)
        self.play(FadeIn(area), run_time=2)
        self.play(Write(explanation), run_time=3)
        self.wait(2)
