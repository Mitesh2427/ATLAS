import networkx as nx
import matplotlib.pyplot as plt
import pandas as pd
import tkinter as tk
from tkinter import ttk
import matplotlib.animation as animation

# ----------- Step 1: Define flights -----------
flights = [
    {"id": 1, "type": "Small", "eta": "12:10", "fuel_level": 60, "emergency": False, "required_runway_length": 8},
    {"id": 2, "type": "Small", "eta": "12:20", "fuel_level": 45, "emergency": True, "required_runway_length": 8},
    {"id": 3, "type": "Small", "eta": "12:25", "fuel_level": 80, "emergency": False, "required_runway_length": 8},
    {"id": 4, "type": "Medium", "eta": "12:15", "fuel_level": 30, "emergency": False, "required_runway_length": 10},
    {"id": 5, "type": "Large", "eta": "12:05", "fuel_level": 70, "emergency": False, "required_runway_length": 12},
    {"id": 6, "type": "Large", "eta": "12:30", "fuel_level": 20, "emergency": True, "required_runway_length": 12},
]

# ----------- Step 2: Sort flights by priority -----------
def flight_priority(f):
    return (
        not f["emergency"],       # Emergency flights first
        f["fuel_level"],          # Lower fuel level has higher priority
        {"Large": 3, "Medium": 2, "Small": 1}[f["type"]]  # Larger flights prioritized
    )

flights_sorted = sorted(flights, key=flight_priority)

# ----------- Step 3: Show tables -----------
def show_table(title, dataframe):
    window = tk.Tk()
    window.title(title)
    window.geometry("800x300")

    frame = ttk.Frame(window)
    frame.pack(fill=tk.BOTH, expand=True)

    tree = ttk.Treeview(frame, columns=list(dataframe.columns), show="headings")
    for col in dataframe.columns:
        tree.heading(col, text=col)
        tree.column(col, width=100)

    for _, row in dataframe.iterrows():
        tree.insert("", "end", values=list(row))

    scrollbar = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
    tree.configure(yscroll=scrollbar.set)
    tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    window.mainloop()

df_unordered = pd.DataFrame(flights)
df_ordered = pd.DataFrame(flights_sorted)
show_table("Unordered Flights", df_unordered)
show_table("Ordered Flights by Priority", df_ordered)

# ----------- Step 4: Setup Runways & Graph -----------
G = nx.DiGraph()
runway_1 = list(range(0, 12))     # Large
runway_2 = list(range(12, 22))    # Medium
runway_3 = list(range(22, 30))    # Small

# Add nodes and edges
for runway in [runway_1, runway_2, runway_3]:
    for node in runway:
        G.add_node(node)
    for i in range(len(runway) - 1):
        G.add_edge(runway[i], runway[i + 1])

# Node positions for plotting
pos = {}
for i in range(12):
    pos[i] = (i, 2)
for i in range(12, 22):
    pos[i] = (i - 12, 1)
for i in range(22, 30):
    pos[i] = (i - 22, 0)

# ----------- Step 5: Assign runways and schedule -----------
runway_next_free_time = {"runway_1": 0, "runway_2": 0, "runway_3": 0}
schedule = []
log_entries = []

for i, flight in enumerate(flights_sorted):
    if flight["type"] == "Large":
        preferred_runways = [("runway_1", runway_1)]
    elif flight["type"] == "Medium":
        preferred_runways = [("runway_2", runway_2), ("runway_1", runway_1)]
    else:
        preferred_runways = [("runway_3", runway_3), ("runway_2", runway_2), ("runway_1", runway_1)]

    # Find the earliest available runway (optimal selection)
    best_option = min(preferred_runways, key=lambda x: runway_next_free_time[x[0]])
    runway_key, runway = best_option

    # Apply conflict buffer (2 frames) after previous flight
    start_time = max(runway_next_free_time[runway_key], len(schedule) * 2)
    end_time = start_time + len(runway) + 2  # traversal + 2 frame wait

    schedule.append({
        "flight": flight,
        "runway": runway,
        "start": start_time,
        "end": end_time
    })
    runway_next_free_time[runway_key] = end_time + 2  # add buffer after landing

    log_entries.append({
        "Flight ID": flight["id"],
        "Type": flight["type"],
        "Emergency": flight["emergency"],
        "Fuel Level": flight["fuel_level"],
        "ETA": flight["eta"],
        "Assigned Runway": runway_key,
        "Start Time": start_time,
        "End Time": end_time
    })

# ----------- Step 6: Animate -----------
fig, ax = plt.subplots(figsize=(10, 6))

def update(frame):
    ax.clear()
    nx.draw(G, pos, with_labels=True, node_size=500, node_color='lightblue', edge_color='gray')

    for sched in schedule:
        flight = sched["flight"]
        runway = sched["runway"]
        start = sched["start"]
        end = sched["end"]

        if start <= frame < end - 2:  # moving
            idx = frame - start
            node = runway[min(idx, len(runway) - 1)]
            nx.draw_networkx_nodes(G, pos, nodelist=[node], node_color='green', node_size=700)
            x, y = pos[node]
            ax.text(x, y + 0.3, f"F{flight['id']}", fontsize=10, fontweight='bold', ha='center')

        elif frame == end - 2 or frame == end - 1:  # waiting
            node = runway[-1]
            nx.draw_networkx_nodes(G, pos, nodelist=[node], node_color='red', node_size=700)
            x, y = pos[node]
            ax.text(x, y + 0.3, f"F{flight['id']} (Wait)", fontsize=10, fontweight='bold', ha='center')

    ax.set_title(f"Flight Landing Simulation - Frame {frame}")
    ax.axis('off')

total_frames = schedule[-1]['end'] + 5
ani = animation.FuncAnimation(fig, update, frames=total_frames, interval=2000, repeat=False)
plt.show()

# ----------- Step 7: Display Runway Allocation Log -----------
df_log = pd.DataFrame(log_entries)
show_table("Runway Allocation Log", df_log)
    