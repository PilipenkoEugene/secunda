from dishka import Provider, Scope, provide, make_async_container
from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker, AsyncSession
from app.infrastructure.database import engine, AsyncSessionLocal

from app.domain.abc_repositories import AbstractBuildingRepository, AbstractActivityRepository, AbstractOrganizationRepository
from app.infrastructure.repositories.activity import ActivityRepository
from app.infrastructure.repositories.building import BuildingRepository
from app.infrastructure.repositories.organization import OrganizationRepository
from app.services.activity import ActivityService
from app.services.building import BuildingService
from app.services.organiztion import OrganizationService


class DatabaseProvider(Provider):
    @provide(scope=Scope.APP)
    def engine(self) -> AsyncEngine:
        return engine

    @provide(scope=Scope.APP)
    def sessionmaker(self, engine: AsyncEngine) -> async_sessionmaker:
        return AsyncSessionLocal

    @provide(scope=Scope.REQUEST)
    async def session(self, sessionmaker: async_sessionmaker) -> AsyncSession:
        session = sessionmaker()
        try:
            return session
        finally:
            await session.close()

class RepositoryProvider(Provider):
    @provide(scope=Scope.REQUEST)
    def building_repo(self, session: AsyncSession) -> AbstractBuildingRepository:
        return BuildingRepository(session)

    @provide(scope=Scope.REQUEST)
    def activity_repo(self, session: AsyncSession) -> AbstractActivityRepository:
        return ActivityRepository(session)

    @provide(scope=Scope.REQUEST)
    def organization_repo(self, session: AsyncSession) -> AbstractOrganizationRepository:
        return OrganizationRepository(session)

class ServiceProvider(Provider):
    @provide(scope=Scope.REQUEST)
    def building_service(self, repo: AbstractBuildingRepository) -> BuildingService:
        return BuildingService(repo)

    @provide(scope=Scope.REQUEST)
    def activity_service(self, repo: AbstractActivityRepository) -> ActivityService:
        return ActivityService(repo)

    @provide(scope=Scope.REQUEST)
    def organization_service(
        self,
        org_repo: AbstractOrganizationRepository,
        activity_repo: AbstractActivityRepository,
        building_repo: AbstractBuildingRepository
    ) -> OrganizationService:
        return OrganizationService(org_repo, activity_repo, building_repo)

def create_container():
    return make_async_container(
        DatabaseProvider(),
        RepositoryProvider(),
        ServiceProvider(),
    )
