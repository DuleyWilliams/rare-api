import pytest
from datetime import timedelta
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token
from rareapi.models import RareUser, Post, Category


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def viewer(db):
    return RareUser.objects.create_user(username="viewer", password="x", is_active=True)


@pytest.fixture
def alice(db):
    return RareUser.objects.create_user(username="alice", password="x", is_active=True)


@pytest.fixture
def bob(db):
    return RareUser.objects.create_user(username="bob", password="x", is_active=True)


@pytest.fixture
def category(db):
    return Category.objects.create(label="General")


def auth(api_client, user):
    token = Token.objects.create(user=user)
    api_client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")


def make_post(user, category, title, approved=True, days_offset=0):
    return Post.objects.create(
        user=user,
        category=category,
        title=title,
        publication_date=timezone.now().date() + timedelta(days=days_offset),
        content="body",
        approved=approved,
    )


class TestPostSearch:
    def test_title_search_returns_matching_posts(self, api_client, viewer, alice, category):
        make_post(alice, category, "Django tips")
        make_post(alice, category, "React hooks")
        auth(api_client, viewer)
        response = api_client.get("/posts/search?q=django")
        assert response.status_code == 200
        titles = [p["title"] for p in response.json()]
        assert "Django tips" in titles
        assert "React hooks" not in titles

    def test_author_search_returns_posts_by_username(self, api_client, viewer, alice, bob, category):
        make_post(alice, category, "Alice post")
        make_post(bob, category, "Bob post")
        auth(api_client, viewer)
        response = api_client.get("/posts/search?author=alice")
        assert response.status_code == 200
        titles = [p["title"] for p in response.json()]
        assert "Alice post" in titles
        assert "Bob post" not in titles

    def test_author_search_is_case_insensitive(self, api_client, viewer, alice, category):
        make_post(alice, category, "Alice post")
        auth(api_client, viewer)
        response = api_client.get("/posts/search?author=ALICE")
        assert response.status_code == 200
        assert len(response.json()) == 1

    def test_combined_search_applies_both_filters(self, api_client, viewer, alice, bob, category):
        make_post(alice, category, "Django tips")
        make_post(alice, category, "React hooks")
        make_post(bob, category, "Django for bob")
        auth(api_client, viewer)
        response = api_client.get("/posts/search?q=django&author=alice")
        assert response.status_code == 200
        titles = [p["title"] for p in response.json()]
        assert titles == ["Django tips"]

    def test_no_params_returns_empty_list(self, api_client, viewer, alice, category):
        make_post(alice, category, "Some post")
        auth(api_client, viewer)
        response = api_client.get("/posts/search")
        assert response.status_code == 200
        assert response.json() == []

    def test_unknown_author_returns_empty_list(self, api_client, viewer, alice, category):
        make_post(alice, category, "Alice post")
        auth(api_client, viewer)
        response = api_client.get("/posts/search?author=nobody")
        assert response.status_code == 200
        assert response.json() == []

    def test_unapproved_post_excluded(self, api_client, viewer, alice, category):
        make_post(alice, category, "Django draft", approved=False)
        auth(api_client, viewer)
        response = api_client.get("/posts/search?q=django")
        assert response.status_code == 200
        assert response.json() == []

    def test_future_publication_date_excluded(self, api_client, viewer, alice, category):
        make_post(alice, category, "Future post", days_offset=1)
        auth(api_client, viewer)
        response = api_client.get("/posts/search?author=alice")
        assert response.status_code == 200
        assert response.json() == []
