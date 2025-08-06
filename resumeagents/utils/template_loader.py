"""
Template Loader for ResumeAgents framework.
"""

import json
import os
from pathlib import Path
from typing import Dict, Any


class TemplateLoader:
    """Loader for JSON templates used by agents."""
    
    def __init__(self, templates_dir: str = "resumeagents/templates"):
        self.templates_dir = Path(templates_dir)
    
    def load_template(self, template_name: str) -> Dict[str, Any]:
        """Load a JSON template by name."""
        template_file = self.templates_dir / f"{template_name}.json"
        
        if not template_file.exists():
            raise FileNotFoundError(f"Template not found: {template_file}")
        
        with open(template_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def get_template_structure(self, template_name: str) -> str:
        """Get the JSON structure as a string for use in prompts."""
        template = self.load_template(template_name)
        return json.dumps(template, ensure_ascii=False, indent=2)
    
    def list_available_templates(self) -> list:
        """List all available templates."""
        templates = []
        for file in self.templates_dir.glob("*.json"):
            templates.append(file.stem)
        return templates
    
    def validate_template(self, template_name: str, data: Dict[str, Any]) -> bool:
        """Validate that data matches the template structure."""
        template = self.load_template(template_name)
        
        def check_structure(template_keys, data_keys):
            """Recursively check if data structure matches template."""
            if isinstance(template_keys, dict):
                if not isinstance(data_keys, dict):
                    return False
                for key in template_keys:
                    if key not in data_keys:
                        return False
                    if not check_structure(template_keys[key], data_keys[key]):
                        return False
            elif isinstance(template_keys, list):
                if not isinstance(data_keys, list):
                    return False
                # For lists, we just check if it's a list, not the content
            return True
        
        return check_structure(template, data) 