import tkinter
import tkinter.messagebox
import customtkinter
from PIL import Image
import MSUW,MSUWFDL
import pickle
import os

customtkinter.set_appearance_mode("System")  # Modes: "System" (standard), "Dark", "Light"
customtkinter.set_default_color_theme("dark-blue")  # Themes: "blue" (standard), "green", "dark-blue" 

     
class CheckBoxesFrame(customtkinter.CTkFrame):
    def __init__(self,master,futures,value,i,checkboxes,user_list_instance):
        super().__init__(master)

        img = futures[i][1]
        self.label = customtkinter.CTkLabel(self, image=img)
        self.label.configure(text="")
        self.label.grid(row=i, column=0, padx=10, pady=(0, 15), sticky="w")
        self.user_list_instance = user_list_instance
        def check():
            self.user_list_instance.CheckAndUncheck(self.user_list_instance,0)
            for i in checkboxes:
                if i.get() == 1:
                    self.user_list_instance.SetUpManga.configure(state="normal")
                    return
            self.user_list_instance.SetUpManga.configure(state="disabled")
            
        self.checkbox = customtkinter.CTkCheckBox(self, text=value,onvalue=1,offvalue=0,command=check)
        self.checkbox.data_secret = i
        self.checkbox.grid(row=i, column=1, padx=0, pady=(0, 20), sticky="w")
        checkboxes.append(self.checkbox)
        

#sticky n,s,e,w it's to where to stick your thing(compass like)
# box where manga shown
class MangaBox(customtkinter.CTkScrollableFrame):
    def __init__(self, master, title, values,serid,user_list_instance): 
        super().__init__(master, label_text=title)
        self.values = values
        self.serid = serid
        self.checkboxes = []
        self.configure(height=3)
        if self.values == None: return
        hwmtimes = 0
        futures = []
        self.mycheckbox=[]
        self.user_list_instance = user_list_instance
        for i, value in enumerate(self.values):
            if os.path.exists(f"images\{serid[hwmtimes]}il.png"):
                img = customtkinter.CTkImage(Image.open(f"images\{serid[hwmtimes]}il.png"), size=[104, 150])
                futures.append((i,img))
                hwmtimes += 1
            self.mycheckbox.append(CheckBoxesFrame(self,futures,value,i,self.checkboxes,self.user_list_instance))
            self.mycheckbox[i].pack(padx=0, pady=0,anchor='nw')
            
    def get(self):
        checked_checkboxes = []
        for checkbox in self.checkboxes:
            if checkbox.get() == 1:
                checked_checkboxes.extend([[self.serid[checkbox.data_secret],self.values[checkbox.data_secret]]])
        return checked_checkboxes

# the app
class UserList(customtkinter.CTkToplevel):
    def __init__(self):
        super().__init__()
        self.grab_set()
        try:
            with open('list.pkl', 'rb') as file:
                self.loaded_data = pickle.load(file)
        except FileNotFoundError:
            self.loaded_data = {}
        self.title("Your List")
        self.geometry("800x550")
        self.minsize(800,550)
        self.DefaultFlag=False
        self.after(250, lambda: self.iconbitmap('iconforMEU.ico'))
        print(self.loaded_data)
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
        # note
        self.note = customtkinter.CTkLabel(self)
        self.note.configure(text="")
        self.note.grid(row=1, column=2, padx=0, pady=(100, 0), sticky="n")
        for i in self.loaded_data:
            if not len(self.loaded_data[i]) > 3:
                self.note.configure(text="You need to set up\n the manga you added",font=('Roboto Regular',14),text_color="yellow")
        # UncheckAllManga button
        self.CheckUncheckAll = customtkinter.CTkButton(master=self, text="Check All", command=lambda:self.CheckAndUncheck(None,1))
        self.CheckUncheckAll.grid(row=1,column=2,padx=(0,10),pady=10,sticky='sew')
        self.CheckUncheckAll.configure(height=50)
        #delete butt
        self.DeleteManga = customtkinter.CTkButton(master=self, text="Delete Manga", command=self.DeleteMangaPress)
        self.DeleteManga.grid(row=1,column=2,padx=(0,10),pady=(10,70),sticky='sew')
        self.DeleteManga.configure(height=50)
        # SetUpManga Button
        self.SetUpManga = customtkinter.CTkButton(master=self, text="Set Up Manga", command=self.SetUpPress)
        self.SetUpManga.grid(row=1,column=2,padx=(0,10),pady=10,sticky='new')
        self.SetUpManga.configure(height=80, state="disabled")
        # button to open default list
        self.OpenOtherList = customtkinter.CTkButton(master=self, text="Open Default List", command=self.OpenOList)
        self.OpenOtherList.grid(row=1,column=2,padx=(0,10),pady=(150,0),sticky='new')
        self.OpenOtherList.configure(height=80)
    
    def makeMangaBox(self,values=None,serid=None):
        if values is None:
            values = []
            for i in self.loaded_data: values.append(self.loaded_data[f'{i}'][2])
        if serid is None:
            serid = []
            for i in self.loaded_data: serid.append(self.loaded_data[f'{i}'][0])
        self.MangaListBox = MangaBox(self, title="Manga/Manhwa/Manhua",values=values,serid=serid,user_list_instance=self)
        self.MangaListBox.grid(row=1, column=1, padx=(10,10), pady=(10, 10), sticky="nsew")
    
    def OpenOList(self):
        if not self.DefaultFlag:
            try:
                with open('defaultopenlist.pkl', 'rb') as file:
                    self.default_list = pickle.load(file)
                    #[seriesid][url,name]
            except FileNotFoundError:
                self.default_list = {}
            if len(self.default_list) > 0:
                print(self.default_list)
                values=[]
                serid=[]
                for i in self.default_list: serid.append(i)
                for i in self.default_list: values.append(self.default_list[i][1])
                self.makeMangaBox(values,serid)
                self.DefaultFlag=True
            else:
                self.note.configure(text="No manga in\nthe default list",font=('Roboto Regular',14),text_color="yellow")
        else:
            try:
                with open('list.pkl', 'rb') as file:
                    self.loaded_data = pickle.load(file)
            except FileNotFoundError:
                self.loaded_data = {}
            self.makeMangaBox()
            self.DefaultFlag=False
        
    
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
                    

    def SetUpPress(self):
        def Change():
            if not self.DefaultFlag:
                try:
                    with open('list.pkl', 'rb') as file:
                        self.loaded_data = pickle.load(file)
                except FileNotFoundError:
                    self.loaded_data = {}
                all_elements_have_more_than_three_items = True
                for element in self.loaded_data.values():
                    if len(element) <= 3:
                        all_elements_have_more_than_three_items = False
                        break
                if all_elements_have_more_than_three_items:
                    self.note.configure(text="")
                self.makeMangaBox()
                self.SetUpManga.configure(state="disabled")
                
        checked_boxes = self.MangaListBox.get()
        if len(checked_boxes) != 0:
            if self.DefaultFlag:
                MSUWFDL.MangaSetUpWindow(checked_boxes)
            else:
                MSUW.MangaSetUpWindow(checked_boxes,Change)

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
                self.SetUpManga.configure(state="normal")
                return
        for i in range(len(self.MangaListBox.mycheckbox)):
            self.MangaListBox.mycheckbox[i].checkbox.deselect()
        self.CheckUncheckAll.configure(text="Check All")
        self.SetUpManga.configure(state="disabled")
    
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
    
    def DeleteMangaPress(self):
        checked_boxes = self.MangaListBox.get()
        if not len(checked_boxes) > 0: return
        wind = self.AreYouSureWindow()
        self.wait_window(wind)
        if not hasattr(wind, 'result'): return
        if not wind.result:
            return
        if not self.DefaultFlag:
            for i in checked_boxes:
                for f in self.loaded_data:
                    if i[0]==self.loaded_data[f'{f}'][0]:
                        try:
                            with open('newchapslinks.pkl', 'rb') as file:
                                self.reading_list = pickle.load(file)
                                #[seriesid][url,name]
                        except FileNotFoundError:
                            self.reading_list = {}
                        if len(self.reading_list) > 0:
                            for j in self.reading_list:
                                if int(j) == i[0]:
                                    del self.reading_list[j]
                                    break
                        file_path = f'images\{i[0]}il.png'
                        try:
                            os.remove(file_path)
                            print(f"Successfully deleted: {file_path}")
                        except FileNotFoundError:
                            print(f"File not found: {file_path}")
                        except PermissionError:
                            print(f"Permission denied: {file_path}")
                        except Exception as e:
                            print(f"Error occurred while deleting the file: {file_path}\nError message: {str(e)}")
                        del self.loaded_data[f'{f}']
                        new_dict = {}
                        for i, value in enumerate(self.loaded_data.values(), start=1):
                            new_dict[str(i)] = value
                        self.loaded_data = new_dict
                        self.makeMangaBox()
                        with open('list.pkl', 'wb') as file:
                            pickle.dump(self.loaded_data, file)
                        break
        else:
            print('yes')
            for i in checked_boxes:
                for f in self.default_list:
                    if i[0]==f:
                        file_path = f'images\{i[0]}il.png'
                        try:
                            os.remove(file_path)
                            print(f"Successfully deleted: {file_path}")
                        except FileNotFoundError:
                            print(f"File not found: {file_path}")
                        except PermissionError:
                            print(f"Permission denied: {file_path}")
                        except Exception as e:
                            print(f"Error occurred while deleting the file: {file_path}\nError message: {str(e)}")
                        del self.default_list[f'{f}']
                        values=[]
                        serid=[]
                        for i in self.default_list: serid.append(i)
                        for i in self.default_list: values.append(self.default_list[i][1])
                        self.makeMangaBox(values,serid)
                        with open('defaultopenlist.pkl', 'wb') as file:
                            pickle.dump(self.default_list, file)
                        break