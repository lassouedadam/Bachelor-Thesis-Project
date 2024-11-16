import tkinter as tk
from tkinter import END, Entry, messagebox
from tkinter import ttk
from PIL import Image, ImageTk
import os
import re
import mysql.connector
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tkinter import Canvas
from Pmw import *
from ttkthemes import ThemedTk
import os
from datetime import date, datetime
from PIL import Image, ImageTk


def authenticate():
    # login function
    def login():
        username = username_entry.get()
        password = password_entry.get()

        mydb = mysql.connector.connect(
            host="127.0.0.1",
            user="root",
            password="Xhh4azsese_",
            database="smartsec"
        )
        cursor = mydb.cursor()

        query = "SELECT * FROM authentification WHERE ID = %s AND password = %s"
        cursor.execute(query, (username, password))
        result = cursor.fetchone()

        if result:
            auth_window.destroy() 
            create_interface()   
        else:
            messagebox.showerror("Erreur", "Identifiant ou mot de passe invalide")

        cursor.close()
        mydb.close()

    # Tkinter window for authentication
    auth_window = tk.Tk()
    auth_window.title("Authentication")
    auth_window.geometry("400x175")
    auth_window.configure(bg="#222222")

    # Username entry
    username_label = tk.Label(auth_window, text="Identifiant:", bg="#222222", fg="white")
    username_label.pack(pady=5)
    username_entry = tk.Entry(auth_window)
    username_entry.pack(pady=5)

    # Password entry
    password_label = tk.Label(auth_window, text="Mot de passe:", bg="#222222", fg="white")
    password_label.pack(pady=5)
    password_entry = tk.Entry(auth_window, show="*")
    password_entry.pack(pady=5)

    # Login Button
    login_button = tk.Button(auth_window, text="Login", command=login)
    login_button.pack(pady=10)

    auth_window.mainloop()



def get_screen_size():
    """Gets the screen width and height."""
    root = tk.Tk()
    width = root.winfo_screenwidth()
    height = root.winfo_screenheight()
    root.destroy()  
    return width, height

def create_interface():
    """Creates the tkinter interface with a large left box and two right boxes,
    loading and displaying extracted data from verification_log.txt."""
    width, height = get_screen_size()

    root = tk.Tk()
    root.title("Security")
    root.geometry(f"{width}x{height}")  

    # color code
    dark_grey = "#222222"
    light_grey = "#DDDDDD"
    white = "#FFFFFF"

  
    
    
    # left frame
    left_frame = tk.Frame(root, width=width // 2, height=height, bg=dark_grey)
    left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    left_box_label = ttk.Label(left_frame, text="Tracking Général", font=("Arial", 14, "bold"), foreground=dark_grey, background=light_grey, padding=5, relief="raised")
    left_box_label.pack(fill=tk.X, pady=(1), padx=1)  # Pack horizontally with padding

    # scrollable canvas
    canvas = tk.Canvas(left_frame, bg=dark_grey)
    canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    scrollbar = tk.Scrollbar(left_frame, orient=tk.VERTICAL, command=canvas.yview, bg=dark_grey, troughcolor=dark_grey)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    canvas.configure(yscrollcommand=scrollbar.set)

    frame = tk.Frame(canvas, bg=dark_grey)
    canvas.create_window((20, 0), window=frame, anchor='nw')

    def on_configure(event):
        canvas.configure(scrollregion=canvas.bbox('all'))

    canvas.bind('<Configure>', on_configure)

    def load_anomalies():
        try:
            if os.path.isfile("verification_log.txt"):
                with open("verification_log.txt", "r") as file:
                    # Read file lines in reverse order
                    lines = file.readlines()[::-1]
                    count = 0
                    row = 0
                    for line in lines:
                        if count >= 32:
                            break
                        # Extract data using regular expressions
                        match = re.search(r"Person: (.+), Date and Time: (.+), Image: (.+), Zone: ([\w\d]+)", line.strip())
                        if match:
                            model_name, now, filename_frame, zone = match.groups()
                            # Formattage (Replacing underscores with spaces)
                            zone = zone.replace("_", " ")
                            try:
                                image = Image.open(filename_frame)
                                image.thumbnail((240, 240))  # Resize the image
                                photo = ImageTk.PhotoImage(image)
                                col = count % 3
                                small_frame = tk.Frame(frame, bg=dark_grey, width=100, height=100)  
                                small_frame.grid(row=row, column=col, padx=5, pady=5)
                                label_image = tk.Label(small_frame, image=photo, bg=dark_grey)
                                label_image.image = photo
                                label_image.pack()
                                label_model = tk.Label(small_frame, text=model_name, font=("Arial", 10, "bold"), fg=white, bg=dark_grey)
                                label_model.pack()
                                label_now = tk.Label(small_frame, text=datetime.strftime(datetime.strptime(now, "%Y-%m-%d_%H-%M-%S"), "%Y-%m-%d | %Hh%M"), font=("Arial", 10), fg=light_grey, bg=dark_grey)
                                label_now.pack()
                                label_camera = tk.Label(small_frame, text=f"Zone: {zone}", font=("Arial", 10), fg=light_grey, bg=dark_grey)
                                label_camera.pack()

                                count += 1
                                if col == 2:
                                    row += 1
                            except Exception as e:
                                print(f"Error loading image: {str(e)}")
                        else:
                            print(f"Invalid line format: {line.strip()}")
            else:
                print("Verification log file not found.")
        except FileNotFoundError:
            print("An error occurred while reading the file.")


    # Load anomalies on interface creation
    load_anomalies()
 
    def fetch_data_from_database():

        mydb = mysql.connector.connect(
        host="127.0.0.1",
        user="root",
        password="Xhh4azsese_",
        database="smartsec2"
        )
        cursor = mydb.cursor()
        
        # Fetch data from the dashboard table
        cursor.execute("SELECT employe FROM dashboard2")        
        data = cursor.fetchall()
        cursor.close()

        return data
    
    data = fetch_data_from_database()  

    # Right frame
    right_frame = tk.Frame(root, width=width // 2, height=height, bg=dark_grey)
    right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

    right_frame_label = ttk.Label(right_frame, text="Tracking Personnel", font=("Arial", 14, "bold"), foreground=dark_grey, background=light_grey, padding=5, relief="raised")
    right_frame_label.pack(fill=tk.X, pady=(1), padx=1)  # Pack horizontally with padding


    # Create today's numbers + employees
    def create_data_labels(text, parent_frame):
        lines = text.splitlines()
        print(lines)

        empty_label = tk.Label(parent_frame, font=("Arial", 12), fg="white", bg=dark_grey, relief="flat", justify=tk.LEFT, anchor=tk.W)
        empty_label.pack(fill=tk.X, expand=False, padx=10, pady=2)

        # today's date
        today_date = datetime.now().strftime("%Y-%m-%d")
        today_label = tk.Label(parent_frame, text="Date d'aujourd'hui: " + today_date, font=("Arial", 12, "bold"), fg="white", bg=dark_grey, relief="flat", justify=tk.LEFT, anchor=tk.W)
        today_label.pack(fill=tk.X, expand=False, padx=10, pady=2)

        # Read the content of the text file into a variable
        file_path = "verification_log.txt"
        with open(file_path, 'r') as file:
            whole_text = file.read()

        whole_text = whole_text.splitlines()

        # Count the number of infractions for today's date
        today_infractions = sum(1 for line in whole_text if today_date in line)

        # Display the number of infractions for today's date
        infractions_label = tk.Label(parent_frame, text=f"Infractions enregistrées aujourd'hui: {today_infractions}", font=("Arial", 12, "bold"), fg="white", bg=dark_grey, relief="flat", justify=tk.LEFT, anchor=tk.W)
        infractions_label.pack(fill=tk.X, expand=False, padx=10, pady=2)

        empty_label = tk.Label(parent_frame, font=("Arial", 12), fg="white", bg=dark_grey, relief="flat", justify=tk.LEFT, anchor=tk.W)
        empty_label.pack(fill=tk.X, expand=False, padx=10, pady=2)

        personinfraction_label = tk.Label(parent_frame, text=f"Employés à infractions récentes", font=("Arial", 12, "bold"), fg="white", bg=dark_grey, relief="flat", justify=tk.LEFT, anchor=tk.W)
        personinfraction_label.pack(fill=tk.X, expand=False, padx=10, pady=2)

        empty_label = tk.Label(parent_frame, font=("Arial", 12), fg="white", bg=dark_grey, relief="flat", justify=tk.LEFT, anchor=tk.W)
        empty_label.pack(fill=tk.X, expand=False, padx=10, pady=2)

        def extract_unique_person_names_from_file(file_path):
            with open(file_path, 'r') as file:
                lines = file.readlines()  
                lines.reverse()  # Reverse the list
                person_names = []  # Use a list to preserve order
                for line in lines:
                    parts = line.split(',')
                    if len(parts) >= 2:  
                        person_name = parts[0].split(':')[1].strip()
                        if person_name not in person_names:
                            person_names.append(person_name)
            return person_names

        # Example usage of extract_person_names_from_file function
        person_names = extract_unique_person_names_from_file("verification_log.txt")
        print(person_names)

        names_and_info_frame = tk.Frame(parent_frame, bg=dark_grey)
        names_and_info_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=2)

        # Display person's info

        info_label = None  
        image_label = None
        view_history_button = None
        

        def display_person_info(event, person_name):
            nonlocal info_label, image_label, view_history_button    

            # Clear any existing info labels and images
            if info_label is not None:
                info_label.destroy()
                info_label = None
            if image_label is not None:
                image_label.destroy()
                image_label = None
            if view_history_button is not None:
                view_history_button.destroy()        

            # DB connection
            mydb = mysql.connector.connect(
                host="127.0.0.1",
                user="root",
                password="Xhh4azsese_",
                database="smartsec2"
            )
            cursor = mydb.cursor()

            # zones autorisées
            cursor.execute("SELECT etage_technique, etage_administratif, rh_et_finance FROM autorisations2 WHERE employe = %s", (person_name,))
            autorisations_data = cursor.fetchone()
            print("autorisation_data=", autorisations_data)

            # zones_autorises string
            zones_autorises = ""
            if autorisations_data:
                if autorisations_data[0] == 1:
                    zones_autorises += "etage_technique"
                if autorisations_data[1] == 1:
                    zones_autorises += "etage_administratif"
                if autorisations_data[2] == 1:
                    zones_autorises += "rh_et_finance"


            # mini_map
            image_path = f"layout/{zones_autorises}.jpg"
            try:
                image = Image.open(image_path)
                image = image.resize((300, 225), Image.LANCZOS)  
                photo = ImageTk.PhotoImage(image)

                image_label = tk.Label(names_and_info_frame, image=photo, bg=dark_grey)
                image_label.image = photo  
                image_label.pack(fill=tk.X, expand=False, padx=10, pady=10)
            except FileNotFoundError:
                print(f"Image not found: {image_path}")
                image_label = None 

            # Fetch data from "dashboard"
            cursor.execute("SELECT * FROM dashboard2 WHERE employe = %s", (person_name,))
            data = cursor.fetchall()

            # Create a Treeview widget
            columns = ('employe', 'detections_non_autorisees', 'Etage_Technique', 'Etage_Administratif', 'RH_et_Finance')
            tree = ttk.Treeview(names_and_info_frame, columns=columns, show='headings', height=1)

            # Define headings
            tree.heading('employe', text='Employé')
            tree.heading('detections_non_autorisees', text='Détections non autorisées')
    
            tree.heading('Etage_Technique', text='Etage Technique')
            tree.heading('Etage_Administratif', text='Etage Administratif')
            tree.heading('RH_et_Finance', text='RH_et_Finance')

            # Define column widths
            tree.column('employe', width=50, anchor=tk.CENTER)
            tree.column('detections_non_autorisees', width=50, anchor=tk.CENTER)
            tree.column('Etage_Technique', width=50, anchor=tk.CENTER)
            tree.column('Etage_Administratif', width=50, anchor=tk.CENTER)
            tree.column('RH_et_Finance', width=50, anchor=tk.CENTER)

            # Insert data into the table
            for row in data:
                tree.insert('', tk.END, values=row)

            # Pack the Treeview widget
            tree.pack(fill=tk.X, expand=False, padx=10, pady=2)

            # Update the info_label reference to the new tree
            info_label = tree

            #personnal pop-up
            def open_info_popup(person_name):
                popup = tk.Toplevel()
                popup.title(f"Tracking Personnel  - {person_name}")  
                popup.configure(bg=dark_grey)

                mydb = mysql.connector.connect(
                    host="127.0.0.1",
                    user="root",
                    password="Xhh4azsese_",
                    database="smartsec2"
                )
                cursor = mydb.cursor()
                

                # personnal total number of infractions
                cursor.execute("SELECT detect_non_auto FROM dashboard2 WHERE employe = %s", (person_name,))
                total_infractions = cursor.fetchone()[0]

                mydb.close()

                total_infractions_label = tk.Label(popup, text=f"Total Infractions: {total_infractions}", font=("Arial", 12), fg="white", bg=dark_grey)
                total_infractions_label.pack()

                # personnal today's ifractions
                today_date = date.today().strftime("%Y-%m-%d")

                daily_detections = 0
                with open("verification_log.txt", "r") as file:
                    for line in file:
                        if f"Person: {person_name}" in line and f"Date and Time: {today_date}" in line:
                            daily_detections += 1

                mydb.close()

                daily_detections_label = tk.Label(popup, text=f"Infractions aujourd'hui: {daily_detections}", font=("Arial", 12), fg="white", bg=dark_grey)
                daily_detections_label.pack()


                # Fetch images + infos
                images_info = []
                with open("verification_log.txt", "r") as file:
                    lines = file.readlines()
                    for line in reversed(lines): 
                        if f"Person: {person_name}" in line:
                            match = re.search(r"Date and Time: (.+), Image: (.+), Zone: (.+)", line.strip())
                            if match:
                                date_time, image_path, zone = match.groups()
                                zone = zone.replace("_", " ")
                                images_info.append((date_time, image_path, zone))

                # frame : image = infos
                info_frame = tk.Frame(popup, bg=dark_grey)
                info_frame.pack()

                # Sort images_info by date_time in descending order
                images_info.sort(key=lambda x: datetime.strptime(x[0], "%Y-%m-%d_%H-%M-%S"), reverse=True)

                for i, (date_time, image_path, zone) in enumerate(images_info):
                    row_num = i // 5  
                    col_num = i % 5   

                    # Load and display the image
                    image = Image.open(image_path)
                    image.thumbnail((150, 150))
                    photo = ImageTk.PhotoImage(image)
                    image_label = tk.Label(info_frame, image=photo, bg=dark_grey)
                    image_label.image = photo
                    image_label.grid(row=row_num * 2, column=col_num, padx=10, pady=5)

                    # Format date and time without seconds
                    formatted_date_time = datetime.strptime(date_time, "%Y-%m-%d_%H-%M-%S").strftime("%Y-%m-%d | %Hh%M")

                    # Create label for date/time information
                    date_time_label = tk.Label(info_frame, text=f"{formatted_date_time}", font=("Arial", 12), fg="white", bg=dark_grey , justify=tk.LEFT, anchor=tk.W)
                    date_time_label.grid(row=row_num * 2 + 1, column=col_num, padx=10, pady=5)

                    # Create label for zone information
                    zone_label = tk.Label(info_frame, text=f"Zone: {zone}", font=("Arial", 12), fg="white", bg=dark_grey, justify=tk.LEFT, anchor=tk.W)
                    zone_label.grid(row=row_num * 3 + 2, column=col_num, padx=10, pady=5)

                    # Bind click event to open_info_popup function
                    image_label.bind("<Button-1>", lambda event, person=person_name: open_info_popup(person_name))

            # Bouton "voir historique en images"
            view_history_button = tk.Button(names_and_info_frame, text="voir historique en images", command=lambda: open_info_popup(person_name))
            view_history_button.pack(fill=tk.X, expand=False, pady=5)



       
                    
        info_label = None
        image_label = None
    
        # all employees
        for person_name in person_names:
            data_label = tk.Label(names_and_info_frame, text=person_name, font=("Arial", 12), fg="white", bg=dark_grey, relief="raised", justify=tk.LEFT, anchor=tk.W)
            data_label.pack(fill=tk.X, expand=False, padx=10, pady=2)
            data_label.bind("<Button-1>", lambda event, person=person_name: display_person_info(event, person))

        



    #fetch data into data
    data = fetch_data_from_database()  

    # Create a text string for data labels
    text = "\n".join([" | ".join("{:<{width}}".format(cell_data, width=25) for cell_data in row_data) for row_data in data])
    print(text)

    create_data_labels(text, right_frame)


    root.mainloop()

if __name__ == "__main__":
    authenticate()
