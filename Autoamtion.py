"""
Automation functions for well analysis
"""
import pandas as pd
import time
from Button_Repository2 import Button_Repository, Cerbers_functions


def run_automation_for_inputs(input_rows, gui=None):
    """
    Run automation for multiple input rows.
    
    Args:
        input_rows: List of dicts with keys: Density_value, RIH_wob_value, POOH_wob_value, WHP_value
        gui: Optional GUI reference to check for stop flag and update runtime
    
    Returns:
        Combined DataFrame with all results
    """
    # Start timer for entire automation
    automation_start = time.perf_counter()
    
    # Initialize automation objects once - share the same Button_Repository instance
    br = Button_Repository()
    cf = Cerbers_functions(br)  # Pass br to Cerbers_functions instead of creating new one
    
    all_results = []
    previous_density = None  # Track previous density to skip if unchanged
    
    total_rows = len(input_rows)
    
    # Process each row
    for idx, row in enumerate(input_rows, 1):
        # Check if user pressed ESC to stop
        if gui and gui.stop_automation:
            break
        
        # Update progress and runtime in GUI
        if gui:
            gui.update_progress(idx, total_rows)
            gui.update_runtime()
        
        # Only change density if it's different from previous row
        current_density = row['Density_value']
        if current_density != previous_density:
            cf.New_Fluid_Density(current_density)
            previous_density = current_density
        
        br.Input_WOB_RIH_POOH_WHP(row['RIH_wob_value'], row['POOH_wob_value'], row['WHP_value'])
        
        br.Trip_in_Out_Buttons()  
        br.Drop_Down_Streatcher()
        br.Modeled_Data_Button()
        
        # Get results
        df = br.Modeled_Data_df()
        
        if df is not None:
            # Add input parameters to the result dataframe
            df.insert(0, 'FOE-Pipe Fluid Density', row['Density_value'])
            df.insert(1, 'FOE-RIH', row['RIH_wob_value'])
            df.insert(2, 'FOE-POOH', row['POOH_wob_value'])
            
            # Reorder columns to match desired output
            # Expected columns from Modeled_Data_df: Tubing Depth, RIH Stretch, POOH Stretch (or similar)
            # Rename columns to match FOE- naming convention
            column_mapping = {}
            for col in df.columns:
                if 'Depth' in col or 'depth' in col.lower():
                    column_mapping[col] = 'FOE-Depth'
                elif 'RIH' in col and ('Stretch' in col or 'stretch' in col.lower()):
                    column_mapping[col] = 'FOE-RIH_Streatch'
                elif 'POOH' in col and ('Stretch' in col or 'stretch' in col.lower()):
                    column_mapping[col] = 'FOE-POOH_Streatch'
            
            df.rename(columns=column_mapping, inplace=True)
            
            # Reorder columns: FOE-Depth, FOE-Pipe Fluid Density, FOE-RIH, FOE-POOH, FOE-RIH_Streatch, FOE-POOH_Streatch
            desired_order = ['FOE-Depth', 'FOE-Pipe Fluid Density', 'FOE-RIH', 'FOE-POOH', 'FOE-RIH_Streatch', 'FOE-POOH_Streatch']
            # Only include columns that exist
            df = df[[col for col in desired_order if col in df.columns]]
            
            all_results.append(df)
        
        # Click OK buttons
        br.OK_Button()
        br.OK_Button()
        
        # Update runtime in GUI
        if gui:
            gui.update_runtime()
    
    if all_results:
        return pd.concat(all_results, ignore_index=True)
    else:
        return None


# Example usage
if __name__ == "__main__":
    # Example input data
    inputs = [
        {'Density_value': 8, 'RIH_wob_value': -1500, 'POOH_wob_value': 1350, 'WHP_value': 0},
        {'Density_value': 8, 'RIH_wob_value': -10000, 'POOH_wob_value': 0, 'WHP_value': 0}
    ]
    
    result_df = run_automation_for_inputs(inputs)
    if result_df is not None:
        print("\nFinal Results:")
        print(result_df)






