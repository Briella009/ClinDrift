"""Streamlit interaction checks for the defense workflow and mobile layouts."""

from streamlit.testing.v1 import AppTest


def make_app():
    app = AppTest.from_file("app.py", default_timeout=15)
    app.run()
    assert not app.exception
    return app


def navigate(app, page):
    app.sidebar.radio[0].set_value(page).run()
    assert not app.exception
    return app


def press(app, label):
    choices = [item for item in app.button if item.label == label]
    assert len(choices) == 1, f"{label}: {[b.label for b in app.button]}"
    choices[0].click().run()
    assert not app.exception
    return app


def load_demo(app):
    navigate(app, "Home")
    press(app, "Load drift example")
    assert app.session_state["analysis"] is None
    assert app.session_state["source_record"] != app.session_state["transformed_record"]
    assert len([m for m in app.session_state["mutation_results"] if m["applied"]]) >= 1
    return app


def run_check(app):
    navigate(app, "Integrity Check")
    press(app, "Run integrity check")
    assert app.session_state["analysis"] is not None
    assert len(app.session_state["analysis"]["findings"]) >= 1
    return app


def test_all_navigation_pages_render_without_running_a_check():
    app = make_app()
    assert app.session_state["analysis"] is None
    assert len(app.sidebar.button) == 0

    for page in ["Home", "Mutation Lab", "Integrity Check", "Evidence", "Audit Report"]:
        navigate(app, page)
        assert app.session_state["analysis"] is None
        assert not app.exception
    navigate(app, "Integrity Check")
    assert len(app.metric) == 0


def test_home_buttons_feedback_and_explicit_analysis():
    app = make_app()
    assert [b.label for b in app.button] == [
        "Load clean sample", "Clear inputs", "Load drift example"
    ]
    assert "Prepare presentation demo" not in [b.label for b in app.button]

    press(app, "Clear inputs")
    assert app.session_state["source_record"] == ""
    assert app.session_state["transformed_record"] == ""
    assert app.session_state["analysis"] is None

    navigate(app, "Integrity Check")
    assert app.button[0].label == "Run integrity check"
    assert app.button[0].disabled
    assert app.session_state["analysis"] is None

    navigate(app, "Home")
    press(app, "Load clean sample")
    assert app.session_state["source_record"] == app.session_state["transformed_record"]
    assert app.session_state["analysis"] is None

    press(app, "Load drift example")
    assert app.session_state["analysis"] is None
    assert app.session_state["mutation_results"]
    assert "controlled changes prepared" in app.session_state["action_feedback"]
    assert any("controlled changes prepared" in item.value for item in app.success)

    navigate(app, "Integrity Check")
    assert app.session_state["analysis"] is None
    assert len(app.metric) == 0
    press(app, "Run integrity check")
    assert len(app.metric) == 4
    assert len(app.dataframe) == 0
    assert len(app.container) >= 3
    assert app.session_state["analysis"]["score"] < 100


def test_mutation_lab_generates_and_clears_vertical_results():
    app = make_app()
    navigate(app, "Mutation Lab")
    press(app, "Generate controlled drift")
    assert app.session_state["analysis"] is None
    assert app.session_state["mutation_results"]
    assert len(app.dataframe) == 0
    assert len(app.container) >= 3

    press(app, "Reset clean sample")
    assert app.session_state["analysis"] is None
    assert app.session_state["mutation_results"] == []
    assert app.session_state["source_record"] == app.session_state["transformed_record"]
    assert len(app.dataframe) == 0


def test_results_visible_only_after_run_then_kept_during_navigation():
    app = make_app()
    load_demo(app)
    navigate(app, "Evidence")
    assert app.session_state["analysis"] is None
    assert len(app.expander) == 0
    assert len(app.button) == 0

    navigate(app, "Audit Report")
    assert app.session_state["analysis"] is None
    assert len(app.download_button) == 0
    assert len(app.button) == 0

    run_check(app)
    navigate(app, "Integrity Check")
    assert len(app.metric) == 4
    assert len(app.dataframe) == 0
    assert any("Latest completed check" in item.value for item in app.caption)

    navigate(app, "Evidence")
    assert len(app.expander) >= 1
    assert len(app.dataframe) == 0

    navigate(app, "Audit Report")
    assert len(app.download_button) == 2
    assert app.download_button[0].label == "Download PDF report"
    assert app.download_button[1].label == "Download JSON report"


def test_manual_home_edits_invalidate_stale_findings_and_reviewer_note():
    app = make_app()
    load_demo(app)
    run_check(app)
    navigate(app, "Evidence")
    note = "Review the allergy contradiction."
    app.text_area[0].set_value(note).run()
    press(app, "Save reviewer note")
    assert app.session_state["review_note_record"] == note

    navigate(app, "Home")
    app.text_area[1].set_value("Patient takes metformin 1000 mg twice a day.").run()
    assert not app.exception
    assert app.session_state["analysis"] is None
    assert app.session_state["mutation_results"] == []
    assert app.session_state["review_note_record"] == ""

    navigate(app, "Integrity Check")
    press(app, "Run integrity check")
    assert any(
        finding.drift_type == "Dosage drift"
        for finding in app.session_state["analysis"]["findings"]
    )


def test_manual_mutation_lab_edits_clear_old_controlled_self_test():
    app = make_app()
    navigate(app, "Mutation Lab")
    press(app, "Generate controlled drift")
    assert app.session_state["mutation_results"]

    app.text_area[1].set_value("Manually edited record.").run()
    assert not app.exception
    assert app.session_state["mutation_results"] == []
    assert app.session_state["analysis"] is None
    assert app.session_state["review_note_record"] == ""


def test_reviewer_note_requires_save_before_export_and_persists():
    app = make_app()
    load_demo(app)
    run_check(app)
    navigate(app, "Evidence")

    note = "Clinician review required: confirm metformin dosage before approval."
    app.text_area[0].set_value(note).run()
    assert not app.exception
    assert app.session_state["review_note_record"] == ""
    assert app.session_state["review_saved"] is False
    assert any("Unsaved changes" in v.value for v in app.warning)

    press(app, "Save reviewer note")
    assert app.session_state["review_note_record"] == note
    assert app.session_state["review_saved"] is True
    assert any("Reviewer note saved" in v.value for v in app.success)

    navigate(app, "Audit Report")
    assert any(note in item.value for item in app.info)
    assert len(app.download_button) == 2
    assert app.session_state["review_note_record"] == note

    navigate(app, "Evidence")
    assert app.text_area[0].value == note
    assert app.session_state["review_note_record"] == note

    app.text_area[0].set_value("New UNSAVED draft").run()
    assert app.session_state["review_note_record"] == note
    assert any("Unsaved changes" in v.value for v in app.warning)
    navigate(app, "Audit Report")
    assert app.session_state["review_note_record"] == note


def test_a_new_demo_clears_old_analysis_and_note():
    app = make_app()
    load_demo(app)
    run_check(app)
    navigate(app, "Evidence")
    app.text_area[0].set_value("Note only for first case.").run()
    press(app, "Save reviewer note")
    assert app.session_state["review_note_record"]

    load_demo(app)
    assert app.session_state["analysis"] is None
    assert app.session_state["review_note_record"] == ""
    assert app.session_state["review_saved"] is False

    navigate(app, "Audit Report")
    assert len(app.download_button) == 0


def test_clear_inputs_resets_all_report_data():
    app = make_app()
    load_demo(app)
    run_check(app)
    navigate(app, "Evidence")
    app.text_area[0].set_value("Note that must be cleared").run()
    press(app, "Save reviewer note")

    navigate(app, "Home")
    press(app, "Clear inputs")
    assert app.session_state["analysis"] is None
    assert app.session_state["source_record"] == ""
    assert app.session_state["transformed_record"] == ""
    assert app.session_state["mutation_results"] == []
    assert app.session_state["review_note_record"] == ""
    navigate(app, "Audit Report")
    assert len(app.download_button) == 0


def test_no_horizontal_dataframe_on_any_page_with_results():
    app = make_app()
    load_demo(app)
    navigate(app, "Mutation Lab")
    assert len(app.dataframe) == 0
    run_check(app)
    for page in ("Integrity Check", "Evidence", "Audit Report"):
        navigate(app, page)
        assert len(app.dataframe) == 0
