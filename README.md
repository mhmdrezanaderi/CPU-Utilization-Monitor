CPU Utilization Monitor
This project simulates a multi-processor CPU environment where tasks are scheduled and executed on different processors. The system monitors CPU utilization in real-time, providing a visual representation of CPU usage over time. The graphical user interface (GUI) is built using Tkinter and Matplotlib, and task scheduling is managed using Python threading and queue modules.

Features
Multi-processor support with configurable number of processors and threads.
Task scheduling using Rate Monotonic Scheduling.
Real-time CPU utilization monitoring with a graphical representation.
User-friendly GUI for adding tasks and monitoring system status.
Simulated resource allocation and deallocation for tasks.
Getting Started
Prerequisites
Make sure you have the following installed:

Python 3.x
Tkinter
Matplotlib
Installation
Clone the repository:

bash
Copy code
git clone https://github.com/your-username/cpu-utilization-monitor.git
cd cpu-utilization-monitor
Install the required Python packages:

bash
Copy code
pip install matplotlib
Running the Application
Run the main script:

bash
Copy code
python cpu_utilization_monitor.py
The GUI will launch, and the simulation will start automatically.

Usage
GUI Components
CPU Utilization Chart: Displays the CPU utilization over time for each processor.
Task Entry Form: Allows users to input new tasks with specified execution time, resource requirements, and processor assignment.
Add Task Button: Adds the entered tasks to the system.
Messages Panel: Displays notifications and status messages about the task execution and system status.
Adding Tasks
Click on the "Add Task" button.
Enter the task details in the task entry form.
Click "Submit" to add the tasks to the simulation.
Monitoring CPU Utilization
The CPU utilization chart updates every second, showing the real-time utilization of each processor.

Code Structure
cpu_utilization_monitor.py: Main script containing the entire application code.
CPUUtilizationMonitor: Main class for the GUI and simulation control.
processor_main: Function to simulate the main loop of each processor.
execute_task: Function to simulate task execution.
calculate_cpu_utilization: Function to calculate and return the current CPU utilization.
Contributing
Contributions are welcome! Please feel free to submit a pull request or open an issue.

License
This project is licensed under the MIT License - see the LICENSE file for details.

Acknowledgments
This project uses the Tkinter library for the GUI and Matplotlib for plotting CPU utilization.
