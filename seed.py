import asyncio

from app.infrastructure.database import engine, AsyncSessionLocal
from app.domain.entities import Base, Building, Activity, Organization, OrganizationActivity
from app.infrastructure.repositories import OrganizationRepository


async def seed_data():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as session:
        async with session.begin():
            org_repo = OrganizationRepository(session)
            if await org_repo.search_by_name('ООО Рога и Копыта'):
                print("Seed data already exists, skipping...")
                return

            building1 = Building(
                address="ул. Ленина, 1",
                latitude=55.7558,
                longitude=37.6173
            )
            building2 = Building(
                address="ул. Мира, 10",
                latitude=55.7580,
                longitude=37.6200
            )
            session.add_all([building1, building2])
            await session.flush()

            activity1 = Activity(name="Еда", parent_id=None)
            activity2 = Activity(name="Автомобили", parent_id=None)
            session.add_all([activity1, activity2])
            await session.flush()

            activity3 = Activity(name="Мясная продукция", parent_id=activity1.id)
            activity4 = Activity(name="Молочная продукция", parent_id=activity1.id)
            activity5 = Activity(name="Запчасти", parent_id=activity2.id)
            activity6 = Activity(name="Аксессуары", parent_id=activity2.id)
            session.add_all([activity3, activity4, activity5, activity6])
            await session.flush()

            organization = Organization(
                name="ООО Рога и Копыта",
                phones=["+79991234567"],
                building_id=building1.id
            )
            session.add(organization)
            await session.flush()

            links = [
                OrganizationActivity(organization_id=organization.id, activity_id=activity1.id),
                OrganizationActivity(organization_id=organization.id, activity_id=activity3.id),
                OrganizationActivity(organization_id=organization.id, activity_id=activity4.id),
            ]
            session.add_all(links)

            print("Seed data inserted successfully.")

if __name__ == "__main__":
    asyncio.run(seed_data())