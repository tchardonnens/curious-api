import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app import models
from app.crud import contents as contents_crud
from app.schemas.contents import Content, ContentBase

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
def sample_content(db_session) -> Content:
    content_create = ContentBase(
        title="Sample Title",
        snippet="Sample Snippet",
        link="https://example.com",
        long_description="Long Description",
        image="https://example.com/image.jpg",
    )
    source = "Test Source"
    return contents_crud.create_content(content_create, source, db_session)


def test_get_content(db_session, sample_content: Content):
    sample_content
    content = contents_crud.get_content(sample_content.id, db_session)
    assert content.id == sample_content.id


def test_get_content_by_link(db_session, sample_content):
    content = contents_crud.get_content_by_link("https://example.com", db_session)
    assert content.link == "https://example.com"


def test_get_content_by_title(db_session, sample_content):
    content = contents_crud.get_content_by_title("Sample Title", db_session)
    assert content.title == "Sample Title"


def test_get_contents(db_session, sample_content):
    contents = contents_crud.get_contents(db_session, skip=0, limit=10)
    assert contents[0].id == sample_content.id


def test_create_content(db_session, sample_content):
    content_create = ContentBase(
        title="Another Title",
        snippet="Another Snippet",
        link="https://anotherexample.com",
        long_description="Another Long Description",
        image="https://anotherexample.com/image.jpg",
    )
    source = "Another Test Source"
    content = contents_crud.create_content(content_create, source, db_session)
    assert content.title == "Another Title"
