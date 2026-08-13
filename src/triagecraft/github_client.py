from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass, field
from typing import Any

import requests


class GitHubAPIError(RuntimeError):
    """Raised when a GitHub API request fails."""


@dataclass(slots=True)
class GitHubClient:
    """
    Minimal GitHub REST client for repository issue actions.
    """

    token: str
    api_base_url: str = "https://api.github.com"
    session: requests.Session = field(default_factory=requests.Session)

    def __post_init__(self) -> None:
        self.session.headers.update(
            {
                "Authorization": f"Bearer {self.token}",
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28",
            }
        )

    def close(self) -> None:
        self.session.close()

    def _request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json_body: dict[str, Any] | None = None,
    ) -> Any:
        url = f"{self.api_base_url.rstrip('/')}/{path.lstrip('/')}"
        normalized_method = method.upper()

        # Only GET requests are retried automatically.
        # POST/PATCH mutations must not be blindly retried because a
        # network failure can happen after GitHub already accepted them.
        max_attempts = 3 if normalized_method == "GET" else 1
        retryable_statuses = {500, 502, 503, 504}

        for attempt in range(1, max_attempts + 1):
            try:
                response = self.session.request(
                    method=normalized_method,
                    url=url,
                    params=params,
                    json=json_body,
                    timeout=30,
                )
                response.raise_for_status()

            except requests.HTTPError as exc:
                # Real requests.HTTPError normally carries response,
                # but our test double does not. Fall back to the response
                # returned by the session so status-based retries still work.
                status_code = getattr(
                    getattr(exc, "response", None),
                    "status_code",
                    None,
                )

                if status_code is None:
                    status_code = getattr(response, "status_code", None)

                if (
                    normalized_method == "GET"
                    and status_code in retryable_statuses
                    and attempt < max_attempts
                ):
                    continue

                raise GitHubAPIError(
                    f"GitHub API request failed: {normalized_method} {path}"
                ) from exc

            except requests.RequestException as exc:
                if normalized_method == "GET" and attempt < max_attempts:
                    continue

                raise GitHubAPIError(
                    f"GitHub API request failed: {normalized_method} {path}"
                ) from exc

            if response.status_code == 204:
                return None

            if response.content:
                return response.json()

            return None

        raise GitHubAPIError(f"GitHub API request failed: {normalized_method} {path}")

    def get_issue(
        self,
        repo_full_name: str,
        issue_number: int,
    ) -> dict[str, Any]:
        path = f"/repos/{repo_full_name}/issues/{issue_number}"
        result = self._request("GET", path)
        assert isinstance(result, dict)
        return result

    def search_issues(
        self,
        repo_full_name: str,
        query: str,
        *,
        state: str = "open",
    ) -> list[dict[str, Any]]:
        q = f"repo:{repo_full_name} is:issue is:{state} {query}".strip()
        result = self._request(
            "GET",
            "/search/issues",
            params={"q": q},
        )
        assert isinstance(result, dict)
        items = result.get("items", [])
        if not isinstance(items, list):
            return []
        return [item for item in items if isinstance(item, dict)]

    def add_labels(
        self,
        repo_full_name: str,
        issue_number: int,
        labels: Iterable[str],
    ) -> list[str]:
        path = f"/repos/{repo_full_name}/issues/{issue_number}/labels"
        result = self._request(
            "POST",
            path,
            json_body={"labels": list(labels)},
        )
        assert isinstance(result, list)
        return [label for label in result if isinstance(label, str)]

    def post_comment(
        self,
        repo_full_name: str,
        issue_number: int,
        body: str,
    ) -> dict[str, Any]:
        path = f"/repos/{repo_full_name}/issues/{issue_number}/comments"
        result = self._request(
            "POST",
            path,
            json_body={"body": body},
        )
        assert isinstance(result, dict)
        return result

    def close_issue(
        self,
        repo_full_name: str,
        issue_number: int,
    ) -> dict[str, Any]:
        path = f"/repos/{repo_full_name}/issues/{issue_number}"
        result = self._request(
            "PATCH",
            path,
            json_body={"state": "closed"},
        )
        assert isinstance(result, dict)
        return result
