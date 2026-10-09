"""Rule loader for parsing and validating YAML detection rules."""

import os
import glob
import logging
from typing import List, Optional
import yaml
from sqlalchemy.orm import Session
from app.config import settings
from app.detection.models import RuleDefinitionSchema
from app.models.rule import DetectionRule

logger = logging.getLogger(__name__)


def load_rule_from_file(file_path: str) -> Optional[RuleDefinitionSchema]:
    """Parse and validate a single YAML rule file."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        if not data:
            return None
        rule_obj = RuleDefinitionSchema(**data)
        return rule_obj
    except Exception as e:
        logger.error(f"Error parsing rule file {file_path}: {e}")
        return None


def load_all_rules_from_disk(rules_dir: Optional[str] = None) -> List[RuleDefinitionSchema]:
    """Load and validate all YAML rules found in the rules directory."""
    target_dir = rules_dir or settings.rules_dir
    if not os.path.isabs(target_dir):
        # Resolve relative to project root or current working dir
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
        resolved_path = os.path.join(base_dir, target_dir.lstrip("./"))
        if os.path.exists(resolved_path):
            target_dir = resolved_path

    if not os.path.exists(target_dir):
        logger.warning(f"Rules directory does not exist: {target_dir}")
        return []

    rules: List[RuleDefinitionSchema] = []
    yaml_files = glob.glob(os.path.join(target_dir, "*.yaml")) + glob.glob(os.path.join(target_dir, "*.yml"))

    for file_path in yaml_files:
        rule = load_rule_from_file(file_path)
        if rule:
            rules.append(rule)

    logger.info(f"Loaded {len(rules)} detection rules from {target_dir}")
    return rules


def sync_rules_to_db(db: Session, rules_dir: Optional[str] = None) -> int:
    """Sync file-based YAML detection rules into the database."""
    disk_rules = load_all_rules_from_disk(rules_dir)
    synced_count = 0

    for r in disk_rules:
        existing = db.query(DetectionRule).filter(DetectionRule.rule_id == r.id).first()
        conditions_dict = r.detection.model_dump()
        mitre_id = r.mitre_attack.technique_id if r.mitre_attack else None
        mitre_name = r.mitre_attack.technique_name if r.mitre_attack else None
        mitre_tactic = r.mitre_attack.tactic if r.mitre_attack else None

        if existing:
            existing.name = r.name
            existing.description = r.description
            existing.severity = r.severity
            existing.category = r.category
            existing.conditions = conditions_dict
            existing.mitre_technique_id = mitre_id
            existing.mitre_technique_name = mitre_name
            existing.mitre_tactic = mitre_tactic
            existing.version = r.version
            existing.rationale = r.rationale
            existing.evidence_fields = r.evidence_fields
            existing.false_positive_notes = r.false_positive_notes
        else:
            new_rule = DetectionRule(
                rule_id=r.id,
                name=r.name,
                description=r.description,
                severity=r.severity,
                category=r.category,
                enabled=r.enabled,
                conditions=conditions_dict,
                mitre_technique_id=mitre_id,
                mitre_technique_name=mitre_name,
                mitre_tactic=mitre_tactic,
                version=r.version,
                rationale=r.rationale,
                evidence_fields=r.evidence_fields,
                false_positive_notes=r.false_positive_notes
            )
            db.add(new_rule)
        synced_count += 1

    db.commit()
    return synced_count
