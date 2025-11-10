import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import pandas as pd
import time
import threading
import ctypes
from Automation import run_automation_for_inputs

class AutomationGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Cerberus Streatch Sensitivity Automation")
        self.root.geometry("1000x700")
        
        # Data storage
        self.input_rows = []
        self.output_df = None
        self.stop_automation = False
        self.automation_start_time = None
        self.keyboard_listener_active = False
        
        # Bind ESC key to stop automation
        self.root.bind('<Escape>', self.stop_automation_handler)
        
        # Start keyboard monitoring thread
        self.start_keyboard_monitor()
        
        # Create main frames
        self.create_input_frame()
        self.create_control_frame()
        self.create_output_frame()
    
    def start_keyboard_monitor(self):
        """Start a background thread to monitor ESC key using Windows API"""
        def monitor_keyboard():
            # Windows Virtual Key code for ESC
            VK_ESCAPE = 0x1B
            
            while True:
                if self.keyboard_listener_active:
                    try:
                        # GetAsyncKeyState returns the state of a key
                        # High bit (0x8000) indicates key is currently pressed
                        if ctypes.windll.user32.GetAsyncKeyState(VK_ESCAPE) & 0x8000:
                            if not self.stop_automation:  # Only trigger once
                                self.stop_automation = True
                                self.root.after(0, lambda: self.status_label.configure(
                                    text="Stopping automation...", foreground="red"))
                            time.sleep(0.5)  # Debounce to avoid multiple triggers
                    except:
                        pass
                time.sleep(0.1)
        
        # Start the monitoring thread as daemon so it exits when app closes
        monitor_thread = threading.Thread(target=monitor_keyboard, daemon=True)
        monitor_thread.start()
        
    def create_input_frame(self):
        """Create the input data entry frame"""
        input_frame = ttk.LabelFrame(self.root, text="Input Parameters", padding=10)
        input_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Create treeview for input data
        columns = ("Density of Pipe Fluid PPG", "RIH-WOB", "POOH_WOB", "Wellhead Pressure")
        self.input_tree = ttk.Treeview(input_frame, columns=columns, show="headings", height=8)
        
        # Define column headings
        for col in columns:
            self.input_tree.heading(col, text=col)
            self.input_tree.column(col, width=200, anchor=tk.CENTER)
        
        # Scrollbar for input tree
        input_scroll = ttk.Scrollbar(input_frame, orient=tk.VERTICAL, command=self.input_tree.yview)
        self.input_tree.configure(yscrollcommand=input_scroll.set)
        
        self.input_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        input_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Button frame below the input tree
        button_frame = ttk.Frame(self.root, padding=5)
        button_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(button_frame, text="Remove Selected", command=self.remove_row).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Clear All", command=self.clear_all).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Paste from Clipboard", command=self.paste_from_clipboard).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Load Sample Data", command=self.load_sample_data).pack(side=tk.LEFT, padx=5)
        
    def create_control_frame(self):
        """Create control buttons frame"""
        control_frame = ttk.Frame(self.root, padding=10)
        control_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.run_button = ttk.Button(control_frame, text="Run Automation", command=self.run_automation, style="Accent.TButton")
        self.run_button.pack(side=tk.LEFT, padx=5)
        
        self.stop_button = ttk.Button(control_frame, text="Stop (ESC)", command=self.stop_automation_handler, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=5)
        
        self.status_label = ttk.Label(control_frame, text="Ready", foreground="green")
        self.status_label.pack(side=tk.LEFT, padx=20)
        
        self.progress_label = ttk.Label(control_frame, text="", foreground="blue")
        self.progress_label.pack(side=tk.LEFT, padx=10)
        
        self.runtime_label = ttk.Label(control_frame, text="Runtime: 0:00", foreground="blue")
        self.runtime_label.pack(side=tk.LEFT, padx=10)
        
        ttk.Button(control_frame, text="Copy Results to Clipboard", command=self.copy_results).pack(side=tk.RIGHT, padx=5)
        ttk.Button(control_frame, text="Export to CSV", command=self.export_csv).pack(side=tk.RIGHT, padx=5)
        
    def create_output_frame(self):
        """Create output results frame"""
        output_frame = ttk.LabelFrame(self.root, text="Output Results", padding=10)
        output_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Text widget for displaying results
        self.output_text = scrolledtext.ScrolledText(output_frame, wrap=tk.NONE, height=15)
        self.output_text.pack(fill=tk.BOTH, expand=True)
        
        # Horizontal scrollbar
        h_scroll = ttk.Scrollbar(output_frame, orient=tk.HORIZONTAL, command=self.output_text.xview)
        self.output_text.configure(xscrollcommand=h_scroll.set)
        h_scroll.pack(fill=tk.X)
    
    def remove_row(self):
        """Remove selected row from input table"""
        selected = self.input_tree.selection()
        if selected:
            self.input_tree.delete(selected)
        else:
            messagebox.showwarning("No Selection", "Please select a row to remove.")
    
    def clear_all(self):
        """Clear all input rows"""
        for item in self.input_tree.get_children():
            self.input_tree.delete(item)
    
    def paste_from_clipboard(self):
        """Paste tab-delimited data from clipboard"""
        try:
            # Get clipboard content
            clipboard_data = self.root.clipboard_get()
            
            # Split by lines
            lines = clipboard_data.strip().split('\n')
            
            rows_added = 0
            for line in lines:
                # Skip empty lines
                if not line.strip():
                    continue
                
                # Split by tab or multiple spaces
                parts = line.split('\t') if '\t' in line else line.split()
                
                # Skip header row if it contains text
                if any(not part.replace('-', '').replace('.', '').replace(',', '').isdigit() for part in parts[:4]):
                    continue
                
                # Parse the values
                if len(parts) >= 4:
                    try:
                        density = float(parts[0].replace(',', ''))
                        rih_wob = float(parts[1].replace(',', ''))
                        pooh_wob = float(parts[2].replace(',', ''))
                        whp = float(parts[3].replace(',', ''))
                        
                        self.input_tree.insert("", tk.END, values=(density, rih_wob, pooh_wob, whp))
                        rows_added += 1
                    except ValueError:
                        continue
            
            # Silently succeed or show warning only if no data found
            if rows_added == 0:
                messagebox.showwarning("No Data", "No valid rows found in clipboard data.")
                
        except tk.TclError:
            messagebox.showerror("Error", "Clipboard is empty or contains invalid data.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to paste data:\n{str(e)}")
                
        except tk.TclError:
            messagebox.showerror("Error", "Clipboard is empty or contains invalid data.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to paste data:\n{str(e)}")
    
    def load_sample_data(self):
        """Load sample data into the table"""
        sample_data = [
            (8, -1500, 1350, 0),
            (8, -10000, 0, 0)
        ]
        
        self.clear_all()
        for row in sample_data:
            self.input_tree.insert("", tk.END, values=row)
    
    def stop_automation_handler(self, event=None):
        """Handle ESC key press to stop automation"""
        self.stop_automation = True
        self.status_label.configure(text="Stopping automation...", foreground="red")
    
    def update_runtime(self):
        """Update the runtime label"""
        if self.automation_start_time:
            elapsed = time.time() - self.automation_start_time
            minutes = int(elapsed // 60)
            seconds = int(elapsed % 60)
            self.runtime_label.configure(text=f"Runtime: {minutes}:{seconds:02d}")
            self.root.update()
    
    def update_progress(self, current, total):
        """Update the progress label"""
        self.progress_label.configure(text=f"Row: {current}/{total}")
        self.root.update()
    
    def run_automation(self):
        """Run the automation for all input rows"""
        # Get all rows from input table
        rows = []
        for item in self.input_tree.get_children():
            values = self.input_tree.item(item)['values']
            rows.append({
                'Density_value': float(values[0]),
                'RIH_wob_value': float(values[1]),
                'POOH_wob_value': float(values[2]),
                'WHP_value': float(values[3])
            })
        
        if not rows:
            messagebox.showwarning("No Data", "Please add at least one row of input data.")
            return
        
        # Reset stop flag and start timer
        self.stop_automation = False
        self.automation_start_time = time.time()
        self.keyboard_listener_active = True  # Enable keyboard monitoring
        
        # Disable run button, enable stop button
        self.run_button.configure(state=tk.DISABLED)
        self.stop_button.configure(state=tk.NORMAL)
        self.status_label.configure(text="Running automation... (Press ESC to stop)", foreground="orange")
        self.progress_label.configure(text="")
        self.update_runtime()
        
        try:
            # Call the automation function from Autoamtion.py
            self.output_df = run_automation_for_inputs(rows, self)
            
            # Final runtime update
            self.update_runtime()
            
            if self.stop_automation:
                self.status_label.configure(text="Automation stopped by user", foreground="red")
            elif self.output_df is not None:
                # Display results
                self.output_text.delete(1.0, tk.END)
                self.output_text.insert(tk.END, self.output_df.to_string(index=False))
                
                elapsed = time.time() - self.automation_start_time
                minutes = int(elapsed // 60)
                seconds = int(elapsed % 60)
                self.status_label.configure(text=f"Completed! Processed {len(rows)} rows in {minutes}:{seconds:02d}", foreground="green")
            else:
                messagebox.showerror("Error", "No results were generated.")
                self.status_label.configure(text="Failed - No results", foreground="red")
                
        except Exception as e:
            messagebox.showerror("Automation Error", f"An error occurred:\n{str(e)}")
            self.status_label.configure(text="Failed - See error", foreground="red")
        
        finally:
            # Re-enable run button, disable stop button, reset timer
            self.keyboard_listener_active = False  # Disable keyboard monitoring
            self.run_button.configure(state=tk.NORMAL)
            self.stop_button.configure(state=tk.DISABLED)
            self.automation_start_time = None
    
    def copy_results(self):
        """Copy results to clipboard in CSV format (comma-delimited for Excel)"""
        if self.output_df is not None:
            self.root.clipboard_clear()
            # Use to_csv with tab=False to get comma-delimited format
            csv_string = self.output_df.to_csv(index=False)
            self.root.clipboard_append(csv_string)
            # Silent on success - no popup
        else:
            messagebox.showwarning("No Results", "Please run the automation first.")
    
    def export_csv(self):
        """Export results to CSV file"""
        if self.output_df is not None:
            from tkinter import filedialog
            filename = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
            )
            if filename:
                self.output_df.to_csv(filename, index=False)
                messagebox.showinfo("Success", f"Results exported to {filename}")
        else:
            messagebox.showwarning("No Results", "Please run the automation first.")


if __name__ == "__main__":
    root = tk.Tk()
    app = AutomationGUI(root)
    root.mainloop()
