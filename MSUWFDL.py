import tkinter
import tkinter.messagebox
import customtkinter
from PIL import Image
import api
import pickle
import os


customtkinter.set_appearance_mode("System")  # Modes: "System" (standard), "Dark", "Light"
customtkinter.set_default_color_theme("dark-blue")



class MangaSetUpWindow(customtkinter.CTkToplevel):
    def __init__(self, series):
        # for _ in checked_boxes(next button returns to the for(mean new manhwa))
        super().__init__()
        self.title("Set Up Manga")
        self.geometry("480x300")
        self.minsize(480,300)
        self.grab_set()
        self.after(250, lambda: self.iconbitmap('iconforMEU.ico'))
    
        def SetUppingManga():
            class MangaBox(customtkinter.CTkFrame):
                def __init__(self,master,manga_index):
                    super().__init__(master)
                    self.configure(fg_color="transparent")
                    if os.path.exists(f"images\{series[manga_index][0]}il.png"):
                        img = customtkinter.CTkImage(Image.open(f"images\{series[manga_index][0]}il.png"), size=[139,200])
                        imghold = customtkinter.CTkLabel(self, image=img)
                        imghold.configure(text="")
                        imghold.grid(row=1,column=0,padx=15, pady=15,sticky="w")
                    for j in loaded_data:
                        if j==series[manga_index][0]:
                            self.currentUrl= customtkinter.StringVar(self, loaded_data[j][0])
                            break
                    else:
                        self.currentUrl=None
                    
                    wrapped_text = "\n".join([series[manga_index][1][i:i+45] for i in range(0, len(series[manga_index][1]), 45)])
                    MangaName = customtkinter.CTkLabel(self,text=wrapped_text,font=('Roboto Regular',20))
                    MangaName.grid(row=0,column=0,padx=15, pady=5,sticky="n",columnspan=4)
                    
                    self.labelUrlPref = customtkinter.CTkLabel(self,text='Preffered URL to open:',font=('Roboto Regular',14))
                    self.labelUrlPref.grid(row=1,column=1,padx=5, pady=(0,0),sticky="nw",columnspan=2)
                    
                    self.UrlPreffered = customtkinter.CTkEntry(self,textvariable=self.currentUrl, placeholder_text="URL",width=250)
                    self.UrlPreffered.grid(row=1,column=1,padx=5,pady=(25,0),sticky='n')
                    
                    def DoneButt(manga_index):
                        def FindTheRightOneAndAdd(url):
                            if len(loaded_data) > 0:
                                for dseries in loaded_data:
                                    if dseries == series[manga_index][0]:
                                        loaded_data[dseries][0]=url
                                        return
                            print('a')
                            
                        if self.UrlPreffered.get() == '' or not self.UrlPreffered.get().startswith("https") or not self.UrlPreffered.get().startswith("http"):
                            url = api.get_specific_series(series[manga_index][0]) 
                            FindTheRightOneAndAdd(url['url'])
                        else:
                            FindTheRightOneAndAdd(self.UrlPreffered.get())
                        if len(series)<manga_index+2:
                            save_data()
                        else:
                            self.destroy()
                            SetUppingManga()
                    
                    self.DoneButton = customtkinter.CTkButton(self, text="Done", command=lambda:DoneButt(manga_index),fg_color='green')
                    self.DoneButton.grid(row=1,column=1,padx=(130,5), pady=(50,0),sticky="se",columnspan=3)
            self.current_manga_index+=1
            s=MangaBox(self,self.current_manga_index)
            s.pack()
            
        try:
            with open('defaultopenlist.pkl', 'rb') as file:
                loaded_data = pickle.load(file)
        except FileNotFoundError:
            loaded_data = {}
        self.current_manga_index = -1
        SetUppingManga()
        #save before exeting the app
        def save_data():
            with open('defaultopenlist.pkl', 'wb') as file:
                pickle.dump(loaded_data, file)
            self.destroy()
            
        self.protocol("WM_DELETE_WINDOW", save_data)
        