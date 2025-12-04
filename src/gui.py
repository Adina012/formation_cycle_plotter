"""GUI module for formation cycle plotter application."""

import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from data_loader import FormationCycleData
from plotter import FormationCyclePlotter
import os


class FormationCycleGUI:
    """Main GUI application for formation cycle plotting."""
    
    def __init__(self, root):
        """Initialize the GUI application."""
        self.root = root
        self.root.title("Formation Cycle Plotter")
        self.root.geometry("500x600")
        
        # Set light purple background color
        light_purple = "#E6D7F0"
        self.root.configure(bg=light_purple)
        
        self.selected_files = []
        self.plotter = FormationCyclePlotter()
        
        self._create_widgets()
    
    def _create_widgets(self):
        """Create and layout GUI widgets."""
        light_purple = "#E6D7F0"
        
        # Title
        title_label = tk.Label(
            self.root,
            text="Formation Cycle Plotter",
            font=("Arial", 16, "bold"),
            bg=light_purple
        )
        title_label.pack(pady=10)
        
        # Mode selection
        mode_frame = tk.LabelFrame(self.root, text="Mode", padx=10, pady=10, bg=light_purple)
        mode_frame.pack(fill="x", padx=10, pady=5)
        
        self.mode_var = tk.StringVar(value="single")
        tk.Radiobutton(
            mode_frame,
            text="Single Plot",
            variable=self.mode_var,
            value="single",
            command=self._update_ui,
            bg=light_purple
        ).pack(anchor="w")
        tk.Radiobutton(
            mode_frame,
            text="Multi-File Comparison",
            variable=self.mode_var,
            value="multi",
            command=self._update_ui,
            bg=light_purple
        ).pack(anchor="w")
        tk.Radiobutton(
            mode_frame,
            text="Cycle Analysis",
            variable=self.mode_var,
            value="cycles",
            command=self._update_ui,
            bg=light_purple
        ).pack(anchor="w")
        
        # File selection
        file_frame = tk.LabelFrame(self.root, text="File Selection", padx=10, pady=10, bg=light_purple)
        file_frame.pack(fill="x", padx=10, pady=5)
        
        self.file_button = tk.Button(
            file_frame,
            text="Select File(s)",
            command=self._select_files,
            bg="#D8B8E8",
            activebackground="#C99DD8"
        )
        self.file_button.pack(fill="x", pady=5)
        
        self.file_label = tk.Label(file_frame, text="No files selected", wraplength=400, bg=light_purple)
        self.file_label.pack(anchor="w")
        
        # Axis selection
        axis_frame = tk.LabelFrame(self.root, text="Axis Selection", padx=10, pady=10, bg=light_purple)
        axis_frame.pack(fill="x", padx=10, pady=5)
        
        tk.Label(axis_frame, text="X-Axis:", bg=light_purple).pack(anchor="w")
        self.x_axis_var = tk.IntVar(value=1)
        x_options = {"Time (s)": 1, "Potential (V)": 2, "Capacity (mAh)": 3, "Current (mA)": 4}
        for text, value in x_options.items():
            tk.Radiobutton(
                axis_frame,
                text=text,
                variable=self.x_axis_var,
                value=value,
                bg=light_purple
            ).pack(anchor="w")
        
        tk.Label(axis_frame, text="Y-Axis:", bg=light_purple).pack(anchor="w", pady=(10, 0))
        self.y_axis_var = tk.IntVar(value=2)
        for text, value in x_options.items():
            tk.Radiobutton(
                axis_frame,
                text=text,
                variable=self.y_axis_var,
                value=value,
                bg=light_purple
            ).pack(anchor="w")
        
        # Options
        options_frame = tk.LabelFrame(self.root, text="Options", padx=10, pady=10, bg=light_purple)
        options_frame.pack(fill="x", padx=10, pady=5)
        
        tk.Label(options_frame, text="Active Mass (g):", bg=light_purple).pack(anchor="w")
        self.mass_entry = tk.Entry(options_frame)
        self.mass_entry.pack(fill="x", pady=5)
        
        tk.Label(options_frame, text="Cycle Number (for cycle analysis):", bg=light_purple).pack(anchor="w")
        self.cycle_entry = tk.Entry(options_frame)
        self.cycle_entry.pack(fill="x", pady=5)
        
        cycle_help = tk.Label(
            options_frame,
            text="Examples: 'discharge 3', 'charge 2', '5', 'all', or leave empty",
            font=("Arial", 8),
            fg="#7D5F91",
            bg=light_purple
        )
        cycle_help.pack(anchor="w")
        self.colormap_var = tk.StringVar(value="viridis")
        colormap_combo = ttk.Combobox(
            options_frame,
            textvariable=self.colormap_var,
            values=["viridis", "plasma", "inferno", "cool", "tab10"],
            state="readonly"
        )
        colormap_combo.pack(fill="x", pady=5)
        
        # Plot button
        self.plot_button = tk.Button(
            self.root,
            text="Generate Plot",
            command=self._generate_plot,
            bg="#B38FD4",
            fg="white",
            font=("Arial", 12, "bold"),
            activebackground="#9B70C1"
        )
        self.plot_button.pack(fill="x", padx=10, pady=10)
        
        # Tagline at bottom
        tagline_label = tk.Label(
            self.root,
            text="plot",
            font=("Arial", 9, "italic"),
            fg="#6B4C7A",
            bg=light_purple
        )
        tagline_label.pack(side="bottom", pady=5)
    
    def _update_ui(self):
        """Update UI based on selected mode."""
        pass
    
    def _select_files(self):
        """Open file dialog for file selection."""
        mode = self.mode_var.get()
        if mode == "single":
            files = filedialog.askopenfilenames(
                title="Select one file",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
            )
            if files:
                self.selected_files = list(files)[:1]  # Only one file
        else:
            files = filedialog.askopenfilenames(
                title="Select files",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
            )
            self.selected_files = list(files)
        
        if self.selected_files:
            file_str = ", ".join([os.path.basename(f) for f in self.selected_files])
            self.file_label.config(text=f"Selected: {file_str}")
            
            # Try to detect columns and show mapping
            try:
                data = FormationCycleData(self.selected_files[0])
                # Apply trimming and normalization BEFORE cycle detection
                data.trim_to_first_cycle()
                data.normalize_time()
                
                col_map = data.get_available_columns()
                mapping_str = "Detected columns: " + ", ".join([f"{orig}→{mapped}" for orig, mapped in col_map.items()])
                
                # Also show cycle information
                discharge_cycles, charge_cycles = data.get_discharge_charge_cycles()
                cycle_info = f"\nCycles: {len(discharge_cycles)} discharge, {len(charge_cycles)} charge ({len(discharge_cycles) + len(charge_cycles)} total)"
                
                self.file_label.config(text=f"Selected: {file_str}\n{mapping_str}{cycle_info}")
            except Exception as e:
                self.file_label.config(text=f"Selected: {file_str}\nWarning: {str(e)}")
    
    def _generate_plot(self):
        """Generate and display the plot."""
        if not self.selected_files:
            messagebox.showerror("Error", "Please select file(s)")
            return
        
        try:
            # Load data
            data_list = []
            for file_path in self.selected_files:
                data = FormationCycleData(file_path)
                data.trim_to_first_cycle()
                data.normalize_time()
                data_list.append(data)
            
            # Get options
            x_col = self.x_axis_var.get()
            y_col = self.y_axis_var.get()
            active_mass = None
            if self.mass_entry.get():
                active_mass = float(self.mass_entry.get())
            
            cycle_input = None
            if self.cycle_entry.get():
                cycle_input = self.cycle_entry.get().strip()
            
            # Create plot
            self.plotter.create_figure()
            mode = self.mode_var.get()
            
            if mode == "single":
                self.plotter.plot_single_file(
                    data_list[0],
                    x_col,
                    y_col,
                    cycle_input=cycle_input,
                    active_mass=active_mass
                )
            else:
                colormap = self.colormap_var.get()
                self.plotter.plot_multi_file(
                    data_list,
                    x_col,
                    y_col,
                    cycle_input=cycle_input,
                    active_mass=active_mass,
                    colormap=colormap
                )
            
            # Finalize
            x_label = self._get_column_label(x_col)
            y_label = self._get_column_label(y_col)
            self.plotter.finalize_plot(x_label, y_label)
            self.plotter.show()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error generating plot:\n{str(e)}")
    
    @staticmethod
    def _get_column_label(col_num: int) -> str:
        """Get label for column number."""
        labels = {1: "Time (h)", 2: "Potential (V)", 3: "Capacity (mAh/g)", 4: "Current (mA)"}
        return labels.get(col_num, "")


def main():
    """Run the GUI application."""
    root = tk.Tk()
    app = FormationCycleGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
