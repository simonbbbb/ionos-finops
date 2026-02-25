import json
import re
from pathlib import Path
from typing import Dict, List, Any, Optional

try:
    import hcl2

    HAS_HCL2 = True
except ImportError:
    HAS_HCL2 = False


class TerraformParser:
    def __init__(self, path: str):
        self.path = Path(path)
        self.resources: List[Dict[str, Any]] = []

    def parse(self) -> List[Dict[str, Any]]:
        if self.path.is_file():
            if self.path.suffix == ".tfplan":
                return self._parse_plan_file()
            elif self.path.suffix == ".tf":
                return self._parse_tf_file(self.path)
        elif self.path.is_dir():
            return self._parse_directory()
        else:
            raise ValueError(f"Path {self.path} is not a valid file or directory")

    def _parse_directory(self) -> List[Dict[str, Any]]:
        resources = []

        for tf_file in self.path.glob("*.tf"):
            resources.extend(self._parse_tf_file(tf_file))

        return resources

    def _parse_tf_file(self, file_path: Path) -> List[Dict[str, Any]]:
        resources = []

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                tf_dict = hcl2.loads(content)

                if "resource" in tf_dict:
                    for resource_block in tf_dict["resource"]:
                        for resource_type, resource_configs in resource_block.items():
                            if resource_type.startswith("ionos_"):
                                for resource_name, config in resource_configs.items():
                                    resources.append(
                                        {
                                            "type": resource_type,
                                            "name": resource_name,
                                            "config": config,
                                            "source_file": str(file_path),
                                        }
                                    )
        except Exception as e:
            print(f"Error parsing {file_path}: {e}")

        return resources

    def _parse_plan_file(self) -> List[Dict[str, Any]]:
        try:
            with open(self.path, "rb") as f:
                import subprocess

                result = subprocess.run(
                    ["terraform", "show", "-json", str(self.path)], capture_output=True, text=True
                )

                if result.returncode != 0:
                    raise ValueError(f"Failed to parse plan file: {result.stderr}")

                plan_data = json.loads(result.stdout)
                return self._extract_resources_from_plan(plan_data)
        except FileNotFoundError:
            raise ValueError("terraform command not found. Please install Terraform.")
        except Exception as e:
            raise ValueError(f"Error parsing plan file: {e}")

    def _extract_resources_from_plan(self, plan_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        resources = []

        if "planned_values" in plan_data and "root_module" in plan_data["planned_values"]:
            root_module = plan_data["planned_values"]["root_module"]

            if "resources" in root_module:
                for resource in root_module["resources"]:
                    resource_type = resource.get("type", "")
                    if resource_type.startswith("ionos_"):
                        resources.append(
                            {
                                "type": resource_type,
                                "name": resource.get("name", ""),
                                "config": resource.get("values", {}),
                                "address": resource.get("address", ""),
                                "mode": resource.get("mode", "managed"),
                            }
                        )

        return resources

    def filter_by_type(self, resource_type: str) -> List[Dict[str, Any]]:
        return [r for r in self.resources if r["type"] == resource_type]

    def get_resource_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        for resource in self.resources:
            if resource["name"] == name:
                return resource
        return None
