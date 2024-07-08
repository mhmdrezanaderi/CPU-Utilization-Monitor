import threading
import queue
import time
import tkinter as tk
from tkinter import ttk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

# Global variables
NUM_PROCESSORS = 3
NUM_THREADS_PER_PROCESSOR = 3

# Mutexes
resource_mutex = threading.Lock()
waiting_queue_mutex = threading.Lock()

# Queues
ready_queues = [queue.Queue() for _ in range(NUM_PROCESSORS)]
waiting_queue = queue.Queue()

# Global resource availability
resources_available = [10,10,10]  

# Variables to track CPU utilization
processor_utilization = [0] * NUM_PROCESSORS
total_processor_time = [0] * NUM_PROCESSORS
running_tasks = ['idle'] * NUM_PROCESSORS  
idle_time = [0] * NUM_PROCESSORS

# Function to simulate task execution
def execute_task(task, processor_id):
    global resources_available, processor_utilization, total_processor_time, running_tasks, idle_time
    start_time = time.time()  # Start time of task execution
    time.sleep(task['execution_time'])  # Simulate task execution time
    end_time = time.time()  # End time of task execution

    execution_time = end_time - start_time

    # Update CPU utilization and total processor time
    processor_utilization[processor_id] += execution_time
    total_processor_time[processor_id] += execution_time
    running_tasks[processor_id] = task['name']  # Update running task

    # Update available resources
    resource_mutex.acquire()
    resources_available[0] += task['resource1']
    resources_available[1] += task['resource2']
    resources_available[2] += task['resource3']
    resource_mutex.release()

def processor_main(processor_id):
    while True:
        task_found = False
        task = None  # Initialize task variable
        
        # Get task from ready queue or waiting queue
        resource_mutex.acquire()
        if not ready_queues[processor_id].empty():
            task = ready_queues[processor_id].get()
            resource_mutex.release()
            task_found = True
        else:
            resource_mutex.release()
            waiting_queue_mutex.acquire()
            if not waiting_queue.empty():
                task = waiting_queue.get()
                waiting_queue_mutex.release()
                task_found = True
            else:
                waiting_queue_mutex.release()
                time.sleep(1)  # Prevent unnecessary waiting when no task is available
                idle_time[processor_id] += 1  # Increase idle time
                continue
        
        if task_found:
            # Check resource availability
            resource_mutex.acquire()
            if resources_available[0] >= task['resource1'] and resources_available[1] >= task['resource2'] and resources_available[2] >= task['resource3']:
                # Allocate resources
                resources_available[0] -= task['resource1']
                resources_available[1] -= task['resource2']
                resources_available[2] -= task['resource3']
                resource_mutex.release()

                execute_task(task, processor_id)
                output = calculate_cpu_utilization()
                for line in output:
                    print(line)
                app.add_message(f"Task {task['name']} executed on CPU {processor_id + 1}")

                # Decrease remaining repetitions or move to waiting queue if more repetitions are needed
                if task['repetitions'] > 1:
                    task['repetitions'] -= 1
                    ready_queues[processor_id].put(task)
                else:
                    app.add_message(f"Task {task['name']} finished all repetitions")
                    print(f"Task {task['name']} finished all repetitions")

                    # Simulate resource deallocation and update waiting queue
                    time.sleep(1)  # Simulate resource deallocation time
                    resource_mutex.acquire()
                    resources_available[0] += task['resource1']
                    resources_available[1] += task['resource2']
                    resources_available[2] += task['resource3']
                    resource_mutex.release()
            else:
                resource_mutex.release()
                app.add_message(f"Not enough resources available for task {task['name']} on CPU {processor_id + 1}. Stopping simulation.")
                # Stop simulation
                # app.after_cancel(app.update_gui)  # Stop updating GUI
                return

def calculate_cpu_utilization():
    output = []
    for i in range(NUM_PROCESSORS):
        total_time = total_processor_time[i] + idle_time[i]  # Total time including idle time
        utilization = (processor_utilization[i] / total_time) * 100 if total_time > 0 else 0
        ready_queue_tasks = [f"{task['name']}:{task['repetitions']}" for task in list(ready_queues[i].queue)]
        running_task = running_tasks[i]
        output.append(f"CPU{i + 1}:\nCPU Utilization: {utilization:.2f}%\nReady Queue: [{', '.join(ready_queue_tasks)}]\nRunning Task: {running_task}\n")
    return output

def receive_and_schedule_tasks():
    # Example input handling, replace with your actual input mechanism
    tasks = [
        {'name': 'T1', 'period': 0, 'execution_time': 8, 'resource1': 0, 'resource2': 0, 'resource3': 0, 'processor_id': 0, 'repetitions': 0},
        {'name': 'T2', 'period': 80, 'execution_time': 16, 'resource1': 0, 'resource2': 2, 'resource3': 1, 'processor_id': 1, 'repetitions': 3},
        {'name': 'T3', 'period': 100, 'execution_time': 20, 'resource1': 2, 'resource2': 0, 'resource3': 1, 'processor_id': 2, 'repetitions': 2},
        {'name': 'T4', 'period': 150, 'execution_time': 25, 'resource1': 0, 'resource2': 0, 'resource3': 2, 'processor_id': 1, 'repetitions': 2},
        {'name': 'T5', 'period': 160, 'execution_time': 30, 'resource1': 2, 'resource2': 2, 'resource3': 1, 'processor_id': 0, 'repetitions': 2},
        {'name': 'T6', 'period': 170, 'execution_time': 35, 'resource1': 2, 'resource2': 3, 'resource3': 1, 'processor_id': 2, 'repetitions': 2},
    ]

    # Sort tasks based on their periods for Rate Monotonic scheduling
    tasks.sort(key=lambda x: x['period'])

    # Calculate deadlines for each task
    for task in tasks:
        task['deadlines'] = [task['period'] * (i + 1) for i in range(task['repetitions'])]

    # Distribute tasks to appropriate ready queues
    for task in tasks:
        ready_queues[task['processor_id']].put(task)

    # Start processor threads
    processor_threads = []
    for i in range(NUM_PROCESSORS):
        thread = threading.Thread(target=processor_main, args=(i,))
        processor_threads.append(thread)
        thread.start()

    # Wait for all threads to finish
    for thread in processor_threads:
        thread.join()

# GUI Code
class CPUUtilizationMonitor(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("CPU Utilization Monitor")
        self.geometry("800x600")
        
        self.fig, self.ax = plt.subplots(figsize=(10, 8))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        self.time_elapsed = 0
        self.utilization_data = {f'CPU{i + 1}': [] for i in range(NUM_PROCESSORS)}

        self.update_gui()
        self.create_task_entry_form()  # Create task entry form
        self.create_add_task_button()  # Create add task button
        self.create_messages_panel()  # Create messages panel for notifications

    def update_gui(self):
        self.ax.clear()
        self.ax.set_title('CPU Utilization Over Time')
        self.ax.set_ylabel('Utilization (%)')
        self.ax.set_ylim(0, 300)
        self.ax.set_xlabel('Time (s)')

        self.time_elapsed += 1

        for i in range(NUM_PROCESSORS):
            total_time = total_processor_time[i] + idle_time[i]
            utilization = (processor_utilization[i] / total_time) * 100 if total_time > 0 else 0
            self.utilization_data[f'CPU{i + 1}'].append(utilization)
            self.ax.plot(range(len(self.utilization_data[f'CPU{i + 1}'])), self.utilization_data[f'CPU{i + 1}'], label=f'CPU{i + 1}')

        self.ax.legend(loc='upper right')
        self.canvas.draw()
        self.after(200, self.update_gui)  # Update every 1 second

    def create_task_entry_form(self):
        # Create a new window for task entry form
        self.task_entry_window = tk.Toplevel(self)
        self.task_entry_window.title("Add New Task")
        self.task_entry_window.geometry("400x300")

        self.tasks_entry_widgets = []

        for i in range(2):  # Example: Create 2 sets of entry widgets for 2 tasks
            frame = ttk.LabelFrame(self.task_entry_window, text=f"Task {i + 1}")
            frame.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)

            tk.Label(frame, text="Task Name:").pack()
            task_name_entry = tk.Entry(frame)
            task_name_entry.pack()

            tk.Label(frame, text="Execution Time (s):").pack()
            execution_time_entry = tk.Entry(frame)
            execution_time_entry.pack()

            tk.Label(frame, text="Resource 1:").pack()
            resource1_entry = tk.Entry(frame)
            resource1_entry.pack()

            tk.Label(frame, text="Resource 2:").pack()
            resource2_entry = tk.Entry(frame)
            resource2_entry.pack()

            tk.Label(frame, text="Resource 3:").pack()
            resource3_entry = tk.Entry(frame)
            resource3_entry.pack()

            tk.Label(frame, text="Processor ID (0 to 2):").pack()
            processor_id_entry = tk.Entry(frame)
            processor_id_entry.pack()

            self.tasks_entry_widgets.append({
                'task_name': task_name_entry,
                'execution_time': execution_time_entry,
                'resource1': resource1_entry,
                'resource2': resource2_entry,
                'resource3': resource3_entry,
                'processor_id': processor_id_entry
            })

    def create_add_task_button(self):
        add_task_button = tk.Button(self, text="Add Task", command=self.add_tasks_from_entry_form)
        add_task_button.pack()

    def create_messages_panel(self):
        self.messages_listbox = tk.Listbox(self, width=100, height=10)
        self.messages_listbox.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

    def add_message(self, message):
        self.messages_listbox.insert(tk.END, message)
        self.messages_listbox.see(tk.END)  # Scroll to the end

    def add_tasks_from_entry_form(self):
        tasks = []
        for widget_set in self.tasks_entry_widgets:
            task = {
                'name': widget_set['task_name'].get(),
                'execution_time': int(widget_set['execution_time'].get()),
                'resource1': int(widget_set['resource1'].get()),
                'resource2': int(widget_set['resource2'].get()),
                'resource3': int(widget_set['resource3'].get()),
                'processor_id': int(widget_set['processor_id'].get()),
                'repetitions': 1  # Initial repetitions, can be adjusted as needed
            }
            tasks.append(task)

        for task in tasks:
            ready_queues[task['processor_id']].put(task)

        self.task_entry_window.destroy()

    def start_simulation(self):
        threading.Thread(target=receive_and_schedule_tasks).start()

if __name__ == "__main__":
    app = CPUUtilizationMonitor()
    app.start_simulation()  # Start simulation thread
    app.mainloop()
