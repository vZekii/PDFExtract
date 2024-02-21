# import customtkinter

# customtkinter.set_appearance_mode("System")  # Modes: system (default), light, dark
# customtkinter.set_default_color_theme("blue")


# class App(customtkinter.CTk):
#     def __init__(self):
#         super().__init__()
#         self.geometry("400x150")

#         self.button = customtkinter.CTkButton(
#             self, text="my button", command=self.button_callbck
#         )
#         self.button.pack(padx=20, pady=20)

#     def button_callbck(self):
#         print("button clicked")


# app = App()
# app.mainloop()


import pandas as pd
import pdfplumber
import re
from pprint import pprint

with pdfplumber.open("./fp.pdf") as pdf:
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
    for i, page in enumerate(pdf.pages):
        printed = False

        text = page.extract_text().split("\n")
        for line in text:
            if line.startswith("Race "):

                upto = 1  # reset back to 1
                data = line.split(" Advertised ")
                print(f"found {data[0]} on page {i}")

                if not printed:

                    table_settings = {
                        "vertical_strategy": "lines",
                        "intersection_y_tolerance": 20,
                    }
                    table = page.extract_table(table_settings=table_settings)
                    df = pd.DataFrame(table[1:], columns=table[0])
                    df = df.rename(columns={"No.": "Num", "Rating": "Rat"})
                    print(df)
                    printed = True

            if line.startswith("Distance"):
                data2 = line.split("Prizemoney: ")
                print(f"Prizemoney: {data2[1]}")

            if line.startswith(f"{upto}. "):
                # print(line)
                next = True

            if next and line.startswith("Overall"):
                upto += 1
                next = False
                data = line.split(" ")
                starts = int(data[1])
                win_times = int(data[3][:-1])
                win_rate = data[5][1:-2]
                if win_rate.isdigit():
                    win_rate = round(int(win_rate) / 100, 2)
                else:
                    win_rate = 0.00

                print(
                    f"Starts: {starts}, Win times: {win_times}, Win Rates: {win_rate}"
                )
                total_starts.append(starts)
                total_wintimes.append(win_times)
                total_winrates.append(win_rate)
                # 'Overall 1 Starts 0w 0p (0%w 0%p)
                # hi
