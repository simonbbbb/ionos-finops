import json
import sys
from pathlib import Path
from typing import Any, Dict, Optional

import click
import yaml

from ionos_finops.output.html import HTMLFormatter
from ionos_finops.output.json import JSONFormatter
from ionos_finops.output.table import TableFormatter
from ionos_finops.pricing.calculator import CostCalculator


@click.group()
@click.version_option(version="0.1.0")
def main():
    pass


@main.command()
@click.option(
    "--path", type=click.Path(exists=True), default=".", help="Path to Terraform directory or file"
)
@click.option(
    "--plan-file", type=click.Path(exists=True), help="Path to Terraform plan file (.tfplan)"
)
@click.option(
    "--format", type=click.Choice(["table", "json", "html"]), default="table", help="Output format"
)
@click.option("--output", type=click.Path(), help="Output file path (default: stdout)")
@click.option("--region", default="de/fra", help="IONOS region")
@click.option("--config", type=click.Path(exists=True), help="Path to configuration file")
@click.option("--use-api", is_flag=True, help="Use IONOS API for real-time pricing")
@click.option("--api-token", envvar="IONOS_TOKEN", help="IONOS API token")
@click.option("--cache-ttl", type=int, default=24, help="Pricing cache TTL in hours")
def breakdown(
    path: str,
    plan_file: Optional[str],
    format: str,
    output: Optional[str],
    region: str,
    config: Optional[str],
    use_api: bool,
    api_token: Optional[str],
    cache_ttl: int,
):
    try:
        custom_pricing = None
        if config:
            custom_pricing = _load_config(config)

        calculator = CostCalculator(
            region=region,
            custom_pricing=custom_pricing,
            use_api=use_api,
            api_token=api_token,
            cache_ttl=cache_ttl,
        )

        target_path = plan_file if plan_file else path
        calculator.load_from_terraform(target_path)

        summary = calculator.get_summary()

        if format == "table":
            table_formatter = TableFormatter()
            result = table_formatter.format(summary)
        elif format == "json":
            json_formatter = JSONFormatter()
            result = json_formatter.format(summary)
        elif format == "html":
            html_formatter = HTMLFormatter()
            result = html_formatter.format(summary)
        else:
            result = str(summary)

        if output:
            with open(output, "w", encoding="utf-8") as f:
                f.write(result)
            click.echo(f"Cost breakdown written to {output}")
        else:
            click.echo(result)

    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@main.command()
@click.option(
    "--path", type=click.Path(exists=True), default=".", help="Path to Terraform directory"
)
@click.option("--region", default="de/fra", help="IONOS region")
def diff(path: str, region: str):
    click.echo("Diff functionality coming soon!")
    click.echo("This will compare current state with planned changes.")


@main.command()
@click.option("--api-token", envvar="IONOS_TOKEN", help="IONOS API token")
@click.option("--region", default="de/fra", help="IONOS region")
def update_pricing(api_token: Optional[str], region: str):
    try:
        if not api_token:
            click.echo("Error: IONOS API token is required", err=True)
            click.echo("Set IONOS_TOKEN environment variable or use --api-token option", err=True)
            sys.exit(1)

        from ionos_finops.pricing.api import IonosAPIError, IonosPricingAPI

        api = IonosPricingAPI(api_token)
        if not api.validate_api_token():
            click.echo("Error: Invalid API token", err=True)
            sys.exit(1)

        click.echo(f"Updating pricing data for {region}...")

        pricing_data = api.get_all_pricing(region)

        # Save to cache
        import json
        from pathlib import Path

        cache_dir = Path.home() / ".ionos-finops" / "cache"
        cache_dir.mkdir(parents=True, exist_ok=True)

        cache_file = cache_dir / f"pricing_{region.replace('/', '_')}.json"
        with open(cache_file, "w", encoding="utf-8") as f:
            json.dump(pricing_data, f, indent=2)

        click.echo(f"✅ Pricing data updated and cached to {cache_file}")
        click.echo(f"Last updated: {pricing_data.get('last_updated')}")
        click.echo(f"Source: {pricing_data.get('source')}")

    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@main.command()
@click.option("--api-token", envvar="IONOS_TOKEN", help="IONOS API token")
@click.option("--interval", type=int, default=24, help="Update interval in hours")
@click.option("--status", is_flag=True, help="Show scheduler status")
@click.option("--stop", is_flag=True, help="Stop the scheduler")
def scheduler(api_token: Optional[str], interval: int, status: bool, stop: bool):
    try:
        from ionos_finops.pricing.scheduler import (
            get_scheduler,
            start_global_scheduler,
            stop_global_scheduler,
        )

        if stop:
            stop_global_scheduler()
            click.echo("🛑 Pricing scheduler stopped")
            return

        if status:
            scheduler = get_scheduler()
            if scheduler:
                update_status = scheduler.get_update_status()
                click.echo("📊 Pricing Scheduler Status:")
                click.echo(f"Running: {'✅' if update_status['scheduler_running'] else '❌'}")
                click.echo(f"API Token: {'✅' if update_status['api_token_configured'] else '❌'}")
                click.echo("\nRegion Status:")
                for region, info in update_status["regions"].items():
                    last_update = info["last_update"]
                    needs_update = info["needs_update"]
                    status_icon = "⚠️" if needs_update else "✅"
                    click.echo(f"  {region}: {status_icon} {last_update or 'Never'}")
            else:
                click.echo("❌ Scheduler is not running")
            return

        if not api_token:
            click.echo("Error: IONOS API token is required", err=True)
            click.echo("Set IONOS_TOKEN environment variable or use --api-token option", err=True)
            sys.exit(1)

        start_global_scheduler(api_token, interval)
        click.echo(f"🚀 Started pricing scheduler with {interval}h interval")
        click.echo("Use 'ionos-finops scheduler --status' to check status")
        click.echo("Use 'ionos-finops scheduler --stop' to stop the scheduler")

    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


def _load_config(config_path: str) -> Dict[str, Any]:
    with open(config_path, "r", encoding="utf-8") as f:
        if config_path.endswith(".json"):
            result: Dict[str, Any] = json.load(f)
            return result
        elif config_path.endswith((".yml", ".yaml")):
            yaml_result = yaml.safe_load(f)
            if isinstance(yaml_result, dict):
                return yaml_result
            return {}
        else:
            raise ValueError("Config file must be JSON or YAML")


if __name__ == "__main__":
    main()
