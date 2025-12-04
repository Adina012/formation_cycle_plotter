# Formation Cycle Plotter

A unified, professional-grade Python application for plotting and analyzing formation cycle electrochemical data with multiple visualization modes and publication-quality formatting.

## Features

### Multiple Plotting Modes
- **Single Plot Mode**: Plot data from a single file with full cycle analysis
- **Multi-File Comparison**: Compare data across multiple files with color gradients
- **Cycle Analysis**: Analyze specific lithiation/delithiation cycles

### Data Processing
- Automatic cycle detection based on current sign changes
- Time normalization (starts at t=0)
- Capacity normalization by active mass
- Threshold-based filtering for non-zero current detection
- Robust error handling for malformed files

### Visualization
- Publication-quality matplotlib formatting (300 DPI)
- Color gradient support (viridis, plasma, inferno, cool, tab10)
- Scientific notation for intensity values
- Professional axis labels and legends
- Optional plot saving in high resolution

### User Interface
- Intuitive GUI with mode selection
- File browser for easy file selection
- Flexible axis selection (Time, Potential, Capacity, Current)
- Customizable options (active mass, cycle number, colormap)

## Project Structure

```
formation_cycle_plotter/
├── main.py              # Entry point
├── src/
│   ├── data_loader.py   # Data loading and processing
│   ├── plotter.py       # Plotting functionality
│   └── gui.py           # GUI application
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

## Installation

### Requirements
- Python 3.7+
- pandas
- numpy
- matplotlib
- tkinter (usually included with Python)

### Setup

```bash
cd formation_cycle_plotter
pip install -r requirements.txt
```

## Usage

### Running the Application

```bash
python main.py
```

This launches the GUI application where you can:

1. **Select Mode**: Choose between Single Plot, Multi-File Comparison, or Cycle Analysis
2. **Select Files**: Click "Select File(s)" to choose your data file(s)
3. **Configure Axes**: Select what you want to plot on X and Y axes
4. **Set Options**: 
   - Active mass (g) for capacity normalization
   - Specific cycle number (for cycle analysis)
   - Colormap preference (for multi-file plots)
5. **Generate Plot**: Click "Generate Plot" to create and display the visualization

### Command Line Usage

You can also use the modules programmatically:

```python
from src.data_loader import FormationCycleData
from src.plotter import FormationCyclePlotter

# Load data
data = FormationCycleData('data.txt')
data.trim_to_first_cycle()
data.normalize_time()

# Create plot
plotter = FormationCyclePlotter()
plotter.create_figure()
plotter.plot_single_file(data, x_col=1, y_col=2, active_mass=100)
plotter.finalize_plot("Time (h)", "Potential (V)")
plotter.show()
```

## Data File Format

Expected format for input files:

```
Tab-separated values with headers:
Cycle Number | Time (s) | Potential (V) | Capacity (mAh) | Current (mA)
```

The files should use:
- Tab (`\t`) as delimiter
- Comma (`,`) as decimal separator

## Column Reference

1. Time (s)
2. Potential (V)
3. Capacity (mAh)
4. Current (mA)

## Cycle Detection

The application automatically detects cycle boundaries by identifying sign changes in the current column. This works for standard lithiation/delithiation test data.

## Output

Plots can be displayed interactively or saved as high-resolution PNG files (300 DPI, publication-quality).

## Features Comparison

| Feature | Single Plot | Multi-File | Cycle Analysis |
|---------|-------------|-----------|-----------------|
| Single file | ✅ | N/A | ✅ |
| Multiple files | ✗ | ✅ | ✗ |
| All cycles | ✅ | ✅ | ✗ |
| Specific cycle | ✅ | ✅ | ✅ |
| Color gradient | ✗ | ✅ | ✗ |
| Capacity normalization | ✅ | ✅ | ✅ |

## License

MIT
