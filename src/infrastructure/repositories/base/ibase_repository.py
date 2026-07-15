from abc import ABC, abstractmethod
from typing import Any, List, Optional


class IBaseRepository(ABC):

    #region INSERT
    @abstractmethod
    async def insert_async(self, entity: object) -> object:
        """Insert a new entity into the database."""
        raise NotImplementedError
    
    @abstractmethod
    async def insert_and_get_id_async(self, entity: object) -> Any:
        """Insert an entity and return its ID."""
        raise NotImplementedError
    #endregion 

    #region GET
    @abstractmethod
    async def get_by_id_async(self, id: Any) -> Optional[object]:
        """Get an entity by ID."""
        raise NotImplementedError

    @abstractmethod
    async def get_all_async(self) -> List[object]:
        """Get all entities."""
        raise NotImplementedError
    #endregion

    #region UPDATE
    @abstractmethod
    async def update_async(self, entity: object) -> object:
        """Update an existing entity."""
        raise NotImplementedError
    #endregion

    #region DELETE
    @abstractmethod
    async def delete_async(self, id: Any) -> bool:
        """Delete an entity by ID."""
        raise NotImplementedError
    #endregion
