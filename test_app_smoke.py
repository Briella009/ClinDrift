from streamlit.testing.v1 import AppTest

def make_app():
    app = AppTest.from_file("app.py", default_timeout=10)
    app.run()
    assert not app.exception
    return app

def test_navigation_views_render():
    app = make_app()
    for page in ["Home", "Mutation Lab", "Integrity Check", "Evidence", "Audit Report"]:
        app.sidebar.radio[0].set_value(page).run()
        assert not app.exception

def test_full_demo_case():
    app = make_app()
    app.sidebar.button[0].click().run()
    assert not app.exception
    assert app.session_state["analysis"] is not None
    assert len(app.session_state["analysis"]["findings"]) >= 1
