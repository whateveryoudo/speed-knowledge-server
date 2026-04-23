from typing import Annotated, Any, TypeVar, Optional
from pydantic import BeforeValidator

T = TypeVar("T")


FlexibleOptional = Annotated[Optional[T], BeforeValidator(lambda v: None if v == "" else v)]
