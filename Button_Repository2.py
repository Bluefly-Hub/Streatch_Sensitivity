from pywinauto import Application, timings
from pywinauto.findwindows import ElementNotFoundError
from pywinauto.controls.uiawrapper import UIAWrapper
from pywinauto.uia_element_info import UIAElementInfo
from pywinauto.uia_defines import IUIA
from pywinauto.uia_defines import get_elem_interface
import time
import comtypes.client
from comtypes.gen.UIAutomationClient import IUIAutomation, TreeScope_Descendants


def timer(func):
    """Decorator to time function execution"""
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        end = time.perf_counter()
        print(f"{func.__name__}: {(end - start):.3f}s")
        return result
    return wrapper

def find_element_fast(root_element, automation_id, found_index=0):
    """
    Fast element search using direct UIA API
    10x faster than pywinauto's window() search
    """
    uia = comtypes.client.GetModule('UIAutomationCore.dll')
    iuia = comtypes.client.CreateObject('{ff48dba4-60ef-4201-aa87-54103eef594e}', interface=IUIAutomation)
    
    condition = iuia.CreatePropertyCondition(30011, automation_id)  # AutomationId
    
    if found_index == 0:
        # Just find first
        element = root_element.FindFirst(TreeScope_Descendants, condition)
        return UIAWrapper(UIAElementInfo(element)) if element else None
    else:
        # Find all and return specific index
        elements_array = root_element.FindAll(TreeScope_Descendants, condition)
        if found_index < elements_array.Length:
            element = elements_array.GetElement(found_index)
            return UIAWrapper(UIAElementInfo(element))
        return None

def find_element_by_title(root_element, title):
    """Fast search by title/name"""
    uia = comtypes.client.GetModule('UIAutomationCore.dll')
    iuia = comtypes.client.CreateObject('{ff48dba4-60ef-4201-aa87-54103eef594e}', interface=IUIAutomation)
    
    condition = iuia.CreatePropertyCondition(30005, title)  # Name property
    element = root_element.FindFirst(TreeScope_Descendants, condition)
    return UIAWrapper(UIAElementInfo(element)) if element else None

class Button_Repository:
    
    def __init__(self):
        # Connect once and reuse the app connection
        self.app = Application(backend="uia").connect(auto_id="frmOrpheus")
        # Get root element for fast searches
        self.root = self.app.top_window().element_info.element

    @timer
    def Window_Orpheus_Main(self):
        # Use FAST direct UIA search
        Fluids_Expand = find_element_fast(self.root, "btnFluids0")
        self.Fluids_Expand = Fluids_Expand
        
        self.Fluids_Expand_click = lambda: (Fluids_Expand.set_focus(), Fluids_Expand.click_input())

    @timer
    def Window_Fluids_Distribution(self):
        # Fast UIA searches
        StringFluidEditor_RIH = find_element_fast(self.root, "cmdStringFluidEditor")
        self.StringFluidEditor_RIH = StringFluidEditor_RIH

        self.StringFluidEditor_RIH_click = lambda: (StringFluidEditor_RIH.set_focus(), StringFluidEditor_RIH.click_input())

        # Find frmFluids window first (fast), then search within it
        frmFluids = find_element_fast(self.root, "frmFluids", found_index=0)
        frmFluids_element = frmFluids.element_info.element
        
        # Search for TabControl within frmFluids
        TabControl = find_element_fast(frmFluids_element, "TabControl1")
        TabControl_element = TabControl.element_info.element
        
        # Search for POOH tab within TabControl
        POOH_Tab = find_element_by_title(TabControl_element, "POOH")
        self.POOH_Tab = POOH_Tab
        self.POOH_Tab_click = lambda: (POOH_Tab.set_focus(), POOH_Tab.click_input())

        # Search for OK button within frmFluids
        Fluids_OK = find_element_by_title(frmFluids_element, "OK")
        self.Fluids_OK = Fluids_OK
        self.Fluids_OK_click = Fluids_OK.click

    @timer
    def StringFluidEditor_POOH(self):
        # Fast UIA search
        StringFluidEditor_POOH_element = find_element_fast(self.root, "cmdStringFluidEditor2")
        self.StringFluidEditor_POOH_element = StringFluidEditor_POOH_element  # Renamed to avoid shadowing method
        self.StringFluidEditor_POOH_click = lambda: (StringFluidEditor_POOH_element.set_focus(), StringFluidEditor_POOH_element.click_input())

    @timer
    def Window_Fluid_Editor(self, force_refresh=False):
        # Fast UIA searches
        Edit_Density = find_element_fast(self.root, "txtDensity")
        
        # Find the second frmFluids window (editor window)
        frmFluids_editor = find_element_fast(self.root, "frmFluids", found_index=1)
        frmFluids_editor_element = frmFluids_editor.element_info.element
        
        # Find toolbar within the editor window
        ToolStrip = find_element_fast(frmFluids_editor_element, "ToolStrip1")
        ToolStrip_element = ToolStrip.element_info.element
        
        # Find Save and Exit buttons within toolbar
        Save_fluid = find_element_by_title(ToolStrip_element, "Save")
        Exit_fluid = find_element_by_title(ToolStrip_element, "Exit")

        # Store the UI elements in self (without executing actions)
        self.Edit_Density = Edit_Density
        self.Save_fluid_element = Save_fluid
        self.Exit_fluid_element = Exit_fluid
        
        # Store callable methods with the action already bound
        self.Edit_Density_set_text = Edit_Density.set_text
        self.Save_fluid = Save_fluid.click  # Now repo.Save_fluid() will call .click()
        self.Exit_fluid = Exit_fluid.click  # Now repo.Exit_fluid() will call .click()

    def Input_WOB_RIH_POOH_WHP(self, RIH_wob_value, POOH_wob_value, WHP_value):
        """Set WOB and ROP values in the ROH tab"""
        # Fast UIA searches - find the panes first
        WOB_RIH_Pane = find_element_fast(self.root, "txtAxialForceOnEndRIH")
        WOB_POOH_Pane = find_element_fast(self.root, "txtAxialForceOnEndPOOH")
        WHP_POOH = find_element_fast(self.root, "txtWellheadPressurePOOH")
        WHP_RIH = find_element_fast(self.root, "txtWellheadPressureRIH")
        
        # Then find txtData within each pane
        WOB_RIH = find_element_fast(WOB_RIH_Pane.element_info.element, "txtData")
        WOB_POOH = find_element_fast(WOB_POOH_Pane.element_info.element, "txtData")
        WHP_POOH = find_element_fast(WHP_POOH.element_info.element, "txtData")
        WHP_RIH = find_element_fast(WHP_RIH.element_info.element, "txtData")

        # Set values
        WOB_RIH.set_text(str(RIH_wob_value))
        WOB_POOH.set_text(str(POOH_wob_value))
        WHP_POOH.set_text(str(WHP_value))
        WHP_RIH.set_text(str(WHP_value))

    def Trip_in_Out_Buttons(self):
        """Find and return Trip In and Trip Out button"""
        # Refresh root in case UI state changed
        self.root = self.app.top_window().element_info.element

        

        
        Trip_In_Out = find_element_fast(self.root, "btnTripInAndOut")
        if Trip_In_Out is None:
            raise Exception("Could not find btnTripInAndOut - UI may not be in correct state")
        
        self.Trip_In_Out = Trip_In_Out

        Trip_In_Out.set_focus()
        Trip_In_Out.click_input()




        # Wait for frmOrpheusGraph window to appear
        time.sleep(0.5)  # Short delay for window to start appearing
        max_wait = 10  # Maximum seconds to wait
        start_time = time.time()
        while time.time() - start_time < max_wait:
            graph_window = find_element_fast(self.root, "frmOrpheusGraph")

            Error_Window= find_element_fast(self.root, "CTESMessageBox")
            if Error_Window is not None:
                Error_Window= find_element_fast(self.root, "CTESMessageBox")
                self.Bypass_Hydraulic_Error()
            if graph_window is not None:
                break
            time.sleep(0.2)


    def Drop_Down_Streatcher(self):
        """Find and click the Drop Down Stretcher button"""
        # Wait for frmOrpheusGraph to be ready
        max_wait = 10
        start_time = time.time()
        graph_window = None
        while time.time() - start_time < max_wait:
            self.root = self.app.top_window().element_info.element
            graph_window = find_element_fast(self.root, "frmOrpheusGraph")
            if graph_window is not None:
                break
            time.sleep(0.2)
        
        if graph_window is None:
            raise Exception("frmOrpheusGraph window not ready for dropdown")
        
        Drop_Down_Stretcher = find_element_fast(self.root, "cmbGraphType")
        if Drop_Down_Stretcher is None:
            raise Exception("Could not find cmbGraphType dropdown - UI may not be in correct state")
        
        self.Drop_Down_Stretcher = Drop_Down_Stretcher
        
        # Try select, but catch errors if it works visually but throws exception
        try:
            Drop_Down_Stretcher.select(2)
        except Exception as e:
            # If select worked but threw an error, just warn and continue
            print(f"Warning: Dropdown select had issue but may have succeeded: {e}")

    def Modeled_Data_Button(self):
        """Find and click the Modeled Data button"""
        # Refresh root in case UI state changed
        self.root = self.app.top_window().element_info.element
        
        menu = find_element_fast(self.root, "menuOrpheusGraph")
        if menu is None:
            raise Exception("Could not find menuOrpheusGraph - UI may not be in correct state")
        
        menu_element = menu.element_info.element

        data = find_element_by_title(self.root, "Data")  # Fixed: use self.root, not menu.root
        Modeled_Data = find_element_by_title(menu_element, "Modeled Data...")

        if data is None or Modeled_Data is None:
            raise Exception("Could not find Data or Modeled Data menu items")

        self.data = data
        self.Modeled_Data = Modeled_Data

        data.set_focus()
        data.click_input()
        Modeled_Data.click_input() 

    def Modeled_Data_df(self):
        """Extract grid data and return as pandas DataFrame"""
        import pandas as pd
        
        # Refresh root to ensure we have current window
        self.root = self.app.top_window().element_info.element
        
        # Find the grid element
        menu = find_element_fast(self.root, "frmOrpheusGraph")
        menu_element = menu.element_info.element
        grid = find_element_fast(menu_element, "grdData")
        self.grid = grid
        
        # Get all text from the grid
        grid_text = grid.texts()
        
        # Try to get rows - grid might have children that are rows

        # Access grid's children (rows)
        rows = grid.children()
        data = []
        headers = []
        
        for i, row in enumerate(rows):
            row_data = []
            cells = row.children()  # Get cells in the row
            for cell in cells:
                # Try to get actual value instead of title
                try:
                    # Try Value pattern first
                    if hasattr(cell, 'iface_value') and cell.iface_value:
                        cell_text = cell.get_value()
                    else:
                        # Fall back to legacy value
                        cell_text = cell.legacy_properties().get('Value', cell.window_text())
                except:
                    # Last resort - use window text
                    cell_text = cell.window_text()
                row_data.append(cell_text)
            
            # Check if this row looks like a header (contains text like "Tubing Depth" or has \r in it)
            is_header = any('Tubing Depth' in str(cell) or 'Stretch' in str(cell) or '\r(' in str(cell) for cell in row_data)
            
            if is_header:
                headers = row_data  # This is a header row
                # Don't add it to data
            else:
                # Only add non-header rows to data
                if headers:  # Only add data if we've found headers
                    data.append(row_data)
        
        # If no headers detected, use first row as headers
        if not headers and data:
            headers = data[0]
            data = data[1:]
        
        # Create DataFrame and drop first column (the first column after dropping the row number)
        df = pd.DataFrame(data, columns=headers)
        df = df.iloc[:, 1:]  # Drop first column
        return df
        
    def OK_Button(self):
        """Find and click the OK button"""
        # Wait for frmOrpheusGraph to be ready
        max_wait = 10
        start_time = time.time()
        graph_window = None
        while time.time() - start_time < max_wait:
            self.root = self.app.top_window().element_info.element
            graph_window = find_element_fast(self.root, "frmOrpheusGraph")
            if graph_window is not None:
                break
            time.sleep(0.2)
        
        if graph_window is None:
            raise Exception("frmOrpheusGraph window not ready for OK button")
        
        OK_Button_element = find_element_fast(self.root, "btnOK")
        self.OK_Button_element = OK_Button_element  # Renamed to avoid shadowing the method
        OK_Button_element.click()
        
    def Bypass_Hydraulic_Error(self):
        """Find and click the No button"""
        # Refresh root in case UI state changed
        self.root = self.app.top_window().element_info.element
        No_button_element = find_element_fast(self.root, "btnNo")
        self.No_button_element = No_button_element  
        No_button_element.click()
        time.sleep(0.2)  # Wait a moment for OK button to appear
        Ok_button_element = find_element_fast(self.root, "btnOK")
        self.OK_Button_element = Ok_button_element  
        Ok_button_element.click()

class Cerbers_functions:
    """High-level automation workflows using Button_Repository"""
    
    def __init__(self, button_repo=None):
        # Use provided Button_Repository or create new one
        self.repo = button_repo if button_repo is not None else Button_Repository()
    
    def New_Fluid_Density(self, value):
        """Complete workflow to set new fluid density for both RIH and POOH"""
        self.repo.Window_Orpheus_Main()
        self.repo.Fluids_Expand_click()
        self.repo.Window_Fluids_Distribution()
        self.repo.StringFluidEditor_RIH_click()
        self.repo.Window_Fluid_Editor()
        self.repo.Edit_Density_set_text(value)
        self.repo.Save_fluid()
        self.repo.Exit_fluid()
        self.repo.POOH_Tab_click()
        self.repo.StringFluidEditor_POOH()
        self.repo.StringFluidEditor_POOH_click()
        self.repo.Window_Fluid_Editor(force_refresh=True)
        self.repo.Exit_fluid()
        self.repo.Fluids_OK_click()

if __name__ == "__main__":
    #cf = Cerbers_functions()
    #cf.New_Fluid_Density("8")
    br= Button_Repository()
    #br.Input_WOB_RIH_POOH_WHP(1600, 5000, 1000)
    #br.Trip_in_Out_Buttons()  
    #br.Drop_Down_Streatcher()  # Added () to actually call the method
    #br.Modeled_Data_Button()
    #df = br.Modeled_Data_df()
    #print(df)
    br.OK_Button()


    #Test=br.Test_Button(br.Trip_in_Out_Buttons())


 



