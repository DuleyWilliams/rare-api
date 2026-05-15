import pytest
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token
from rareapi.models import RareUser, Post, Category, Comment, Reaction, PostReaction


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def viewer(db):
    return RareUser.objects.create_user(username="viewer", password="x", is_active=True)


@pytest.fixture
def category(db):
    return Category.objects.create(label="General")


@pytest.fixture
def post(db, viewer, category):
    return Post.objects.create(
        user=viewer,
        category=category,
        title="Test Post",
        content="This is the post content.",
        publication_date=timezone.now().date(),
        approved=True,
    )


def auth(api_client, user):
    token = Token.objects.create(user=user)
    api_client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")


class TestPostListFields:
    def test_author_name_returns_full_name(self, api_client, db, category):
        author = RareUser.objects.create_user(
            username="jdoe", password="x", is_active=True,
            first_name="Jane", last_name="Doe",
        )
        Post.objects.create(
            user=author, category=category, title="A",
            content="x", publication_date=timezone.now().date(), approved=True,
        )
        auth(api_client, author)
        response = api_client.get("/posts")
        assert response.status_code == 200
        posts = response.json()
        assert any(p["author_name"] == "Jane Doe" for p in posts)

    def test_author_name_falls_back_to_username(self, api_client, viewer, post):
        auth(api_client, viewer)
        response = api_client.get("/posts")
        assert response.status_code == 200
        assert response.json()[0]["author_name"] == "viewer"

    def test_comment_count(self, api_client, viewer, post):
        Comment.objects.create(post=post, author=viewer, subject="s1", content="c1")
        Comment.objects.create(post=post, author=viewer, subject="s2", content="c2")
        auth(api_client, viewer)
        response = api_client.get("/posts")
        assert response.status_code == 200
        assert response.json()[0]["comment_count"] == 2

    def test_reaction_count(self, api_client, viewer, post, db):
        user2 = RareUser.objects.create_user(username="user2", password="x", is_active=True)
        user3 = RareUser.objects.create_user(username="user3", password="x", is_active=True)
        reaction = Reaction.objects.create(label="like", image_url="like")
        PostReaction.objects.create(post=post, user=viewer, reaction=reaction)
        PostReaction.objects.create(post=post, user=user2, reaction=reaction)
        PostReaction.objects.create(post=post, user=user3, reaction=reaction)
        auth(api_client, viewer)
        response = api_client.get("/posts")
        assert response.status_code == 200
        assert response.json()[0]["reaction_count"] == 3

    def test_content_is_present(self, api_client, viewer, post):
        auth(api_client, viewer)
        response = api_client.get("/posts")
        assert response.status_code == 200
        assert response.json()[0]["content"] == "This is the post content."
