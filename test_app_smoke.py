from streamlit.testing.v1 import AppTest


def make_app():
    app = AppTest.from_file("app.py", default_timeout=10)
    app.run()
    assert not app.exception
    return app


def navigate(app, page):
    app.sidebar.radio[0].set_value(page).run()
    assert not app.exception
    return app


def test_navigation_views_render():
    app = make_app()
    for page in ["Home", "Mutation Lab", "Integrity Check", "Evidence", "Audit Report"]:
        navigate(app, page)


def test_full_demo_case():
    app = make_app()
    app.sidebar.button[0].click().run()
    assert not app.exception
    assert app.session_state["analysis"] is not None
    assert len(app.session_state["analysis"]["findings"]) >= 1
    assert len(
        [m for m in app.session_state["mutation_results"] if m.get("applied")]
    ) >= 1
    assert app.session_state["source_record"] != app.session_state["transformed_record"]


def test_home_action_buttons():
    app = make_app()

    # Clear persistent records.
    app.button[1].click().run()
    assert not app.exception
    assert app.session_state["source_record"] == ""
    assert app.session_state["transformed_record"] == ""

    # Load the clean synthetic sample.
    app.button[0].click().run()
    assert not app.exception
    assert app.session_state["source_record"]
    assert app.session_state["source_record"] == app.session_state["transformed_record"]

    # Prepare the complete presentation case from Home.
    app.button[2].click().run()
    assert not app.exception
    assert app.session_state["analysis"] is not None
    assert app.session_state["source_record"] != app.session_state["transformed_record"]


def test_mutation_lab_buttons():
    app = make_app()
    navigate(app, "Mutation Lab")

    app.button[0].click().run()
    assert not app.exception
    assert app.session_state["mutation_results"]
    assert app.session_state["source_record"] != app.session_state["transformed_record"]

    app.button[1].click().run()
    assert not app.exception
    assert app.session_state["mutation_results"] == []
    assert app.session_state["source_record"] == app.session_state["transformed_record"]


def test_integrity_and_evidence_workflow():
    app = make_app()
    app.sidebar.button[0].click().run()
    assert app.session_state["analysis"] is not None

    navigate(app, "Integrity Check")
    app.button[0].click().run()
    assert not app.exception
    assert app.session_state["analysis"] is not None

    navigate(app, "Evidence")
    assert not app.exception
    assert len(app.expander) >= 1
    assert len(app.text_area) >= 1

    app.text_area[0].set_value("Reviewed during presentation test.").run()
    assert not app.exception
    assert (
        app.session_state["review_note_record"]
        == "Reviewed during presentation test."
    )


def test_audit_report_renders_after_analysis():
    app = make_app()
    app.sidebar.button[0].click().run()
    navigate(app, "Audit Report")
    assert not app.exception
    assert app.session_state["analysis"] is not None
    assert len(app.download_button) == 2



def test_home_text_edits_invalidate_old_analysis_and_mutations():
    app = make_app()
    app.sidebar.button[0].click().run()
    assert app.session_state["analysis"] is not None
    assert app.session_state["mutation_results"]

    navigate(app, "Home")
    app.text_area[1].set_value(
        "Patient takes metformin 1000 mg twice a day."
    ).run()
    assert not app.exception
    assert app.session_state["analysis"] is None
    assert app.session_state["mutation_results"] == []

    navigate(app, "Integrity Check")
    app.button[0].click().run()
    assert not app.exception
    assert any(
        finding.drift_type == "Dosage drift"
        for finding in app.session_state["analysis"]["findings"]
    )


def test_manual_mutation_lab_edits_invalidate_stale_mutation_self_test():
    app = make_app()
    navigate(app, "Mutation Lab")
    app.button[0].click().run()
    assert app.session_state["mutation_results"]

    app.text_area[1].set_value("Manually changed record.").run()
    assert not app.exception
    assert app.session_state["analysis"] is None
    assert app.session_state["mutation_results"] == []


def test_reviewer_note_save_visible_and_persists_across_pages():
    app = make_app()
    app.sidebar.button[0].click().run()
    navigate(app, "Evidence")

    note = "Clinician review required: confirm metformin dosage before approval."
    app.text_area[0].set_value(note).run()
    assert not app.exception
    assert app.session_state["review_note_record"] == note
    assert app.button[0].label == "Save reviewer note"
    app.button[0].click().run()
    assert not app.exception
    assert app.session_state["review_note_record"] == note
    assert any("Reviewer note saved" in value.value for value in app.success)

    navigate(app, "Audit Report")
    assert not app.exception
    assert any(note in value.value for value in app.info)
    assert any(note in value.value for value in app.code)
    assert len(app.download_button) == 2
    assert app.download_button[0].label == "Download PDF report"
    assert app.download_button[1].label == "Download JSON report"

    navigate(app, "Evidence")
    assert app.text_area[0].value == note

    # Starting a new case clears the old reviewer note.
    app.sidebar.button[0].click().run()
    assert not app.exception
    assert app.session_state["review_note_record"] == ""


def test_run_integrity_check_now_from_unanalysed_evidence_and_report():
    for page in ("Evidence", "Audit Report"):
        app = make_app()
        navigate(app, page)
        assert app.button[0].label == "Run integrity check now"
        app.button[0].click().run()
        assert not app.exception
        assert app.session_state["analysis"] is not None
        if page == "Audit Report":
            assert len(app.download_button) == 2


def test_clear_inputs_clears_analysis_note_and_export_controls():
    app = make_app()
    app.sidebar.button[0].click().run()
    navigate(app, "Evidence")
    app.text_area[0].set_value("Note that should not remain").run()
    navigate(app, "Home")
    app.button[1].click().run()
    assert not app.exception
    assert app.session_state["source_record"] == ""
    assert app.session_state["transformed_record"] == ""
    assert app.session_state["review_note_record"] == ""
    assert app.session_state["mutation_results"] == []
    assert app.session_state["analysis"] is None
    navigate(app, "Audit Report")
    assert not app.exception
    assert len(app.download_button) == 0
