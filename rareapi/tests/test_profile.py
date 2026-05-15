import pytest
from datetime import date
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token
from rareapi.models import RareUser, Post, Category


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def viewer(db):
    return RareUser.objects.create_user(
        username="viewer", password="x", is_active=True
    )


@pytest.fixture
def profile_user(db):
    return RareUser.objects.create_user(
        username="author", password="x", is_active=True
    )


@pytest.fixture
def category(db):
    return Category.objects.create(label="General")


class TestProfilePostCount:
    def test_zero_when_no_posts(self, api_client, viewer, profile_user):
        token = Token.objects.create(user=viewer)
        api_client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")
        response = api_client.get(f"/profiles/{profile_user.id}")
        assert response.status_code == 200
        assert response.json()["post_count"] == 0

    def test_counts_only_approved_posts(self, api_client, viewer, profile_user, category):
        Post.objects.create(user=profile_user, category=category, title="A", publication_date=date.today(), content="x", approved=True)
        Post.objects.create(user=profile_user, category=category, title="B", publication_date=date.today(), content="x", approved=True)
        Post.objects.create(user=profile_user, category=category, title="C", publication_date=date.today(), content="x", approved=False)
        token = Token.objects.create(user=viewer)
        api_client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")
        response = api_client.get(f"/profiles/{profile_user.id}")
        assert response.status_code == 200
        assert response.json()["post_count"] == 2

    def test_zero_when_only_unapproved(self, api_client, viewer, profile_user, category):
        Post.objects.create(user=profile_user, category=category, title="Draft", publication_date=date.today(), content="x", approved=False)
        token = Token.objects.create(user=viewer)
        api_client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")
        response = api_client.get(f"/profiles/{profile_user.id}")
        assert response.status_code == 200
        assert response.json()["post_count"] == 0

    def test_excludes_other_users_posts(self, api_client, viewer, profile_user, category):
        other = RareUser.objects.create_user(username="other", password="x", is_active=True)
        Post.objects.create(user=other, category=category, title="Other", publication_date=date.today(), content="x", approved=True)
        Post.objects.create(user=profile_user, category=category, title="Mine", publication_date=date.today(), content="x", approved=True)
        token = Token.objects.create(user=viewer)
        api_client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")
        response = api_client.get(f"/profiles/{profile_user.id}")
        assert response.status_code == 200
        assert response.json()["post_count"] == 1


class TestProfileEdit:
    def test_owner_can_update_profile(self, api_client, profile_user):
        token = Token.objects.create(user=profile_user)
        api_client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")
        response = api_client.put(
            f"/profiles/{profile_user.id}",
            {"bio": "Hello world", "first_name": "Jane", "last_name": "Doe"},
            format="json",
        )
        assert response.status_code == 200
        data = response.json()
        assert data["bio"] == "Hello world"
        assert data["full_name"] == "Jane Doe"

    def test_non_owner_cannot_update_profile(self, api_client, viewer, profile_user):
        token = Token.objects.create(user=viewer)
        api_client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")
        response = api_client.put(
            f"/profiles/{profile_user.id}",
            {"bio": "Hack"},
            format="json",
        )
        assert response.status_code == 403

    def test_get_profile_returns_bio(self, api_client, viewer, profile_user):
        profile_user.bio = "My bio"
        profile_user.save()
        token = Token.objects.create(user=viewer)
        api_client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")
        response = api_client.get(f"/profiles/{profile_user.id}")
        assert response.status_code == 200
        assert response.json()["bio"] == "My bio"
