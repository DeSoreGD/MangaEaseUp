import tkinter
import tkinter.messagebox
import customtkinter
from PIL import Image
import api
import pickle
import os
from math import floor
import webbrowser
#import numpy as np


customtkinter.set_appearance_mode("System")  # Modes: "System" (standard), "Dark", "Light"
customtkinter.set_default_color_theme("dark-blue")



class MangaSetUpWindow(customtkinter.CTkToplevel):
    def __init__(self, series,callback=None):
        # for _ in checked_boxes(next button returns to the for(mean new manhwa))
        super().__init__()
        self.title("Adding Manga")
        self.geometry("480x335")
        self.minsize(480,335)
        self.grab_set()
        self.after(250, lambda: self.iconbitmap('iconforMEU.ico'))
        
        def SetUppingManga(loaded_data):
            class MangaBox(customtkinter.CTkFrame):
                def __init__(self,master,manga_index,loaded_data):
                    self.loaded_data = loaded_data
                    super().__init__(master)
                    self.configure(fg_color="transparent")
                    if os.path.exists(f"images\{series[manga_index][0]}il.png"):
                        img = customtkinter.CTkImage(Image.open(f"images\{series[manga_index][0]}il.png"), size=[139,200])
                        imghold = customtkinter.CTkLabel(self, image=img)
                        imghold.configure(text="")
                        imghold.grid(row=1,column=0,padx=15, pady=15,sticky="w")
                    def getVariables():
                        for j in self.loaded_data:
                            if self.loaded_data[j][0]==series[manga_index][0] and len(self.loaded_data[j])>3:
                                self.currentUrl= customtkinter.StringVar(self, self.loaded_data[j][3])
                                self.currentChapter=customtkinter.StringVar(self, str(self.loaded_data[j][4]))
                                self.combobox_var = customtkinter.StringVar(value=self.loaded_data[j][5])
                                return
                        self.currentUrl= None
                        self.currentChapter=None
                        self.combobox_var = None
                    getVariables()
                    self.DoneAlready = False
                    wrapped_text = "\n".join([series[manga_index][1][i:i+45] for i in range(0, len(series[manga_index][1]), 45)])
                    MangaName = customtkinter.CTkLabel(self,text=wrapped_text,font=('Roboto Regular',20))
                    MangaName.grid(row=0,column=0,padx=15, pady=5,sticky="n",columnspan=4)
                    
                    self.labelUrlPref = customtkinter.CTkLabel(self,text='Preffered URL to open:',font=('Roboto Regular',14))
                    self.labelUrlPref.grid(row=1,column=1,padx=5, pady=(0,0),sticky="nw",columnspan=2)
                    grouptransl=api.get_group_scanlating(series[manga_index][0])
                    self.UrlPreffered = customtkinter.CTkEntry(self,textvariable=self.currentUrl, placeholder_text="URL",width=250)
                    self.UrlPreffered.grid(row=1,column=1,padx=5,pady=(25,0),sticky='n')

                    self.labelLastChapter = customtkinter.CTkLabel(self,text='Last Chapter Readed:',font=('Roboto Regular',14))
                    self.labelLastChapter.grid(row=1,column=1,padx=5, pady=(55,0),sticky="nw",columnspan=2)
                    
                    self.LastChapter = customtkinter.CTkEntry(self, textvariable=self.currentChapter, placeholder_text="Chapter Number",width=150)
                    self.LastChapter.grid(row=1,column=1,padx=5,pady=(80,0),sticky='nw')
                    
                    self.labelGrouptranslating = customtkinter.CTkLabel(self,text='Group which translates:',font=('Roboto Regular',14))
                    self.labelGrouptranslating.grid(row=1,column=1,padx=5, pady=(110,0),sticky="nw",columnspan=2)
                    # in combobox text hold text=don't choose if you want ...?
                    self.Grouptranslating = customtkinter.CTkComboBox(self,state='readonly', values=[chapter['name'] for chapter in grouptransl['groups']],width=150, variable=self.combobox_var)
                    self.Grouptranslating.grid(row=1,column=1,padx=5,pady=(135,0),sticky='nw')
                    
                    self.ToDefaultListCheck = customtkinter.CTkCheckBox(self, text="Save it in default list")
                    self.ToDefaultListCheck.grid(row=2,column=0,padx=(5,5),pady=0,sticky='sw')
                    
                    def DoneButt(manga_index):
                        def FindTheRightOneAndAdd(url):
                            if self.ToDefaultListCheck.get() == 1: # add to default open list if checked
                                try:
                                    with open('defaultopenlist.pkl', 'rb') as file:
                                        default_list = pickle.load(file)
                                        #[seriesid][url]
                                except FileNotFoundError:
                                    default_list = {}
                                for i in self.loaded_data:
                                    if self.loaded_data[i][0]==series[manga_index][0]:
                                        del self.loaded_data[f'{i}']
                                        new_dict = {}
                                        for j, value in enumerate(self.loaded_data.values(), start=1):
                                            new_dict[str(j)] = value
                                        self.loaded_data = new_dict
                                        break
                                with open('list.pkl', 'wb') as file:
                                    pickle.dump(self.loaded_data, file)
                                if len(default_list) > 0:
                                    for dseries in default_list:
                                        if int(dseries) == series[manga_index][0]:
                                            default_list[dseries]=[url,series[manga_index][1]]
                                            self.DoneAlready = True
                                            with open('defaultopenlist.pkl', 'wb') as file:
                                                pickle.dump(default_list, file)
                                if self.DoneAlready: return
                                default_list[f'{series[manga_index][0]}']=[url,series[manga_index][1]]
                                self.DoneAlready = True
                                with open('defaultopenlist.pkl', 'wb') as file:
                                    pickle.dump(default_list, file)
                                return
                            if self.DoneAlready: 
                                self.DoneAlready = False
                                return
                            def changeInReadingList(seriesid,lastchapter):
                                try:
                                    with open('newchapslinks.pkl', 'rb') as file:
                                        reading_list = pickle.load(file)
                                except FileNotFoundError:
                                    reading_list = {}
                                if len(reading_list) > 0:
                                    for series in reading_list:
                                        if int(series) == int(seriesid):
                                            if reading_list[f'{series}'][3] == lastchapter:
                                                del reading_list[series]
                                                break
                                            else:
                                                reading_list[f'{series}'][2]=lastchapter
                                            with open('newchapslinks.pkl', 'wb') as file:
                                                pickle.dump(reading_list, file)
                            for j in self.loaded_data:
                                if self.loaded_data[j][0]==series[manga_index][0] and len(self.loaded_data[j])>3:
                                    self.loaded_data[j][3]=url 
                                    group=self.Grouptranslating.get()
                                    if group != '': #                            two times the same code(bellow) make it def?
                                        for f in grouptransl['groups']:
                                            if f['name'] == group:
                                                self.loaded_data[j][5]=f['name']
                                    else:
                                        for f in grouptransl['groups']: 
                                            self.loaded_data[j][5]=f['name']
                                            break
                                    # getting and checking what chapter is set
                                    if self.LastChapter.get() == '':
                                        self.loaded_data[j][4] = 1
                                    else:
                                        try:
                                            last_chapter = float(self.LastChapter.get())
                                            if last_chapter.is_integer():
                                                self.loaded_data[j][4] = int(last_chapter)
                                            else:
                                                self.loaded_data[j][4] = floor(last_chapter)
                                            changeInReadingList(self.loaded_data[j][0], self.loaded_data[j][4])
                                        except ValueError:
                                            self.loaded_data[j][4] = 1
                                    break
                                elif self.loaded_data[j][0]==series[manga_index][0] and len(self.loaded_data[j])==3:
                                    # getting and checking what chapter is set
                                    if self.LastChapter.get() == '':
                                        self.loaded_data[j].extend([url,1])
                                    else:
                                        try:
                                            last_chapter = float(self.LastChapter.get())
                                            if last_chapter.is_integer():
                                                self.loaded_data[j].extend([url,int(last_chapter)])
                                            else:
                                                floor(last_chapter)
                                                self.loaded_data[j].extend([url,int(last_chapter)])
                                            changeInReadingList(self.loaded_data[j][0], self.loaded_data[j][4])
                                        except ValueError:
                                            self.loaded_data[j][4] = 1
                                    group=self.Grouptranslating.get()
                                    if group != '':
                                        for f in grouptransl['groups']:
                                            if f['name'] == group:
                                                self.loaded_data[j].append(f['name'])
                                                break
                                    else:
                                        for f in grouptransl['groups']:
                                            self.loaded_data[j].append(f['name'])
                                            break
                                    self.loaded_data[j].append(None)
                                    break
                        if self.UrlPreffered.get() == '':
                            url = api.get_specific_series(series[manga_index][0])
                            FindTheRightOneAndAdd(url['url'])
                        else:
                            FindTheRightOneAndAdd(self.UrlPreffered.get())
                        if len(series)<manga_index+2:
                            print(self.loaded_data,' ae')
                            save_data(self.loaded_data)
                        else:
                            self.destroy()
                            SetUppingManga(self.loaded_data)
                    
                    self.DoneButton = customtkinter.CTkButton(self, text="Done", command=lambda:DoneButt(manga_index),fg_color='green')
                    self.DoneButton.grid(row=1,column=1,padx=(130,5), pady=(50,0),sticky="se",columnspan=3)
                    def CheckButt():
                        url = api.get_specific_series(series[manga_index][0])
                        webbrowser.open_new_tab(url['url'])
                    self.CheckButton = customtkinter.CTkButton(self, text="Check", command=CheckButt,fg_color='green')
                    self.CheckButton.configure(width=50)
                    self.CheckButton.grid(row=1,column=1,padx=(5,5), pady=(50,0),sticky="sw")
            self.current_manga_index+=1
            s=MangaBox(self,self.current_manga_index,loaded_data)
            s.pack()
            
        try:
            with open('list.pkl', 'rb') as file:
                self.loaded_data = pickle.load(file)
        except FileNotFoundError:
            self.loaded_data = {}
        self.current_manga_index = -1
        SetUppingManga(self.loaded_data)
        #save before exeting the app
        def save_data(loaded_data=self.loaded_data):
            if not callback == None: callback()
            with open('list.pkl', 'wb') as file:
                pickle.dump(loaded_data, file)
            self.destroy()
            
        self.protocol("WM_DELETE_WINDOW", save_data)
        