
from tkinter import filedialog 
import os
import json
from tkinter import filedialog

class Script: 
    SCRIPT_DATA_FILE='script_data.txt'
    import os

    def add_script(self):
        # Ask user to select a file
        filepath = filedialog.askopenfilename()

        # Check if filepath ends with .py
        if not filepath.lower().endswith('.py'):
            print("Error: Selected file is not a Python script (.py).")
            return

        try:
            if os.path.exists(self.SCRIPT_DATA_FILE):
                with open(self.SCRIPT_DATA_FILE, 'r') as file:
                    script_data = json.load(file)
            else:
                script_data = []
        except (FileNotFoundError, json.JSONDecodeError):
            script_data = []

        # Ensure the data is a list
        if not isinstance(script_data, list):
            script_data = []

        # Check if the script path already exists
        for scrpt in script_data:
            if scrpt["script_path"] == filepath:
                print("Error: Script path already exists.")
                return

        # Determine the new ID
        if script_data:
            max_id = max(script["id"] for script in script_data)
            new_id = max_id + 1
        else:
            new_id = 0

        # Add the new script data
        new_script = {"id": new_id, "script_path": filepath}
        script_data.append(new_script)

        # Write the updated data back to the JSON file
        with open(self.SCRIPT_DATA_FILE, "w") as file:
            json.dump(script_data, file, indent=4)
        print("Script added successfully.")



    def fetch_all_scripts(self):
        try:
            if os.path.exists(self.SCRIPT_DATA_FILE):
                with open(self.SCRIPT_DATA_FILE, 'r') as file:
                    script_data = json.load(file)
            else:
                script_data = []
        except (FileNotFoundError, json.JSONDecodeError):
            script_data = []

        # Ensure the data is a list
        if not isinstance(script_data, list):
            script_data = []

        return script_data
