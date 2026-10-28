from app.agents.base_agent import BaseAgent


class ProductManagerAgent(BaseAgent):
    """Translate product requests into structured task descriptions."""

    def __init__(self) -> None:
        """Initialize the product manager with its role."""
        super().__init__(
            name="Product Manager",
            role="Product planning and requirements",
        )

    def run(self, task: str) -> str:
        """Return a basic requirements brief for the requested task."""
        if not task.strip():
            raise ValueError("Task must not be empty.")

        return (
            f"PRODUCT REQUIREMENTS\n"
            f"Objective: {task.strip()}\n"
            f"Role: {self.role}\n"
            f"Next action: Define scope, user needs, and acceptance criteria."
        )
