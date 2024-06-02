import customtkinter as ctk
import os, cv2, time, threading, mysql.connector
from datetime import datetime
from pygrabber.dshow_graph import FilterGraph
from PIL import Image
from detect import VehicleDetection
from multiprocessing import Process, Queue


ctk.set_appearance_mode("dark")  # Modes: "System" (standard), "Dark", "Light"
ctk.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue")


class LPUpdater(threading.Thread):
    def __init__(self, app):
        super().__init__()
        self.daemon = True
        self.app = app
        self.last_lp = None

    # Inside the LPUpdater class
    def run(self):
        while True:
            if not message_queue.empty():
                message = message_queue.get()
                print('Message: ', message)
                gate_id, lp, car_type = message
                if lp != self.last_lp:
                    self.last_lp = lp
                    self.app.on_existed_car(gate_id, lp, car_type)
            time.sleep(0.1)


class App(ctk.CTk):
    def __init__(self, mydb, gate_id):
        super().__init__()

        self.mydb = mydb
        self.cursor = mydb.cursor()

        self.processes = {}

        self.cursor.execute('SELECT id FROM gates')
        ids = self.cursor.fetchall()

        if len(ids) > 0:
            for id in ids:
                self.start_detection_process(id)


        self.screen_width = self.winfo_screenwidth()
        self.screen_height = self.winfo_screenheight()

        self.gateBtns = {}
        self.gate_id = gate_id
        self.addGate = None
        self.deleteGate = None
        self.gate_btn = None
        self.open_gate = None
        self.close_gate = None
        self.existed_car = False
        self.LP_content = None

        self.fg_color = "#1F6AA5"

        self.title("Gate App")
        self.geometry(f"{self.screen_width}x{self.screen_height}+0+0")

        self.grid_columnconfigure((1, 2, 3), weight=1)
        self.grid_rowconfigure(0, weight=1)

        if self.open_gate:
            self.open_gate.destroy()
        
        if self.close_gate:
            self.close_gate.destroy()

        # create sidebar frame with widgets
        self.sidebar_frame = ctk.CTkFrame(self, corner_radius=5)
        self.sidebar_frame.grid(row=0, column=0, rowspan=10, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure((3), weight=1)

        self.sidebar_frame_width = calcProc(15, self.screen_width)
        self.sidebar_frame.configure(width=self.sidebar_frame_width)

        self.gateList = ctk.CTkLabel(self.sidebar_frame, text="Opțiuni poartă", font=ctk.CTkFont(size=20, weight="bold"))
        self.gateList.grid(row=0, column=0, padx=20, pady=20)

        self.gateFrame = ctk.CTkFrame(self.sidebar_frame, fg_color='transparent')
        self.gateFrame.grid(row=1, column=0, pady=0, padx=0, sticky='nsew')

        self.btnsUpdate()
        
        
        # create video feed with buttons
        self.videoContainer = ctk.CTkFrame(self, corner_radius=5)
        self.videoContainer.grid(row=0, column=1, padx=20, pady=20, rowspan=5, sticky="nsew")

        self.videoContainerWidth = calcProc(70, self.screen_width)
        self.videoContainer.configure(width=self.videoContainerWidth)
        self.videoContainer.configure(height=calcProc(85, self.screen_height))

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.video = ctk.CTkFrame(self.videoContainer)
        self.video.grid(row=0, column=0, padx=30, pady=(50, 30), sticky="nsew")

        self.videoWidth = calcProc(80, self.videoContainerWidth)
        self.video.configure(width=self.videoWidth)
        self.video.configure(height=calcProc(65, self.screen_height))


        self.video.columnconfigure((0, 1), weight=1)
        self.video.rowconfigure((0, 1), weight=1)

        self.videoContainer.grid_columnconfigure(0, weight=1)

        self.btns = ctk.CTkFrame(self.videoContainer, fg_color='transparent')
        self.btns.grid(row=1, column=0, padx=20, pady=(20, 0), sticky="nsew")

        self.btns.grid_columnconfigure((0, 1), weight=1)


        #license plates area
        self.LP_container = ctk.CTkFrame(self)
        self.LP_container.grid(row=0, column=2, padx=20, pady=20, sticky='nsew')
        self.LP_container.grid_columnconfigure((0), weight=1)
        self.LP_container.grid_rowconfigure(1, weight=1)

        self.LP_label = ctk.CTkLabel(self.LP_container, 
                                     text='Număr de înmatriculare', 
                                     font=ctk.CTkFont(size=18, weight="bold"))
        self.LP_label.grid(row=0, column=0, pady=20, padx=20, sticky='nsew')

        self.LP_c2 = ctk.CTkLabel(self.LP_container, 
                                     text='Nu exista date', 
                                     font=ctk.CTkFont(size=14, weight="bold"))
        self.LP_c2.grid(row=1, column=0, pady=20, padx=20, sticky='nsew')

    
    def alternate_color(self, gate_id):
        self.fg_color = '#FF9500' if self.fg_color == '#1F6AA5' else '#1F6AA5'
        self.gate_btn.configure(fg_color=self.fg_color)
        self.after(500, self.alternate_color, gate_id)
    
    def on_existed_car(self, gate_id, msg, car_type):
        if car_type == 0:
            self.openGate()
            self.LP_content = msg
            self.addEntry(car_type)
        else:
            self.existed_car = True
            self.LPDetected(msg)
            self.gateView(gate_id)
            self.alternate_color(gate_id)
            self.LP_content = msg
            self.addEntry(car_type)


    def addGateFunction(self):
        if self.video:
            self.video.destroy()

        self.video = ctk.CTkFrame(self.videoContainer)
        self.video.grid(row=0, column=0, padx=30, pady=(50, 30), sticky="nsew")

        self.video.configure(width=self.videoWidth)
        self.video.configure(height=calcProc(65, self.screen_height))


        self.video.columnconfigure((0, 1), weight=1)
        self.video.rowconfigure((0, 1), weight=1)

        # Create gateName entry widget inside gateDetails frame
        self.gateName = ctk.CTkEntry(self.video, placeholder_text='Denumire Poarta')
        self.gateName.grid(row=0, column=0, padx=100, pady=(200, 20), columnspan=3, sticky='nsew')

        #create webcams dropdown
        self.webcamsLabel = ctk.CTkLabel(self.video, text='Selecteaza camera')
        self.webcamsLabel.grid(row=1, column=0, padx=20, pady=20, sticky='nsew')

        self.webcams, self.camsDict = self.getCameras()

        self.var = ctk.StringVar(value='')
        
        self.webcamsDropDown = ctk.CTkOptionMenu(master=self.video, variable=self.var, values=self.webcams)
        self.webcamsDropDown.grid(row=1, column=2, pady=20, padx=20, sticky='nsew')

        self.addGateBtn = ctk.CTkButton(self.video, text='Adauga și pornește detectarea', command=lambda: self.selectVariant())
        self.addGateBtn.grid(row=3, column=1, rowspan=3, sticky='nsew', pady=(50, 200))

        

    
    def getCameras(self):
        cameras = {}
        graph = FilterGraph()

        variants = graph.get_input_devices()
        
        for i, variant in enumerate(variants):
            cameras[i] = variant

        return variants, cameras


    def selectVariant(self):


        gate_name = self.gateName.get()
        chosenCamera = self.webcamsDropDown.get()

        for id, title in self.camsDict.items():
            if title == chosenCamera:
                try:
                    sql = "INSERT INTO gates (id, name, camera) VALUES (%s, %s, %s)"
                    val = (id, gate_name, chosenCamera)

                    self.cursor.execute(sql, val)
                    self.mydb.commit()
                    self.start_detection_process(id)
                except Exception as e:
                    print(e)
                self.btnsUpdate()


    def btnsUpdate(self):
        if self.gate_btn:
            self.gate_btn.destroy()

        self.cursor.execute("SELECT * FROM gates")
        rows = self.cursor.fetchall()
        rowNr = 0
        for row in rows:
            id = row[0]
            name = row[1]

            btn_command = lambda gate_id=id: self.gateView(gate_id)
            self.gate_btn = ctk.CTkButton(self.gateFrame, text=name, command=btn_command)
            self.gate_btn.grid(row=rowNr, column=0, pady=(20, 0), padx=20, sticky='nsew')
            rowNr += 1
        if len(rows) >= 1:
            if self.addGate:
                self.addGate.destroy()

            self.deleteGate = ctk.CTkButton(self.sidebar_frame, text="Șterge poartă", fg_color='#F62B2B', cursor='hand2', command=lambda: self.deleteGateCommand(id))
            self.deleteGate.grid(row=6, column=0, padx=20, pady=(10, 20))
        else:
            if self.deleteGate:
                self.deleteGate.destroy()

            self.addGate = ctk.CTkButton(self.sidebar_frame, text="Adaugă poartă", command=lambda: self.addGateFunction())
            self.addGate.grid(row=5, column=0, padx=20, pady=10)


    def LPDetected(self, lp_text):
        self.LP_container.grid_rowconfigure((4), weight=1)
        self.LP_container.grid_rowconfigure(1, weight=0)

        self.LP_c2 = ctk.CTkFrame(self.LP_container)
        self.LP_c2.grid(row=1, column=0, pady=20, padx=20, sticky='nsew')
        self.LP_c2.columnconfigure(0, weight=1)

        self.LP_img = ctk.CTkImage(dark_image=Image.open(os.path.join('app', 'img', 'lp_img.jpg')), size=(100, 25))

        self.LP_img_container = ctk.CTkLabel(self.LP_c2, text='', image=self.LP_img)
        self.LP_img_container.grid(row=0, column=0, pady=(30, 10), padx=20, sticky='nsew')

        self.LP_text_string = ctk.CTkLabel( self.LP_c2, 
                                            text=lp_text,
                                            font=ctk.CTkFont(size=28, weight='bold'), 
                                            text_color=("gray10", '#FAFAFA'))
        self.LP_text_string.grid(row=1, column=0, pady=(20, 50), padx=20, sticky='nsew')

        self.LP_c3 = ctk.CTkFrame(self.LP_container)
        self.LP_c3.grid(row=2, column=0, pady=20, padx=20, sticky='nsew')
        self.LP_c3.columnconfigure((0, 1), weight=1)

        self.add_to_label = ctk.CTkLabel(self.LP_c3, text='Adaugă la', anchor='w')
        self.add_to_label.grid(row=0, column=0, pady=20, padx=20, sticky='nsew')

        self.add_to = ctk.CTkOptionMenu(self.LP_c3, values=['White List', 'Black List'])
        self.add_to.grid(row=0, column=1, pady=20, padx=20)

        self.person_name = ctk.CTkEntry(self.LP_c3, placeholder_text='Detinator autovehicul')
        self.person_name.grid(row=1, column=0, pady=10, columnspan=2, padx=20, sticky='nsew')

        self.LP_entry = ctk.CTkEntry(self.LP_c3, placeholder_text=lp_text)
        self.LP_entry.grid(row=2, column=0, pady=10, columnspan=2, padx=20, sticky='nsew')

        self.LP_c4 = ctk.CTkFrame(self.LP_container,fg_color='transparent')
        self.LP_c4.grid(row=4, column=0, pady=20, padx=20, sticky='e')
        self.LP_c4.columnconfigure(1, weight=1)

        self.add_to_btn = ctk.CTkButton(self.LP_c4, text='Adaugă', command=lambda: self.addTo)
        self.add_to_btn.grid(row=0, column=1, pady=10, padx=10, sticky='e')


    def gateView(self, gate_id):
        self.gate_btn.configure(fg_color='#1F6AA5')
        if self.video:
            self.video.destroy()

        self.video = ctk.CTkFrame(self.videoContainer)
        self.video.grid(row=0, column=0, padx=30, pady=(50, 30), sticky="nsew")

        self.video.configure(width=self.videoWidth)
        self.video.configure(height=calcProc(65, self.screen_height))


        self.video.columnconfigure((0, 1), weight=1)
        self.video.rowconfigure((0, 1), weight=1)

        if self.existed_car:
            self.car_img = ctk.CTkImage(dark_image=Image.open(os.path.join('app', 'img', 'car_img.jpg')), size=(self.videoWidth, calcProc(65, self.screen_height)))
            
            self.carImg = ctk.CTkLabel(self.video, text='', image=self.car_img)
            self.carImg.grid(row=0, column=0, padx=0, pady=0, rowspan=5, columnspan=2, sticky='nsew')
        
        else:
            self.carImg = ctk.CTkLabel(self.video, text='Nu sunt detectate autovehicule')
            self.carImg.grid(row=0, column=0, padx=0, pady=0, rowspan=5, columnspan=2, sticky='nsew')

        self.carImg.configure(width=self.videoWidth)
        self.carImg.configure(height=calcProc(65, self.screen_height))
        
        self.open_gate = ctk.CTkButton(self.btns, text='Deschide poarta', command=self.openGate)
        self.open_gate.grid(row=0, column=0, pady=5, padx=5)

        self.close_gate = ctk.CTkButton(self.btns, 
                                        text='Închide poarta', 
                                        command=self.closeGate,
                                        fg_color='#F62B2B')
        self.close_gate.grid(row=0, column=1, pady=5, padx=5)


    def start_detection_process(self, gate_id):
        detector = VehicleDetection(gate_id, message_queue)
        p = Process(target=detector.process_video)
        p.start()
        self.processes[gate_id] = p

    def deleteGateCommand(self, gate_id):
        try:
            sql = "SELECT * FROM gates WHERE id = %s"
            self.cursor.execute(sql, (gate_id,))
            gate = self.cursor.fetchone()

            if gate:
                sql = "DELETE FROM gates WHERE id = %s"
                self.cursor.execute(sql, (gate_id,))
                self.mydb.commit()

                if gate_id in self.processes:
                    self.processes[gate_id].terminate()
                    del self.processes[gate_id]
                self.btnsUpdate()

                print('Button Deleted')
        except Exception as e:
            print('Error: ', e)


    def openGate(self):
        print('Opening gate')
        self.existed_car = False


    def closeGate(self):
        print('Closing gate')
        self.existed_car = False


    def addEntry(self, car_type):
        if self.LP_content is not None:
            if car_type != 0:
                sql = "SELECT * FROM `white list` WHERE license_plate = %s"
                values = (self.LP_content,)
                self.cursor.execute(sql, values)

                result = self.cursor.fetchone()

                if result:
                    name = result['person']

                else:
                    self.dialog = ctk.CTkInputDialog(text='Detinatorul autovehiculului: ', title='Detalii')
                    
                    while self.dialog.get_input() is None:
                        self.dialog = ctk.CTkInputDialog(text='Detinatorul autovehiculului: ', title='Detalii')

                    name = self.dialog.get_input()

                sql = "INSERT INTO entries (license_plate, person, intrare) VALUES (%s, %s, %s)"
                val = (self.LP_content, name, datetime.now())

                try:
                    self.cursor.execute(sql, val)
                    self.mydb.commit()
                except Exception as e:
                    print('Error: ', e)
            else:
                sql = "INSERT INTO entries (license_plate, person, intrare) VALUES (%s, %s, %s)"
                val = (self.LP_content, 'Autospeciala', datetime.now())

                try:
                    self.cursor.execute(sql, val)
                    self.mydb.commit()
                except Exception as e:
                    print('Error: ', e)

    def addOut(self):
        pass


    def addTo(self):
        name = self.person_name.get()
        where = self.add_to.get()

        if name is None or where is None:
            self.name_val = ctk.CTkLabel(self.LP_c3, text='Completati toate rubricile', text_color='red', font=ctk.CTkFont(size=12, weight='bold'))
            self.name_val.grid(row=4, column=0, pady=5, padx=10)
            if name is None:
                self.person_name.configure(border_color = 'red')
            if where is None:
                self.add_to.configure(border_color = 'red')


def calcProc(proc, value):
    return proc * value / 100


def connectDB():
    try:
        mydb = mysql.connector.connect(
            host='127.0.0.1',
            port=3306,
            user='root',
            password='Start12345!',
            database='management'
        )
        mycursor = mydb.cursor()

        mycursor.execute("SHOW TABLES LIKE 'gates'")
        table_exists = mycursor.fetchone()
        if not table_exists:
            mycursor.execute("CREATE TABLE gates (id INT PRIMARY KEY, name VARCHAR(255), camera VARCHAR(255))")

        mycursor.execute("SHOW TABLES LIKE 'white list'")
        table_exists = mycursor.fetchone()
        if not table_exists:
            mycursor.execute("CREATE TABLE `white list` (id INT AUTO_INCREMENT PRIMARY KEY, license_plate VARCHAR(255), person VARCHAR(255))")

        mycursor.execute("SHOW TABLES LIKE 'black list'")
        table_exists = mycursor.fetchone()
        if not table_exists:
            mycursor.execute("CREATE TABLE `black list` (id INT AUTO_INCREMENT PRIMARY KEY, license_plate VARCHAR(255), person VARCHAR(255))")

        mycursor.execute("SHOW TABLES LIKE 'entries'")
        table_exists = mycursor.fetchone()
        if not table_exists:
            mycursor.execute("CREATE TABLE `entries` (id INT AUTO_INCREMENT PRIMARY KEY, license_plate VARCHAR(255), person VARCHAR(255), intrare TIMESTAMP, iesire TIMESTAMP)")
        
        return mydb
    except mysql.connector.Error as err:
        print('Error:', err)
        print('Creating database...')
        try:
            mydb = mysql.connector.connect(
                host='127.0.0.1',
                port=3306,
                user='root',
                password='Start12345!'
            )
            mycursor = mydb.cursor()

            mycursor.execute('CREATE DATABASE management')

            mydb = mysql.connector.connect(
                host='127.0.0.1',
                port=3306,
                user='root',
                password='Start12345!',
                database='management'
            )
            
            mycursor.execute("SHOW TABLES LIKE 'gates'")
            table_exists = mycursor.fetchone()
            if not table_exists:
                mycursor.execute("CREATE TABLE gates (id INT PRIMARY KEY, name VARCHAR(255), camera VARCHAR(255))")

            mycursor.execute("SHOW TABLES LIKE 'white list'")
            table_exists = mycursor.fetchone()
            if not table_exists:
                mycursor.execute("CREATE TABLE `white list` (id INT AUTO_INCREMENT PRIMARY KEY, license_plate VARCHAR(255), person VARCHAR(255))")

            mycursor.execute("SHOW TABLES LIKE 'black list'")
            table_exists = mycursor.fetchone()
            if not table_exists:
                mycursor.execute("CREATE TABLE `black list` (id INT AUTO_INCREMENT PRIMARY KEY, license_plate VARCHAR(255), person VARCHAR(255))")
            
            mycursor.execute("SHOW TABLES LIKE 'entries'")
            table_exists = mycursor.fetchone()
            if not table_exists:
                mycursor.execute("CREATE TABLE `entries` (id INT AUTO_INCREMENT PRIMARY KEY, license_plate VARCHAR(255), person VARCHAR(255), intrare TIMESTAMP, iesire TIMESTAMP)")
            
            return mydb
        except mysql.connector.Error as err:
            print('Error creating database:', err)


message_queue = Queue()

if __name__ == "__main__":
    gate_id = 0

    mydb = connectDB()

    app = App(mydb, gate_id)

    updater = LPUpdater(app)
    updater.start()

    app.mainloop()


