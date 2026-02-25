import os
import json
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import threading
import time

from ionos_finops.pricing.api import IonosPricingAPI, IonosAPIError

logger = logging.getLogger(__name__)


class PricingScheduler:
    def __init__(self, api_token: Optional[str] = None, cache_dir: Optional[Path] = None):
        self.api_token = api_token or os.getenv("IONOS_TOKEN")
        self.cache_dir = cache_dir or (Path.home() / ".ionos-finops" / "cache")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.running = False
        self.thread: Optional[threading.Thread] = None

        # Default regions to update
        self.regions = [
            "de/fra",
            "de/ber",
            "de/fra2",
            "gb/lhr",
            "gb/wor",
            "fr/par",
            "es/log",
            "us/las",
            "us/ewr",
            "us/kc",
        ]

    def start_scheduler(self, update_interval_hours: int = 24) -> None:
        """Start the background pricing update scheduler"""
        if self.running:
            logger.warning("Scheduler is already running")
            return

        if not self.api_token:
            logger.error("No API token provided, cannot start scheduler")
            return

        self.running = True
        self.thread = threading.Thread(
            target=self._run_scheduler, args=(update_interval_hours,), daemon=True
        )
        self.thread.start()
        logger.info(f"Started pricing scheduler with {update_interval_hours}h interval")

    def stop_scheduler(self) -> None:
        """Stop the background pricing update scheduler"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=10)
        logger.info("Stopped pricing scheduler")

    def _run_scheduler(self, update_interval_hours: int) -> None:
        """Run the scheduler loop"""
        while self.running:
            try:
                self._update_all_regions()

                # Sleep until next update
                sleep_time = update_interval_hours * 3600
                for _ in range(int(sleep_time)):
                    if not self.running:
                        break
                    time.sleep(1)

            except Exception as e:
                logger.error(f"Error in scheduler loop: {e}")
                # Sleep for a shorter interval on error
                time.sleep(300)  # 5 minutes

    def _update_all_regions(self) -> None:
        """Update pricing for all configured regions"""
        logger.info(f"Starting pricing update for {len(self.regions)} regions")

        api = IonosPricingAPI(self.api_token)
        if not api.validate_api_token():
            logger.error("Invalid API token, skipping update")
            return

        success_count = 0
        for region in self.regions:
            try:
                pricing_data = api.get_all_pricing(region)
                self._save_region_pricing(region, pricing_data)
                success_count += 1
                logger.info(f"✅ Updated pricing for {region}")
            except IonosAPIError as e:
                logger.error(f"❌ Failed to update pricing for {region}: {e}")

        logger.info(f"Pricing update complete: {success_count}/{len(self.regions)} regions updated")

    def _save_region_pricing(self, region: str, pricing_data: Dict[str, Any]) -> None:
        """Save pricing data for a specific region"""
        cache_file = self.cache_dir / f"pricing_{region.replace('/', '_')}.json"
        with open(cache_file, "w", encoding="utf-8") as f:
            json.dump(pricing_data, f, indent=2)

    def update_region_now(self, region: str) -> bool:
        """Manually update pricing for a specific region"""
        try:
            api = IonosPricingAPI(self.api_token)
            if not api.validate_api_token():
                logger.error("Invalid API token")
                return False

            pricing_data = api.get_all_pricing(region)
            self._save_region_pricing(region, pricing_data)
            logger.info(f"✅ Updated pricing for {region}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to update pricing for {region}: {e}")
            return False

    def get_last_update_time(self, region: str) -> Optional[datetime]:
        """Get the last update time for a region"""
        cache_file = self.cache_dir / f"pricing_{region.replace('/', '_')}.json"

        if not cache_file.exists():
            return None

        try:
            with open(cache_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                last_updated = data.get("last_updated")
                if last_updated:
                    return datetime.fromisoformat(last_updated.replace("Z", "+00:00"))
        except (ValueError, TypeError, json.JSONDecodeError):
            pass

        return None

    def is_update_needed(self, region: str, max_age_hours: int = 24) -> bool:
        """Check if pricing update is needed for a region"""
        last_update = self.get_last_update_time(region)

        if not last_update:
            return True

        return datetime.now() - last_update > timedelta(hours=max_age_hours)

    def get_update_status(self) -> Dict[str, Any]:
        """Get the update status for all regions"""
        status = {}

        for region in self.regions:
            last_update = self.get_last_update_time(region)
            status[region] = {
                "last_update": last_update.isoformat() if last_update else None,
                "needs_update": self.is_update_needed(region),
                "cache_file": str(self.cache_dir / f"pricing_{region.replace('/', '_')}.json"),
            }

        return {
            "scheduler_running": self.running,
            "api_token_configured": bool(self.api_token),
            "regions": status,
        }


# Global scheduler instance
_scheduler_instance: Optional[PricingScheduler] = None


def get_scheduler() -> Optional[PricingScheduler]:
    """Get the global scheduler instance"""
    global _scheduler_instance
    return _scheduler_instance


def start_global_scheduler(
    api_token: Optional[str] = None, update_interval_hours: int = 24
) -> None:
    """Start the global pricing scheduler"""
    global _scheduler_instance
    _scheduler_instance = PricingScheduler(api_token)
    _scheduler_instance.start_scheduler(update_interval_hours)


def stop_global_scheduler() -> None:
    """Stop the global pricing scheduler"""
    global _scheduler_instance
    if _scheduler_instance:
        _scheduler_instance.stop_scheduler()
        _scheduler_instance = None
