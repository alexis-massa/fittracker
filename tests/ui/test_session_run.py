import json

from src.models.exercise import SessionExercise
from src.models.session import Session
from src.ui.pages.session_run import _build_phases
from src.ui.pages.session_run import _phase_payload
from src.ui.pages.session_run import _runner_config
from src.ui.pages.session_run import _script_json


def _session() -> Session:
    return Session(
        _id="7",
        date="2026-03-04",
        workout=[
            SessionExercise(
                name="A", label="Pushup", variant_name="1", sets=2, reps=8, rest_before=10
            ),
            SessionExercise(name="B", sets=1, duration=30, rest_seconds=0),
        ],
    )


def test_rest_phase_title_and_subtitle_describe_the_next_series() -> None:
    phases = _build_phases(_session())
    payload = _phase_payload(phases[0])
    assert payload == {
        "seconds": 10,
        "title": "Rest · A1 Pushup",
        "subtitle": "Series 1/2 · Workout 1/2",
    }


def test_reps_based_work_phase_shows_reps_and_has_no_countdown() -> None:
    work = _phase_payload(_build_phases(_session())[1])
    assert work["seconds"] == 0
    assert work["title"] == "Work · A1 Pushup"
    assert work["subtitle"].endswith("· 8 reps")


def test_timed_work_phase_keeps_its_duration() -> None:
    last = _phase_payload(_build_phases(_session())[-1])
    assert last["seconds"] == 30
    assert "reps" not in last["subtitle"]


def test_runner_config_links_back_to_the_session() -> None:
    config = _runner_config(_session(), _build_phases(_session()))
    assert config["backUrl"] == "/sessions/7"
    assert len(config["phases"]) == len(_build_phases(_session()))


def test_embedded_json_cannot_break_out_of_the_script_tag() -> None:
    hostile = {"title": "</script><script>alert(1)</script>"}
    embedded = _script_json(hostile)
    assert "<" not in embedded
    assert json.loads(embedded) == hostile
