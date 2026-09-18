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
    assert len([m for m in app.session_state["mutation_results"] if m.get("applied")]) >= 1


def test_home_action_buttons():
    app = make_app()

    # Clear inputs.
    app.button[1].click().run()
    assert not app.exception
    assert app.session_state["source_input"] == ""
    assert app.session_state["transformed_input"] == ""

    # Load the clean synthetic sample.
    app.button[0].click().run()
    assert not app.exception
    assert app.session_state["source_input"]
    assert app.session_state["source_input"] == app.session_state["transformed_input"]

    # Prepare the complete presentation case from Home.
    app.button[2].click().run()
    assert not app.exception
    assert app.session_state["analysis"] is not None
    assert app.session_state["source_input"] != app.session_state["transformed_input"]


def test_mutation_lab_buttons():
    app = make_app()
    navigate(app, "Mutation Lab")

    app.button[0].click().run()
    assert not app.exception
    assert app.session_state["mutation_results"]
    assert app.session_state["source_input"] != app.session_state["transformed_input"]

    app.button[1].click().run()
    assert not app.exception
    assert app.session_state["mutation_results"] == []
    assert app.session_state["source_input"] == app.session_state["transformed_input"]


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
    assert app.session_state["review_note"] == "Reviewed during presentation test."


def test_audit_report_renders_after_analysis():
    app = make_app()
    app.sidebar.button[0].click().run()
    navigate(app, "Audit Report")
    assert not app.exception
    assert app.session_state["analysis"] is not None
    assert len(app.download_button) >= 1
