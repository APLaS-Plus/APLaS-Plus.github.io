from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

FEATURE_DIMS = [4, 16, 64, 128, 256]
X_MIN = -np.pi
X_MAX = np.pi
OUTPUT_PATH = Path(__file__).resolve().parent / "sin_linear_fit_comparison.png"
IMAGE_SIZE = (2500, 580)
BACKGROUND = "white"
PANEL_BORDER = "#d0d0d0"
GRID_COLOR = "#ebebeb"
AXIS_COLOR = "#666666"
SIN_COLOR = "#1f77b4"
FIT_COLOR = "#d62728"
TEXT_COLOR = "#222222"


def target_function(x: np.ndarray) -> np.ndarray:
    return np.sin(x**2)


def hat_features(x: np.ndarray, feature_dim: int) -> np.ndarray:
    """Build a fixed D-dimensional basis so the model stays linear in weights."""
    centers = np.linspace(X_MIN, X_MAX, feature_dim, dtype=np.float64)
    if feature_dim == 1:
        return np.ones((x.shape[0], 1), dtype=np.float64)

    step = centers[1] - centers[0]
    distances = np.abs(x[:, None] - centers[None, :])
    return np.clip(1.0 - distances / step, 0.0, None)


def fit_linear_model(feature_dim: int, x_train: np.ndarray, y_train: np.ndarray, x_eval: np.ndarray) -> tuple[np.ndarray, float]:
    phi_train = hat_features(x_train, feature_dim)
    weights, *_ = np.linalg.lstsq(phi_train, y_train, rcond=None)
    y_pred = hat_features(x_eval, feature_dim) @ weights
    mse = float(np.mean((y_pred - target_function(x_eval)) ** 2))
    return y_pred, mse


def load_font(size: int) -> ImageFont.ImageFont:
    for font_path in (
        "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/segoeui.ttf",
    ):
        try:
            return ImageFont.truetype(font_path, size=size)
        except OSError:
            continue
    return ImageFont.load_default()


def map_points(
    x_values: np.ndarray,
    y_values: np.ndarray,
    left: int,
    top: int,
    width: int,
    height: int,
    y_min: float,
    y_max: float,
) -> list[tuple[float, float]]:
    x_pixels = left + (x_values - X_MIN) / (X_MAX - X_MIN) * width
    y_pixels = top + (y_max - y_values) / (y_max - y_min) * height
    return list(zip(x_pixels.tolist(), y_pixels.tolist()))


def draw_centered_text(draw: ImageDraw.ImageDraw, xy: tuple[int, int], text: str, font: ImageFont.ImageFont, fill: str) -> None:
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    draw.text((xy[0] - text_width / 2, xy[1] - text_height / 2), text, font=font, fill=fill)


def main() -> None:
    x_train = np.linspace(X_MIN, X_MAX, 512, dtype=np.float64)
    y_train = target_function(x_train)
    x_eval = np.linspace(X_MIN, X_MAX, 1600, dtype=np.float64)
    y_true = target_function(x_eval)

    image = Image.new("RGB", IMAGE_SIZE, BACKGROUND)
    draw = ImageDraw.Draw(image)
    title_font = load_font(28)
    panel_title_font = load_font(20)
    label_font = load_font(16)
    tick_font = load_font(15)

    draw_centered_text(
        draw,
        (IMAGE_SIZE[0] // 2, 28),
        "Fitting sin(x^2) with linear models of different feature dimensions",
        title_font,
        TEXT_COLOR,
    )

    outer_left = 55
    outer_top = 70
    outer_right = 40
    outer_bottom = 35
    gap = 24
    panel_width = (IMAGE_SIZE[0] - outer_left - outer_right - gap * (len(FEATURE_DIMS) - 1)) // len(FEATURE_DIMS)
    panel_height = IMAGE_SIZE[1] - outer_top - outer_bottom

    plot_margin_left = 46
    plot_margin_right = 14
    plot_margin_top = 62
    plot_margin_bottom = 52
    y_min, y_max = -1.25, 1.25

    for idx, feature_dim in enumerate(FEATURE_DIMS):
        panel_left = outer_left + idx * (panel_width + gap)
        panel_top = outer_top
        panel_right = panel_left + panel_width
        panel_bottom = panel_top + panel_height
        plot_left = panel_left + plot_margin_left
        plot_top = panel_top + plot_margin_top
        plot_width = panel_width - plot_margin_left - plot_margin_right
        plot_height = panel_height - plot_margin_top - plot_margin_bottom
        plot_right = plot_left + plot_width
        plot_bottom = plot_top + plot_height

        y_pred, mse = fit_linear_model(feature_dim, x_train, y_train, x_eval)

        draw.rounded_rectangle((panel_left, panel_top, panel_right, panel_bottom), radius=18, outline=PANEL_BORDER, width=2)

        draw_centered_text(
            draw,
            (panel_left + panel_width // 2, panel_top + 22),
            f"{feature_dim}D",
            panel_title_font,
            TEXT_COLOR,
        )
        draw_centered_text(
            draw,
            (panel_left + panel_width // 2, panel_top + 46),
            f"MSE = {mse:.2e}",
            label_font,
            "#555555",
        )

        for x_tick, tick_label in ((X_MIN, "-pi"), (0.0, "0"), (X_MAX, "pi")):
            x_pixel = plot_left + (x_tick - X_MIN) / (X_MAX - X_MIN) * plot_width
            draw.line((x_pixel, plot_top, x_pixel, plot_bottom), fill=GRID_COLOR, width=1)
            draw_centered_text(draw, (int(x_pixel), plot_bottom + 18), tick_label, tick_font, "#666666")

        for y_tick in (-1.0, 0.0, 1.0):
            y_pixel = plot_top + (y_max - y_tick) / (y_max - y_min) * plot_height
            draw.line((plot_left, y_pixel, plot_right, y_pixel), fill=GRID_COLOR, width=1)
            bbox = draw.textbbox((0, 0), f"{y_tick:.0f}", font=tick_font)
            text_height = bbox[3] - bbox[1]
            draw.text((panel_left + 10, y_pixel - text_height / 2), f"{y_tick:.0f}", font=tick_font, fill="#666666")

        x_axis_y = plot_top + (y_max - 0.0) / (y_max - y_min) * plot_height
        draw.line((plot_left, x_axis_y, plot_right, x_axis_y), fill=AXIS_COLOR, width=2)
        draw.line((plot_left, plot_top, plot_left, plot_bottom), fill=AXIS_COLOR, width=2)

        sin_points = map_points(x_eval, y_true, plot_left, plot_top, plot_width, plot_height, y_min, y_max)
        fit_points = map_points(x_eval, y_pred, plot_left, plot_top, plot_width, plot_height, y_min, y_max)
        draw.line(sin_points, fill=SIN_COLOR, width=4)
        draw.line(fit_points, fill=FIT_COLOR, width=4)

        if idx == 0:
            legend_x = plot_left + 8
            legend_y = plot_top + 8
            draw.line((legend_x, legend_y, legend_x + 28, legend_y), fill=SIN_COLOR, width=4)
            draw.text((legend_x + 36, legend_y - 10), "sin(x^2)", font=label_font, fill=TEXT_COLOR)
            draw.line((legend_x, legend_y + 24, legend_x + 28, legend_y + 24), fill=FIT_COLOR, width=4)
            draw.text((legend_x + 36, legend_y + 14), "linear fit", font=label_font, fill=TEXT_COLOR)

    image.save(OUTPUT_PATH)


if __name__ == "__main__":
    main()
