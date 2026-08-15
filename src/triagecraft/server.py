from __future__ import annotations

import hashlib
import hmac
import json
import logging
from typing import Any

from fastapi import FastAPI, Header, HTTPException, Request

from triagecraft.app import TriageApp, handle_webhook_payload

logger = logging.getLogger(__name__)


def _verify_signature(secret: str, body: bytes, signature: str | None) -> None:
    if signature is None or not signature.startswith("sha256="):
        raise HTTPException(status_code=401, detail="Missing or invalid signature.")

    expected = (
        "sha256="
        + hmac.new(
            secret.encode("utf-8"),
            body,
            hashlib.sha256,
        ).hexdigest()
    )

    if not hmac.compare_digest(expected, signature):
        raise HTTPException(status_code=401, detail="Invalid signature.")


def create_server(triage_app: TriageApp) -> FastAPI:
    app = FastAPI(title="TriageCraft", version="0.1.0")

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.post("/webhooks/github")
    async def github_webhook(
        request: Request,
        x_github_delivery: str | None = Header(default=None),
        x_github_event: str | None = Header(default=None),
        x_hub_signature_256: str | None = Header(default=None),
    ) -> dict[str, Any]:
        if x_github_delivery is None or not x_github_delivery.strip():
            raise HTTPException(status_code=400, detail="Missing X-GitHub-Delivery header.")

        if x_github_event is None or not x_github_event.strip():
            raise HTTPException(status_code=400, detail="Missing X-GitHub-Event header.")

        raw_body = await request.body()

        logger.info(
            "Webhook received delivery=%s event=%s",
            x_github_delivery,
            x_github_event,
        )

        if triage_app.config.webhook_secret:
            _verify_signature(
                triage_app.config.webhook_secret,
                raw_body,
                x_hub_signature_256,
            )

        if x_github_event != "issues":
            logger.info(
                "Ignoring webhook delivery=%s event=%s",
                x_github_delivery,
                x_github_event,
            )
            return {"status": "ignored", "event": x_github_event}

        try:
            payload = json.loads(raw_body.decode("utf-8"))
        except json.JSONDecodeError as exc:
            raise HTTPException(status_code=400, detail="Invalid JSON payload.") from exc

        if not isinstance(payload, dict):
            raise HTTPException(status_code=400, detail="JSON payload must be an object.")

        action = payload.get("action")
        if action not in {"opened", "reopened"}:
            logger.info(
                "Ignoring webhook delivery=%s event=%s action=%s",
                x_github_delivery,
                x_github_event,
                action,
            )
            return {
                "status": "ignored",
                "event": x_github_event,
                "action": action,
            }

        internal_payload = dict(payload)
        internal_payload["event_type"] = x_github_event

        execution = handle_webhook_payload(
            triage_app,
            internal_payload,
            event_id=x_github_delivery,
            corpus=[],
        )

        response = execution.to_dict()
        response["status"] = "processed"
        response["event"] = x_github_event
        response["delivery_id"] = x_github_delivery

        logger.info(
            "Webhook processed delivery=%s issue=%s",
            x_github_delivery,
            response["issue"],
        )

        return response

    return app
