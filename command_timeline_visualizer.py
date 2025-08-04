#!/usr/bin/env python3
"""
Command Timeline Visualizer

This script analyzes a command history file and creates a visualization showing:
- Y-axis: Hours of the day (0-23)
- X-axis: Different dates
- Colored dots: Presence of commands at specific times

The visualization helps identify patterns in command usage over time.
"""

import re
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
import numpy as np
from collections import defaultdict

def parse_history_file(file_path):
    """
    Parse the history file and extract timestamp and command information.
    
    Args:
        file_path (str): Path to the history file
    
    Returns:
        list: List of tuples containing (datetime, command)
    """
    commands = []
    
    # Regular expression to match the format: "number  DD.M.YYYY HH:MM  command"
    pattern = r'^\s*\d+\s+(\d{1,2})\.(\d{1,2})\.(\d{4})\s+(\d{1,2}):(\d{2})\s+(.+)$'
    
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            for line_num, line in enumerate(file, 1):
                line = line.strip()
                if not line:
                    continue
                
                match = re.match(pattern, line)
                if match:
                    day, month, year, hour, minute, command = match.groups()
                    try:
                        # Create datetime object
                        dt = datetime(int(year), int(month), int(day), int(hour), int(minute))
                        commands.append((dt, command.strip()))
                    except ValueError as e:
                        print(f"Warning: Invalid date on line {line_num}: {e}")
                        continue
                else:
                    # Try to handle potential edge cases or malformed lines
                    print(f"Warning: Could not parse line {line_num}: {line[:50]}...")
    
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        return []
    except Exception as e:
        print(f"Error reading file: {e}")
        return []
    
    print(f"Successfully parsed {len(commands)} commands from {file_path}")
    return commands

def create_timeline_plot(commands, output_file=None):
    """
    Create a timeline visualization of the commands.
    
    Args:
        commands (list): List of (datetime, command) tuples
        output_file (str, optional): Path to save the plot
    """
    if not commands:
        print("No commands to visualize.")
        return
    
    # Extract dates and hours
    dates = []
    hours = []
    command_types = []
    
    # Categorize commands by type for different colors
    command_categories = {
        'git': ['git'],
        'file_ops': ['ls', 'cd', 'mkdir', 'rm', 'mv', 'cp', 'cat', 'vim', 'code'],
        'julia': ['julia'],
        'other': []
    }
    
    def categorize_command(cmd):
        """Categorize a command based on its first word."""
        first_word = cmd.split()[0] if cmd.split() else ''
        
        for category, keywords in command_categories.items():
            if category != 'other' and first_word in keywords:
                return category
        return 'other'
    
    for dt, cmd in commands:
        dates.append(dt.date())
        hours.append(dt.hour + dt.minute / 60.0)  # Convert to decimal hours for better precision
        command_types.append(categorize_command(cmd))
    
    # Create the plot
    fig, ax = plt.subplots(figsize=(6, 3))
    
    # Define colors for different command categories
    colors = {
        'git': '#FF6B6B',      # Red
        'file_ops': '#4ECDC4', # Teal
        'julia': "#E2E609FF",   # Blue
        'other': '#DDA0DD'     # Plum
    }
    
    # Convert dates to numbers for plotting
    unique_dates = sorted(list(set(dates)))
    date_to_num = {date: i for i, date in enumerate(unique_dates)}
    x_positions = [date_to_num[date] for date in dates]
    
    # Create scatter plot
    for category in colors.keys():
        mask = [ct == category for ct in command_types]
        if any(mask):
            x_cat = [x_positions[i] for i in range(len(x_positions)) if mask[i]]
            y_cat = [hours[i] for i in range(len(hours)) if mask[i]]
            ax.scatter(x_cat, y_cat, c=colors[category], label=category, alpha=0.6, s=30)
    
    # Customize the plot
    ax.set_ylabel('Hour of Day', fontsize=12)
    
    # Set y-axis to show hours
    ax.set_ylim(-0.5, 23.5)
    ax.set_yticks(range(0, 24, 2))
    ax.set_yticklabels([f'{h:02d}:00' for h in range(0, 24, 2)])
    ax.invert_yaxis()  # Invert so midnight is at top, noon at bottom
    
    # Set x-axis to show dates
    ax.set_xlim(-0.5, len(unique_dates) - 0.5)
    
    # Format x-axis labels
    if False:#len(unique_dates) <= 10:
        # Show all dates if there are few
        ax.set_xticks(range(len(unique_dates)))
        ax.set_xticklabels([date.strftime('%d/%m') for date in unique_dates], rotation=45)
    else:
        # Show every nth date if there are many
        step = max(1, len(unique_dates) // 5)
        tick_positions = range(0, len(unique_dates), step)
        ax.set_xticks(tick_positions)
        ax.set_xticklabels([unique_dates[i].strftime('%d/%m/%y') for i in tick_positions], rotation=45)
    
    # Add legend
    ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    
    # Add grid
    ax.grid(True, alpha=0.3)
    
    # Adjust layout to prevent label cutoff
    plt.tight_layout()
    
    # Add statistics text
    # stats_text = f"Total commands: {len(commands)}\n"
    # stats_text += f"Date range: {min(unique_dates)} to {max(unique_dates)}\n"
    # stats_text += f"Total days: {len(unique_dates)}"
    # 
    # ax.text(0.02, 0.98, stats_text, transform=ax.transAxes, fontsize=10,
    #         verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
    
    # Save or show the plot
    if output_file:
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"Plot saved to {output_file}")
    else:
        plt.show()

def print_summary_statistics(commands):
    """Print summary statistics about the command usage."""
    if not commands:
        return
    
    print("\n" + "="*50)
    print("COMMAND USAGE SUMMARY")
    print("="*50)
    
    # Basic statistics
    dates = [dt.date() for dt, _ in commands]
    hours = [dt.hour for dt, _ in commands]
    
    print(f"Total commands: {len(commands)}")
    print(f"Date range: {min(dates)} to {max(dates)}")
    print(f"Number of unique days: {len(set(dates))}")
    
    # Commands per day
    daily_counts = defaultdict(int)
    for date in dates:
        daily_counts[date] += 1
    
    print(f"Average commands per day: {len(commands) / len(set(dates)):.1f}")
    print(f"Most active day: {max(daily_counts, key=daily_counts.get)} ({max(daily_counts.values())} commands)")
    
    # Hourly distribution
    hourly_counts = defaultdict(int)
    for hour in hours:
        hourly_counts[hour] += 1
    
    print(f"Most active hour: {max(hourly_counts, key=hourly_counts.get)}:00 ({max(hourly_counts.values())} commands)")
    
    # Top commands
    command_counts = defaultdict(int)
    for _, cmd in commands:
        first_word = cmd.split()[0] if cmd.split() else ''
        command_counts[first_word] += 1
    
    print("\nTop 10 most used commands:")
    for cmd, count in sorted(command_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"  {cmd}: {count}")

def main():
    """Main function to run the visualization."""
    import sys
    import os
    
    # Get the history file path
    if len(sys.argv) > 1:
        history_file = sys.argv[1]
    else:
        # Default to the file in the current directory
        history_file = "/Users/mmm/history_up_to_20_luglio.txt"
    
    if not os.path.exists(history_file):
        print(f"Error: File '{history_file}' not found.")
        print("Usage: python command_timeline_visualizer.py [history_file_path]")
        return
    
    # Parse the history file
    print(f"Parsing history file: {history_file}")
    commands = parse_history_file(history_file)
    
    if not commands:
        print("No commands found in the file.")
        return
    
    # Print summary statistics
    print_summary_statistics(commands)
    
    # Create the visualization
    print("\nCreating timeline visualization...")
    output_file = "command_timeline.png"
    create_timeline_plot(commands, output_file)
    
    print(f"\nVisualization complete! Check '{output_file}' for the timeline plot.")

if __name__ == "__main__":
    main()
