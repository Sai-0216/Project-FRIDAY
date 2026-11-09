from proactive.self_correction import SelfCorrection, SelfCorrectionStore


def test_progress_assessment():
    correction = SelfCorrection()
    result = correction.assess(0.9, 0.5)

    assert result["needs_correction"] is True
    assert correction.validate_assessment(result)


def test_progress_correction():
    correction = SelfCorrection()
    assessment = correction.assess(0.9, 0.5)

    result = correction.create_correction(assessment, "Review the plan")

    assert result["state"] == "corrected"
    assert correction.validate_correction(result)


def test_create_strategy_correction():
    result = SelfCorrection.create(
        SelfCorrection.CHANGE_STRATEGY,
        target="VERIFY_FIRST",
        reason="Improve reasoning reliability",
        confidence="HIGH",
        evidence={"source": "regression_test"},
    )

    assert result is not None
    assert result.is_valid()
    assert result.to_dict()["target"] == "VERIFY_FIRST"


def test_safety_validation_confidence_levels():
    high = SelfCorrection.create(
        SelfCorrection.CHANGE_STRATEGY,
        target="VERIFY_FIRST",
        confidence="HIGH",
    )
    low = SelfCorrection.create(
        SelfCorrection.CHANGE_STRATEGY,
        target="VERIFY_FIRST",
        confidence="LOW",
    )

    assert SelfCorrection.safety_validate(high) == "SAFE"
    assert SelfCorrection.safety_validate(low) == "REVIEW"


def test_forbidden_authorization_data_is_blocked():
    correction = SelfCorrection.create(
        SelfCorrection.CHANGE_STRATEGY,
        target="VERIFY_FIRST",
        confidence="HIGH",
        evidence={"authorization": True},
    )

    assert SelfCorrection.safety_validate(correction) == "BLOCKED"


def test_strategy_preview_does_not_apply_change():
    correction = SelfCorrection.create(
        SelfCorrection.CHANGE_STRATEGY,
        target="VERIFY_FIRST",
        confidence="HIGH",
    )

    preview = SelfCorrection.preview_strategy_correction(
        correction,
        "DIRECT",
        ["DIRECT", "VERIFY_FIRST"],
    )

    assert preview["status"] == "PREVIEW"
    assert preview["current_strategy"] == "DIRECT"
    assert preview["proposed_strategy"] == "VERIFY_FIRST"
    assert preview["applied"] is False


def test_strategy_preview_rejects_unknown_strategy():
    correction = SelfCorrection.create(
        SelfCorrection.CHANGE_STRATEGY,
        target="UNKNOWN",
        confidence="HIGH",
    )

    assert SelfCorrection.preview_strategy_correction(
        correction, "DIRECT", ["DIRECT", "VERIFY_FIRST"]
    ) is None


def test_store_persists_safe_correction(tmp_path):
    store_file = tmp_path / "corrections.json"
    store = SelfCorrectionStore(store_file)

    correction = SelfCorrection.create(
        SelfCorrection.CHANGE_STRATEGY,
        target="VERIFY_FIRST",
        confidence="HIGH",
    )

    assert store.record(correction) is True
    assert store.count() == 1

    reloaded = SelfCorrectionStore(store_file)
    assert reloaded.count() == 1
    assert reloaded.recent(1)[0]["target"] == "VERIFY_FIRST"


def test_store_rejects_low_confidence_correction(tmp_path):
    store = SelfCorrectionStore(tmp_path / "corrections.json")

    correction = SelfCorrection.create(
        SelfCorrection.CHANGE_STRATEGY,
        target="VERIFY_FIRST",
        confidence="LOW",
    )

    assert store.record(correction) is False
    assert store.count() == 0
