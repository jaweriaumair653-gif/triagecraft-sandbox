from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pytest
import requests

from triagecraft.github_client import GitHubAPIError, GitHubClient


@dataclass
class FakeResponse:
    status_code: int
    payload: Any = None
    content: bytes = b"{}"
    should_raise: bool = False

    def raise_for_status(self) -> None:
        if self.should_raise:
            raise requests.HTTPError("boom")

    def json(self) -> Any:
        return self.payload


class FakeSession:
    def __init__(self, response: FakeResponse) -> None:
        self.response = response
        self.headers: dict[str, str] = {}
        self.requests: list[dict[str, Any]] = []

    def request(
        self,
        method: str,
        url: str,
        params: dict[str, Any] | None = None,
        json: dict[str, Any] | None = None,
        timeout: int | float | None = None,
    ) -> FakeResponse:
        self.requests.append(
            {
                "method": method,
                "url": url,
                "params": params,
                "json": json,
                "timeout": timeout,
            }
        )
        return self.response

    def close(self) -> None:
        pass


def test_client_initializes_headers() -> None:
    session = FakeSession(FakeResponse(status_code=200, payload={}))
    GitHubClient(token="secret", session=session)

    assert "Authorization" in session.headers
    assert session.headers["Authorization"] == "Bearer secret"
    assert "Accept" in session.headers


def test_get_issue_builds_correct_request() -> None:
    session = FakeSession(
        FakeResponse(
            status_code=200,
            payload={"id": 1, "title": "Bug"},
            content=b'{"id":1,"title":"Bug"}',
        )
    )
    client = GitHubClient(token="secret", session=session)

    issue = client.get_issue("owner/repo", 7)

    assert issue["id"] == 1
    assert session.requests[0]["method"] == "GET"
    assert session.requests[0]["url"] == "https://api.github.com/repos/owner/repo/issues/7"


def test_search_issues_sends_repo_scoped_query() -> None:
    session = FakeSession(
        FakeResponse(
            status_code=200,
            payload={"items": [{"id": 1}, {"id": 2}]},
            content=b'{"items":[{"id":1},{"id":2}]}',
        )
    )
    client = GitHubClient(token="secret", session=session)

    results = client.search_issues("owner/repo", "crash login")

    assert len(results) == 2
    assert "repo:owner/repo" in session.requests[0]["params"]["q"]
    assert "is:issue" in session.requests[0]["params"]["q"]
    assert "crash login" in session.requests[0]["params"]["q"]


def test_add_labels_posts_label_list() -> None:
    session = FakeSession(
        FakeResponse(
            status_code=200,
            payload=["bug", "help wanted"],
            content=b'["bug","help wanted"]',
        )
    )
    client = GitHubClient(token="secret", session=session)

    labels = client.add_labels("owner/repo", 7, ["bug", "help wanted"])

    assert labels == ["bug", "help wanted"]
    assert session.requests[0]["method"] == "POST"
    assert session.requests[0]["json"] == {"labels": ["bug", "help wanted"]}


def test_post_comment_posts_body() -> None:
    session = FakeSession(
        FakeResponse(
            status_code=201,
            payload={"id": 99, "body": "hello"},
            content=b'{"id":99,"body":"hello"}',
        )
    )
    client = GitHubClient(token="secret", session=session)

    comment = client.post_comment("owner/repo", 7, "hello")

    assert comment["id"] == 99
    assert session.requests[0]["method"] == "POST"
    assert session.requests[0]["json"] == {"body": "hello"}


def test_close_issue_patches_state_closed() -> None:
    session = FakeSession(
        FakeResponse(
            status_code=200,
            payload={"id": 7, "state": "closed"},
            content=b'{"id":7,"state":"closed"}',
        )
    )
    client = GitHubClient(token="secret", session=session)

    result = client.close_issue("owner/repo", 7)

    assert result["state"] == "closed"
    assert session.requests[0]["method"] == "PATCH"
    assert session.requests[0]["json"] == {"state": "closed"}


def test_http_errors_become_github_api_errors() -> None:
    session = FakeSession(
        FakeResponse(status_code=500, payload={"message": "error"}, should_raise=True)
    )
    client = GitHubClient(token="secret", session=session)

    with pytest.raises(GitHubAPIError):
        client.get_issue("owner/repo", 7)
