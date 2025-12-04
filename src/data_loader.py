"""Data loading and processing module for formation cycle data."""

import pandas as pd
import numpy as np
from typing import Tuple, List, Optional
import os


class FormationCycleData:
    """Handle loading and processing of formation cycle data files."""
    
    # Expected column patterns (case-insensitive)
    COLUMN_PATTERNS = {
        'cycle': ['cycle', 'cycle number'],
        'time': ['time', 'time/s', 'time (s)'],
        'potential': ['ewe', 'potential', 'e/v', 'potential (v)', 'ewe/v'],
        'capacity': ['capacity', 'q charge', 'capacity/ma.h', 'capacity (mah)'],
        'current': ['i', 'current', 'i/ma', 'current (ma)', 'i/mA']
    }
    
    def __init__(self, file_path: str, auto_detect: bool = True):
        """
        Load and initialize formation cycle data.
        
        Args:
            file_path: Path to the data file (.txt or .csv)
            auto_detect: Whether to auto-detect columns
        """
        self.file_path = file_path
        self.filename = os.path.basename(file_path)
        self.df = None
        self.column_mapping = {}
        self.load_file(auto_detect=auto_detect)
    
    def load_file(self, auto_detect: bool = True):
        """Load data from file with proper delimiter and decimal handling."""
        try:
            self.df = pd.read_csv(
                self.file_path,
                delimiter="\t",
                decimal=",",
                header=0
            )
            
            if auto_detect:
                self._auto_detect_columns()
            else:
                self._validate_columns()
                
        except Exception as e:
            raise ValueError(f"Error loading {self.filename}: {e}")
    
    def _auto_detect_columns(self):
        """Auto-detect and map column names to standard names."""
        df_columns = [col.strip().lower() for col in self.df.columns]
        
        for standard_col, patterns in self.COLUMN_PATTERNS.items():
            for i, col in enumerate(df_columns):
                for pattern in patterns:
                    if pattern.lower() in col:
                        self.column_mapping[standard_col] = i
                        break
                if standard_col in self.column_mapping:
                    break
        
        # Validate that we found at least time, potential, capacity, and current
        required = ['time', 'potential', 'capacity', 'current']
        missing = [col for col in required if col not in self.column_mapping]
        
        if missing:
            raise ValueError(
                f"Could not auto-detect columns for: {missing}. "
                f"Available columns: {list(self.df.columns)}"
            )
    
    def _validate_columns(self):
        """Validate that required columns exist."""
        required_cols = ['time', 'potential', 'capacity', 'current']
        for req_col in required_cols:
            if req_col not in self.column_mapping:
                raise ValueError(f"Missing required column: {req_col}")
    
    def _get_col_idx(self, col_name: str) -> int:
        """Get column index by standard name."""
        if col_name not in self.column_mapping:
            raise ValueError(f"Column '{col_name}' not found or not mapped")
        return self.column_mapping[col_name]
    
    def get_cycles(self, threshold: float = 1e-6) -> List[Tuple[int, int]]:
        """
        Detect cycle boundaries based on current sign changes.
        
        Args:
            threshold: Threshold for detecting non-zero current
            
        Returns:
            List of (start_idx, end_idx) tuples for each cycle
        """
        current_idx = self._get_col_idx('current')
        current_col = self.df.iloc[:, current_idx]
        
        # Find first non-zero current
        non_zero_mask = current_col.abs() > threshold
        if not non_zero_mask.any():
            raise ValueError(f"No non-zero current in {self.filename}")
        
        first_nonzero = non_zero_mask.idxmax()
        
        # Detect sign changes
        sign_change_indices = [first_nonzero]
        for i in range(first_nonzero, len(self.df) - 1):
            if np.sign(self.df.iloc[i, current_idx]) != np.sign(self.df.iloc[i + 1, current_idx]):
                sign_change_indices.append(i + 1)
        sign_change_indices.append(len(self.df) - 1)
        
        cycles = []
        for i in range(len(sign_change_indices) - 1):
            cycles.append((sign_change_indices[i], sign_change_indices[i + 1]))
        
        return cycles
    
    def get_discharge_charge_cycles(self, threshold: float = 1e-6) -> Tuple[List[Tuple[int, int]], List[Tuple[int, int]]]:
        """
        Detect and separate discharge and charge cycles.
        
        Args:
            threshold: Threshold for detecting non-zero current
            
        Returns:
            Tuple of (discharge_cycles, charge_cycles), each is a list of (start_idx, end_idx) tuples
        """
        cycles = self.get_cycles(threshold)
        current_idx = self._get_col_idx('current')
        
        discharge_cycles = []
        charge_cycles = []
        
        for start_idx, end_idx in cycles:
            # Determine if discharge (negative) or charge (positive)
            avg_current = self.df.iloc[start_idx:end_idx, current_idx].mean()
            if avg_current < 0:
                discharge_cycles.append((start_idx, end_idx))
            else:
                charge_cycles.append((start_idx, end_idx))
        
        return discharge_cycles, charge_cycles
    
    def trim_to_first_cycle(self):
        """Trim data to start from first non-zero current."""
        current_idx = self._get_col_idx('current')
        current_col = self.df.iloc[:, current_idx]
        non_zero_mask = current_col.abs() > 1e-6
        if non_zero_mask.any():
            first_nonzero = non_zero_mask.idxmax()
            self.df = self.df.loc[first_nonzero:].reset_index(drop=True)
    
    def normalize_time(self):
        """Shift time so first measurement is at t=0."""
        time_idx = self._get_col_idx('time')
        initial_time = float(self.df.iloc[0, time_idx])
        self.df.iloc[:, time_idx] = self.df.iloc[:, time_idx] - initial_time
    
    def get_cycle_data(self, cycle_num: int) -> Tuple[int, int]:
        """
        Extract data for a specific cycle.
        
        Args:
            cycle_num: Cycle number (1-indexed)
            
        Returns:
            Tuple of (start_idx, end_idx)
        """
        cycles = self.get_cycles()
        if cycle_num < 1 or cycle_num > len(cycles):
            raise ValueError(f"Invalid cycle number {cycle_num}. Available: 1-{len(cycles)}")
        
        return cycles[cycle_num - 1]
    
    def get_column_data(self, col_name: str, cycle_range: Tuple[int, int] = None) -> np.ndarray:
        """
        Get data from a specific column by standard name.
        
        Args:
            col_name: Column name ('time', 'potential', 'capacity', 'current')
            cycle_range: Optional (start_idx, end_idx) tuple
            
        Returns:
            Numpy array of column data
        """
        col_idx = self._get_col_idx(col_name)
        if cycle_range:
            start_idx, end_idx = cycle_range
            return self.df.iloc[start_idx:end_idx, col_idx].values
        return self.df.iloc[:, col_idx].values
    
    def get_available_columns(self) -> dict:
        """Get list of detected column mappings."""
        reverse_mapping = {v: k for k, v in self.column_mapping.items()}
        return {self.df.columns[idx]: name for idx, name in reverse_mapping.items()}
