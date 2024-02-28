import customtkinter

import pandas as pd
import pdfplumber
import re
from pprint import pprint





customtkinter.set_appearance_mode("System")  # Modes: system (default), light, dark
customtkinter.set_default_color_theme("blue")


from tkinter import StringVar, W, filedialog as fd
import os


class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        self.geometry("600x200")

        self.selected_file = StringVar(value="None Selected")

        self.title_label = customtkinter.CTkLabel(self, text="PDF Text Extract", font=("Arial", 25))
        self.title_label.grid(row=1, column=1, columnspan=2, padx=5, pady=5)
        
        self.select_file_button = customtkinter.CTkButton(self, text="Select a file", command=self.select_file)
        self.select_file_button.grid(row=2, column=1, sticky=W, pady=2, padx=5)

        self.selected_file_label = customtkinter.CTkLabel(self, textvariable=self.selected_file)
        self.selected_file_label.grid(row=2, column=2, sticky=W, pady=2, padx=5)
       

        self.start_button = customtkinter.CTkButton(self, text="Start Extraction", command=self.extract)
        self.start_button.grid(row=3, column=1)


    def select_file(self):
        self.selected_file.set(fd.askopenfilename(initialdir=os.getcwd(), filetypes=[("pdf", "*.pdf")]))

    def extract(self):
        with pdfplumber.open(self.selected_file.get()) as pdf:
            table_settings = {
                "vertical_strategy": "lines",
                "intersection_x_tolerance": 20,
            }
            # im = pdf.pages[0].to_image(resolution=150)
            # # im.draw_rects(pdf.pages[0].extract_words())
            # im.debug_tablefinder(tf=table_settings)
            # im.save("test.png", format="PNG", quantize=True, colors=256, bits=8)

            # table = pdf.pages[0].extract_table(table_settings=table_settings)
            # df = pd.DataFrame(table[1:], columns=table[0])
            # print(df)

            upto = 1
            next = False
            total_starts = []
            total_winrates = []
            total_wintimes = []

            finished_datasets = {}
            
            #current_race = ""
            df = None
            for i, page in enumerate(pdf.pages):
                printed = False

                text = page.extract_text().split("\n")
                for line in text:
                    if line.startswith("Race "):
                        upto = 1  # reset back to 1
                        data = line.split(" Advertised ")
                        print(f"found {data[0]} on page {i}")

                        if df is not None:
                            df["Starts"] = total_starts
                            df["Winrate"] = total_winrates
                            df["Win Times"] = total_wintimes
                            total_starts = []
                            total_winrates = []
                            total_wintimes = []
                            finished_datasets[data[0]] = df
                            print(df)

                        

                        if not printed:

                            table_settings = {
                                "vertical_strategy": "lines",
                                "intersection_y_tolerance": 20,
                            }
                            table = page.extract_table(table_settings=table_settings)
                            df = pd.DataFrame(table[1:], columns=table[0])
                            df = df.rename(columns={"No.": "Num", "Rating": "Rat"})
                            print(df.columns)
                            df.drop(['Last 5 Runs', 'Runner', 'TcDW', 'Jockey', 'Trainer', 'Weight'], axis=1, inplace=True)
                            printed = True

                    if line.startswith("Distance"):
                        data2 = line.split("Prizemoney: ")
                        print(f"Prizemoney: {data2[1]}")

                    if line.startswith(f"{upto}. "):
                        # print(line)
                        next = True

                    if next and line.startswith("Overall"):
                            
                        next = False
                        data = line.split(" ")
                        starts = int(data[1])
                        win_times = int(data[3][:-1])
                        win_rate = data[5][1:-2]
                        if win_rate.isdigit():
                            win_rate = round(int(win_rate) / 100, 2)
                        else:
                            win_rate = 0.00

                        # print(f"{upto} | Starts: {starts}, Win times: {win_times}, Win Rates: {win_rate}")
                        total_starts.append(starts)
                        total_wintimes.append(win_times)
                        total_winrates.append(win_rate)

                        upto += 1
                        # 'Overall 1 Starts 0w 0p (0%w 0%p)
                        # hi
            
            with pd.ExcelWriter('output.xlsx') as writer:  
                for k,v in finished_datasets.items():
                    v.to_excel(writer, sheet_name=k)

            
                


app = App()
app.mainloop()
