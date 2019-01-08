import tkinter as tk
from tkinter.ttk import *
from tkinter import filedialog
import datetime as dt
import time
from tkinter import messagebox
from tkinter import scrolledtext
import pandas as pd
import os
import pytz
import platform
from threading import Thread
import matplotlib
from noaa_weather_data_scraper import nwds
#If Mac OS we use TkAgg backend from matplotlib
if(platform.system() == "Darwin"):
    matplotlib.use('TkAgg')


class MainApp(tk.Tk):
    """ Main class of the GUI app """
    
    def __init__(self):
        tk.Tk.__init__(self)

        self._frame = None
        #Initiate at the HomePage
        self.switch_frame(HomePage)
        
    
    def switch_frame(self, frame_class, *t):
        """Switch the instance frame (destroy the last one)"""
        new_frame = frame_class(self, t)
        if self._frame is not None:
            self._frame.destroy()
        self._frame = new_frame
        self._frame.pack(padx=20, pady=20)
        
class HomePage(tk.Frame):
    
    """ HomePage design """
    def __init__(self, master, *t):
        tk.Frame.__init__(self, master)
        self['bg'] = 'white'
        
        #TITLE 
        p0_l1 = tk.Label(self, 
                         text="Collect weather data : ",
                         fg="#0c7d6a",
                         font=("Verdana", 14, "bold"),
                         justify='left',
                         bg='white')
        p0_l2 = tk.Label(self,
                         text="Select collect mode",
                         fg="#0c7d6a",
                         font=("Verdana", 11),
                         justify='left',
                         bg='white')
        
        #BUTTON
        page0_b1 = tk.Button(self, 
                             text="One zip code and specific time period",
                             relief='raised',
                             width=50,
                             command=lambda: master.switch_frame(PageOne))
        page0_b2 = tk.Button(self, 
                             text="Add weather data in csv files with M&V2.0 pattern",
                             relief='raised',
                             width=50,
                             command=lambda: master.switch_frame(PageTwo))
        
        #SET UP POSITION
        p0_l1.grid(row=0, padx=10, pady=10)
        p0_l2.grid(row=1, padx=10, pady=10)
        page0_b1.grid(row=2, padx=20, pady=10)
        page0_b2.grid(row=3, padx=20, pady=10)


class PageOne(tk.Frame):
    
    """ PageOne design : mode "one zip code" """
    def __init__(self, master, *t):
        
        tk.Frame.__init__(self, master)
        self['bg'] = 'white'
        
        #TITLE
        p1_l1 = tk.Label(self, 
                         text="Collect weather data : ",
                         fg="#0c7d6a",
                         font=("Verdana", 14, "bold"),
                         justify='left',
                         bg='white')
        p1_l2 = tk.Label(self,
                         text="Specfic zip code and time period",
                         fg="#0c7d6a",
                         font=("Verdana", 11),
                         justify='left',
                         bg='white')
        
        #BODY FRAME (FORMS)
        p1_f1 = tk.LabelFrame(self, borderwidth=2, relief='groove', text=' Collect set up ',  bg='white')
        
        #FORMS DESIGN ::
    
            #WEATHER SOURCE
        p1_f1_l1 = tk.Label(p1_f1,
                            text="\nSelect weather source :",
                            justify="left",
                            fg="#0c7d6a",
                            font=("Verdana", 10, "underline"),
                            bg='white')
        
        source = tk.StringVar(value='NOAA')
        source.set("NOAA")
        p1_f1_rad1 = tk.Radiobutton(p1_f1, text='National Oceanic and Atmospheric Administration', variable = source, value='NOAA', bg='white') 
        
        
        
            #TIME PERIOD
        p1_f1_l2 = tk.Label(p1_f1,
                            text="\nDefine Time Period :",
                            justify="left",
                            fg="#0c7d6a",
                            font=("Verdana", 10, "underline"),
                            bg='white')
        p1_f1_l3 = tk.Label(p1_f1,
                            text="Date format : mm/dd/yy H:M  (ex : 08/16/18 13:39)\n",
                            justify="left",
                            font=("Verdana", 8, "italic"),
                            bg='white')
        
        p1_f1_l4 = tk.Label(p1_f1,
                            text="First Date :",
                            justify="left",
                            font=("Verdana", 10),
                            bg='white')
        p1_f1_e1 = tk.Entry(p1_f1,width=20,bd=2, bg="#d5f2e5")
        
        p1_f1_l5 = tk.Label(p1_f1,
                            text="Last Date :",
                            justify="left",
                            font=("Verdana", 10),
                            bg='white')
        p1_f1_e2 = tk.Entry(p1_f1,width=20,bd=2, bg="#d5f2e5")
        
        
        p1_f1_l12 = tk.Label(p1_f1,
                            text="Time zone :",
                            justify="left",
                            font=("Verdana", 10),
                            bg='white')
        p1_f1_l121 = tk.Label(p1_f1,
                            text="Select your timezone",
                            justify="left",
                            font=("Verdana", 8, "italic"),
                            bg='white')
        
        tz = tk.StringVar(value='US/Pacific')
        tz.set('US/Pacific')
        tzg = tz.get()
        p1_f1_om1 = Combobox(p1_f1, state='readonly', textvariable=tzg, value=pytz.all_timezones)
        p1_f1_om1.set('US/Pacific')
        
        
            #LOCATION
        p1_f1_l6 = tk.Label(p1_f1,
                            text="\nDefine Location:",
                            justify="left",
                            fg="#0c7d6a",
                            font=("Verdana", 10, "underline"),
                            bg='white')
        p1_f1_l7 = tk.Label(p1_f1,
                            text="Country :",
                            justify="left",
                            font=("Verdana", 10),
                            bg='white')
        p1_f1_e3 = tk.Entry(p1_f1,width=20,bd=2, bg="#d5f2e5")
                            
        p1_f1_l8 = tk.Label(p1_f1,
                            text="Zip code :",
                            justify="left",
                            font=("Verdana", 10),
                            bg='white')
        p1_f1_e4 = tk.Entry(p1_f1,width=20,bd=2, bg="#d5f2e5")
                            
          #SAVE
        p1_f1_l9 = tk.Label(p1_f1,
                            text="\nOutput Folder :",
                            justify="left",
                            fg="#0c7d6a",
                            font=("Verdana", 10, "underline"),
                            bg='white')
        p1_f1_l10 = tk.Label(p1_f1,
                            text="Select folder to save the output file",
                            justify="left",
                            font=("Verdana", 8, "italic"),
                            bg='white')
        
        self.output_folder = ""
        def browsefunc():
            filename = tk.filedialog.askdirectory()
            self.output_folder = filename
            p1_f1_l11.config(text=filename)
            
        p1_f1_l11 = tk.Label(p1_f1,
                            text="...",
                            font=("Verdana", 8, "italic"),
                            justify="left",
                            bd=2,
                            relief='groove',
                            width=80,
                            bg="#d5f2e5")
        p1_f1_b1 = tk.Button(p1_f1, text="Select Folder", command=browsefunc, relief='groove')
        
        #VERIFY INPUT FORMS
        def Check_Forms():
            
            """ CHECK EACH ENTRY OF THE FORM """
            nb_error = 0
            msg_error = ""
            
            #FIRST DATE (TRY TO SET UP WITH THE GOOD FORMAT)
            try:
                first_date = dt.datetime.strptime(str(p1_f1_e1.get()), '%m/%d/%y %H:%M')
            except:
                nb_error += 1
                msg_error += "First Date format invalid \n"
            
            #LAST DATE (TRY TO SET UP WITH THE GOOD FORMAT)
            try:
                last_date = dt.datetime.strptime(str(p1_f1_e2.get()), '%m/%d/%y %H:%M')
            except:
                nb_error += 1
                msg_error += "Last Date format invalid \n"
            
            #TIMEZONE
            if(tzg == ""):
                nb_error += 1
                msg_error += "Timezone unspecified \n"
            
            #COUNTRY
            if(p1_f1_e3.get() != ""):
                cntry = p1_f1_e3.get()
            else:
                nb_error += 1
                msg_error += "Country invalid \n"
            
            #ZIP CODE
            if(len(p1_f1_e4.get()) >= 5):
                zip_code = p1_f1_e4.get()
            else:
                nb_error += 1
                msg_error += "Zip code invalid \n"
              
            #OUTPUT FOLDER
            if(self.output_folder == "" or self.output_folder == "..."):
                nb_error += 1
                msg_error += "Output Folder invalid \n"
                
            #CHECK IF ERROR(S)
            if(nb_error):
                messagebox.showerror("Error", "Error number : " + str(nb_error) + "\n\n" + msg_error)
            else:
                master.switch_frame(ValidOne, first_date,
                                    last_date,
                                    tzg,
                                    cntry,
                                    zip_code,
                                    self.output_folder)
                
        #BUTTON VALIDATE FORMS
        ok_button = tk.Button(p1_f1, text="Collect Data", relief='groove', command=Check_Forms)
        #FORMS LAY OUT
        
            #SOURCE
        p1_f1_l1.grid(row=0, columnspan=3, sticky='w', padx=5)
        p1_f1_rad1.grid(row=1, columnspan=3, sticky='w', padx=5)
        p1_f1_l2.grid(row=2, columnspan=3, sticky='w', padx=5)
        
            #TIME PERIOD
        p1_f1_l3.grid(row=3, columnspan=3, sticky='w', padx=5)
        p1_f1_l4.grid(row=4, column=0, sticky='e', padx=5)
        p1_f1_e1.grid(row=4, column=1, columnspan=2, sticky='w', padx=5)
        p1_f1_l5.grid(row=5, column=0, sticky='e', padx=5)
        p1_f1_e2.grid(row=5, column=1, columnspan=2, sticky='w', padx=5)
        p1_f1_l12.grid(row=6, column=0, sticky='e', padx=5)
        p1_f1_l121.grid(row=7, column=1, sticky='w', padx=5)
        p1_f1_om1.grid(row=6, column=1, sticky='w', padx=5)
        
            #LOCATION
        p1_f1_l6.grid(row=8, columnspan=3, sticky='w', padx=5)
        p1_f1_l7.grid(row=9, column=0, sticky='e', padx=5)
        p1_f1_e3.grid(row=9, column=1, columnspan=2, sticky='w', padx=5)
        p1_f1_l8.grid(row=10, column=0, sticky='e', padx=5)
        p1_f1_e4.grid(row=10, column=1, columnspan=2, sticky='w', padx=5)
        
            #SAVE
        p1_f1_l9.grid(row=11, columnspan=3, sticky='w', padx=5)
        p1_f1_l10.grid(row=12, columnspan=3, sticky='w', padx=5)
        p1_f1_l11.grid(row=13, columnspan=3, sticky='w', padx=5, pady=5)
        p1_f1_b1.grid(row=14, column=0, sticky='w', padx=5, pady=5)
        ok_button.grid(row=15, column=2, sticky='nsew', padx=5, pady=5)
        
            #BUTTON BACK HOME PAGE
        back_button = tk.Button(self, text="Back Home", command=lambda: master.switch_frame(HomePage), relief='groove')
        
            #LAY OUT OUTFRAME
        p1_l1.grid(row=0)
        p1_l2.grid(row=1)
        p1_f1.grid(row=2, sticky='nsew', padx=5, pady=5)
        back_button.grid(row=3, sticky='w', padx=5, pady=5)

class ValidOne(tk.Frame):
    
    """ Collect data page for mode ' one zip code ' """
    def __init__(self, master, t):
        
        tk.Frame.__init__(self, master)
        self['bg'] = 'white'
        
        #TITLE
        p3_l1 = tk.Label(self, 
                         text="Collect weather data : ",
                         fg="#0c7d6a",
                         font=("Verdana", 14, "bold"),
                         justify='left',
                         bg='white')
        #BLOCK WAITING
        p3_l2 = tk.Label(self,
                         text="Collect in progress...",
                         fg="#0c7d6a",
                         relief='sunken',
                         width=50,
                         bg='white')
        
        p3_l1.grid(row=0, padx=20, pady=10)
        p3_l2.grid(row=1, padx=20, pady=10)
        
        
        def Collect():

            """ Launch collect data (from scrape_ftp_noaa) and update the current frame """
            #t[0] = first_date
            #t[1] = last_date
            #t[2] = timezone
            #t[3] = cntry
            #t[4] = zip_code
            #t[5] = output_folder
            #Collect longitude and latitude of the zip code
            zlo, zla = nwds.GeoLocZip(t[4], t[3])
            
            #Set up the dataframe dictionnary
            nwds.Set_dict_DF(t[0], t[1])
            
            #Collect the data and some informations 
                                #data = weather data
                                #NS = Name station
                                #DO = Great circle distance
                                #rep = Response for the GUI/Console
            data, quality, NS, DO, rep = nwds.Collect_data(zlo, zla, t[0], t[1], t[4], "", t[3], t[2])
            final_data = pd.DataFrame()
            final_data['time'] = data.index.strftime('%m/%d/%y %H:%M')
            final_data['Temp'] = data['Temp'].values
            final_data['HR'] = data['HR'].values
            #Save the data in the output folder (named by zip_code.csv)
            final_data.to_csv(str(t[5])+"/"+str(t[4])+".csv", index=False)
            
            #Collect finish (refresh information's frame)
            p3_l2.configure(text="Collect completed",
                            fg='white',
                            bg="#0c7d6a")
                            
            p3_l3 = tk.Label(self,
                            text="Output File :",
                            justify="left",
                            fg="#0c7d6a",
                            font=("Verdana", 10, "underline"),
                            bg='white')
            p3_l4 = tk.Label(self,
                            text=str(t[5])+"/"+str(t[4])+".csv",
                            font=("Verdana", 8, "italic"),
                            justify="left",
                            bd=2,
                            relief='groove',
                            width=80,
                            bg="#d5f2e5")
            p3_l5 = tk.Label(self,
                            text="\nReport :",
                            justify="left",
                            fg="#0c7d6a",
                            font=("Verdana", 10, "underline"),
                            bg='white')
            txt = scrolledtext.ScrolledText(self,width=55,height=20, fg='white', bg='black', relief='sunken')
            
            #Lay out
            p3_l3.grid(row=2, padx=20)
            p3_l4.grid(row=3, padx=20)
            p3_l5.grid(row=4, padx=20)
            txt.grid(row=5, padx=5)
            
            #Insert information in the GUI console
            txt.insert(tk.INSERT, '## Collect weather data = [zip code: '+str(t[4])+']['+str(t[3])+'] ##\n')
            txt.insert(tk.INSERT, '# Got Location = [lon : '+str(round(zlo,3))+'][lat : '+str(round(zla,3))+']\n')
            txt.insert(tk.INSERT, rep)
            txt.insert(tk.INSERT, '# Global quality = '+str(round(quality, 2))+'% \n \n')
            
        self.after(2000, Collect)
        
    
class PageTwo(tk.Frame):
    
    """ PageTwo design : mode ' rmv2.0 pattern ' """
    def __init__(self, master, *t):
        tk.Frame.__init__(self, master)
        self['bg'] = 'white'
        
        #HEADER
        p2_l1 = tk.Label(self, 
                         text="Collect weather data : ",
                         fg="#0c7d6a",
                         font=("Verdana", 14, "bold"),
                         justify='left',
                         bg='white')
        p2_l2 = tk.Label(self,
                         text="Add weather data in csv files with M&V2.0 pattern\n",
                         fg="#0c7d6a",
                         font=("Verdana", 11),
                         justify='left',
                         bg='white')
        p2_l3 = tk.Label(self,
                         text="Input CSV file's fomat required :",
                         fg="#0c7d6a",
                         font=("Verdana", 9, "underline"),
                         justify='left',
                         bg='white')
        #Format table
        p2_f1 = tk.Frame(self, bg='white')
        p2_f1_l1 = tk.Label(p2_f1,
                            width=20,
                            text="buildingID",
                            relief="groove").grid(row=0, column=0)
        p2_f1_l2 = tk.Label(p2_f1,
                            width=20,
                            text="zip",
                            relief="groove").grid(row=0, column=1)
        p2_f1_l3 = tk.Label(p2_f1,
                            width=20,
                            text="country",
                            relief="groove").grid(row=0, column=2)
        p2_f1_l4 = tk.Label(p2_f1,
                            width=20,
                            text="12799",
                            fg="#6A6A6A",
                            relief="groove").grid(row=1, column=0)
        p2_f1_l5 = tk.Label(p2_f1,
                            width=20,
                            text="90018",
                            fg="#6A6A6A",
                            relief="groove").grid(row=1, column=1)
        p2_f1_l6 = tk.Label(p2_f1,
                            width=20,
                            text="US",
                            fg="#6A6A6A",
                            relief="groove").grid(row=1, column=2)
        p2_f1_l7 = tk.Label(p2_f1,
                            width=20,
                            text="time",
                            relief="groove").grid(row=2, column=0)
        p2_f1_l8 = tk.Label(p2_f1,
                            width=20,
                            text="eload",
                            relief="groove").grid(row=2, column=1)
        p2_f1_l7 = tk.Label(p2_f1,
                            width=20,
                            text="01/01/17 00:00",
                            fg="#6A6A6A",
                            relief="groove").grid(row=3, column=0)
        p2_f1_l8 = tk.Label(p2_f1,
                            width=20,
                            text="1.45",
                            fg="#6A6A6A",
                            relief="groove").grid(row=3, column=1)
        p2_f1_l7 = tk.Label(p2_f1,
                            width=20,
                            text="...",
                            fg="#6A6A6A",
                            relief="groove").grid(row=4, column=0)
        p2_f1_l8 = tk.Label(p2_f1,
                            width=20,
                            text="...",
                            fg="#6A6A6A",
                            relief="groove").grid(row=4, column=1)
        p2_f1_l7 = tk.Label(p2_f1,
                            width=20,
                            text="12/31/17 23:59",
                            fg="#6A6A6A",
                            relief="groove").grid(row=5, column=0)
        p2_f1_l8 = tk.Label(p2_f1,
                            width=20,
                            text="0.48",
                            fg="#6A6A6A",
                            relief="groove").grid(row=5, column=1)
        
        #Set up form
        p2_f2 = tk.LabelFrame(self, borderwidth=2, relief='groove', text=' Collect set up ',  bg='white')

            #SOURCE
        p2_f2_l1 = tk.Label(p2_f2,
                            text="\nSelect weather source :",
                            justify="left",
                            fg="#0c7d6a",
                            font=("Verdana", 10, "underline"),
                            bg='white')
        
        source = tk.StringVar(value='NOAA')
        
        p2_f2_rad1 = tk.Radiobutton(p2_f2, text='National Oceanic and Atmospheric Administration', variable = source, value='NOAA', bg='white') 
        
        #Location country, timezone
        p2_f2_l2 = tk.Label(p2_f2,
                            text="\nLocation parameters :",
                            justify="left",
                            fg="#0c7d6a",
                            font=("Verdana", 10, "underline"),
                            bg='white')
        p2_f2_l3 = tk.Label(p2_f2,
                            text="Time zone :",
                            justify="left",
                            font=("Verdana", 10),
                            bg='white')
        tz = tk.StringVar(value='US/Pacific')
        tz.set('US/Pacific')
        tzg = tz.get()
        p2_f2_om1 = Combobox(p2_f2, state='readonly', textvariable=tzg, value=pytz.all_timezones)
        p2_f2_om1.set('US/Pacific')
        
                            
           #Folder input
        p2_f2_l5 = tk.Label(p2_f2,
                            text="\nInput folder :",
                            justify="left",
                            fg="#0c7d6a",
                            font=("Verdana", 10, "underline"),
                            bg='white')
        p2_f2_l6 = tk.Label(p2_f2,
                            text="Select folder which contains csv files",
                            justify="left",
                            font=("Verdana", 8, "italic"),
                            bg='white')
        
        self.input_folder = ""
        def browsefunc1():
            filename = tk.filedialog.askdirectory()
            self.input_folder = filename
            p2_f2_l7.config(text=filename)
            
        p2_f2_l7 = tk.Label(p2_f2,
                            text="...",
                            font=("Verdana", 8, "italic"),
                            justify="left",
                            bd=2,
                            relief='groove',
                            width=80,
                            bg="#d5f2e5")
                            
        p2_f2_b1 = tk.Button(p2_f2, text="Select Folder", command=browsefunc1, relief='groove')
        
        
           #Folder output
        p2_f2_l8 = tk.Label(p2_f2,
                            text="\nOutput folder :",
                            justify="left",
                            fg="#0c7d6a",
                            font=("Verdana", 10, "underline"),
                            bg='white')
        p2_f2_l9 = tk.Label(p2_f2,
                            text="Select folder to save the output files",
                            justify="left",
                            font=("Verdana", 8, "italic"),
                            bg='white')
        
        self.output1_folder = ""
        def browsefunc2():
            filename = tk.filedialog.askdirectory()
            self.output1_folder = filename
            p2_f2_l10.config(text=filename)
            
        p2_f2_l10 = tk.Label(p2_f2,
                            text="...",
                            font=("Verdana", 8, "italic"),
                            justify="left",
                            bd=2,
                            relief='groove',
                            width=80,
                            bg="#d5f2e5")
        p2_f2_b2 = tk.Button(p2_f2, text="Select Folder", command=browsefunc2, relief='groove')
        
        
        def CheckForms2():
            
            """ CHECK INPUT'S FORMS """
            nb_error = 0
            msg_error = ""
            
            #OUTPUT FOLDER
            if(self.output1_folder == "" or self.output1_folder == "..."):
                nb_error += 1
                msg_error += "Output Folder invalid \n"
                
            #INPUT FOLDER
            if(self.input_folder == "" or self.input_folder == "..."):
                nb_error += 1
                msg_error += "Input Folder invalid \n"
            
            #TIMEZONE
            if(tzg == ""):
                nb_error += 1
                msg_error += "Unspecified timezone"
            
            #CHECK ERRORS
            if(nb_error):
                messagebox.showerror("Error", "Error number : " + str(nb_error) + "\n\n" + msg_error)
            else:
                master.switch_frame(ValidTwo, self.input_folder,
                                    self.output1_folder, tzg)
            #Confirm form's button
        p2_ok_button = tk.Button(p2_f2, text="Collect Data", relief='groove', width=20,command=CheckForms2)
        
        #Lay out forms
        p2_f2_l1.grid(row=0, columnspan=2, sticky='w')
        p2_f2_rad1.grid(row=1, columnspan=2, sticky='w')
        p2_f2_l2.grid(row=2, columnspan=2, sticky='w')
        p2_f2_l3.grid(row=3, column=0, sticky='e')
        p2_f2_om1.grid(row=3, column=1, sticky='w')
        p2_f2_l5.grid(row=4, columnspan=2, sticky='w')
        p2_f2_l6.grid(row=5, columnspan=2, sticky='w')
        p2_f2_l7.grid(row=6, columnspan=2, sticky='w')
        p2_f2_b1.grid(row=7, columnspan=2, sticky='w', padx=5, pady=5)
        p2_f2_l8.grid(row=8, columnspan=2, sticky='w')
        p2_f2_l9.grid(row=9, columnspan=2, sticky='w')
        p2_f2_l10.grid(row=10, columnspan=2, sticky='w')
        p2_f2_b2.grid(row=11, columnspan=2, sticky='w', padx=5, pady=5)
        p2_ok_button.grid(row=12, columnspan=2, sticky='e', padx=5, pady=5)
        
        #Back Home page button
        back2_button = tk.Button(self, text="Back Home",
                                 command=lambda: master.switch_frame(HomePage))
        #Lay out frame
        p2_l1.grid(row=0)
        p2_l2.grid(row=1)
        p2_l3.grid(row=2, sticky='w')
        p2_f1.grid(row=3, sticky='nsew', padx=5, pady=5)
        p2_f2.grid(row=4, sticky='nsew', padx=5, pady=5)
        back2_button.grid(row=5, sticky='w', padx=5, pady=5)
        
class ValidTwo(tk.Frame):

    """ Collect data page for mode "rmv2.0 pattern " """
    def __init__(self, master, t):
        
        tk.Frame.__init__(self, master)
        self['bg'] = 'white'
        
        #HEADER
        p4_l1 = tk.Label(self, 
                         text="Collect weather data : ",
                         fg="#0c7d6a",
                         font=("Verdana", 14, "bold"),
                         justify='left',
                         bg='white')
        #PROGRESS BAR
        p4_l2 = tk.Label(self,
                         text="Collect in progress : 0 %",
                         fg="#0c7d6a",
                         bg='white')
        p4_pb = Progressbar(self, length=600)
        p4_pb['value'] = 0
        
        #CONSOLE REPORT
        p4_l3 = tk.Label(self,
                            text="\nReport :",
                            justify="left",
                            fg="#0c7d6a",
                            font=("Verdana", 10, "underline"),
                            bg='white')
        txt = scrolledtext.ScrolledText(self,width=60,height=20, fg='white', bg='black', relief='sunken')
        #LAY OUT
        p4_l1.grid(row=0, padx=20, pady=10)
        p4_l2.grid(row=1, padx=20, sticky='w')
        p4_pb.grid(row=2, padx=20, sticky='w')
        p4_l3.grid(row=3, padx=20)
        txt.grid(row=4, padx=5)
        
        
        def fakef():
            """ Use another thread to don't freeze the GUI """
            self._thread = Thread(target=Collect)
            self._thread.start()
            
        def Collect():
            """ Collect data """
            #t[0] = input
            #t[1] = output
            #t[2] = timezone
            
            #Check if the input folder exist
            try : 
                in_fold = os.listdir(str(t[0]))
            except:
                messagebox.showerror("Error", "Invalid input folder")
                master.switch_frame(PageTwo)
            nf = 0
            
            #Check if something is in the input folder
            if(len(in_fold) >= 1):
                
                #Loop on each files in the input folder
                for f in in_fold:
                    nf += 1
                    
                    #Fetch only CSV files
                    if('.csv' in f):
                        
                        #console report
                        txt.insert(tk.INSERT, '### Input File = '+str(f)+' ### \n')
                                   
                        #Collect input data
                        db = pd.read_csv(t[0]+'/'+f)
                        
                        #Extract information input data
                        zip_code = db.iloc[0, 1]
                        cntry = db.iloc[0, 2]
                        
                        #Collect longitude and latitude of the zip code
                        zlo, zla = nwds.GeoLocZip(zip_code, cntry)
                        
                        #Format input date
                        first_date = dt.datetime.strptime(db.iloc[2,0], '%m/%d/%y %H:%M')
                        last_date = dt.datetime.strptime(db.iloc[-1,0], '%m/%d/%y %H:%M')
                        
                        #Set up dataframe dictionnary
                        nwds.Set_dict_DF(first_date, last_date)
                        
                        #Console report
                        txt.insert(tk.INSERT, '## Collect weather data = [zip code: '+str(zip_code)+']['+str(cntry)+'] ##\n')
                        txt.insert(tk.INSERT, '# Got Location = [lon : '+str(round(zlo,3))+'][lat : '+str(round(zla,3))+']\n')
                        
                        #Collect the data and some informations 
                                #data = weather data
                                #NS = Name station
                                #DO = Great circle distance
                                #rep = Response for the GUI/Console           
                        data, quality, NS, DO, rep = nwds.Collect_data(zlo, zla, first_date, last_date, zip_code, db['buildingID'][2:].values,cntry, t[2])
                        
                        #Console report from Collect_data()
                        txt.insert(tk.INSERT, rep)
                            
                        #Prepare output data
                            #Insert temperature data in the input data model
                            #Set up the " RMV2.0 " pattern
                        df_fil = pd.DataFrame()
                        df_fil['time'] = data.index.strftime('%m/%d/%y %H:%M')
                        print(len(df_fil))
                        print(df_fil.time)
                        print(db.buildingID)
                        print(db.buildingID[2:])
                        df_fil['eload'] = db['zip'][2:].values
                        df_fil['Temp'] = data['Temp'].values
                        
                        #Save data
                        df_fil.to_csv(t[1]+'/'+f, index=False)
                        
                        #Final report
                        txt.insert(tk.INSERT, '# Global quality = '+str(round(quality, 2))+'% \n')
                        txt.insert(tk.INSERT, '### Output File = '+str(f)+' ### \n \n')
                        
                        #Refresh progress bar and compute status
                        prog = round((nf/len(in_fold))*100)
                        p4_l2.configure(text="Collect in progress : "+str(prog)+" %")
                        p4_pb['value'] = prog
                        
                        #Frefresh App
                        app.update_idletasks()
                        
                        #Delay
                        time.sleep(1)

                    else:
                        txt.insert(tk.INSERT, '@@@ Wrong format = '+str(f)+' @@@ \n (Format expected : ".csv")\n')
        self.after(2000, fakef)
        

if __name__ == "__main__":
    
    #Launch GUI App
    app = MainApp()
    app.title("Weather data collect app")
    app['bg']= 'white'
    app.mainloop()