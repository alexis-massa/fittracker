from src.models import exercise
from src.models.exercise import ExerciseDefinition
from src.models.exercise import ExerciseVariant
from src.models.exercise import SessionExercise
from src.utils import pg
from src.utils.pg import PgTable


def test_exercise_variant_display_name_includes_label_when_present() -> None:
    variant = ExerciseVariant(name="1", label="Wide")
    assert variant.display_name == "1 — Wide"


def test_exercise_variant_display_name_falls_back_to_name_only() -> None:
    variant = ExerciseVariant(name="1")
    assert variant.display_name == "1"


def test_exercise_variant_from_doc_defaults_missing_fields() -> None:
    variant = ExerciseVariant.from_doc({})
    assert variant == ExerciseVariant(name="", label="")


def test_exercise_variant_round_trips_through_doc() -> None:
    variant = ExerciseVariant(name="2", label="Narrow")
    assert ExerciseVariant.from_doc(variant.to_doc()) == variant


def test_exercise_definition_display_name_includes_label_when_present() -> None:
    defn = ExerciseDefinition(name="A", label="Pushup")
    assert defn.display_name == "A — Pushup"


def test_exercise_definition_display_name_falls_back_to_name_only() -> None:
    defn = ExerciseDefinition(name="A")
    assert defn.display_name == "A"


def test_exercise_definition_id_property_reflects_underlying_field() -> None:
    defn = ExerciseDefinition.from_doc({"_id": "abc123", "name": "A"})
    assert defn.id == "abc123"


def test_exercise_definition_get_variant_finds_matching_variant() -> None:
    variant = ExerciseVariant(name="1", label="Wide")
    defn = ExerciseDefinition(name="A", variants=[variant])
    assert defn.get_variant("1") is variant


def test_exercise_definition_get_variant_returns_none_when_absent() -> None:
    defn = ExerciseDefinition(name="A", variants=[])
    assert defn.get_variant("1") is None


def test_exercise_definition_from_doc_parses_nested_variants() -> None:
    defn = ExerciseDefinition.from_doc(
        {
            "_id": "abc123",
            "name": "A",
            "label": "Pushup",
            "variants": [{"name": "1", "label": "Wide"}],
        }
    )
    assert defn.name == "A"
    assert defn.label == "Pushup"
    assert defn.variants == [ExerciseVariant(name="1", label="Wide")]


def test_exercise_definition_to_doc_omits_id() -> None:
    defn = ExerciseDefinition.from_doc({"_id": "abc123", "name": "A"})
    assert "_id" not in defn.to_doc()


def test_exercise_definition_to_doc_serializes_variants() -> None:
    defn = ExerciseDefinition(name="A", variants=[ExerciseVariant(name="1", label="Wide")])
    assert defn.to_doc()["variants"] == [{"name": "1", "label": "Wide"}]


def test_session_exercise_short_name_includes_variant_when_present() -> None:
    se = SessionExercise(name="A", variant_name="1")
    assert se.short_name == "A1"


def test_session_exercise_short_name_omits_variant_when_absent() -> None:
    se = SessionExercise(name="A")
    assert se.short_name == "A"


def test_session_exercise_display_name_with_label_and_variant() -> None:
    se = SessionExercise(name="A", label="Pushup", variant_name="1", variant_label="Wide")
    assert se.display_name == "A — Pushup / 1 — Wide"


def test_session_exercise_display_name_name_only() -> None:
    se = SessionExercise(name="A")
    assert se.display_name == "A"


def test_session_exercise_from_doc_defaults_missing_fields() -> None:
    se = SessionExercise.from_doc({"name": "A"})
    assert se == SessionExercise(name="A")


def test_session_exercise_round_trips_through_doc() -> None:
    se = SessionExercise(
        name="A",
        label="Pushup",
        variant_name="1",
        variant_label="Wide",
        sets=4,
        reps=8,
        duration=30,
        rest_before=10,
        rest_seconds=60,
    )
    assert SessionExercise.from_doc(se.to_doc()) == se


def test_session_exercise_from_definition_without_variant() -> None:
    defn = ExerciseDefinition(name="A", label="Pushup")
    se = SessionExercise.from_definition(defn)
    assert se.name == "A"
    assert se.label == "Pushup"
    assert se.variant_name == ""
    assert se.variant_label == ""


def test_session_exercise_from_definition_with_variant() -> None:
    defn = ExerciseDefinition(name="A", label="Pushup")
    variant = ExerciseVariant(name="1", label="Wide")
    se = SessionExercise.from_definition(defn, variant)
    assert se.variant_name == "1"
    assert se.variant_label == "Wide"


def test_get_all_returns_definitions_sorted_by_name(exercises_table: PgTable) -> None:
    pg.insert_one(exercises_table, {"name": "B", "label": "Situp", "variants": []})
    pg.insert_one(exercises_table, {"name": "A", "label": "Pushup", "variants": []})
    assert [defn.name for defn in exercise.get_all()] == ["A", "B"]


def test_get_by_id_returns_matching_definition(exercises_table: PgTable) -> None:
    inserted_id = pg.insert_one(exercises_table, {"name": "A", "label": "Pushup", "variants": []})
    defn = exercise.get_by_id(inserted_id)
    assert defn is not None
    assert defn.name == "A"


def test_get_by_id_returns_none_when_missing(exercises_table: PgTable) -> None:
    assert exercise.get_by_id("999999") is None


def test_create_persists_definition_and_returns_id(exercises_table: PgTable) -> None:
    defn = ExerciseDefinition(name="A", label="Pushup")
    new_id = exercise.create(defn)
    stored = exercise.get_by_id(new_id)
    assert stored is not None
    assert stored.name == "A"


def test_update_modifies_existing_definition(exercises_table: PgTable) -> None:
    defn = ExerciseDefinition(name="A", label="Pushup")
    new_id = exercise.create(defn)
    updated = ExerciseDefinition(name="A", label="Push-up")
    assert exercise.update(new_id, updated) is True
    assert exercise.get_by_id(new_id).label == "Push-up"  # type: ignore[union-attr]


def test_delete_removes_definition(exercises_table: PgTable) -> None:
    defn = ExerciseDefinition(name="A", label="Pushup")
    new_id = exercise.create(defn)
    assert exercise.delete(new_id) is True
    assert exercise.get_by_id(new_id) is None
