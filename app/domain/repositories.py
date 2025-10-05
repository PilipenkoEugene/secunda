from abc import ABC, abstractmethod
from typing import Generic, TypeVar, List
from app.domain.entities import Organization, Building, Activity

T = TypeVar('T')

class AbstractRepository(ABC, Generic[T]):
    @abstractmethod
    async def get_all(self) -> List[T]:
        pass

    @abstractmethod
    async def get_by_id(self, entity_id: int) -> T | None:
        pass

    @abstractmethod
    async def create(self, **kwargs) -> T:
        pass

    @abstractmethod
    async def update(self, entity: T, **kwargs) -> T:
        pass

    @abstractmethod
    async def delete(self, entity: T) -> None:
        pass

class AbstractBuildingRepository(AbstractRepository[Building]):
    pass

class AbstractActivityRepository(AbstractRepository[Activity]):
    @abstractmethod
    async def get_by_name(self, name: str) -> Activity | None:
        pass

    @abstractmethod
    async def get_sub_activities(self, activity_id: int, depth: int = 3) -> List[Activity]:
        pass

    @abstractmethod
    async def get_depth(self, activity: Activity) -> int:
        pass

class AbstractOrganizationRepository(AbstractRepository[Organization]):
    @abstractmethod
    async def get_by_building(self, building_id: int) -> List[Organization]:
        pass

    @abstractmethod
    async def get_by_activity(self, activity_id: int, sub_activities: list[Activity]) -> List[Organization]:
        pass

    @abstractmethod
    async def get_in_radius(self, lat: float, lon: float, radius_km: float) -> List[Organization]:
        pass

    @abstractmethod
    async def get_in_rect(self, min_lat: float, max_lat: float, min_lon: float, max_lon: float) -> List[Organization]:
        pass

    @abstractmethod
    async def search_by_name(self, name: str) -> List[Organization]:
        pass
