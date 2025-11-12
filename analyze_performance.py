"""
Analyze performance log to track automation speed improvements
"""
import pandas as pd
from pathlib import Path
from datetime import datetime


def analyze_performance_log(log_file="performance_log.csv"):
    """Analyze and display performance statistics"""
    log_path = Path(__file__).parent / log_file
    
    if not log_path.exists():
        print(f"No performance log found at: {log_path}")
        return
    
    # Read the log
    df = pd.read_csv(log_path)
    df['elapsed'] = df['elapsed'].astype(float)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    print("=" * 80)
    print("PERFORMANCE ANALYSIS")
    print("=" * 80)
    
    # Overall statistics
    print(f"\nTotal logged calls: {len(df)}")
    print(f"Date range: {df['timestamp'].min()} to {df['timestamp'].max()}")
    print(f"Functions tracked: {df['function'].nunique()}")
    
    # Statistics by function
    print("\n" + "=" * 80)
    print("STATISTICS BY FUNCTION")
    print("=" * 80)
    
    stats = df.groupby('function')['elapsed'].agg(['count', 'mean', 'min', 'max', 'std'])
    stats = stats.sort_values('mean', ascending=False)
    stats['mean'] = stats['mean'].round(3)
    stats['min'] = stats['min'].round(3)
    stats['max'] = stats['max'].round(3)
    stats['std'] = stats['std'].round(3)
    
    print(stats.to_string())
    
    # Recent performance (last 10 automation runs)
    print("\n" + "=" * 80)
    print("RECENT PERFORMANCE TRENDS")
    print("=" * 80)
    
    # Group by timestamp to identify separate runs
    df['run_id'] = (df['timestamp'].diff() > pd.Timedelta(seconds=5)).cumsum()
    
    recent_runs = df.groupby('run_id').tail(50)  # Last 50 entries
    recent_stats = recent_runs.groupby('function')['elapsed'].agg(['mean', 'count'])
    recent_stats = recent_stats.sort_values('mean', ascending=False)
    recent_stats['mean'] = recent_stats['mean'].round(3)
    
    print("\nRecent Average Times (last 50 entries):")
    print(recent_stats.to_string())
    
    # Total time per automation run
    print("\n" + "=" * 80)
    print("TOTAL TIME PER AUTOMATION RUN")
    print("=" * 80)
    
    run_totals = df.groupby('run_id').agg({
        'elapsed': 'sum',
        'timestamp': 'min'
    }).tail(10)  # Last 10 runs
    
    run_totals['elapsed'] = run_totals['elapsed'].round(2)
    run_totals.columns = ['Total Time (s)', 'Run Start']
    
    print("\nLast 10 automation runs:")
    print(run_totals.to_string())
    
    # Identify slowest operations
    print("\n" + "=" * 80)
    print("SLOWEST INDIVIDUAL CALLS (Top 20)")
    print("=" * 80)
    
    slowest = df.nlargest(20, 'elapsed')[['timestamp', 'function', 'elapsed']]
    slowest['elapsed'] = slowest['elapsed'].round(3)
    print(slowest.to_string(index=False))
    
    print("\n" + "=" * 80)


def compare_before_after(before_date):
    """Compare performance before and after a specific date"""
    log_path = Path(__file__).parent / "performance_log.csv"
    
    if not log_path.exists():
        print("No performance log found")
        return
    
    df = pd.read_csv(log_path)
    df['elapsed'] = df['elapsed'].astype(float)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    before = df[df['timestamp'] < pd.to_datetime(before_date)]
    after = df[df['timestamp'] >= pd.to_datetime(before_date)]
    
    print("=" * 80)
    print(f"PERFORMANCE COMPARISON (Before vs After {before_date})")
    print("=" * 80)
    
    comparison = pd.DataFrame({
        'Before Mean': before.groupby('function')['elapsed'].mean(),
        'After Mean': after.groupby('function')['elapsed'].mean(),
    })
    
    comparison['Improvement (s)'] = comparison['Before Mean'] - comparison['After Mean']
    comparison['Improvement (%)'] = ((comparison['Before Mean'] - comparison['After Mean']) / comparison['Before Mean'] * 100).round(1)
    comparison = comparison.round(3)
    comparison = comparison.sort_values('Improvement (s)', ascending=False)
    
    print(comparison.to_string())
    print("\n" + "=" * 80)


if __name__ == "__main__":
    analyze_performance_log()
    
    # Uncomment to compare before/after optimization
    # compare_before_after("2025-11-12 12:00:00")
