"""
Validation utilities for the agent framework.

This module provides utilities for validating input data.
"""
from typing import Dict, List, Any, Optional, Tuple, Callable, TypeVar, Generic, Union
import re
import json
import jsonschema
from jsonschema.exceptions import ValidationError as JsonSchemaValidationError

from agents.refactored.core.errors import ValidationError


T = TypeVar('T')


class Validator(Generic[T]):
    """
    Base validator class.
    
    This class provides a foundation for building validators that can validate
    and transform input data.
    """
    
    def __init__(self, name: str):
        """
        Initialize the validator.
        
        Args:
            name: The name of the field being validated
        """
        self.name = name
    
    def validate(self, value: Any) -> T:
        """
        Validate and transform the input value.
        
        Args:
            value: The value to validate
            
        Returns:
            The validated and transformed value
            
        Raises:
            ValidationError: If validation fails
        """
        raise NotImplementedError("Subclasses must implement validate()")


class StringValidator(Validator[str]):
    """Validator for string values."""
    
    def __init__(
        self,
        name: str,
        min_length: Optional[int] = None,
        max_length: Optional[int] = None,
        pattern: Optional[str] = None,
        required: bool = True
    ):
        """
        Initialize the string validator.
        
        Args:
            name: The name of the field being validated
            min_length: Minimum length of the string
            max_length: Maximum length of the string
            pattern: Regular expression pattern to match
            required: Whether the field is required
        """
        super().__init__(name)
        self.min_length = min_length
        self.max_length = max_length
        self.pattern = pattern
        self.required = required
        
        # Compile the pattern if provided
        self.pattern_re = re.compile(pattern) if pattern else None
    
    def validate(self, value: Any) -> str:
        """
        Validate and transform the input value.
        
        Args:
            value: The value to validate
            
        Returns:
            The validated string
            
        Raises:
            ValidationError: If validation fails
        """
        # Check if the value is None or empty
        if value is None or (isinstance(value, str) and value.strip() == ""):
            if self.required:
                raise ValidationError(f"{self.name} is required", self.name)
            return ""
        
        # Convert to string if not already
        if not isinstance(value, str):
            value = str(value)
        
        # Check length constraints
        if self.min_length is not None and len(value) < self.min_length:
            raise ValidationError(
                f"{self.name} must be at least {self.min_length} characters long",
                self.name
            )
        
        if self.max_length is not None and len(value) > self.max_length:
            raise ValidationError(
                f"{self.name} must be at most {self.max_length} characters long",
                self.name
            )
        
        # Check pattern constraint
        if self.pattern_re and not self.pattern_re.match(value):
            raise ValidationError(
                f"{self.name} must match pattern: {self.pattern}",
                self.name
            )
        
        return value


class NumberValidator(Validator[Union[int, float]]):
    """Validator for numeric values."""
    
    def __init__(
        self,
        name: str,
        min_value: Optional[Union[int, float]] = None,
        max_value: Optional[Union[int, float]] = None,
        integer_only: bool = False,
        required: bool = True
    ):
        """
        Initialize the number validator.
        
        Args:
            name: The name of the field being validated
            min_value: Minimum allowed value
            max_value: Maximum allowed value
            integer_only: Whether to allow only integers
            required: Whether the field is required
        """
        super().__init__(name)
        self.min_value = min_value
        self.max_value = max_value
        self.integer_only = integer_only
        self.required = required
    
    def validate(self, value: Any) -> Union[int, float]:
        """
        Validate and transform the input value.
        
        Args:
            value: The value to validate
            
        Returns:
            The validated number
            
        Raises:
            ValidationError: If validation fails
        """
        # Check if the value is None or empty
        if value is None or (isinstance(value, str) and value.strip() == ""):
            if self.required:
                raise ValidationError(f"{self.name} is required", self.name)
            return 0
        
        # Convert to number
        try:
            if self.integer_only:
                if isinstance(value, float):
                    if value.is_integer():
                        value = int(value)
                    else:
                        raise ValidationError(
                            f"{self.name} must be an integer",
                            self.name
                        )
                else:
                    value = int(value)
            else:
                value = float(value)
        except (ValueError, TypeError):
            raise ValidationError(
                f"{self.name} must be a valid number",
                self.name
            )
        
        # Check range constraints
        if self.min_value is not None and value < self.min_value:
            raise ValidationError(
                f"{self.name} must be at least {self.min_value}",
                self.name
            )
        
        if self.max_value is not None and value > self.max_value:
            raise ValidationError(
                f"{self.name} must be at most {self.max_value}",
                self.name
            )
        
        return value


class BooleanValidator(Validator[bool]):
    """Validator for boolean values."""
    
    def __init__(self, name: str, required: bool = True):
        """
        Initialize the boolean validator.
        
        Args:
            name: The name of the field being validated
            required: Whether the field is required
        """
        super().__init__(name)
        self.required = required
    
    def validate(self, value: Any) -> bool:
        """
        Validate and transform the input value.
        
        Args:
            value: The value to validate
            
        Returns:
            The validated boolean
            
        Raises:
            ValidationError: If validation fails
        """
        # Check if the value is None or empty
        if value is None or (isinstance(value, str) and value.strip() == ""):
            if self.required:
                raise ValidationError(f"{self.name} is required", self.name)
            return False
        
        # Convert to boolean
        if isinstance(value, bool):
            return value
        
        if isinstance(value, str):
            value = value.lower()
            if value in ("true", "yes", "1", "y", "t"):
                return True
            if value in ("false", "no", "0", "n", "f"):
                return False
        
        if isinstance(value, (int, float)):
            return bool(value)
        
        raise ValidationError(
            f"{self.name} must be a valid boolean",
            self.name
        )


class ListValidator(Validator[List[Any]]):
    """Validator for list values."""
    
    def __init__(
        self,
        name: str,
        item_validator: Optional[Validator] = None,
        min_length: Optional[int] = None,
        max_length: Optional[int] = None,
        required: bool = True
    ):
        """
        Initialize the list validator.
        
        Args:
            name: The name of the field being validated
            item_validator: Optional validator for list items
            min_length: Minimum length of the list
            max_length: Maximum length of the list
            required: Whether the field is required
        """
        super().__init__(name)
        self.item_validator = item_validator
        self.min_length = min_length
        self.max_length = max_length
        self.required = required
    
    def validate(self, value: Any) -> List[Any]:
        """
        Validate and transform the input value.
        
        Args:
            value: The value to validate
            
        Returns:
            The validated list
            
        Raises:
            ValidationError: If validation fails
        """
        # Check if the value is None or empty
        if value is None or (isinstance(value, (str, list)) and len(value) == 0):
            if self.required:
                raise ValidationError(f"{self.name} is required", self.name)
            return []
        
        # Convert to list if not already
        if isinstance(value, str):
            try:
                value = json.loads(value)
                if not isinstance(value, list):
                    value = [value]
            except json.JSONDecodeError:
                value = [value]
        elif not isinstance(value, list):
            value = [value]
        
        # Check length constraints
        if self.min_length is not None and len(value) < self.min_length:
            raise ValidationError(
                f"{self.name} must have at least {self.min_length} items",
                self.name
            )
        
        if self.max_length is not None and len(value) > self.max_length:
            raise ValidationError(
                f"{self.name} must have at most {self.max_length} items",
                self.name
            )
        
        # Validate items if item validator is provided
        if self.item_validator:
            validated_items = []
            for i, item in enumerate(value):
                try:
                    validated_item = self.item_validator.validate(item)
                    validated_items.append(validated_item)
                except ValidationError as e:
                    raise ValidationError(
                        f"{self.name}[{i}]: {e.message}",
                        self.name
                    )
            value = validated_items
        
        return value


class DictValidator(Validator[Dict[str, Any]]):
    """Validator for dictionary values."""
    
    def __init__(
        self,
        name: str,
        schema: Optional[Dict[str, Validator]] = None,
        required: bool = True
    ):
        """
        Initialize the dictionary validator.
        
        Args:
            name: The name of the field being validated
            schema: Optional schema for dictionary fields
            required: Whether the field is required
        """
        super().__init__(name)
        self.schema = schema or {}
        self.required = required
    
    def validate(self, value: Any) -> Dict[str, Any]:
        """
        Validate and transform the input value.
        
        Args:
            value: The value to validate
            
        Returns:
            The validated dictionary
            
        Raises:
            ValidationError: If validation fails
        """
        # Check if the value is None or empty
        if value is None or (isinstance(value, (str, dict)) and len(value) == 0):
            if self.required:
                raise ValidationError(f"{self.name} is required", self.name)
            return {}
        
        # Convert to dict if not already
        if isinstance(value, str):
            try:
                value = json.loads(value)
                if not isinstance(value, dict):
                    raise ValidationError(
                        f"{self.name} must be a valid dictionary",
                        self.name
                    )
            except json.JSONDecodeError:
                raise ValidationError(
                    f"{self.name} must be a valid JSON object",
                    self.name
                )
        elif not isinstance(value, dict):
            raise ValidationError(
                f"{self.name} must be a dictionary",
                self.name
            )
        
        # Validate fields if schema is provided
        if self.schema:
            validated_dict = {}
            for field_name, validator in self.schema.items():
                field_value = value.get(field_name)
                try:
                    validated_value = validator.validate(field_value)
                    validated_dict[field_name] = validated_value
                except ValidationError as e:
                    raise ValidationError(
                        f"{self.name}.{field_name}: {e.message}",
                        self.name
                    )
            
            # Copy any additional fields not in the schema
            for field_name, field_value in value.items():
                if field_name not in self.schema:
                    validated_dict[field_name] = field_value
            
            value = validated_dict
        
        return value


class JsonSchemaValidator(Validator[Any]):
    """Validator using JSON Schema."""
    
    def __init__(self, name: str, schema: Dict[str, Any], required: bool = True):
        """
        Initialize the JSON Schema validator.
        
        Args:
            name: The name of the field being validated
            schema: The JSON Schema to validate against
            required: Whether the field is required
        """
        super().__init__(name)
        self.schema = schema
        self.required = required
    
    def validate(self, value: Any) -> Any:
        """
        Validate the input value against the JSON Schema.
        
        Args:
            value: The value to validate
            
        Returns:
            The validated value
            
        Raises:
            ValidationError: If validation fails
        """
        # Check if the value is None or empty
        if value is None or (isinstance(value, (str, dict, list)) and len(value) == 0):
            if self.required:
                raise ValidationError(f"{self.name} is required", self.name)
            return {} if isinstance(value, dict) else [] if isinstance(value, list) else ""
        
        # Convert string to JSON if needed
        if isinstance(value, str):
            try:
                value = json.loads(value)
            except json.JSONDecodeError:
                raise ValidationError(
                    f"{self.name} must be valid JSON",
                    self.name
                )
        
        # Validate against the schema
        try:
            jsonschema.validate(instance=value, schema=self.schema)
        except JsonSchemaValidationError as e:
            raise ValidationError(
                f"{self.name}: {e.message}",
                self.name
            )
        
        return value


def validate_coordinates(coords: Any) -> Tuple[float, float]:
    """
    Validate and normalize coordinates.
    
    Args:
        coords: The coordinates to validate (tuple, list, or string)
        
    Returns:
        A tuple of (latitude, longitude)
        
    Raises:
        ValidationError: If validation fails
    """
    if coords is None:
        raise ValidationError("Coordinates are required")
    
    # Handle string input (e.g., "37.7749, -122.4194")
    if isinstance(coords, str):
        try:
            parts = coords.split(",")
            if len(parts) != 2:
                raise ValidationError("Coordinates must be in the format 'lat,lng'")
            
            lat = float(parts[0].strip())
            lng = float(parts[1].strip())
        except ValueError:
            raise ValidationError("Coordinates must be valid numbers")
    
    # Handle list or tuple input
    elif isinstance(coords, (list, tuple)):
        if len(coords) != 2:
            raise ValidationError("Coordinates must be a tuple or list of [lat, lng]")
        
        try:
            lat = float(coords[0])
            lng = float(coords[1])
        except (ValueError, TypeError):
            raise ValidationError("Coordinates must be valid numbers")
    
    # Handle dictionary input (e.g., {"lat": 37.7749, "lng": -122.4194})
    elif isinstance(coords, dict):
        lat = coords.get("lat") or coords.get("latitude")
        lng = coords.get("lng") or coords.get("longitude")
        
        if lat is None or lng is None:
            raise ValidationError("Coordinates dictionary must have lat/lng or latitude/longitude keys")
        
        try:
            lat = float(lat)
            lng = float(lng)
        except (ValueError, TypeError):
            raise ValidationError("Coordinates must be valid numbers")
    
    else:
        raise ValidationError("Coordinates must be a tuple, list, string, or dictionary")
    
    # Validate latitude and longitude ranges
    if lat < -90 or lat > 90:
        raise ValidationError("Latitude must be between -90 and 90")
    
    if lng < -180 or lng > 180:
        raise ValidationError("Longitude must be between -180 and 180")
    
    return (lat, lng)
