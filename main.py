import tkinter
import tkinter.messagebox
import customtkinter
from PIL import Image
import api, list, ReadingList,MSUW
import requests
from io import BytesIO
import pickle
import concurrent.futures
import os
import re
import webbrowser



customtkinter.set_appearance_mode("System")  # Modes: "System" (standard), "Dark", "Light"
customtkinter.set_default_color_theme("dark-blue")  # Themes: "blue" (standard), "green", "dark-blue"        

# series_id[0][0] = serid, [number of manga][1]=thumb, [0][2]=title, [3]=url to pref site, [4]= last chapt r, [5] = group to check
#sticky n,s,e,w it's to where to stick your thing(compass like)
# box where manga shown
class MyScrollableCheckboxFrame(customtkinter.CTkScrollableFrame):
    def __init__(self, master, title, values, imges,serid,urls): # cache imgs here and delete not checked imges when add button
        super().__init__(master, label_text=title)
        self.values = values
        self.imges = imges
        self.serid = serid
        self.checkboxes = []
        self.urls = urls
        self.configure(height=3)
        if not os.path.exists("images\\"):
            # Create the folder
            os.makedirs("images\\")
        def load_image(url,seriesid):
            response = requests.get(url)
            img = Image.open(BytesIO(response.content))
            imgc=customtkinter.CTkImage(img, size=[104, 150])
            img.save(f"images\{seriesid}.png")
            return imgc
        if self.values == None: return
        hwmtimes = 0
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = []
            for i, value in enumerate(self.values):
                if imges[hwmtimes] is not None:
                    if os.path.exists(f"images\{serid[hwmtimes]}il.png"):
                        img = customtkinter.CTkImage(Image.open(f"images\{serid[hwmtimes]}il.png"), size=[104, 150])
                        futures.append((i,img))
                        hwmtimes += 1
                    else: 
                        future = executor.submit(load_image, imges[hwmtimes],serid[hwmtimes])
                        futures.append((i, future))
                        hwmtimes += 1
                else:
                    continue
                checkbox = customtkinter.CTkCheckBox(self, text=value)
                checkbox.data_secret = i
                checkbox.grid(row=i, column=1, padx=0, pady=(0, 20), sticky="w")
                self.checkboxes.append(checkbox)
                
            def button_event(button_id):
                webbrowser.open_new_tab(self.urls[button_id])
                
            for i,_ in enumerate(self.urls):
                CheckButton = customtkinter.CTkButton(self, text="Check", command=lambda button_id=i: button_event(button_id))
                CheckButton.grid(row=i,column=1,padx=0, pady=(0, 14), sticky="sw")
                

            for i, future in futures:
                if isinstance(future, customtkinter.CTkImage):
                    img = future  # Use the existing CTkImage object directly
                else:
                    img = future.result()

                label = customtkinter.CTkLabel(self, image=img)
                label.configure(text="")
                label.grid(row=i, column=0, padx=10, pady=(0, 15), sticky="w")
            
            
    def get(self):
        checked_checkboxes = []
        for checkbox in self.checkboxes:
            if checkbox.get() == 1:
                checked_checkboxes.extend([[self.serid[checkbox.data_secret],self.imges[checkbox.data_secret],self.values[checkbox.data_secret]]])
        return checked_checkboxes

# the app
class MUApp(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        self.numberofpage=1
        self.title("MangaEaseUp")
        self.geometry("800x550")
        self.minsize(800,550)
        self.iconbitmap('iconforMEU.ico')
        # grid configuration
        self.grid_columnconfigure((1,2,3,4), weight=3)
        self.grid_columnconfigure((4),weight=1)
        self.grid_rowconfigure((1), weight=1)
        
        # Row 0
        # Search for Manga
        self.MangaSearch = customtkinter.CTkEntry(self, placeholder_text="Search for manga...")
        self.MangaSearch.grid(row=0,column=0,padx=10,pady=(10,0), sticky='ew',columnspan = 4)
        self.MangaSearch.configure(height=35)
        # Button for search
        
        
        self.MangaSearchButton = customtkinter.CTkButton(master=self, text="Search", command= lambda: self.SearchButtPress(None))
        self.MangaSearchButton.grid(row=0,column=4,padx=(0,10),pady=(10,0),sticky='new')
        self.MangaSearchButton.configure(height=35)
        
        # Row 1
        # add Manga button 
        self.AddMangaButton = customtkinter.CTkButton(master=self, text="Add", command=self.AddMangaButtonPressed)
        self.AddMangaButton.grid(row=1,column=4,padx=(0,10),pady=10,sticky='new')
        self.AddMangaButton.configure(height=80,state="disabled")
        # manga info label
        self.MangaInfoAdd = customtkinter.CTkLabel(self, text="", fg_color="transparent")
        self.MangaInfoAdd.grid(row=1,column=4,padx=(0,10),pady=(100,0),sticky='new')
        # next page button
        self.NextPage = customtkinter.CTkButton(master=self, text="Next Page", command= self.NextPageButtonPress)
        self.NextPage.grid(row=1,column=4,padx=(0,10),pady=0,sticky='sew')
        self.NextPage.configure(height=40, state="disabled")
        # previous page button
        self.PrevPage = customtkinter.CTkButton(master=self, text="Prev Page", command= self.PrevPageButtonPress)
        self.PrevPage.grid(row=1,column=4,padx=(0,10),pady=(0,50),sticky='sew')
        self.PrevPage.configure(height=40, state="disabled")
        # empty box
        
        self.EmptyBoxOfManhwa = MyScrollableCheckboxFrame(self, title="Manga/Manhwa/Manhua",values=None,imges=[None],serid=[None],urls=[None])
        self.EmptyBoxOfManhwa.grid(row=1, column=0, padx=(10,10), pady=(10, 0), sticky="nsew", columnspan = 4)
        
        # Row 2
        # check for new chapters button
        self.CheckForNewChaps = customtkinter.CTkButton(master=self, text="Check \nfor new chapters", command=self.checkForNewChapsPress)
        self.CheckForNewChaps.grid(row=2,column=1,padx=(10,0),pady=(76,15),sticky='w')
        self.CheckForNewChaps.configure(height=45,width=200)
        # info about chapters
        self.infoAboutChapters = customtkinter.CTkLabel(self, text="", fg_color="transparent")
        self.infoAboutChapters.grid(row=2,column=1,padx=(220,0),pady=(76,15),sticky='w')
        # show User List Button
        self.UsersList = customtkinter.CTkButton(master=self, text="Your List", command=self.ShowYourList)
        self.UsersList.grid(row=2,column=1,padx=(10,0),pady=(0,50),sticky='w')
        self.UsersList.configure(height=45,width=200)
        # Open New Chapters Button
        self.OpenNewChaps = customtkinter.CTkButton(master=self, text="Open New Chapters", command=self.OpenNewChapsPress)
        self.OpenNewChaps.grid(row=2,column=0,padx=(10,0),pady=(20,15),sticky='w')
        self.OpenNewChaps.configure(height=100,width=150)
        # Info Button
        self.InfoButt = customtkinter.CTkButton(master=self, text="Info", command=self.InfoPress)
        self.InfoButt.grid(row=2,column=4,padx=(0,10),pady=(75,0),sticky='e')
        self.InfoButt.configure(height=35,width=75)
        
        self.bind('<Return>', self.SearchButtPress)
    
    def ReturnButtToNormal(self):
        self.after(1000, lambda: self.MangaSearchButton.configure(state="normal"))
        self.after(1000, lambda: self.AddMangaButton.configure(state="normal"))
        self.after(1000, lambda: self.NextPage.configure(state="normal"))
        self.after(1000, lambda: self.PrevPage.configure(state="normal"))
    
    def DisableButtons(self):
        self.MangaSearchButton.configure(state="disabled")
        self.AddMangaButton.configure(state="disabled")
        self.NextPage.configure(state="disabled")
        self.PrevPage.configure(state="disabled")
    
    def check_and_search(self,event):
        if self.MangaSearch.focus_get() == self.MangaSearch:
            self.SearchButtPress()

    def RemoveNeedlesImages(self):
        files = os.listdir('images/')
        # Iterate over the files and delete the ones that don't match the pattern
        for file in files:
            if not file.endswith("il.png"):
                file_path = os.path.join('images/', file)
                os.remove(file_path)

    def SearchButtPress(self,event):
        self.MangaInfoAdd.configure(text='')
        # Call the API function and get the results
        if not event == None:
            if not str(self.focus_get()) == '.!ctkentry.!entry':
                return
        search_query = self.MangaSearch.get()
        if search_query == '': return
        self.MangaSearchButton.configure(state="disabled")
        self.numberofpage=1
        results = api.search_manga(search_query,self.numberofpage)
        # box with Manga
        values = []
        serid=[]
        imges=[]
        urls=[]
        for result in results: imges.append(result['thumb'])
        for result in results: serid.append(result['series_id'])
        for result in results: values.append(result['title'])
        for result in results: urls.append(result['url'])
        self.EmptyBoxOfManhwa.destroy()
        self.scrollable_checkbox_frame = MyScrollableCheckboxFrame(self, title="Manga/Manhwa/Manhua", values=values,imges=imges,serid=serid,urls=urls)
        self.scrollable_checkbox_frame.grid(row=1, column=0, padx=(10,10), pady=(10, 0), sticky="nsew", columnspan = 4)
        self.ReturnButtToNormal()
    
    def PrevPageButtonPress(self):
        if self.numberofpage == 1: return
        self.MangaInfoAdd.configure(text='')
        self.numberofpage -= 1
        self.DisableButtons()
        search_query = self.MangaSearch.get()
        results = api.search_manga(search_query,self.numberofpage)
        values = []
        serid=[]
        imges=[]
        urls=[]
        for result in results: imges.append(result['thumb'])
        for result in results: serid.append(result['series_id'])
        for result in results: values.append(result['title'])
        for result in results: urls.append(result['url'])
        self.scrollable_checkbox_frame = MyScrollableCheckboxFrame(self, title="Manga/Manhwa/Manhua", values=values,imges=imges,serid=serid,urls=urls)
        self.scrollable_checkbox_frame.grid(row=1, column=0, padx=(10,10), pady=(10, 0), sticky="nsew", columnspan = 4)
        self.ReturnButtToNormal()
    
    def NextPageButtonPress(self):
        self.MangaInfoAdd.configure(text='')
        self.numberofpage += 1
        self.DisableButtons()
        search_query = self.MangaSearch.get()
        results = api.search_manga(search_query,self.numberofpage)
        values = []
        serid=[]
        imges=[]
        urls=[]
        for result in results: imges.append(result['thumb'])
        for result in results: serid.append(result['series_id'])
        for result in results: values.append(result['title'])
        for result in results: urls.append(result['url'])
        self.scrollable_checkbox_frame = MyScrollableCheckboxFrame(self, title="Manga/Manhwa/Manhua", values=values,imges=imges,serid=serid,urls=urls)
        self.scrollable_checkbox_frame.grid(row=1, column=0, padx=(10,10), pady=(10, 0), sticky="nsew", columnspan = 4)
        self.ReturnButtToNormal()
        
    def AddMangaButtonPressed(self):
        def AddManga(series):
            try:
                with open('list.pkl', 'rb') as file:
                    loaded_data = pickle.load(file)
            except FileNotFoundError:
                loaded_data = {}
            
            # append added info by the user
            AlreadExists=False
            
            for i in series:
                if len(loaded_data)==0:
                    print('empty file')
                    loaded_data[f'{len(loaded_data) + 1}'] = i
                    if os.path.exists(f"images\{i[0]}.png"):
                        os.rename(f"images\{i[0]}.png", f"images\{i[0]}il.png")
                    with open('list.pkl', 'wb') as file:
                        pickle.dump(loaded_data, file)
                for j in loaded_data:  # j is key
                    if loaded_data[j][0]==i[0]:
                        self.MangaInfoAdd.configure(text='Already exists in the list')
                        AlreadExists=True
                        break
                print(loaded_data)
                if not AlreadExists:
                    self.MangaInfoAdd.configure(text='Manga added')
                    loaded_data[f'{len(loaded_data) + 1}'] = i
                    if os.path.exists(f"images\{i[0]}.png"):
                        os.rename(f"images\{i[0]}.png", f"images\{i[0]}il.png")
                    with open('list.pkl', 'wb') as file:
                        pickle.dump(loaded_data, file)
                else:
                    AlreadExists=False
            
            
                
        checked_boxes = self.scrollable_checkbox_frame.get()
        if len(checked_boxes) != 0:
            AddManga(checked_boxes)
        else:
            self.MangaInfoAdd.configure(text='Nothing was checked')
            print('nothing was checked')
            return
        
    def checkForNewChapsPress(self):
        self.MangaInfoAdd.configure(text='')
        try:
            with open('list.pkl', 'rb') as file:
                loaded_data = pickle.load(file)
        except FileNotFoundError:
            loaded_data = {}
        self.CheckForNewChaps.configure(state='disabled')
        self.OpenNewChaps.configure(state='disabled')
        templinks={}
        for i in loaded_data:
            if len(loaded_data[f'{i}']) >= 5 and not loaded_data[f'{i}'][5] == None:
                lastChapter = api.getlastchapterofmanga(loaded_data[f'{i}'][0],loaded_data[f'{i}'][5])
                if lastChapter is None: # doesn't have chapters on mangaupdates
                    continue
                match = re.search(r'c\.(\d+)', lastChapter)
                if match:
                    number = int(match.group(1))
                    if number > loaded_data[f'{i}'][4]:
                        print(number, ' ', loaded_data[f'{i}'][4])
                        g=f'{i}'
                        templinks[f'{loaded_data[g][0]}'] = [loaded_data[g][2], loaded_data[g][3], loaded_data[g][4], number]
                else:
                    print("No number found in the string.")
        if len(templinks) > 0:
            try:
                with open('newchapslinks.pkl', 'rb') as file:
                    links = pickle.load(file)
            except FileNotFoundError:
                links = {}
            new_templinks = {}
            for templink in templinks:
                for link in links:
                    if templinks[templink] == links[link]:
                        break
                else:
                    new_templinks[f'{templink}'] = templinks[f'{templink}']
            if len(new_templinks)>0: links.update(new_templinks)
            with open('newchapslinks.pkl', 'wb') as file:
                pickle.dump(links, file)
            self.after(1000, lambda:self.OpenNewChaps.configure(state='normal'))
            self.infoAboutChapters.configure(text=f'{len(templinks)} manga with new chapter(s)')
        else:
            self.infoAboutChapters.configure(text='No new chapters')
        self.after(5000, lambda:self.CheckForNewChaps.configure(state='normal'))
                
    def OpenNewChapsPress(self):
        self.MangaInfoAdd.configure(text='')
        try:
            with open('newchapslinks.pkl', 'rb') as file:
                links = pickle.load(file)
        except FileNotFoundError:
            links = {}
        ReadingList.ReadingUserList(links)

    def ShowYourList(self):
        self.listuser=list.UserList()
    
    def InfoPress(self):
        class UserList(customtkinter.CTkToplevel):
            def __init__(self):
                super().__init__()
                self.grab_set()
                self.after(250, lambda: self.iconbitmap('iconforMEU.ico'))
                self.title("Info")
                self.geometry("780x150")
                self.minsize(780,150)
                
                self.Credit = customtkinter.CTkLabel(self, text="Credits:\nThis was made possible thanks to MangaUpdates API(https://api.mangaupdates.com/ & https://www.mangaupdates.com/)\nI did this mainly because I needed programming experience, but also so that reading manga wouldn't take too much time.\nIf anything, these are my contacts:\nDiscord: desore(It's so weird without the hashtag lol)\nMy email: desoreoff@gmail.com", fg_color="transparent")
                self.Credit.configure(font=('Roboto Regular',14),text_color="white")
                self.Credit.grid(row=0,column=0,padx=10,pady=20,sticky='n')
        UserList()
            
    def on_closing(self):
        self.RemoveNeedlesImages()
        self.destroy()


# change
# add credit to api
MUAppW = MUApp()
MUAppW.wm_protocol("WM_DELETE_WINDOW", MUAppW.on_closing)
MUAppW.mainloop()