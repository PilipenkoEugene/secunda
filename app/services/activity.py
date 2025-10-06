from typing import List

from fastapi import HTTPException

from app.domain.abc_repositories import AbstractActivityRepository
from app.domain.entities import Activity


class ActivityService:
    def __init__(self, activity_repo: AbstractActivityRepository):
        self.activity_repo = activity_repo

    async def get_all(self) -> List[Activity]:
        return await self.activity_repo.get_all()

    async def get_by_id(self, activity_id: int) -> Activity | None:
        return await self.activity_repo.get_by_id(activity_id)

    async def create(self, name: str, parent_id: int = None) -> Activity:
        if parent_id is not None:
            parent = await self.activity_repo.get_by_id(parent_id)
            if not parent:
                raise HTTPException(
                    status_code=400, detail='Родительский вид деятельности не обнаружен'
                )
            if await self.activity_repo.get_depth(parent.id) >= 2:
                raise HTTPException(
                    status_code=400, detail='Превышен лимит вложенности. Максимальный уровень - 3'
                )
        return await self.activity_repo.create(name=name, parent_id=parent_id)

    async def update(
        self, activity: Activity, name: str = None, parent_id: int = None
    ) -> Activity:
        if parent_id is not None:
            parent = await self.activity_repo.get_by_id(parent_id)
            if activity.id == parent_id:
                raise HTTPException(status_code=400, detail='Запись не может зависеть от себя')
            if not parent:
                raise HTTPException(
                    status_code=400, detail='Указанный родительский элемент не существует'
                )
            if await self.activity_repo.get_depth(parent.id) >= 2:
                raise HTTPException(
                    status_code=400, detail='Превышен лимит вложенности. Максимальный уровень - 3'
                )
        return await self.activity_repo.update(activity, name=name, parent_id=parent_id)

    async def delete(self, activity_id: int) -> None:
        activity = await self.get_by_id(activity_id)
        if not activity:
            raise ValueError(f'Не обнаружена активность с id {activity_id}')
        await self.activity_repo.delete(activity)

    async def get_sub_activities(self, activity_id: int) -> List[Activity]:
        return await self.activity_repo.get_sub_activities(activity_id)
