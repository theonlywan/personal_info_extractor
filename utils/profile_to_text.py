from schema.personal_profile import PersonalProfile
from typing import List, Optional, Union, Any
from pydantic import BaseModel

def _is_empty(value: Any) -> bool:
    """Checks if a value is considered empty."""
    if value is None:
        return True
    if isinstance(value, str):
        return value.strip() == ""
    if isinstance(value, list):
        return not value
    if isinstance(value, BaseModel):
        return not value.model_dump(exclude_defaults=True, exclude_none=True)
    return False


def _convert_value_to_text(value: Any, indent_level: int = 0) -> Optional[str]:
    """
    Recursively converts a Pydantic field value (or any value) into a text string
    suitable for embedding. Handles nested models and lists of models.
    """
    if _is_empty(value):
        return None

    prefix = "  " * indent_level

    if isinstance(value, str):
        return value
    elif isinstance(value, int) or isinstance(value, float):
        return str(value)
    elif isinstance(value, list):
        item_texts = []
        for item in value:
            item_text = _convert_value_to_text(item, indent_level + 1)
            if item_text:
                item_texts.append(item_text.strip()) 

        if item_texts:
            if all(isinstance(item, str) for item in value):
                return "; ".join(item_texts)
            else:
                return " ".join(item_texts)
        return None

    elif isinstance(value, BaseModel):
        model_parts = []
        for field_name, field_value in value.model_dump(exclude_none=True, exclude_defaults=True).items():
            converted_field_value = _convert_value_to_text(field_value, indent_level + 1)
            if converted_field_value:
                model_parts.append(f"{field_name.replace('_', ' ').capitalize()}: {converted_field_value.strip()}")
        
        if model_parts:
            return " | ".join(model_parts)
        return None

    return None


def convert_profile_to_embeddable_text(profile: PersonalProfile) -> str:
    """
    Converts a PersonalProfile Pydantic model into a comprehensive text string
    suitable for generating embeddings. Handles all nested structures.
    """
    if not profile or _is_empty(profile):
        return ""

    parts = []

    for field_name, field_info in profile.model_fields.items():
        value = getattr(profile, field_name)

        if _is_empty(value):
            continue

        field_text = _convert_value_to_text(value)
        
        if field_text:
            parts.append(f"{field_name.replace('_', ' ').capitalize()}: {field_text}.")

    return " ".join(filter(None, parts)).strip()