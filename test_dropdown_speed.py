"""
Test script to diagnose and optimize Drop_Down_Streatcher performance
"""
import time
import comtypes.client
from comtypes.gen.UIAutomationClient import IUIAutomation, TreeScope_Descendants
from pywinauto import Application
from pywinauto.controls.uiawrapper import UIAWrapper
from pywinauto.uia_element_info import UIAElementInfo


def find_element_fast(root_element, automation_id, found_index=0):
    """Fast element search using direct UIA API"""
    uia = comtypes.client.GetModule('UIAutomationCore.dll')
    iuia = comtypes.client.CreateObject('{ff48dba4-60ef-4201-aa87-54103eef594e}', interface=IUIAutomation)
    
    condition = iuia.CreatePropertyCondition(30011, automation_id)  # AutomationId
    
    if found_index == 0:
        element = root_element.FindFirst(TreeScope_Descendants, condition)
        return UIAWrapper(UIAElementInfo(element)) if element else None
    else:
        elements_array = root_element.FindAll(TreeScope_Descendants, condition)
        if found_index < elements_array.Length:
            element = elements_array.GetElement(found_index)
            return UIAWrapper(UIAElementInfo(element))
        return None


def test_method_1_original():
    """Original method from Drop_Down_Streatcher"""
    print("\n=== Method 1: Original (with waits and refresh) ===")
    start = time.perf_counter()
    
    app = Application(backend="uia").connect(auto_id="frmOrpheus")
    
    # Wait for frmOrpheusGraph to be ready
    max_wait = 10
    start_time = time.time()
    graph_window = None
    while time.time() - start_time < max_wait:
        root = app.top_window().element_info.element
        graph_window = find_element_fast(root, "frmOrpheusGraph")
        if graph_window is not None:
            break
        time.sleep(0.2)
    
    if graph_window is None:
        print("ERROR: frmOrpheusGraph window not found")
        return
    
    Drop_Down_Stretcher = find_element_fast(root, "cmbGraphType")
    if Drop_Down_Stretcher is None:
        print("ERROR: cmbGraphType dropdown not found")
        return
    
    try:
        Drop_Down_Stretcher.select(2)
        print("✓ Dropdown selected successfully")
    except Exception as e:
        print(f"Warning: {e}")
    
    end = time.perf_counter()
    print(f"Time: {(end - start):.3f}s")


def test_method_2_no_wait():
    """Try without waiting for graph window"""
    print("\n=== Method 2: No wait loop (assume window exists) ===")
    start = time.perf_counter()
    
    app = Application(backend="uia").connect(auto_id="frmOrpheus")
    root = app.top_window().element_info.element
    
    graph_window = find_element_fast(root, "frmOrpheusGraph")
    if graph_window is None:
        print("ERROR: frmOrpheusGraph window not found")
        return
    
    Drop_Down_Stretcher = find_element_fast(root, "cmbGraphType")
    if Drop_Down_Stretcher is None:
        print("ERROR: cmbGraphType dropdown not found")
        return
    
    try:
        Drop_Down_Stretcher.select(2)
        print("✓ Dropdown selected successfully")
    except Exception as e:
        print(f"Warning: {e}")
    
    end = time.perf_counter()
    print(f"Time: {(end - start):.3f}s")


def test_method_3_cached_root():
    """Use cached root element (assume Button_Repository already has it)"""
    print("\n=== Method 3: Using cached root element ===")
    start = time.perf_counter()
    
    # Simulate already having cached root from Button_Repository
    app = Application(backend="uia").connect(auto_id="frmOrpheus")
    root = app.top_window().element_info.element
    
    Drop_Down_Stretcher = find_element_fast(root, "cmbGraphType")
    if Drop_Down_Stretcher is None:
        print("ERROR: cmbGraphType dropdown not found")
        return
    
    try:
        Drop_Down_Stretcher.select(2)
        print("✓ Dropdown selected successfully")
    except Exception as e:
        print(f"Warning: {e}")
    
    end = time.perf_counter()
    print(f"Time: {(end - start):.3f}s")


def test_method_4_expand_collapse():
    """Try expand then collapse instead of select"""
    print("\n=== Method 4: Expand/Collapse pattern ===")
    start = time.perf_counter()
    
    app = Application(backend="uia").connect(auto_id="frmOrpheus")
    root = app.top_window().element_info.element
    
    Drop_Down_Stretcher = find_element_fast(root, "cmbGraphType")
    if Drop_Down_Stretcher is None:
        print("ERROR: cmbGraphType dropdown not found")
        return
    
    try:
        # Try expand/collapse pattern
        if hasattr(Drop_Down_Stretcher, 'expand'):
            Drop_Down_Stretcher.expand()
            time.sleep(0.1)
        
        # Select item 2
        Drop_Down_Stretcher.select(2)
        print("✓ Dropdown selected successfully")
    except Exception as e:
        print(f"Warning: {e}")
    
    end = time.perf_counter()
    print(f"Time: {(end - start):.3f}s")


def test_method_5_direct_invoke():
    """Try direct invoke pattern"""
    print("\n=== Method 5: Direct invoke on list item ===")
    start = time.perf_counter()
    
    app = Application(backend="uia").connect(auto_id="frmOrpheus")
    root = app.top_window().element_info.element
    
    Drop_Down_Stretcher = find_element_fast(root, "cmbGraphType")
    if Drop_Down_Stretcher is None:
        print("ERROR: cmbGraphType dropdown not found")
        return
    
    try:
        # Try to get children (dropdown items)
        children = Drop_Down_Stretcher.children()
        print(f"Found {len(children)} dropdown items")
        
        if len(children) > 2:
            # Directly invoke the 3rd item (index 2)
            children[2].click_input()
            print("✓ Clicked item directly")
        else:
            # Fallback to select
            Drop_Down_Stretcher.select(2)
            print("✓ Used select fallback")
            
    except Exception as e:
        print(f"Error: {e}")
        # Fallback to regular select
        try:
            Drop_Down_Stretcher.select(2)
            print("✓ Fallback select worked")
        except Exception as e2:
            print(f"Fallback failed: {e2}")
    
    end = time.perf_counter()
    print(f"Time: {(end - start):.3f}s")


def test_method_6_keyboard():
    """Try keyboard navigation"""
    print("\n=== Method 6: Keyboard navigation ===")
    start = time.perf_counter()
    
    app = Application(backend="uia").connect(auto_id="frmOrpheus")
    root = app.top_window().element_info.element
    
    Drop_Down_Stretcher = find_element_fast(root, "cmbGraphType")
    if Drop_Down_Stretcher is None:
        print("ERROR: cmbGraphType dropdown not found")
        return
    
    try:
        # Focus the dropdown
        Drop_Down_Stretcher.set_focus()
        time.sleep(0.05)
        
        # Press down arrow twice to select 3rd item
        Drop_Down_Stretcher.type_keys("{DOWN}{DOWN}")
        print("✓ Used keyboard navigation")
        
    except Exception as e:
        print(f"Error: {e}")
    
    end = time.perf_counter()
    print(f"Time: {(end - start):.3f}s")


def analyze_dropdown_properties():
    """Analyze the dropdown to understand its structure"""
    print("\n=== Analyzing Dropdown Properties ===")
    
    app = Application(backend="uia").connect(auto_id="frmOrpheus")
    root = app.top_window().element_info.element
    
    Drop_Down_Stretcher = find_element_fast(root, "cmbGraphType")
    if Drop_Down_Stretcher is None:
        print("ERROR: cmbGraphType dropdown not found")
        return
    
    print(f"Control Type: {Drop_Down_Stretcher.element_info.control_type}")
    print(f"Class Name: {Drop_Down_Stretcher.class_name()}")
    
    # Check available patterns
    print("\nAvailable Patterns:")
    try:
        if hasattr(Drop_Down_Stretcher, 'iface_value'):
            print("  - Value Pattern")
    except:
        pass
    
    try:
        if hasattr(Drop_Down_Stretcher, 'iface_selection'):
            print("  - Selection Pattern")
    except:
        pass
    
    try:
        if hasattr(Drop_Down_Stretcher, 'iface_expand_collapse'):
            print("  - ExpandCollapse Pattern")
    except:
        pass
    
    # Try to get current items
    try:
        texts = Drop_Down_Stretcher.texts()
        print(f"\nDropdown texts: {texts}")
    except Exception as e:
        print(f"Could not get texts: {e}")
    
    try:
        children = Drop_Down_Stretcher.children()
        print(f"Number of children: {len(children)}")
        for i, child in enumerate(children[:5]):  # First 5 only
            print(f"  Child {i}: {child.window_text()}")
    except Exception as e:
        print(f"Could not get children: {e}")


def main():
    """Run all tests"""
    print("=" * 60)
    print("Drop_Down_Streatcher Performance Analysis")
    print("=" * 60)
    
    # First analyze the dropdown
    analyze_dropdown_properties()
    
    # Run all test methods
    print("\n" + "=" * 60)
    print("Running Speed Tests")
    print("=" * 60)
    
    try:
        test_method_1_original()
    except Exception as e:
        print(f"Method 1 failed: {e}")
    
    try:
        test_method_2_no_wait()
    except Exception as e:
        print(f"Method 2 failed: {e}")
    
    try:
        test_method_3_cached_root()
    except Exception as e:
        print(f"Method 3 failed: {e}")
    
    try:
        test_method_4_expand_collapse()
    except Exception as e:
        print(f"Method 4 failed: {e}")
    
    try:
        test_method_5_direct_invoke()
    except Exception as e:
        print(f"Method 5 failed: {e}")
    
    try:
        test_method_6_keyboard()
    except Exception as e:
        print(f"Method 6 failed: {e}")
    
    print("\n" + "=" * 60)
    print("Tests Complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
