from typing import Union, Dict, List, Any
from bson import ObjectId
from pydantic import BaseModel


def str_to_objectid(id_str: Union[str, ObjectId]) -> ObjectId:
    """Convert string to ObjectId."""
    if isinstance(id_str, str):
        if ObjectId.is_valid(id_str):
            return ObjectId(id_str)
        raise ValueError(f"Invalid ObjectId: {id_str}")
    return id_str


def objectid_to_str(obj_id: ObjectId) -> str:
    """Convert ObjectId to string."""
    return str(obj_id)


def convert_objectids_to_str(data: Dict[str, Any]) -> Dict[str, Any]:
    """Convert all ObjectId values in a dict to strings."""
    result = {}
    for key, value in data.items():
        if isinstance(value, ObjectId):
            result[key] = str(value)
        elif isinstance(value, dict):
            result[key] = convert_objectids_to_str(value)
        elif isinstance(value, list):
            result[key] = [
                convert_objectids_to_str(item) if isinstance(item, dict)
                else str(item) if isinstance(item, ObjectId)
                else item
                for item in value
            ]
        else:
            result[key] = value
    return result


def convert_objectids_in_model(model: BaseModel) -> Dict[str, Any]:
    """Convert all ObjectId values in a Pydantic model to strings."""
    model_dict = model.dict()
    return convert_objectids_to_str(model_dict)


def prepare_for_mongo_query(query_filter: Dict[str, Any]) -> Dict[str, Any]:
    """Convert string IDs to ObjectIds in a query filter."""
    result = {}
    for key, value in query_filter.items():
        if key == "_id" and isinstance(value, str) and ObjectId.is_valid(value):
            result[key] = ObjectId(value)
        elif isinstance(value, dict):
            result[key] = prepare_for_mongo_query(value)
        elif isinstance(value, list):
            result[key] = [
                prepare_for_mongo_query(item) if isinstance(item, dict)
                else ObjectId(item) if key == "_id" and isinstance(item, str) and ObjectId.is_valid(item)
                else item
                for item in value
            ]
        else:
            result[key] = value
    return result 