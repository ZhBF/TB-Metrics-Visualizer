# 📊 TensorBoard Metrics Visualizer

> A powerful batch visualization tool for aggregating and comparing TensorBoard scalar metrics across multiple experimental runs.

[![Python 3.6+](https://img.shields.io/badge/python-3.6+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## ✨ Features

- 🔍 **Recursive Discovery**: Automatically finds all TensorBoard event files (`events.out.tfevents*`) in specified directories
- 📈 **Multi-Run Aggregation**: Combines scalar metrics from multiple runs into unified plots for easy comparison
- 🎯 **Flexible Layout**: Automatic subplot arrangement with customizable dimensions and columns per row
- 🔄 **Curve Smoothing**: Optional smoothing with Exponential Moving Average (EMA) or Moving Average (MA)
- 👀 **Dual Visualization**: Display raw and smoothed curves together for better analysis
- 🖼️ **GUI Display**: Show visualization window directly (with graceful fallback for headless environments)
- 💾 **High-Quality Export**: Generates crisp PNG images at 150 DPI for presentations and publications

## 📋 Requirements

- Python 3.6+ (compatible with Python 3.6 through 3.12+)
- TensorBoard (any recent version)
- NumPy (any recent version)
- Matplotlib (any recent version)

All dependencies will be automatically installed with the package.

## ⚡ Installation

### Option 1: Install as a Package (Recommended)

Install the tool globally with automatic dependency management:

```bash
# Clone or download the project
cd TB-Metrics-Visualizer

# Install in editable mode (for development)
pip install -e .

# Or install normally
pip install .
```

After installation, you can use the `tb-visualizer` or `tbviz` command anywhere:

```bash
tb-visualizer ./run1 ./run2 -o results.png
```

### Option 2: Manual Installation

If you prefer to run the script directly:

```bash
pip install -r requirements.txt
python main.py ./run1 ./run2 -o results.png
```

### Uninstallation

To uninstall the globally installed command:

```bash
pip uninstall tb-metrics-visualizer
```

See [INSTALL.md](INSTALL.md) for detailed installation instructions and troubleshooting.

## 🚀 Quick Start

**Basic usage** — combine all metrics from two runs:
```bash
# Using installed command
tb-visualizer ./run1 ./run2 -o results.png

# Or using Python script directly
python main.py ./run1 ./run2 -o results.png
```

**Multiple runs with wildcards**:
```bash
tb-visualizer ./experiments/* -o output.png
```

**Show visualization window**:
```bash
tb-visualizer ./logs --show
```

**Enable curve smoothing**:
```bash
tb-visualizer ./logs --smooth ema --smooth-window 10
```

**Show raw and smoothed curves together**:
```bash
tb-visualizer ./logs --smooth ema --show-both -o comparison.png
```

## 📖 Command-Line Arguments

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `directories` | path(s) | - | **Required**. One or more directories containing TensorBoard logs |
| `-o, --output` | path | `tensorboard_visualization.png` | Output PNG file path |
| `--width` | float | `8` | Width of each subplot (inches) |
| `--height` | float | `4` | Height of each subplot (inches) |
| `--max-cols` | int | `3` | Maximum number of subplots per row |
| `--show` | flag | disabled | Display visualization window (if display available) |
| `--smooth` | `{ema,ma}` | disabled | Smoothing method: `ema` (exponential) or `ma` (moving average) |
| `--smooth-window` | int | `10` | Window size for smoothing algorithm |
| `--show-both` | flag | disabled | Display both raw and smoothed curves together (requires `--smooth`) |

## 💡 Usage Examples

### Comparing Multiple Experiments
```bash
tb-visualizer ./exp_lr_0.001 ./exp_lr_0.01 ./exp_lr_0.1 \
  -o learning_rate_comparison.png \
  --max-cols 2
```

### Smoothed Metrics with Custom Dimensions
```bash
tb-visualizer ./training_logs \
  --smooth ema \
  --smooth-window 15 \
  --width 10 \
  --height 5 \
  -o smoothed_metrics.png
```

### Interactive Viewing with Smoothing
```bash
tb-visualizer ./results \
  --smooth ma \
  --show-both \
  --show
```

### Batch Processing Multiple Experiments
```bash
tb-visualizer ./runs/* \
  -o final_results.png \
  --width 12 \
  --height 6 \
  --max-cols 4 \
  --smooth ema
```

## 📝 Notes

- **Scalar Metrics Only**: Only scalar metrics from TensorBoard are processed (histograms, images, etc. are ignored)
- **Run Naming**: Run names are automatically derived from relative paths to the input base directories
- **Headless Support**: The tool gracefully handles environments without display (X11/Wayland) — just skip the `--show` flag
- **Legend**: Legends are automatically shown when multiple runs are present for a metric

## 🔧 Troubleshooting

### No event files found
- Ensure you're pointing to the correct log directory containing `events.out.tfevents*` files
- Check that you have read permissions on the log files

### Cannot show visualization window
- Ensure X11/Wayland is available if running remotely
- Use `--show` flag only when needed; the tool always saves to PNG regardless

### Smoothing not applied
- Use `--smooth ema` or `--smooth ma` to enable smoothing
- Adjust `--smooth-window` (larger values = more smoothing)
- Use `--show-both` to compare raw vs smoothed

## 📄 License

MIT
