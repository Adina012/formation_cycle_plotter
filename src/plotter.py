"""Plotting module for formation cycle data visualization."""

import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
from typing import List, Tuple, Optional
from data_loader import FormationCycleData


class FormationCyclePlotter:
    """Handle plotting of formation cycle data."""
    
    COLUMN_MAP = {
        1: ("Time (s)", 1),
        2: ("Potential (V)", 2),
        3: ("Capacity (mAh)", 3),
        4: ("Current (mA)", 4)
    }
    
    def __init__(self):
        """Initialize plotter with publication-quality settings."""
        self._setup_matplotlib()
        self.fig = None
        self.ax = None
    
    @staticmethod
    def _setup_matplotlib():
        """Configure matplotlib for publication-quality output."""
        plt.rcParams['figure.dpi'] = 300
        plt.rcParams['savefig.dpi'] = 300
        plt.rcParams['font.size'] = 10
        plt.rcParams['font.family'] = 'sans-serif'
        plt.rcParams['axes.linewidth'] = 1.0
        plt.rcParams['lines.linewidth'] = 0.8
        plt.rcParams['xtick.major.width'] = 0.8
        plt.rcParams['ytick.major.width'] = 0.8
        plt.rcParams['xtick.minor.width'] = 0.5
        plt.rcParams['ytick.minor.width'] = 0.5
    
    def create_figure(self, figsize: Tuple[float, float] = (10, 6)):
        """Create a new figure."""
        self.fig, self.ax = plt.subplots(figsize=figsize)
        self._format_axes()
    
    def _format_axes(self):
        """Apply publication-quality formatting to axes."""
        self.ax.spines['top'].set_visible(False)
        self.ax.spines['right'].set_visible(False)
        self.ax.tick_params(axis='both', which='major', labelsize=9)
        self.ax.yaxis.set_major_formatter(ticker.ScalarFormatter(useMathText=True))
        self.ax.ticklabel_format(style='sci', axis='y', scilimits=(0, 0))
    
    @staticmethod
    def _parse_cycle_input(cycle_input: Optional[str], data: FormationCycleData) -> Optional[List[int]]:
        """
        Parse user cycle input into a list of cycle indices.
        
        Supports formats:
        - 'discharge 3' -> discharge cycle #3
        - 'charge 2' -> charge cycle #2
        - '5' -> cycle #5 (all cycles)
        - 'all' or None -> all cycles
        
        Args:
            cycle_input: User input string
            data: FormationCycleData object to get discharge/charge info
            
        Returns:
            List of cycle indices to plot (1-indexed), or None for all cycles
        """
        if not cycle_input or cycle_input.lower() == 'all':
            return None
        
        cycle_input = cycle_input.lower().strip()
        
        # Check for "discharge X" or "charge X" format
        if cycle_input.startswith('discharge'):
            parts = cycle_input.split()
            if len(parts) == 2:
                try:
                    discharge_num = int(parts[1])
                    discharge_cycles, _ = data.get_discharge_charge_cycles()
                    if 1 <= discharge_num <= len(discharge_cycles):
                        # Find which cycle index this corresponds to
                        target_range = discharge_cycles[discharge_num - 1]
                        all_cycles = data.get_cycles()
                        for idx, cycle_range in enumerate(all_cycles):
                            if cycle_range == target_range:
                                return [idx + 1]  # Return 1-indexed
                    else:
                        raise ValueError(f"Discharge cycle {discharge_num} not found. Available: 1-{len(discharge_cycles)}")
                except (ValueError, IndexError) as e:
                    raise ValueError(f"Invalid discharge format: {cycle_input}. Use 'discharge X' where X is 1, 2, 3, etc.")
        
        elif cycle_input.startswith('charge'):
            parts = cycle_input.split()
            if len(parts) == 2:
                try:
                    charge_num = int(parts[1])
                    _, charge_cycles = data.get_discharge_charge_cycles()
                    if 1 <= charge_num <= len(charge_cycles):
                        # Find which cycle index this corresponds to
                        target_range = charge_cycles[charge_num - 1]
                        all_cycles = data.get_cycles()
                        for idx, cycle_range in enumerate(all_cycles):
                            if cycle_range == target_range:
                                return [idx + 1]  # Return 1-indexed
                    else:
                        raise ValueError(f"Charge cycle {charge_num} not found. Available: 1-{len(charge_cycles)}")
                except (ValueError, IndexError) as e:
                    raise ValueError(f"Invalid charge format: {cycle_input}. Use 'charge X' where X is 1, 2, 3, etc.")
        
        else:
            # Try to parse as integer (cycle number)
            try:
                cycle_num = int(cycle_input)
                return [cycle_num]
            except ValueError:
                raise ValueError(f"Invalid cycle format: {cycle_input}. Use 'discharge X', 'charge X', or a cycle number.")
    
    def plot_single_file(
        self,
        data: FormationCycleData,
        x_col: int,
        y_col: int,
        cycle_input: Optional[str] = None,
        active_mass: Optional[float] = None,
        color: str = 'black'
    ):
        """
        Plot data from a single file.
        
        Args:
            data: FormationCycleData object
            x_col: X-axis column number (1-4)
            y_col: Y-axis column number (1-4)
            cycle_input: Cycle specification ('discharge 3', 'charge 2', '5', 'all', or None)
            active_mass: Active mass for capacity normalization
            color: Line color
        """
        if not self.fig:
            self.create_figure()
        
        # Map column numbers to column names
        col_names = {1: 'time', 2: 'potential', 3: 'capacity', 4: 'current'}
        x_col_name = col_names[x_col]
        y_col_name = col_names[y_col]
        
        cycles = data.get_cycles()
        
        # Parse cycle input to determine which cycles to plot
        cycle_indices = self._parse_cycle_input(cycle_input, data)
        
        if cycle_indices is None:
            # Plot all cycles
            cycle_range_list = list(range(len(cycles)))
        else:
            # Plot specified cycles (convert to 0-indexed)
            cycle_range_list = [idx - 1 for idx in cycle_indices if 1 <= idx <= len(cycles)]
        
        for cycle_idx in cycle_range_list:
            start_idx, end_idx = cycles[cycle_idx]
            x_data = data.get_column_data(x_col_name, (start_idx, end_idx))
            y_data = data.get_column_data(y_col_name, (start_idx, end_idx))
            
            # Process x-axis
            if x_col == 1:  # Time to hours
                x_data = x_data / 3600
            elif x_col == 3 and active_mass:  # Normalize capacity by mass
                x_data = x_data / active_mass
            
            label = data.filename if cycle_idx == cycle_range_list[0] else ""
            self.ax.plot(x_data, y_data, color=color, label=label)
    
    def plot_multi_file(
        self,
        data_list: List[FormationCycleData],
        x_col: int,
        y_col: int,
        cycle_input: Optional[str] = None,
        active_mass: Optional[float] = None,
        colormap: str = 'viridis'
    ):
        """
        Plot data from multiple files with color gradient.
        
        Args:
            data_list: List of FormationCycleData objects
            x_col: X-axis column number (1-4)
            y_col: Y-axis column number (1-4)
            cycle_input: Cycle specification ('discharge 3', 'charge 2', '5', 'all', or None)
            active_mass: Active mass for capacity normalization
            colormap: Matplotlib colormap name
        """
        if not self.fig:
            self.create_figure()
        
        # Map column numbers to column names
        col_names = {1: 'time', 2: 'potential', 3: 'capacity', 4: 'current'}
        x_col_name = col_names[x_col]
        y_col_name = col_names[y_col]
        
        colors = plt.cm.get_cmap(colormap)(np.linspace(0, 1, len(data_list)))
        
        for file_idx, data in enumerate(data_list):
            cycles = data.get_cycles()
            
            # Parse cycle input to determine which cycles to plot
            cycle_indices = self._parse_cycle_input(cycle_input, data)
            
            if cycle_indices is None:
                # Plot all cycles
                cycle_range_list = list(range(len(cycles)))
            else:
                # Plot specified cycles (convert to 0-indexed)
                cycle_range_list = [idx - 1 for idx in cycle_indices if 1 <= idx <= len(cycles)]
            
            for cycle_count, cycle_idx in enumerate(cycle_range_list):
                start_idx, end_idx = cycles[cycle_idx]
                x_data = data.get_column_data(x_col_name, (start_idx, end_idx))
                y_data = data.get_column_data(y_col_name, (start_idx, end_idx))
                
                # Process x-axis
                if x_col == 1:  # Time to hours
                    x_data = x_data / 3600
                elif x_col == 3 and active_mass:  # Normalize capacity by mass
                    x_data = x_data / active_mass
                
                label = data.filename if cycle_count == 0 else ""
                self.ax.plot(x_data, y_data, color=colors[file_idx], label=label)
    
    def finalize_plot(
        self,
        x_label: str,
        y_label: str,
        title: str = "Formation Cycle Data",
        save_path: Optional[str] = None
    ):
        """
        Finalize plot formatting and optionally save.
        
        Args:
            x_label: X-axis label
            y_label: Y-axis label
            title: Plot title
            save_path: Optional path to save plot
        """
        self.ax.set_xlabel(x_label, fontsize=10)
        self.ax.set_ylabel(y_label, fontsize=10)
        self.fig.suptitle(title, fontsize=12, y=0.995)
        self.ax.legend(fontsize=9, frameon=False, loc='best')
        self.ax.grid(True, alpha=0.3)
        
        plt.tight_layout(rect=[0, 0, 1, 0.99])
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Plot saved to: {save_path}")
    
    def show(self):
        """Display the plot."""
        plt.show()
    
    def close(self):
        """Close the figure."""
        if self.fig:
            plt.close(self.fig)
            self.fig = None
            self.ax = None
