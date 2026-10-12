# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }
"""ProofPulse Stage 1: deterministic obligation registry and lifecycle."""

from datetime import datetime, timezone
import json
import re

from genlayer import *

MAX_OBLIGATIONS = 128
MAX_ID_BYTES = 64
MAX_DESCRIPTION_BYTES = 512
MAX_POLICY_JSON_BYTES = 2048
MAX_POLICY_ITEMS = 8
MAX_POLICY_ITEM_BYTES = 256
MAX_TIMESTAMP = 253402300799  # 9999-12-31T23:59:59Z
MIN_PERIOD_SECONDS = 60
MAX_PERIOD_SECONDS = 31536000  # 365 days


class ProofPulse(gl.Contract):
    """Bounded registry; evidence evaluation and PoCC are deliberately absent."""

    owners: TreeMap[str, Address]
    descriptions: TreeMap[str, str]
    statuses: TreeMap[str, str]
    registered_at: TreeMap[str, u64]
    deadlines: TreeMap[str, u64]
    observation_periods: TreeMap[str, u64]
    requirements_json: TreeMap[str, str]
    sources_json: TreeMap[str, str]
    obligation_count: u32

    def __init__(self):
        self.obligation_count = u32(0)

    @gl.public.write
    def register_obligation(
        self,
        obligation_id: str,
        description: str,
        requirements_json: str,
        approved_sources_json: str,
        deadline_timestamp: u64,
        observation_period_seconds: u64,
    ) -> str:
        """Register an obligation using JSON arrays for immutable policy lists."""
        self._validate_identifier(obligation_id)
        if self.obligation_count >= MAX_OBLIGATIONS:
            raise gl.vm.UserError("registry capacity reached")
        if self.statuses.get(obligation_id, "") != "":
            raise gl.vm.UserError("obligation identifier already exists")

        if not isinstance(description, str) or not description.strip():
            raise gl.vm.UserError("description must be non-empty")
        if len(description.encode("utf-8")) > MAX_DESCRIPTION_BYTES:
            raise gl.vm.UserError("description exceeds byte limit")
        if description != description.strip():
            raise gl.vm.UserError("description must not have surrounding whitespace")

        requirements = self._parse_policy_list(requirements_json, "requirements")
        approved_sources = self._parse_policy_list(approved_sources_json, "approved sources")

        if deadline_timestamp > MAX_TIMESTAMP:
            raise gl.vm.UserError("deadline timestamp is out of range")
        if deadline_timestamp != u64(0) and deadline_timestamp <= self._transaction_timestamp():
            raise gl.vm.UserError("deadline must be after registration time")
        if observation_period_seconds != u64(0) and not (
            MIN_PERIOD_SECONDS <= observation_period_seconds <= MAX_PERIOD_SECONDS
        ):
            raise gl.vm.UserError("observation period is out of range")
        if deadline_timestamp == u64(0) and observation_period_seconds == u64(0):
            raise gl.vm.UserError("a deadline or observation period is required")

        # All validation precedes mutation. Rejected calls leave registry state untouched.
        registered_at = self._transaction_timestamp()
        self.owners[obligation_id] = gl.message.sender_address
        self.descriptions[obligation_id] = description
        self.statuses[obligation_id] = "ACTIVE"
        self.registered_at[obligation_id] = u64(registered_at)
        self.deadlines[obligation_id] = deadline_timestamp
        self.observation_periods[obligation_id] = observation_period_seconds
        self.requirements_json[obligation_id] = json.dumps(
            requirements, ensure_ascii=False, separators=(",", ":")
        )
        self.sources_json[obligation_id] = json.dumps(
            approved_sources, ensure_ascii=False, separators=(",", ":")
        )
        self.obligation_count = u32(self.obligation_count + u32(1))
        return obligation_id

    @gl.public.write
    def close_obligation(self, obligation_id: str) -> None:
        self._require_registered(obligation_id)
        if gl.message.sender_address != self.owners[obligation_id]:
            raise gl.vm.UserError("only the obligation owner may close it")
        if self.statuses[obligation_id] != "ACTIVE":
            raise gl.vm.UserError("only an active obligation may be closed")
        self.statuses[obligation_id] = "CLOSED"

    @gl.public.view
    def get_obligation_metadata(self, obligation_id: str) -> str:
        self._require_registered(obligation_id)
        return json.dumps(
            {
                "obligation_id": obligation_id,
                "creator": self.owners[obligation_id].as_hex,
                "description": self.descriptions[obligation_id],
                "status": self.statuses[obligation_id],
                "registered_at": int(self.registered_at[obligation_id]),
                "deadline_timestamp": int(self.deadlines[obligation_id]),
                "observation_period_seconds": int(self.observation_periods[obligation_id]),
            },
            ensure_ascii=False,
            separators=(",", ":"),
        )

    @gl.public.view
    def get_lifecycle_state(self, obligation_id: str) -> str:
        self._require_registered(obligation_id)
        return self.statuses[obligation_id]

    @gl.public.view
    def get_policy(self, obligation_id: str) -> str:
        self._require_registered(obligation_id)
        return json.dumps(
            {
                "version": 1,
                "requirements": json.loads(self.requirements_json[obligation_id]),
                "approved_sources": json.loads(self.sources_json[obligation_id]),
            },
            ensure_ascii=False,
            separators=(",", ":"),
        )

    @gl.public.view
    def get_owner(self, obligation_id: str) -> str:
        self._require_registered(obligation_id)
        return self.owners[obligation_id].as_hex

    @gl.public.view
    def get_obligation_counters(self, obligation_id: str) -> str:
        self._require_registered(obligation_id)
        return json.dumps(
            {
                "registry_count": int(self.obligation_count),
                "requirement_count": len(json.loads(self.requirements_json[obligation_id])),
                "approved_source_count": len(json.loads(self.sources_json[obligation_id])),
            },
            separators=(",", ":"),
        )

    @gl.public.view
    def get_registry_count(self) -> u32:
        return self.obligation_count

    def _validate_identifier(self, obligation_id: str) -> None:
        if not isinstance(obligation_id, str) or len(obligation_id.encode("utf-8")) > MAX_ID_BYTES:
            raise gl.vm.UserError("obligation identifier is invalid or too long")
        if re.fullmatch(r"[a-z0-9][a-z0-9._:-]*", obligation_id) is None:
            raise gl.vm.UserError("identifier must use lowercase ASCII letters, digits, dot, underscore, colon, or hyphen")

    def _parse_policy_list(self, encoded: str, label: str) -> list[str]:
        if not isinstance(encoded, str) or len(encoded.encode("utf-8")) > MAX_POLICY_JSON_BYTES:
            raise gl.vm.UserError(label + " JSON exceeds byte limit")
        try:
            values = json.loads(encoded)
        except Exception:
            raise gl.vm.UserError(label + " must be a JSON array")
        if not isinstance(values, list) or not values or len(values) > MAX_POLICY_ITEMS:
            raise gl.vm.UserError(label + " must contain between 1 and 8 entries")
        normalized = []
        for value in values:
            if not isinstance(value, str) or not value.strip():
                raise gl.vm.UserError(label + " entries must be non-empty strings")
            if value != value.strip() or len(value.encode("utf-8")) > MAX_POLICY_ITEM_BYTES:
                raise gl.vm.UserError(label + " entry has whitespace or exceeds byte limit")
            if value in normalized:
                raise gl.vm.UserError(label + " entries must be unique")
            normalized.append(value)
        return normalized

    def _require_registered(self, obligation_id: str) -> None:
        self._validate_identifier(obligation_id)
        if self.statuses.get(obligation_id, "") == "":
            raise gl.vm.UserError("obligation does not exist")

    def _transaction_timestamp(self) -> int:
        return int(datetime.now(timezone.utc).timestamp())
