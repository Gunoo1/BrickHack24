from manim import *

class RiemannSumVisualization(Scene):
    def construct(self):
        # Title
        title = Text("Riemann Sum Visualization", font_size=48)
        self.play(title.animate.to_edge(UP))
        self.wait(1)

        # Axes
        axes = Axes(x_range=[0, 10, 1], y_range=[0, 10, 1],
                    axis_config={"include_tip": False})
        labels = axes.get_axis_labels(x_label="x", y_label="f(x)")

        # Function Graph
        graph = axes.plot(lambda x: 0.1 * x * (x - 10) + 10, color=BLUE)
        func_label = MathTex("f(x) = 0.1x(x-10) + 10").next_to(graph, UP, buff=0.5)

        # Riemann Rectangles
        riemann_rects = axes.get_riemann_rectangles(
            graph,
            x_range=[1, 9],
            dx=0.5,
            stroke_width=1,
            stroke_color=WHITE
        )

        # Add everything to the scene
        self.play(Create(axes), Write(labels))
        self.play(Create(graph), Write(func_label))
        self.wait(1)
        self.play(Create(riemann_rects))
        self.wait(2)

        # Explanation
        explanation = Tex(
            "Riemann sums approximate the area under a curve.",
            " By dividing the area into rectangles, ",
            "we can sum their areas to get an approximation.",
            font_size=32
        ).next_to(riemann_rects, DOWN, buff=0.5)

        self.play(Write(explanation))
        self.wait(3)
