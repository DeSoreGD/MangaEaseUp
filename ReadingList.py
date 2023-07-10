import tkinter
import tkinter.messagebox
import customtkinter
from PIL import Image
import pickle
import os
import webbrowser

customtkinter.set_appearance_mode("System")  # Modes: "System" (standard), "Dark", "Light"
customtkinter.set_default_color_theme("dark-blue")  # Themes: "blue" (standard), "green", "dark-blue" 

     
class CheckBoxesFrame(customtkinter.CTkFrame):
    def __init__(self,master,futures,value,i,checkboxes,user_list_instance,serid):
        super().__init__(master)
        self.grid_columnconfigure(1, weight=0)
        img = futures[i][1]
        self.label = customtkinter.CTkLabel(self, image=img)
        self.label.configure(text="")
        self.label.grid(row=i, column=0, padx=10, pady=(0, 15), sticky="w")
        self.user_list_instance = user_list_instance
        def check():
            self.user_list_instance.CheckAndUncheck(self.user_list_instance,0)
            for i in checkboxes:
                if i.get() == 1:
                    self.user_list_instance.ReadManga.configure(state="normal")
                    self.user_list_instance.OpenManga.configure(state="normal")
                    return
            self.user_list_instance.ReadManga.configure(state="disabled")
            self.user_list_instance.OpenManga.configure(state="disabled")
        wrapped_text = "\n".join([value[i:i+35] for i in range(0, len(value), 35)])
        self.checkbox = customtkinter.CTkCheckBox(self, text=wrapped_text,onvalue=1,offvalue=0,command=check)
        self.checkbox.data_secret = i
        self.checkbox.grid(row=i, column=1, padx=0, pady=(0, 20), sticky="w",columnspan=2)
        checkboxes.append(self.checkbox)
        combobox_var = customtkinter.StringVar(value=user_list_instance.loaded_data[f'{serid[i]}'][2])
        chapt_values = []
        start_chapter = user_list_instance.loaded_data[serid[i]][2]
        num_chapters = user_list_instance.loaded_data[serid[i]][3]
        for f in range(start_chapter, num_chapters+1):
            chapt_values.append(f)
        self.LastChapter = customtkinter.CTkComboBox(self, values=[str(chapter) for chapter in chapt_values],variable=combobox_var)
        self.LastChapter.grid(row=i,column=2,padx=(280,5),pady=(5,25),sticky='e')
        


# box where manga shown
class MangaBox(customtkinter.CTkScrollableFrame):
    def __init__(self, master, title, values,serid,user_list_instance): 
        super().__init__(master, label_text=title)
        self.values = values
        self.serid = serid
        self.checkboxes = []
        self.configure(height=3)
        if self.values == None: return
        futures = []
        self.mycheckbox=[]
        self.user_list_instance = user_list_instance
        for i, value in enumerate(self.values):
            if os.path.exists(f"images\{serid[i]}il.png"):
                img = customtkinter.CTkImage(Image.open(f"images\{serid[i]}il.png"), size=[104, 150])
                futures.append((i,img))
                self.mycheckbox.append(CheckBoxesFrame(self,futures,value,i,self.checkboxes,self.user_list_instance,self.serid))
                self.mycheckbox[i].pack(padx=0, pady=0,anchor='nw')
            
    def get(self):
        checked_checkboxes = []
        for checkbox in self.checkboxes:
            if checkbox.get() == 1:
                checked_checkboxes.extend([[self.serid[checkbox.data_secret],self.values[checkbox.data_secret],checkbox.data_secret]]) # return two arrays because you will have several manga
        return checked_checkboxes

# the app
class ReadingUserList(customtkinter.CTkToplevel):
    def __init__(self,links):
        super().__init__()
        self.grab_set()
        self.loaded_data = links
        self.title("Reading List")
        self.geometry("800x550")
        self.minsize(815,550)
        print(links)
        self.after(250, lambda: self.iconbitmap('iconforMEU.ico'))
        # grid configuration
        self.grid_columnconfigure(1, weight=8)
        self.grid_columnconfigure(2,weight=1)
        self.grid_rowconfigure(1, weight=1)
        # Row 0
        # Search for Manga
        self.MangaSearch = customtkinter.CTkEntry(self, placeholder_text="Search for manga...")
        self.MangaSearch.grid(row=0,column=1,padx=10,pady=(10,0), sticky='ew',columnspan=2)
        self.MangaSearch.configure(height=35)
        self.MangaSearch.bind("<KeyRelease>", self.on_entry_change)
        
        # column 1
        self.makeMangaBox()
        # column 2
        # Uncheck/checkAllManga button
        self.CheckUncheckAll = customtkinter.CTkButton(master=self, text="Check All", command=lambda:self.CheckAndUncheck(None,1))
        self.CheckUncheckAll.grid(row=1,column=2,padx=(0,10),pady=10,sticky='sew')
        self.CheckUncheckAll.configure(height=50)
        #open default list
        self.OpenDefaults = customtkinter.CTkButton(master=self, text="Open defaults", command=self.OpenDefList)
        self.OpenDefaults.grid(row=1,column=2,padx=(0,10),pady=(0,70),sticky='sew')
        self.OpenDefaults.configure(height=50)
        # ReadManga Button
        self.ReadManga = customtkinter.CTkButton(master=self, text="Read", command=self.ReadMangaPress)
        self.ReadManga.grid(row=1,column=2,padx=(0,10),pady=10,sticky='new')
        self.ReadManga.configure(height=80, state="disabled")
        # Open Manga button
        self.OpenManga = customtkinter.CTkButton(master=self, text="Open in browser", command=self.OpenMangaPress)
        self.OpenManga.grid(row=1,column=2,padx=(0,10),pady=(100,0),sticky='new')
        self.OpenManga.configure(height=80, state="disabled")
        # Note About Check Read
        self.NoteACR = customtkinter.CTkLabel(self)
        self.NoteACR.configure(text="If checked and chapter is\n not changed, it makes it go\n to the last chapter",font=('Roboto Regular',14),text_color='yellow')
        self.NoteACR.grid(row=1, column=2, padx=0, pady=(190, 0), sticky="n")
    
    def makeMangaBox(self):
        values=[]
        serid=[]
        for i in self.loaded_data: values.append(self.loaded_data[f'{i}'][0])
        print(values)
        for i in self.loaded_data: serid.append(i)
        self.MangaListBox = MangaBox(self, title="Manga/Manhwa/Manhua",values=values,serid=serid,user_list_instance=self)
        self.MangaListBox.grid(row=1, column=1, padx=(10,10), pady=(10, 10), sticky="nsew")
    
    def OpenDefList(self):
        try:
            with open('defaultopenlist.pkl', 'rb') as file:
                default_list = pickle.load(file)
        except FileNotFoundError:
            default_list = {}
        if not len(default_list) > 0: return 
        for check in default_list:
            webbrowser.open_new_tab(default_list[check][0])
    
    def OpenMangaPress(self):
        checked_boxes = self.MangaListBox.get()
        if len(checked_boxes) == 0: return #??? it can't be 0 anyways when you press it, comment it after
        for check in checked_boxes:
            webbrowser.open_new_tab(self.loaded_data[check[0]][1])
    
    def on_entry_change(self,event):
        value = self.MangaSearch.get()
        if value == '':
            for i in self.MangaListBox.mycheckbox: 
                if not i.winfo_ismapped():
                    i.pack(padx=0, pady=0,anchor='nw')
        for i,checkbox in enumerate(self.MangaListBox.checkboxes): 
            if value.lower() not in checkbox.cget("text").lower():
                self.MangaListBox.mycheckbox[i].pack_forget()
            else:
                if not checkbox.winfo_ismapped():
                    self.MangaListBox.mycheckbox[i].pack(padx=0, pady=0,anchor='nw')
                    

    def ReadMangaPress(self):
        checked_boxes = self.MangaListBox.get()
        if len(checked_boxes) == 0: return #??? it can't be 0 anyways when you press it, comment it after
        class AreYouSureWindow(customtkinter.CTkToplevel):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.geometry("330x100")
                self.grab_set()
                self.title('Confirm')

                def button1():
                    self.destroy()
                    self.result = True
                
                def button2():
                    self.destroy()
                    self.result = False
                
                self.label = customtkinter.CTkLabel(self, text="Are you sure?", fg_color="transparent")
                self.label.grid(row=0,column=0,columnspan=2,sticky='n')
                
                self.button1 = customtkinter.CTkButton(self, text="Yes", command=button1)
                self.button1.grid(row=1,column=0,padx=10,pady=10,sticky='se')
                
                self.button2 = customtkinter.CTkButton(self, text="No", command=button2)
                self.button2.grid(row=1,column=1,padx=10,pady=10,sticky='sw')
        wind = AreYouSureWindow()
        self.wait_window(wind)
        if not hasattr(wind, 'result'): return
        if not wind.result:
            return
        try:
            with open('list.pkl', 'rb') as file:
                list = pickle.load(file)
        except FileNotFoundError:
            print('error')
            return
        for check in checked_boxes:
            print(check)
            lastchap=int(self.MangaListBox.mycheckbox[check[2]].LastChapter.get())
            if lastchap == self.loaded_data[check[0]][2]:
                for item in list:
                    if list[f'{item}'][0] == int(check[0]):
                        print(item, ' ', {check[0]})
                        list[f'{item}'][4]=self.loaded_data[f'{check[0]}'][3]
                        del self.loaded_data[f'{check[0]}']
                        break
            elif lastchap < self.loaded_data[check[0]][3]:
                self.loaded_data[f'{check[0]}'][2]=lastchap
                for item in list:
                    if list[f'{item}'][0] == int(check[0]):
                        list[f'{item}'][4]=lastchap
                        break
            else:
                for item in list:
                    if list[f'{item}'][0] == int(check[0]):
                        print(item, ' ', {check[0]})
                        list[f'{item}'][4]=self.loaded_data[f'{check[0]}'][3]
                        del self.loaded_data[f'{check[0]}']
                        break
        self.MangaListBox.destroy()
        self.makeMangaBox()
        with open('list.pkl', 'wb') as file:
            pickle.dump(list, file)
        with open('newchapslinks.pkl', 'wb') as file:
            pickle.dump(self.loaded_data, file)
                

    def CheckAndUncheck(self,_,whattype):
        if whattype == 0:
            for i in range(len(self.MangaListBox.mycheckbox)):
                if self.MangaListBox.mycheckbox[i].checkbox.get()==0:
                    self.CheckUncheckAll.configure(text="Check All")
                    return
            self.CheckUncheckAll.configure(text="Uncheck All")
            return
        for i in range(len(self.MangaListBox.mycheckbox)):
            if self.MangaListBox.mycheckbox[i].checkbox.get()==0:
                for j in range(len(self.MangaListBox.mycheckbox)):
                    self.MangaListBox.mycheckbox[j].checkbox.select()
                self.CheckUncheckAll.configure(text="Uncheck All")
                self.ReadManga.configure(state="normal")
                self.OpenManga.configure(state="normal")
                return
        for i in range(len(self.MangaListBox.mycheckbox)):
            self.MangaListBox.mycheckbox[i].checkbox.deselect()
        self.CheckUncheckAll.configure(text="Check All")
        self.ReadManga.configure(state="disabled")
        self.OpenManga.configure(state="disabled")