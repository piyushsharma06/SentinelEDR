"""Detection condition evaluator engine."""

import ipaddress
import re
from typing import Any, Dict, List, Optional
from app.detection.models import ConditionSchema, DetectionBlockSchema


def get_field_value(event_dict: Dict[str, Any], field_name: str) -> Any:
    """
    Extract field value from normalized event dictionary or its nested `data` payload.
    Supports dot-notation if nested fields exist.
    """
    if field_name in event_dict:
        return event_dict[field_name]
    
    # Check inside 'data' payload
    data_payload = event_dict.get("data", {})
    if isinstance(data_payload, dict) and field_name in data_payload:
        return data_payload[field_name]
    
    # Support dot notation (e.g. data.process_name)
    if "." in field_name:
        parts = field_name.split(".")
        current = event_dict
        for p in parts:
            if isinstance(current, dict) and p in current:
                current = current[p]
            else:
                return None
        return current

    return None


def evaluate_condition(condition: ConditionSchema, event_dict: Dict[str, Any]) -> bool:
    """Evaluate a single condition against the event attributes."""
    val = get_field_value(event_dict, condition.field)
    if val is None:
        return False

    op = condition.operator
    target = condition.value

    # Normalize strings for case-insensitive comparisons
    str_val = str(val).lower() if isinstance(val, (str, int, float)) else ""

    if op == "equals":
        if isinstance(target, str) and isinstance(val, str):
            return str_val == str(target).lower()
        return val == target

    elif op == "not_equals":
        if isinstance(target, str) and isinstance(val, str):
            return str_val != str(target).lower()
        return val != target

    elif op == "in":
        if isinstance(target, list):
            target_lower = [str(x).lower() for x in target]
            return str_val in target_lower
        return False

    elif op == "not_in":
        if isinstance(target, list):
            target_lower = [str(x).lower() for x in target]
            return str_val not in target_lower
        return True

    elif op == "contains":
        return str(target).lower() in str_val

    elif op == "matches_any_substring":
        if isinstance(target, list):
            return any(str(sub).lower() in str_val for sub in target)
        elif isinstance(target, str):
            return str(target).lower() in str_val
        return False

    elif op == "matches_regex":
        try:
            pattern = re.compile(str(target), re.IGNORECASE)
            return bool(pattern.search(str(val)))
        except re.error:
            return False

    elif op == "greater_than":
        try:
            return float(val) > float(target)
        except (ValueError, TypeError):
            return False

    elif op == "less_than":
        try:
            return float(val) < float(target)
        except (ValueError, TypeError):
            return False

    elif op == "not_in_cidr_or_local":
        # Check if remote IP is NOT in local/loopback/specified networks
        try:
            ip_obj = ipaddress.ip_address(str(val).strip())
            if ip_obj.is_loopback or ip_obj.is_unspecified:
                return False
            # If target specifies list of addresses or subnets
            if isinstance(target, list):
                for excluded in target:
                    try:
                        if "/" in str(excluded):
                            if ip_obj in ipaddress.ip_network(str(excluded), strict=False):
                                return False
                        else:
                            if ip_obj == ipaddress.ip_address(str(excluded)):
                                return False
                    except ValueError:
                        continue
            return True
        except ValueError:
            return False

    return False


def evaluate_detection_block(block: DetectionBlockSchema, event_dict: Dict[str, Any]) -> bool:
    """Evaluate full detection logic (all or any) for a given event."""
    if event_dict.get("event_type") != block.event_type:
        return False

    if not block.conditions:
        return False

    if block.logic == "all":
        return all(evaluate_condition(cond, event_dict) for cond in block.conditions)
    elif block.logic == "any":
        return any(evaluate_condition(cond, event_dict) for cond in block.conditions)
    
    return False
