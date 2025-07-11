from schema.personal_profile import (
    PersonalProfile, WorkPreferences, SocialEngagement,
    EducationEntry, WorkExperienceEntry, ProjectEntry, PublicationEntry,
    SkillEntry, CertificationEntry, AchievementEntry, ChallengeEntry,
    StrengthEntry, WeaknessEntry, GoalEntry, MotivationEntry, ValueEntry,
    ContactInfoEntry
)
from typing import List, Optional, Union, Any, Type, Dict
from pydantic import BaseModel
import json

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

def _merge_simple_field(existing_field: Optional[Union[str, int]], new_field: Optional[Union[str, int]], field_name: str) -> Optional[Union[str, int]]:
    """
    Merges simple fields (str or int).
    Prioritizes new, non-empty values. Special handling for professional_background.
    """
    if _is_empty(new_field):
        return existing_field

    if _is_empty(existing_field):
        return new_field

    if isinstance(existing_field, str) and isinstance(new_field, str):
        if field_name == "professional_background_summary":
            if new_field.lower() not in existing_field.lower() and existing_field.lower() not in new_field.lower():
                if len(new_field) < len(existing_field) - 15 or len(new_field) > len(existing_field) + 15:
                    return f"{existing_field.strip()} {new_field.strip()}".strip()
            return existing_field
        else:
            if len(new_field) < len(existing_field):
                return existing_field
            return new_field
    
    elif isinstance(existing_field, int) and isinstance(new_field, int):
        return new_field

    return new_field


def _merge_list_of_simple_types(existing_list: Optional[List[Any]], new_list: Optional[List[Any]]) -> Optional[List[Any]]:
    """Merges lists of simple types (str, int) using set union to remove duplicates."""
    if _is_empty(new_list):
        return existing_list
    if _is_empty(existing_list):
        return new_list

    merged_set = set(existing_list) | set(new_list)
    return list(merged_set)

def _get_model_identifier(model_obj: BaseModel) -> str:
    """Generates a semi-unique identifier for a BaseModel instance for merging."""
    if isinstance(model_obj, EducationEntry):
        return f"EDU_{model_obj.institution or ''}_{model_obj.degree or ''}_{model_obj.major or ''}".lower()
    elif isinstance(model_obj, WorkExperienceEntry):
        return f"WORK_{model_obj.company or ''}_{model_obj.title or ''}_{model_obj.start_date or ''}".lower()
    elif isinstance(model_obj, ProjectEntry):
        return f"PROJ_{model_obj.name or ''}_{model_obj.description or ''}".lower()
    elif isinstance(model_obj, PublicationEntry):
        return f"PUB_{model_obj.title or ''}_{model_obj.publication_date or ''}".lower()
    elif isinstance(model_obj, SkillEntry):
        return f"SKILL_{model_obj.name or ''}_{model_obj.category or ''}".lower()
    elif isinstance(model_obj, AchievementEntry):
        return f"ACHV_{model_obj.description or ''}".lower()
    return str(hash(json.dumps(model_obj.model_dump(sort_keys=True))))

def _deep_merge_model(existing_model: BaseModel, new_model: BaseModel) -> BaseModel:
    """
    Recursively merges fields of two BaseModel instances.
    Prioritizes new non-empty values for simple fields, and recursively merges nested models/lists.
    """
    merged_data = existing_model.model_dump(exclude_none=True, exclude_defaults=True)
    new_data = new_model.model_dump(exclude_none=True, exclude_defaults=True)

    for field_name, new_value in new_data.items():
        existing_value = merged_data.get(field_name)

        if _is_empty(new_value):
            continue

        if _is_empty(existing_value):
            merged_data[field_name] = new_value
            continue

        if isinstance(existing_value, BaseModel) and isinstance(new_value, BaseModel) and type(existing_value) == type(new_value):
            merged_data[field_name] = _deep_merge_model(existing_value, new_value).model_dump(exclude_none=True)
        elif isinstance(existing_value, list) and isinstance(new_value, list):
            if new_value and isinstance(new_value[0], BaseModel):
                merged_data[field_name] = [item.model_dump(exclude_none=True) for item in _merge_list_of_models(
                    [existing_model.__class__.model_fields[field_name].annotation.__args__[0].model_validate(item) for item in existing_value],
                    new_value
                )]
            else:
                merged_data[field_name] = _merge_list_of_simple_types(existing_value, new_value)
        else:
            merged_data[field_name] = new_value
    
    return existing_model.__class__(**merged_data)


def _merge_list_of_models(existing_list: List[BaseModel], new_list: List[BaseModel]) -> List[BaseModel]:
    """
    Merges two lists of BaseModel objects.
    Identifies existing items, deep merges them with new matching items,
    and appends new items not found in the existing list.
    """
    if _is_empty(new_list):
        return existing_list
    if _is_empty(existing_list):
        return new_list

    existing_items_map: Dict[str, BaseModel] = {}
    for item in existing_list:
        identifier = _get_model_identifier(item)
        if identifier:
            existing_items_map[identifier] = item

    merged_items: List[BaseModel] = []
    processed_identifiers = set()

    for new_item in new_list:
        identifier = _get_model_identifier(new_item)
        if identifier and identifier in existing_items_map:
            merged_item = _deep_merge_model(existing_items_map[identifier], new_item)
            merged_items.append(merged_item)
            processed_identifiers.add(identifier)
        else:
            merged_items.append(new_item)
            if identifier:
                processed_identifiers.add(identifier)

    for item in existing_list:
        identifier = _get_model_identifier(item)
        if identifier not in processed_identifiers:
            merged_items.append(item)

    return merged_items


def merge_personal_profiles(existing_profile: PersonalProfile, new_profile: PersonalProfile) -> PersonalProfile:
    """
    Deep merges a new PersonalProfile into an existing one.
    Handles simple fields, lists of simple types, lists of BaseModel, and nested BaseModels.
    """

    merged_profile = existing_profile.model_copy(deep=True)

    for field_name, new_field_obj in new_profile.model_dump(exclude_none=True, exclude_defaults=True).items():
        existing_field_obj = getattr(merged_profile, field_name, None)

        if _is_empty(new_field_obj):
            continue

        if _is_empty(existing_field_obj):
            setattr(merged_profile, field_name, new_field_obj) 
            continue

        if isinstance(new_field_obj, list) and isinstance(existing_field_obj, list):
            if new_field_obj and isinstance(new_field_obj[0], dict) and isinstance(new_profile.model_fields[field_name].annotation, type(List[BaseModel])):
                list_item_type = new_profile.model_fields[field_name].annotation.__args__[0]
                
                if issubclass(list_item_type, BaseModel):
                    reconstructed_existing_list = [list_item_type.model_validate(item) for item in existing_field_obj]
                    reconstructed_new_list = [list_item_type.model_validate(item) for item in new_field_obj]

                    merged_list = _merge_list_of_models(reconstructed_existing_list, reconstructed_new_list)
                    setattr(merged_profile, field_name, merged_list)
                else:
                    setattr(merged_profile, field_name, _merge_list_of_simple_types(existing_field_obj, new_field_obj))
            elif new_field_obj and isinstance(new_field_obj[0], BaseModel):
                 setattr(merged_profile, field_name, _merge_list_of_models(existing_field_obj, new_field_obj))
            else:
                setattr(merged_profile, field_name, _merge_list_of_simple_types(existing_field_obj, new_field_obj))

        elif isinstance(new_field_obj, BaseModel) and isinstance(existing_field_obj, BaseModel) and type(new_field_obj) == type(existing_field_obj):
            setattr(merged_profile, field_name, _deep_merge_model(existing_field_obj, new_field_obj))

        elif isinstance(new_field_obj, (str, int)) and isinstance(existing_field_obj, (str, int)):
            setattr(merged_profile, field_name, _merge_simple_field(existing_field_obj, new_field_obj, field_name))
        
        else:
            setattr(merged_profile, field_name, new_field_obj)
            
    return merged_profile