"""Data loading and processing module for formation cycle data."""

import pandas as pd
import numpy as np
from typing import Tuple, List
import os


class FormationCycleData:
    """Handle loading and processing of formation cycle data files."""
    
    COLUMN_NAMES = ["Cycle Number", "Time (s)", "Potential (V)", "Capacity (mAh)", "Current (mA)"]
    
    def __init__(self, file_path: str):
        """
        Load and initialize formation cycle data.
        
        Args:
            file_path: Path to the data file (.txt or .csv)
        """
        self.file_path = file_path
        self.filename = os.path.basename(file_path)
        self.df = None
        self.load_file()
    
    def load_file(self):
        """Load data from file with proper delimiter and decimal handling."""
        try:
            self.df = pd.read_csv(
                self.file_path,
                delimiter="\t",
                decimal=",",
                header=None,
                names=self.COLUMN_NAMES
            )
        except Exception as e:
            raise ValueError(f"Error loading {self.filename}: {e}")
    
    def get_cycles(self, threshold: float = 1e-6) -> List[Tuple[int, int]]:
        """
        Detect cycle boundaries based on current sign changes.
        
        Args:
            threshold: Threshold for detecting non-zero current
            
        Returns:
            List of (start_idx, end_idx) tuples for each cycle
        """
        current_col = self.df.iloc[:, 4]  # Current column
        
        # Find first non-zero current
        non_zero_mask = current_col.abs() > threshold
        if not non_zero_mask.any():
            raise ValueError(f"No non-zero current in {self.filename}")
        
        first_nonzero = non_zero_mask.idxmax()
        
        # Detect sign changes
        sign_change_indices = [first_nonzero]
        for i in range(first_nonzero, len(self.df) - 1):
            if np.sign(self.df.iloc[i, 4]) != np.sign(self.df.iloc[i + 1, 4]):
                sign_change_indices.append(i + 1)
        sign_change_indices.append(len(self.df) - 1)
        
        cycles = []
        for i in range(len(sign_change_indices) - 1):
            cycles.append((sign_change_indices[i], sign_change_indices[i + 1]))
        
        return cycles
    
    def trim_to_first_cycle(self):
        """Trim data to start from first non-zero current."""
        current_col = self.df.iloc[:, 4]
        non_zero_mask = current_col.abs() > 1e-6
        if non_zero_mask.any():
            first_nonzero = non_zero_mask.idxmax()
            self.df = self.df.loc[first_nonzero:].reset_index(drop=True)
    
    def normalize_time(self):
        """Shift time so first measurement is at t=0."""
        initial_time = float(self.df.iloc[0, 1])
        self.df.iloc[:, 1] = self.df.iloc[:, 1] - initial_time
    
    def get_cycle_data(self, cycle_num: int) -> Tuple[np.ndarray, np.ndarray, int, int]:
        """
        Extract data for a specific cycle.
        
        Args:
            cycle_num: Cycle number (1-indexed)
            
        Returns:
            Tuple of (x_data, y_data, start_idx, end_idx)
        """
        cycles = self.get_cycles()
        if cycle_num < 1 or cycle_num > len(cycles):
            raise ValueError(f"Invalid cycle number {cycle_num}. Available: 1-{len(cycles)}")
        
        start_idx, end_idx = cycles[cycle_num - 1]
        return start_idx, end_idx
    
    def get_column_data(self, col_num: int, cycle_range: Tuple[int, int] = None) -> np.ndarray:
        """
        Get data from a specific column, optionally for a cycle range.
        
        Args:
            col_num: Column number (0-indexed)
            cycle_range: Optional (start_idx, end_idx) tuple
            
        Returns:
            Numpy array of column data
        """
        if cycle_range:
            start_idx, end_idx = cycle_range
            return self.df.iloc[start_idx:end_idx, col_num].values
        return self.df.iloc[:, col_num].values
