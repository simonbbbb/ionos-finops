from typing import Dict, Any
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text


class TableFormatter:
    def __init__(self):
        self.console = Console()

    def format(self, summary: Dict[str, Any]) -> str:
        output_lines = []

        output_lines.append(f"\nProject: {summary.get('region', 'Unknown')}")
        output_lines.append(f"Total Resources: {summary.get('total_resources', 0)}\n")

        table = Table(title="Cost Breakdown", show_header=True, header_style="bold magenta")
        table.add_column("Resource", style="cyan", no_wrap=False)
        table.add_column("Monthly Cost", justify="right", style="green")
        table.add_column("Yearly Cost", justify="right", style="yellow")

        resources = summary.get("resources", [])

        for resource in resources:
            name = f"{resource['type']}.{resource['name']}"
            costs = resource.get("costs", {})
            monthly = costs.get("monthly", 0.0)
            yearly = costs.get("yearly", 0.0)

            table.add_row(name, f"€{monthly:.2f}", f"€{yearly:.2f}")

            breakdown = costs.get("breakdown", {})
            for component, cost in breakdown.items():
                if cost > 0:
                    table.add_row(
                        f"  └─ {component}", f"€{cost:.2f}", f"€{cost * 12:.2f}", style="dim"
                    )

        total_cost = summary.get("total_cost", {})
        table.add_section()
        table.add_row(
            "TOTAL",
            f"€{total_cost.get('monthly', 0.0):.2f}",
            f"€{total_cost.get('yearly', 0.0):.2f}",
            style="bold",
        )

        with self.console.capture() as capture:
            self.console.print(table)

        output_lines.append(capture.get())

        return "\n".join(output_lines)
