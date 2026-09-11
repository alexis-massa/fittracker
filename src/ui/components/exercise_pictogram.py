# src/ui/components/exercise_pictogram.py
from nicegui import ui

_SVG_OPEN = (
    '<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg" '
    'fill="none" stroke="currentColor" stroke-width="4" '
    'stroke-linecap="round" stroke-linejoin="round">'
)
_SVG_CLOSE = "</svg>"


def _svg(*body: str) -> str:
    return _SVG_OPEN + "".join(body) + _SVG_CLOSE


def _head(cx: float, cy: float) -> str:
    return f'<circle cx="{cx}" cy="{cy}" r="6"/>'


def _line(x1: float, y1: float, x2: float, y2: float) -> str:
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}"/>'


def _bar(x1: float, y: float, x2: float) -> str:
    return _line(x1, y, x2, y)


# One simple line-art pictogram per base (letter) exercise - a rough, at-a-glance
# pose sketch, not an anatomically precise illustration. Keyed by ExerciseDefinition.name.
_PICTOGRAMS: dict[str, str] = {
    "A": _svg(  # pompes - plank, one arm to floor under shoulder
        _line(5, 90, 95, 90),
        _head(15, 65),
        _line(20, 68, 70, 72),
        _line(22, 68, 22, 90),
        _line(70, 72, 88, 90),
    ),
    "B": _svg(  # dips - suspended between two chair backs
        _line(20, 40, 20, 90),
        _line(70, 40, 70, 90),
        _head(45, 35),
        _line(45, 41, 45, 65),
        _line(45, 55, 20, 50),
        _line(45, 55, 70, 50),
        _line(45, 65, 55, 75),
        _line(55, 75, 65, 70),
    ),
    "C": _svg(  # traction - hanging pull-up, narrow grip
        _bar(20, 15, 80),
        _head(50, 25),
        _line(30, 15, 50, 30),
        _line(70, 15, 50, 30),
        _line(50, 31, 50, 60),
        _line(50, 60, 45, 80),
        _line(50, 60, 55, 80),
    ),
    "D": _svg(  # extension triceps - horizontal between two chairs
        _line(20, 70, 20, 90),
        _line(80, 70, 80, 90),
        _head(30, 55),
        _line(30, 58, 70, 62),
        _line(30, 58, 20, 70),
        _line(70, 62, 80, 75),
    ),
    "E": _svg(  # squat unijambiste - pistol squat, arms forward
        _head(35, 30),
        _line(35, 36, 40, 55),
        _line(40, 55, 45, 70),
        _line(45, 70, 40, 85),
        _line(40, 55, 65, 60),
        _line(65, 60, 80, 58),
        _line(37, 40, 55, 35),
    ),
    "F": _svg(  # gainage mural - wall sit
        _line(15, 10, 15, 90),
        _head(30, 40),
        _line(30, 46, 25, 60),
        _line(25, 60, 50, 60),
        _line(50, 60, 50, 85),
    ),
    "G": _svg(  # crunch - lying, knee bent, torso curling up
        _line(5, 85, 95, 85),
        _line(40, 85, 55, 65),
        _line(55, 65, 65, 80),
        _line(40, 85, 25, 72),
        _head(20, 68),
    ),
    "H": _svg(  # releve de jambes suspendu - hanging knee raise
        _bar(25, 12, 75),
        _head(50, 22),
        _line(30, 12, 50, 28),
        _line(70, 12, 50, 28),
        _line(50, 29, 50, 55),
        _line(50, 55, 68, 60),
        _line(68, 60, 72, 45),
    ),
    "I": _svg(  # traction large - wide-grip pull-up
        _bar(10, 12, 90),
        _head(50, 26),
        _line(15, 12, 50, 32),
        _line(85, 12, 50, 32),
        _line(50, 33, 50, 62),
        _line(50, 62, 45, 82),
        _line(50, 62, 55, 82),
    ),
    "J": _svg(  # pompe piquee - pike push-up, feet on chair
        _line(80, 55, 80, 90),
        _line(55, 45, 80, 55),
        _line(55, 45, 30, 60),
        _line(30, 60, 22, 63),
        _head(22, 63),
        _line(30, 60, 30, 85),
    ),
    "K": _svg(  # extension triceps - forearm plank incline
        _line(5, 88, 95, 88),
        _head(18, 68),
        _line(24, 70, 70, 75),
        _line(26, 72, 26, 88),
        _line(70, 75, 88, 88),
    ),
    "L": _svg(  # pompe pivotante - rotating push-up
        _line(5, 90, 95, 90),
        _head(15, 65),
        _line(20, 68, 65, 72),
        _line(22, 68, 22, 90),
        _line(30, 68, 45, 50),
        _line(65, 72, 85, 90),
    ),
    "M": _svg(  # extension lombaire - back extension on bench
        _bar(30, 70, 70),
        _line(30, 70, 30, 80),
        _line(70, 70, 70, 80),
        _line(60, 70, 80, 72),
        _line(60, 68, 40, 55),
        _line(40, 55, 25, 50),
        _head(20, 48),
    ),
    "N": _svg(  # releve de buste lateral - side bench raise
        _bar(35, 65, 75),
        _line(35, 65, 35, 75),
        _line(75, 65, 75, 75),
        _line(60, 65, 78, 66),
        _line(60, 63, 45, 48),
        _head(40, 44),
    ),
    "O": _svg(  # crunch croise - cross/bicycle crunch
        _line(5, 85, 95, 85),
        _line(45, 85, 55, 68),
        _line(55, 68, 50, 60),
        _line(45, 85, 30, 70),
        _head(26, 66),
    ),
    "P": _svg(  # crunch jambes flechies - reverse-style crunch
        _line(5, 85, 95, 85),
        _line(45, 85, 60, 70),
        _line(60, 70, 62, 85),
        _line(45, 85, 35, 68),
        _line(35, 68, 32, 70),
        _head(28, 66),
    ),
    "Q": _svg(  # pompe laterale - single-arm lateral plank
        _head(20, 55),
        _line(25, 58, 65, 72),
        _line(28, 60, 28, 88),
        _line(65, 72, 88, 80),
        _line(65, 72, 75, 85),
    ),
    "R": _svg(  # haussement d'epaules suspendu - shrug hold on bars
        _line(30, 40, 30, 90),
        _line(70, 40, 70, 90),
        _head(50, 35),
        _line(50, 42, 50, 70),
        _line(50, 42, 30, 40),
        _line(50, 42, 70, 40),
        _line(50, 70, 45, 90),
        _line(50, 70, 55, 90),
        _line(38, 36, 42, 30),
        _line(62, 36, 58, 30),
    ),
    "S": _svg(  # extension de nuque - lying, head hanging off bench
        _bar(28, 60, 72),
        _line(28, 60, 28, 78),
        _line(72, 60, 72, 78),
        _line(40, 58, 65, 58),
        _line(40, 58, 32, 78),
        _line(65, 58, 74, 68),
        _head(78, 74),
    ),
    "T": _svg(  # rotation du buste assis - seated twist with stick
        _line(45, 80, 60, 78),
        _line(60, 78, 65, 85),
        _line(45, 80, 45, 55),
        _head(45, 50),
        _line(25, 58, 65, 58),
    ),
    "U": _svg(  # enroule - jackknife roll
        _line(15, 80, 85, 80),
        _line(25, 78, 45, 78),
        _line(45, 78, 50, 50),
        _line(50, 50, 38, 34),
        _head(25, 76),
    ),
    "V": _svg(  # natation - superman
        _line(5, 80, 95, 80),
        _line(30, 65, 65, 65),
        _head(22, 63),
        _line(30, 65, 15, 55),
        _line(65, 65, 85, 58),
    ),
    "W": _svg(  # extension mollet - single-leg calf raise on block
        _line(40, 82, 58, 82),
        _line(48, 82, 48, 75),
        _line(48, 75, 50, 60),
        _line(50, 60, 60, 60),
        _line(60, 60, 58, 72),
        _line(50, 50, 50, 60),
        _head(47, 25),
        _line(50, 50, 48, 30),
        _line(48, 35, 65, 30),
    ),
    "X": _svg(  # rotation debout - standing twist with stick
        _line(45, 60, 40, 85),
        _line(45, 60, 50, 85),
        _line(45, 60, 45, 40),
        _head(45, 34),
        _line(25, 48, 65, 48),
        _line(45, 45, 25, 48),
        _line(45, 45, 65, 48),
    ),
    "Y": _svg(  # rotation de la nuque - lying, head turning
        _line(15, 72, 30, 68),
        _line(30, 68, 70, 70),
        _line(70, 70, 82, 78),
        _head(20, 63),
        _line(10, 55, 16, 60),
        _line(24, 60, 30, 55),
    ),
    "Z": _svg(  # le pont - bridge / backbend
        _line(5, 85, 95, 85),
        _line(25, 85, 30, 60),
        _line(30, 60, 50, 45),
        _line(50, 45, 70, 55),
        _line(70, 55, 80, 85),
        _head(35, 72),
    ),
}

_FALLBACK = _svg(_head(50, 30), _line(50, 36, 50, 65), _line(50, 45, 30, 55), _line(50, 45, 70, 55))


def pictogram_svg(name: str) -> str:
    return _PICTOGRAMS.get(name.upper(), _FALLBACK)


def exercise_pictogram(name: str, size: str = "40px") -> None:
    """Small clickable pictogram; opens a larger version on click."""
    svg = pictogram_svg(name)

    with ui.dialog() as dialog, ui.card().classes("items-center"):
        ui.html(svg).style("width:min(70vw,320px);height:min(70vw,320px)")
        ui.button("Close", on_click=dialog.close).props("flat")

    ui.html(svg).style(f"width:{size};height:{size};cursor:pointer;flex-shrink:0").on(
        "click", dialog.open
    )
