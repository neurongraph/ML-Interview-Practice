import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False


class ProfileManager:
    """Manages interview profiles: CRUD, question counts, YAML import."""

    def __init__(self, profiles_dir: Path):
        self.profiles_dir = profiles_dir
        profiles_dir.mkdir(parents=True, exist_ok=True)

    # ─── Profile CRUD ────────────────────────────────────────────────────────

    def list_profiles(self) -> List[str]:
        """Return sorted list of profile names (those with a profile.json)."""
        return sorted(
            d.name
            for d in self.profiles_dir.iterdir()
            if d.is_dir() and (d / "profile.json").exists()
        )

    def get_profile(self, name: str) -> Optional[Dict]:
        """Load and return profile config dict, or None if not found."""
        profile_file = self.profiles_dir / name / "profile.json"
        if not profile_file.exists():
            return None
        with open(profile_file) as f:
            return json.load(f)

    def save_profile(self, config: Dict) -> Path:
        """Persist a profile config. Creates directory. Returns profile dir path."""
        name = config["name"]
        profile_dir = self.profiles_dir / name
        profile_dir.mkdir(parents=True, exist_ok=True)
        config.setdefault("created_at", datetime.now().isoformat())
        with open(profile_dir / "profile.json", "w") as f:
            json.dump(config, f, indent=2)
        return profile_dir

    def delete_profile(self, name: str) -> bool:
        """Delete a profile directory. Returns True on success."""
        profile_dir = self.profiles_dir / name
        if profile_dir.exists():
            shutil.rmtree(profile_dir)
            return True
        return False

    # ─── YAML import ─────────────────────────────────────────────────────────

    def load_from_yaml(self, yaml_path: Path) -> Dict:
        """Load a profile config from a YAML file."""
        if not HAS_YAML:
            raise ImportError(
                "PyYAML is not installed. Run: uv add pyyaml"
            )
        with open(yaml_path) as f:
            return yaml.safe_load(f)

    # ─── Questions helpers ────────────────────────────────────────────────────

    def get_questions_path(self, profile_name: str) -> Path:
        return self.profiles_dir / profile_name / "questions.json"

    def get_question_count(self, profile_name: str) -> int:
        path = self.get_questions_path(profile_name)
        if not path.exists():
            return 0
        with open(path) as f:
            return len(json.load(f).get("questions", []))

    def get_topic_question_counts(self, profile_name: str) -> Dict[str, int]:
        """Return {topic_name: count} for all topics in a profile."""
        path = self.get_questions_path(profile_name)
        if not path.exists():
            return {}
        with open(path) as f:
            questions = json.load(f).get("questions", [])
        counts: Dict[str, int] = {}
        for q in questions:
            topic = q.get("topic", "Unknown")
            counts[topic] = counts.get(topic, 0) + 1
        return counts
