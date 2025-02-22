from manim import *

class EulerTheoremFixed(Scene):
    def construct(self):
        # Title
        title = Text("Euler's Theorem", font_size=48)
        self.play(Write(title))
        self.wait(2)
        self.play(title.animate.to_edge(UP))

        # Euler's Theorem statement
        theorem = Text("If gcd(a, n) = 1, then a^phi(n) = 1 (mod n)", font_size=28)
        explanation = Text("Where phi(n) is Euler's totient function.", font_size=24)
        theorem.next_to(title, DOWN, buff=1)
        explanation.next_to(theorem, DOWN, buff=0.5)
        self.play(Write(theorem))
        self.wait(2)
        self.play(Write(explanation))
        self.wait(2)

        # Example
        example_title = Text("Example:", font_size=28)
        example_title.next_to(explanation, DOWN, buff=1)
        self.play(Write(example_title))

        example = Text("a = 3, n = 7", font_size=28)
        example.next_to(example_title, DOWN, buff=0.5)
        self.play(Write(example))
        self.wait(2)

        gcd_part = Text("gcd(3, 7) = 1", font_size=28)
        gcd_part.next_to(example, DOWN, buff=0.5)
        self.play(Write(gcd_part))
        self.wait(2)

        phi_part = Text("phi(7) = 6", font_size=28)
        phi_part.next_to(gcd_part, DOWN, buff=0.5)
        self.play(Write(phi_part))
        self.wait(2)

        result_part = Text("3^6 = 1 (mod 7)", font_size=28)
        result_part.next_to(phi_part, DOWN, buff=0.5)
        self.play(Write(result_part))
        self.wait(3)

        # Conclusion
        conclusion = Text("Thus, Euler's theorem is verified for a=3, n=7", font_size=28)
        conclusion.next_to(result_part, DOWN, buff=1)
        self.play(Write(conclusion))
        self.wait(3)