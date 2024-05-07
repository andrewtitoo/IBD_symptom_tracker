import tkinter as tk
from tkinter import ttk, messagebox, Toplevel
import sqlite3
import csv
import os
import datetime

# A dictionary to hold trigger selections
trigger_choices = {
    "Food/Diet": False,
    "Sleep Disturbance": False,
    "Increased Stress": False,
    "Medication Issues": False
}

treatment_choices = [
    "Use Mesalamine enema",
    "Use Budesonide",
    "Use Prednisone",
    "Rest",
    "Epson Salt Bath",
    "Email Doctor",
    "Request Labs",
    "Need a doctor visit",
    "Need an emergency visit"
]

# Initialize global notes variables
trigger_notes = ""
treatment_notes = ""  # Added initialization for treatment notes

def init_db():
    conn = sqlite3.connect('ibd_symptoms.db')
    cursor = conn.cursor()
    cursor.execute('DROP TABLE IF EXISTS symptoms')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS symptoms (
            id INTEGER PRIMARY KEY,
            pain_level INTEGER,
            urgency TEXT,
            visits TEXT,
            bristol_scale INTEGER,
            blood_presence TEXT,
            fatigue TEXT,
            joint_pain TEXT,
            mood TEXT,
            triggers TEXT,
            treatments TEXT,
            notes TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def save_to_database(form_data):
    conn = sqlite3.connect('ibd_symptoms.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO symptoms (
            pain_level, urgency, visits, bristol_scale, blood_presence,
            fatigue, joint_pain, mood, triggers, treatments, notes
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', form_data)
    conn.commit()
    conn.close()

app = tk.Tk()
app.title("IBD Symptom Tracker")

def log_symptoms_to_csv(form_data):
    now = datetime.datetime.now()
    timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
    form_data_with_timestamp = [timestamp] + form_data
    csv_file_path = 'symptoms_log.csv'
    file_exists = os.path.isfile(csv_file_path)
    with open(csv_file_path, mode='a', newline='') as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(['Timestamp', 'Pain Level', 'Urgency', 'Visits', 'Bristol Scale', 'Blood Presence', 'Fatigue', 'Joint Pain', 'Mood', 'Triggers', 'Treatments', 'Notes'])
        writer.writerow(form_data_with_timestamp)

def ask_triggers_window(callback):
    def submit_triggers():
        selected_triggers = [key for key, var in trigger_checkboxes.items() if var.get()]
        global trigger_notes, treatment_notes  # Ensure they are recognized as global variables
        trigger_notes = ', '.join(selected_triggers) if selected_triggers else "NULL"
        selected_treatments = [option for option, var in treatment_checkboxes.items() if var.get()]
        treatment_notes = ', '.join(selected_treatments) if selected_treatments else "NULL"
        window.destroy()
        callback()

    window = Toplevel(app)
    window.title("Select Triggers and Treatments")

    ttk.Label(window, text="Please select the potential triggers:").grid(row=0, column=0, columnspan=2, pady=5)
    trigger_checkboxes = {}
    for index, trigger in enumerate(trigger_choices.keys(), start=1):
        var = tk.BooleanVar(value=False)
        trigger_checkboxes[trigger] = var
        ttk.Checkbutton(window, text=trigger, variable=var).grid(row=index, column=0, sticky=tk.W, padx=10)

    # Treatment checklist
    ttk.Label(window, text="Please select the treatment options:").grid(row=index + 1, column=0, columnspan=2, pady=5)
    treatment_checkboxes = {}
    for index2, treatment in enumerate(treatment_choices, start=index+2):
        var = tk.BooleanVar(value=False)
        treatment_checkboxes[treatment] = var
        ttk.Checkbutton(window, text=treatment, variable=var).grid(row=index2, column=0, sticky=tk.W, padx=10)

    ttk.Button(window, text="Submit", command=submit_triggers).grid(row=index2 + 1, column=0, pady=10)

def process_submission(form_data):
    form_data.extend([trigger_notes, treatment_notes])
    if not validate_form_data(form_data):
        return
    save_to_database(form_data)
    log_symptoms_to_csv(form_data)
    messagebox.showinfo("Success", "Symptoms submitted and logged successfully!")

def submit():
    try:
        form_data = [
            pain_level.get(),
            urgency.get(),
            visits.get(),
            bristol_scale.get(),
            blood_presence.get(),
            fatigue.get(),
            joint_pain.get(),
            mood.get()
        ]

        # Get the user's notes
        user_notes = notes_entry.get("1.0", tk.END).strip() or "NULL"

        # Check for conditions that require asking about triggers
        pain_level_value = int(pain_level.get())
        blood_presence_value = blood_presence.get()
        if pain_level_value >= 5 or blood_presence_value == "Yes":
            ask_triggers_window(lambda: process_submission(form_data + [user_notes]))
        else:
            process_submission(form_data + [user_notes])
    except Exception as e:
        messagebox.showerror("Submission Error", str(e))

# GUI Setup for Notes Entry
notes_entry_label = ttk.Label(app, text="Provide any additional notes:")
notes_entry_label.grid(row=8, column=0, pady=5)
notes_entry = tk.Text(app, height=4, width=40)
notes_entry.grid(row=8, column=1, padx=10, pady=5)

def validate_form_data(form_data):
    # Validate form data
    try:
        if not 1 <= int(form_data[0]) <= 10:
            raise ValueError("Pain level must be between 1 and 10.")
        return True
    except ValueError as ve:
        messagebox.showerror("Validation Error", str(ve))
        return False

pain_level = ttk.Combobox(app, values=list(range(1, 11)))
pain_level.grid(row=0, column=1, pady=2, padx=2)
ttk.Label(app, text="Pain Level (1-10):").grid(row=0, column=0, sticky=tk.W)

urgency = ttk.Combobox(app, values=["None", "Mild", "Moderate", "Severe"])
urgency.grid(row=1, column=1, pady=2, padx=2)
ttk.Label(app, text="Urgency to use the restroom:").grid(row=1, column=0, sticky=tk.W)

visits = ttk.Combobox(app, values=["Normal", "1-2 more than normal", "3-4 more than normal", "5+ more than normal"])
visits.grid(row=2, column=1, pady=2, padx=2)
ttk.Label(app, text="Number of bathroom visits:").grid(row=2, column=0, sticky=tk.W)

bristol_scale = ttk.Combobox(app, values=[
    "1 - Separate hard lumps, like nuts (hard to pass)",
    "2 - Sausage-shaped but lumpy",
    "3 - Like a sausage but with cracks on the surface",
    "4 - Like a sausage or snake, smooth and soft",
    "5 - Soft blobs with clear-cut edges (passed easily)",
    "6 - Fluffy pieces with ragged edges, a mushy stool",
    "7 - Watery, no solid pieces (entirely liquid)"
])
bristol_scale.grid(row=3, column=1, pady=2, padx=2)
ttk.Label(app, text="Stool condition (Bristol Scale):").grid(row=3, column=0, sticky=tk.W)


blood_presence = ttk.Combobox(app, values=["No", "Yes"])
blood_presence.grid(row=4, column=1, pady=2, padx=2)
ttk.Label(app, text="Presence of blood in stool:").grid(row=4, column=0, sticky=tk.W)

fatigue = ttk.Combobox(app, values=["No", "Yes"])
fatigue.grid(row=5, column=1, pady=2, padx=2)
ttk.Label(app, text="Experiencing Fatigue?:").grid(row=5, column=0, sticky=tk.W)

joint_pain = ttk.Combobox(app, values=["No", "Yes"])
joint_pain.grid(row=6, column=1, pady=2, padx=2)
ttk.Label(app, text="Experiencing Joint Pain?:").grid(row=6, column=0, sticky=tk.W)

mood = ttk.Combobox(app, values=["None", "Anxious", "Depressed", "Frustrated"])
mood.grid(row=7, column=1, pady=2, padx=2)
ttk.Label(app, text="Any effect on emotions?").grid(row=7, column=0, sticky=tk.W)

submit_button = ttk.Button(app, text="Submit", command=submit)
submit_button.grid(row=9, column=1, pady=10)

if __name__ == "__main__":
    init_db()
    app.mainloop()

