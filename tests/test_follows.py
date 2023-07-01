import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app import models
from app.crud import follows as follows_crud
from app.schemas.follows import FollowCreate

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"


def create_test_engine():
    return create_engine(
        SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
    )


@pytest.fixture(scope="function")
def db_session():
    engine = create_test_engine()
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    models.Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    yield session
    session.close()
    models.Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def sample_follow(db_session):
    follow_create = FollowCreate(user_id=1, follow_id=2)
    return follows_crud.create_follow(follow_create, db_session)


def test_get_follows_by_user_id(db_session, sample_follow):
    follows = follows_crud.get_follows_by_user_id(1, db_session)
    assert follows[0].user_id == 1


def test_get_followers_by_user_id(db_session, sample_follow):
    follows = follows_crud.get_followers_by_user_id(2, db_session)
    assert follows[0].follow_id == 2


def test_get_follow_by_user_id_and_follow_id(db_session, sample_follow):
    follow = follows_crud.get_follow_by_user_id_and_follow_id(1, 2, db_session)
    assert follow.user_id == 1 and follow.follow_id == 2


def test_create_follow(db_session):
    follow_create = FollowCreate(user_id=3, follow_id=4)
    follow = follows_crud.create_follow(follow_create, db_session)
    assert follow.user_id == 3 and follow.follow_id == 4
