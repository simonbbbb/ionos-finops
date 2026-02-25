from typing import Dict, Any
from jinja2 import Template


class HTMLFormatter:
    def __init__(self):
        self.template = self._get_template()
    
    def format(self, summary: Dict[str, Any]) -> str:
        return self.template.render(summary=summary)
    
    def _get_template(self) -> Template:
        template_str = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>IONOS FinOps Cost Report</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
        }
        .header h1 {
            margin: 0 0 10px 0;
        }
        .summary {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .summary-card {
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .summary-card h3 {
            margin: 0 0 10px 0;
            color: #666;
            font-size: 14px;
            text-transform: uppercase;
        }
        .summary-card .value {
            font-size: 32px;
            font-weight: bold;
            color: #333;
        }
        .resources {
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        table {
            width: 100%;
            border-collapse: collapse;
        }
        th {
            background-color: #f8f9fa;
            padding: 12px;
            text-align: left;
            font-weight: 600;
            border-bottom: 2px solid #dee2e6;
        }
        td {
            padding: 12px;
            border-bottom: 1px solid #dee2e6;
        }
        tr:hover {
            background-color: #f8f9fa;
        }
        .resource-name {
            font-family: 'Courier New', monospace;
            color: #667eea;
        }
        .breakdown {
            font-size: 12px;
            color: #666;
            padding-left: 20px;
        }
        .total-row {
            font-weight: bold;
            background-color: #f8f9fa;
        }
        .cost {
            text-align: right;
            font-family: 'Courier New', monospace;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>IONOS FinOps Cost Report</h1>
        <p>Region: {{ summary.region }} | Resources: {{ summary.total_resources }}</p>
    </div>
    
    <div class="summary">
        <div class="summary-card">
            <h3>Monthly Cost</h3>
            <div class="value">€{{ "%.2f"|format(summary.total_cost.monthly) }}</div>
        </div>
        <div class="summary-card">
            <h3>Yearly Cost</h3>
            <div class="value">€{{ "%.2f"|format(summary.total_cost.yearly) }}</div>
        </div>
        <div class="summary-card">
            <h3>Hourly Cost</h3>
            <div class="value">€{{ "%.4f"|format(summary.total_cost.hourly) }}</div>
        </div>
    </div>
    
    <div class="resources">
        <h2>Resource Breakdown</h2>
        <table>
            <thead>
                <tr>
                    <th>Resource</th>
                    <th style="text-align: right;">Monthly</th>
                    <th style="text-align: right;">Yearly</th>
                </tr>
            </thead>
            <tbody>
                {% for resource in summary.resources %}
                <tr>
                    <td class="resource-name">{{ resource.type }}.{{ resource.name }}</td>
                    <td class="cost">€{{ "%.2f"|format(resource.costs.monthly) }}</td>
                    <td class="cost">€{{ "%.2f"|format(resource.costs.yearly) }}</td>
                </tr>
                {% for component, cost in resource.costs.breakdown.items() %}
                {% if cost > 0 %}
                <tr>
                    <td class="breakdown">└─ {{ component }}</td>
                    <td class="cost breakdown">€{{ "%.2f"|format(cost) }}</td>
                    <td class="cost breakdown">€{{ "%.2f"|format(cost * 12) }}</td>
                </tr>
                {% endif %}
                {% endfor %}
                {% endfor %}
                <tr class="total-row">
                    <td>TOTAL</td>
                    <td class="cost">€{{ "%.2f"|format(summary.total_cost.monthly) }}</td>
                    <td class="cost">€{{ "%.2f"|format(summary.total_cost.yearly) }}</td>
                </tr>
            </tbody>
        </table>
    </div>
    
    <div style="margin-top: 30px; text-align: center; color: #666; font-size: 12px;">
        Generated by IONOS FinOps
    </div>
</body>
</html>
        """
        return Template(template_str)
