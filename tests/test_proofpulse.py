import json


CONTRACT = "contracts/proofpulse.py"
REQUIREMENTS = '["maintain coverage","submit quarterly report"]'
SOURCES = '["source:policy","source:reporting-portal"]'


def register(contract, obligation_id="policy-001", **overrides):
    args = {
        "obligation_id": obligation_id,
        "description": "Maintain the required insurance coverage",
        "requirements_json": REQUIREMENTS,
        "approved_sources_json": SOURCES,
        "deadline_timestamp": 0,
        "observation_period_seconds": 3600,
    }
    args.update(overrides)
    return contract.register_obligation(**args)


def test_valid_registration_and_persistent_reads(direct_deploy):
    contract = direct_deploy(CONTRACT)
    assert register(contract) == "policy-001"
    metadata = json.loads(contract.get_obligation_metadata("policy-001"))
    policy = json.loads(contract.get_policy("policy-001"))
    counters = json.loads(contract.get_obligation_counters("policy-001"))

    assert metadata["obligation_id"] == "policy-001"
    assert metadata["status"] == "ACTIVE"
    assert metadata["registered_at"] > 0
    assert metadata["observation_period_seconds"] == 3600
    assert policy == {
        "version": 1,
        "requirements": ["maintain coverage", "submit quarterly report"],
        "approved_sources": ["source:policy", "source:reporting-portal"],
    }
    assert contract.get_lifecycle_state("policy-001") == "ACTIVE"
    assert contract.get_owner("policy-001")
    assert counters == {"registry_count": 1, "requirement_count": 2, "approved_source_count": 2}


def test_registration_rejects_empty_description_without_mutation(direct_deploy, direct_vm):
    contract = direct_deploy(CONTRACT)
    with direct_vm.expect_revert("description must be non-empty"):
        register(contract, description="   ")
    assert contract.get_registry_count() == 0


def test_registration_rejects_malformed_identifier(direct_deploy, direct_vm):
    contract = direct_deploy(CONTRACT)
    with direct_vm.expect_revert("identifier must use lowercase ASCII"):
        register(contract, obligation_id="Bad ID")
    assert contract.get_registry_count() == 0


def test_registration_rejects_invalid_policy_json_and_duplicate_entries(direct_deploy, direct_vm):
    contract = direct_deploy(CONTRACT)
    with direct_vm.expect_revert("requirements must be a JSON array"):
        register(contract, requirements_json="not-json")
    with direct_vm.expect_revert("requirements entries must be unique"):
        register(contract, requirements_json='["one","one"]')
    assert contract.get_registry_count() == 0


def test_duplicate_obligation_id_is_rejected(direct_deploy, direct_vm):
    contract = direct_deploy(CONTRACT)
    register(contract)
    with direct_vm.expect_revert("obligation identifier already exists"):
        register(contract)
    assert contract.get_registry_count() == 1


def test_creator_address_is_taken_from_genlayer_transaction_context(
    direct_deploy, direct_owner
):
    contract = direct_deploy(CONTRACT)
    register(contract)
    assert contract.get_owner("policy-001").lower() == "0x" + direct_owner.hex()


def test_only_owner_can_close_obligation(direct_deploy, direct_vm, direct_alice):
    contract = direct_deploy(CONTRACT)
    register(contract)
    with direct_vm.prank(direct_alice):
        with direct_vm.expect_revert("only the obligation owner may close it"):
            contract.close_obligation("policy-001")
    assert contract.get_lifecycle_state("policy-001") == "ACTIVE"


def test_owner_can_close_and_policy_stays_immutable(direct_deploy):
    contract = direct_deploy(CONTRACT)
    register(contract)
    policy_before = contract.get_policy("policy-001")
    contract.close_obligation("policy-001")
    assert contract.get_lifecycle_state("policy-001") == "CLOSED"
    assert contract.get_policy("policy-001") == policy_before


def test_deadline_must_be_future_and_is_stored(direct_deploy, direct_vm, direct_owner):
    contract = direct_deploy(CONTRACT)
    direct_vm.warp("2026-10-12T12:00:00Z")
    now = 1791806400
    with direct_vm.expect_revert("deadline must be after registration time"):
        register(contract, deadline_timestamp=now, observation_period_seconds=0)
    register(contract, "future-deadline", deadline_timestamp=now + 60, observation_period_seconds=0)
    metadata = json.loads(contract.get_obligation_metadata("future-deadline"))
    assert metadata["registered_at"] == now
    assert metadata["deadline_timestamp"] == now + 60


def test_lifecycle_rejects_nonexistent_and_repeated_close(direct_deploy, direct_vm):
    contract = direct_deploy(CONTRACT)
    with direct_vm.expect_revert("obligation does not exist"):
        contract.close_obligation("missing")
    register(contract)
    contract.close_obligation("policy-001")
    with direct_vm.expect_revert("only an active obligation may be closed"):
        contract.close_obligation("policy-001")


def test_oversized_inputs_and_invalid_period_are_rejected(direct_deploy, direct_vm):
    contract = direct_deploy(CONTRACT)
    with direct_vm.expect_revert("identifier is invalid or too long"):
        register(contract, obligation_id="a" * 65)
    with direct_vm.expect_revert("description exceeds byte limit"):
        register(contract, description="x" * 513)
    with direct_vm.expect_revert("requirements must contain between 1 and 8 entries"):
        register(contract, requirements_json=json.dumps([str(i) for i in range(9)]))
    with direct_vm.expect_revert("observation period is out of range"):
        register(contract, observation_period_seconds=59)
    assert contract.get_registry_count() == 0


def test_failed_registration_is_atomic_and_obligations_are_independent(
    direct_deploy, direct_vm, direct_alice
):
    contract = direct_deploy(CONTRACT)
    with direct_vm.expect_revert("a deadline or observation period is required"):
        register(contract, observation_period_seconds=0)
    assert contract.get_registry_count() == 0

    register(contract, "alpha")
    with direct_vm.prank(direct_alice):
        register(contract, "beta")
    contract.close_obligation("alpha")
    assert contract.get_registry_count() == 2
    assert contract.get_lifecycle_state("alpha") == "CLOSED"
    assert contract.get_lifecycle_state("beta") == "ACTIVE"
    assert contract.get_owner("beta").lower() == "0x" + direct_alice.hex()
