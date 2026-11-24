//! The JSON documents stored in `exercises.doc` and `sessions.doc`.
//!
//! Field names, defaults and `null`s are exactly those of the Python version (`python-final`), so rows
//! written by either version read the same: missing fields take the defaults below, and every field is
//! written back.

use chrono::Local;
use serde::{Deserialize, Serialize};

/// A variant of a library exercise, e.g. `1 — Wide`.
#[derive(Debug, Clone, Default, PartialEq, Serialize, Deserialize)]
#[serde(default)]
pub struct Variant {
    pub name: String,
    pub label: String,
}

/// A library exercise, e.g. `A — Pushup`, with its variants.
#[derive(Debug, Clone, Default, PartialEq, Serialize, Deserialize)]
#[serde(default)]
pub struct Exercise {
    pub name: String,
    pub label: String,
    pub variants: Vec<Variant>,
}

/// One exercise of a session, with its effort.
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(default)]
pub struct SessionExercise {
    pub name: String,
    pub label: String,
    pub variant_name: String,
    pub variant_label: String,
    pub sets: i32,
    pub reps: i32,
    /// Seconds; used instead of reps when not 0.
    pub duration: i32,
    /// Seconds of rest before the first set.
    pub rest_before: i32,
    /// Seconds of rest between sets.
    pub rest_seconds: i32,
}

impl Default for SessionExercise {
    fn default() -> Self {
        Self {
            name: String::new(),
            label: String::new(),
            variant_name: String::new(),
            variant_label: String::new(),
            sets: 3,
            reps: 10,
            duration: 0,
            rest_before: 0,
            rest_seconds: 90,
        }
    }
}

/// How the session went compared with the previous one.
#[derive(Debug, Clone, Copy, Default, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "UPPERCASE")]
pub enum Progress {
    Progress,
    #[default]
    Maintain,
    Regress,
}

/// A workout: a plan until it is run, then also how it went (`completed`).
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
#[serde(default)]
pub struct Workout {
    /// ISO date, `YYYY-MM-DD`.
    pub date: String,
    /// Body weight in kg.
    pub weight: Option<f64>,
    pub notes: Option<String>,
    /// 1 (low) to 5 (high).
    pub energy_level: Option<u8>,
    pub progress: Progress,
    pub warmup: Vec<SessionExercise>,
    pub workout: Vec<SessionExercise>,
    pub stretches: Vec<SessionExercise>,
    /// False for a plan not yet run: date, weight, energy, progress and notes are placeholders until then.
    pub completed: bool,
}

impl Default for Workout {
    fn default() -> Self {
        Self {
            date: Local::now().date_naive().to_string(),
            weight: None,
            notes: None,
            energy_level: None,
            progress: Progress::Maintain,
            warmup: Vec::new(),
            workout: Vec::new(),
            stretches: Vec::new(),
            completed: false,
        }
    }
}

impl Workout {
    /// Warmup, workout and stretches, in that order.
    pub fn exercises(&self) -> impl Iterator<Item = &SessionExercise> {
        self.warmup
            .iter()
            .chain(&self.workout)
            .chain(&self.stretches)
    }
}

/// The most recent use of exercise `name` in `sessions` (newest first), preferring one with the same
/// variant; pre-fills the effort of a new row.
pub fn last_used<'a>(
    sessions: impl IntoIterator<Item = &'a Workout>,
    name: &str,
    variant: &str,
) -> Option<&'a SessionExercise> {
    let mut fallback = None;
    for ex in sessions.into_iter().flat_map(Workout::exercises) {
        if ex.name != name {
            continue;
        }
        if ex.variant_name == variant {
            return Some(ex);
        }
        fallback = fallback.or(Some(ex));
    }
    fallback
}

/// The weight of the most recent completed session in `sessions` (newest first), if it has one.
pub fn last_weight<'a>(sessions: impl IntoIterator<Item = &'a Workout>) -> Option<f64> {
    sessions
        .into_iter()
        .find(|s| s.completed)
        .and_then(|s| s.weight)
}

/// Checks the API applies before storing documents (the Python version did them in its forms).
pub mod validate {
    use super::{Exercise, SessionExercise, Workout};

    /// Trim names and drop variants without a name; the name is required.
    pub fn exercise(mut ex: Exercise) -> Result<Exercise, String> {
        ex.name = ex.name.trim().to_owned();
        ex.label = ex.label.trim().to_owned();
        if ex.name.is_empty() {
            return Err("Name is required".into());
        }
        ex.variants.retain_mut(|v| {
            v.name = v.name.trim().to_owned();
            v.label = v.label.trim().to_owned();
            !v.name.is_empty()
        });
        Ok(ex)
    }

    /// Ranges of the Python form; a date when completed; energy 1–5; reps or duration, not both.
    pub fn session(mut s: Workout) -> Result<Workout, String> {
        s.date = s.date.trim().to_owned();
        s.notes = s
            .notes
            .map(|n| n.trim().to_owned())
            .filter(|n| !n.is_empty());
        if chrono::NaiveDate::parse_from_str(&s.date, "%Y-%m-%d").is_err() {
            return Err("Date is required (YYYY-MM-DD)".into());
        }
        if s.energy_level.is_some_and(|e| !(1..=5).contains(&e)) {
            return Err("Energy must be between 1 and 5".into());
        }
        if s.weight.is_some_and(|w| !(0.0..=999.0).contains(&w)) {
            return Err("Weight must be between 0 and 999 kg".into());
        }
        s.exercises().try_for_each(session_exercise)?;
        Ok(s)
    }

    fn session_exercise(ex: &SessionExercise) -> Result<(), String> {
        let name = &ex.name;
        let in_range = |v: i32, lo: i32, hi: i32, what: &str| {
            if (lo..=hi).contains(&v) {
                Ok(())
            } else {
                Err(format!("{name}: {what} must be between {lo} and {hi}"))
            }
        };
        if name.trim().is_empty() {
            return Err("Exercise name is required".into());
        }
        in_range(ex.sets, 1, 100, "sets")?;
        in_range(ex.reps, 0, 200, "reps")?;
        in_range(ex.duration, 0, 999, "duration")?;
        in_range(ex.rest_before, 0, 3600, "rest before")?;
        in_range(ex.rest_seconds, 0, 3600, "rest between sets")?;
        if ex.reps != 0 && ex.duration != 0 {
            return Err(format!("{name}: choose reps or duration, not both"));
        }
        Ok(())
    }
}

#[cfg(test)]
mod tests {
    use serde_json::json;

    use super::*;

    #[test]
    fn missing_fields_take_the_python_defaults() {
        let s: Workout = serde_json::from_value(json!({ "workout": [{ "name": "A" }] })).unwrap();
        assert_eq!(s.progress, Progress::Maintain);
        assert!(!s.completed && s.energy_level.is_none());
        assert_eq!(s.date, Local::now().date_naive().to_string());
        let ex = &s.workout[0];
        assert_eq!(
            (
                ex.sets,
                ex.reps,
                ex.duration,
                ex.rest_before,
                ex.rest_seconds
            ),
            (3, 10, 0, 0, 90)
        );
    }

    #[test]
    fn documents_round_trip_with_python_field_names() {
        let doc = json!({
            "date": "2026-10-12", "weight": 72.5, "notes": null, "energy_level": 3, "progress": "PROGRESS",
            "warmup": [], "stretches": [], "completed": true,
            "workout": [{ "name": "A", "label": "Pushup", "variant_name": "1", "variant_label": "Wide",
                          "sets": 4, "reps": 0, "duration": 30, "rest_before": 60, "rest_seconds": 90 }],
        });
        let s: Workout = serde_json::from_value(doc.clone()).unwrap();
        assert_eq!(serde_json::to_value(&s).unwrap(), doc);
        let ex = json!({ "name": "A", "label": "Pushup", "variants": [{ "name": "1", "label": "Wide" }] });
        let parsed: Exercise = serde_json::from_value(ex.clone()).unwrap();
        assert_eq!(serde_json::to_value(parsed).unwrap(), ex);
    }

    fn session_with(
        completed: bool,
        weight: Option<f64>,
        exercises: &[(&str, &str, i32)],
    ) -> Workout {
        let workout = exercises
            .iter()
            .map(|(name, variant, sets)| SessionExercise {
                name: (*name).into(),
                variant_name: (*variant).into(),
                sets: *sets,
                ..Default::default()
            })
            .collect();
        Workout {
            completed,
            weight,
            workout,
            ..Default::default()
        }
    }

    #[test]
    fn last_used_prefers_the_same_variant_then_the_newest() {
        let newest_first = [
            session_with(false, None, &[("A", "2", 5)]),
            session_with(true, None, &[("A", "1", 4), ("B", "", 2)]),
            session_with(true, None, &[("A", "1", 3)]),
        ];
        assert_eq!(last_used(&newest_first, "A", "1").unwrap().sets, 4);
        assert_eq!(last_used(&newest_first, "A", "9").unwrap().sets, 5);
        assert!(last_used(&newest_first, "C", "").is_none());
    }

    #[test]
    fn last_weight_comes_from_the_newest_completed_session() {
        let newest_first = [
            session_with(false, Some(90.0), &[]),
            session_with(true, Some(72.5), &[]),
            session_with(true, Some(70.0), &[]),
        ];
        assert_eq!(last_weight(&newest_first), Some(72.5));
        assert_eq!(last_weight(&newest_first[..1]), None);
    }

    #[test]
    fn exercise_validation_trims_and_drops_unnamed_variants() {
        let ex = Exercise {
            name: " A ".into(),
            label: "Pushup ".into(),
            variants: vec![
                Variant {
                    name: "1".into(),
                    label: "Wide".into(),
                },
                Variant {
                    name: " ".into(),
                    label: "dropped".into(),
                },
            ],
        };
        let ex = validate::exercise(ex).unwrap();
        assert_eq!(
            (ex.name.as_str(), ex.label.as_str(), ex.variants.len()),
            ("A", "Pushup", 1)
        );
        assert!(validate::exercise(Exercise::default()).is_err());
    }

    #[test]
    fn session_validation_follows_the_form_rules() {
        let with = |f: fn(&mut SessionExercise)| {
            let mut ex = SessionExercise {
                name: "A".into(),
                ..Default::default()
            };
            f(&mut ex);
            validate::session(Workout {
                workout: vec![ex],
                ..Default::default()
            })
        };
        assert!(with(|_| {}).is_ok());
        assert!(with(|e| e.duration = 30).unwrap_err().contains("not both"));
        assert!(with(|e| e.sets = 0).is_err());
        assert!(with(|e| e.rest_seconds = 3601).is_err());
        assert!(with(|e| e.name.clear()).is_err());
        let bad_date = Workout {
            date: "yesterday".into(),
            ..Default::default()
        };
        assert!(validate::session(bad_date).is_err());
        let bad_energy = Workout {
            energy_level: Some(6),
            ..Default::default()
        };
        assert!(validate::session(bad_energy).is_err());
    }
}
