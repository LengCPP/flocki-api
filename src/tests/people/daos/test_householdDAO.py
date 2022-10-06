from datetime import datetime

import pytest

from src.app.database import get_db, SessionLocal, Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.app.media.models.database import models as media_models

from src.app.people.models.database import models
# test_database.py
from src.app.people.daos.householdDAO import HouseholdDAO

SQLALCHEMY_DATABASE_URL = "sqlite:///./test_db.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
models.Base.metadata.create_all(engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


@pytest.fixture()
def test_db():
    Base.metadata.create_all(bind=engine)
    yield
    try:
        Base.metadata.drop_all(bind=engine)
    except Exception as e:
        print("teardown of DB failed")
        print(e)

db = next(override_get_db())
householdDAO = HouseholdDAO(db)


def test_get_all_households_no_households(test_db):
    households = householdDAO.get_all_households()
    len(households) == 0


def test_get_all_households_one_household(test_db):
    household = models.Household(
        leader_id=1,
        address_id=1,
    )
    db.add(household)
    db.commit()
    households = householdDAO.get_all_households()
    assert len(households) == 1


def test_get_all_households_many_households(test_db):
    household =  models.Household(
        leader_id=1,
        address_id=1,
    )
    household_2 =  models.Household(
        leader_id=1,
        address_id=1,
    )
    db.add(household)
    db.add(household_2)
    db.commit()
    households = householdDAO.get_all_households()
    assert len(households) == 2


def test_get_household_by_id_one_household(test_db):
    household = models.Household(
        leader_id=1,
        address_id=1,
    )
    db.add(household)
    db.commit()
    household = householdDAO.get_household_by_id(household.id)
    assert household is not None
    assert household.leader_id == 1
    assert household.address_id == 1


def test_get_household_by_id_no_household(test_db):
    household = householdDAO.get_household_by_id(99)
    assert household is None


def test_add_household(test_db):
    household = models.Household(
        leader_id=1,
        address_id=1,
    )
    household = householdDAO.add_household(household)

    assert household is not None
    assert household.leader_id == 1
    assert household.address_id == 1

    household_queried = db.query(models.Household).filter(models.Household.id == household.id).first()
    assert household_queried is not None
    assert household_queried.leader_id == 1
    assert household_queried.address_id == 1


def test_add_household_image(test_db):
    household = models.Household(
        leader_id=1,
        address_id=1,
    )
    household = householdDAO.add_household(household)

    image = media_models.Image(
        address="test",
        description="test",
        store="local",
        created=datetime.now(),
    )
    db.add(image)
    db.commit()
    db.refresh(image)
    householdDAO.add_household_image(household, image)

    household_queried = db.query(models.Household).filter(models.Household.id == household.id).first()

    assert household_queried.household_images is not None
    assert len(household_queried.household_images) == 1
    assert household_queried.household_images[0].image.address == "test"
    assert household_queried.household_images[0].image.description == "test"

