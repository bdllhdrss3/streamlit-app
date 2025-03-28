# -*- coding: utf-8 -*-
"""
Created on Thu Mar 27 16:20:46 2025

@author: 285810
"""

import os
import re
import requests
import vertexai
import pandas as pd
import tkinter as tk
from io import StringIO
from tkinter import ttk, scrolledtext, filedialog, messagebox
from PIL import Image, ImageTk
from vertexai.preview.generative_models import GenerativeModel

# === CONFIGURATIONS ===
SUBSCRIBER_FILE = "./SubscriberProfileData.csv"
PRODUCT_FILE = "./ProductCatalogue.csv"
#CREDENTIALS_FILE = "./hackathon2025-454908-0a52f19ef9b1.json"
CREDENTIALS_FILE = "./testproject-21156-533ad1f570c0.json"
LOGO_FILE = "./New-mtn-logo.jpg"

# === CATEGORY COLORS ===
category_colors = {
    "Gaming": "#d1f0ff",
    "Health": "#d1ffd6",
    "Entertainment": "#ffe6cc",
    "Education": "#e6ccff",
    "Other": "#f2f2f2"
}

# === HEALTH CHECK FUNCTION ===
def check_integration_health():
    status = {}
    tooltips = {}
    try:
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = CREDENTIALS_FILE
        #vertexai.init(project="hackathon2025-454908", location="us-central1")
        vertexai.init(project="testproject-21156", location="us-central1")
        model = GenerativeModel("gemini-2.0-flash-001")
        model.generate_content("ping")
        status["Gemini API"] = True
    except Exception as e:
        status["Gemini API"] = False
        print(e)
    status["Subscriber CSV"] = os.path.isfile(SUBSCRIBER_FILE)
    status["Product Catalogue CSV"] = os.path.isfile(PRODUCT_FILE)
    status["Credentials File"] = os.path.isfile(CREDENTIALS_FILE)

    tooltips = {
        "Gemini API": "Checks connection to Google's Gemini AI API",
        "Subscriber CSV": "Checks for presence of SubscriberProfileData.csv",
        "Product Catalogue CSV": "Checks for presence of ProductCatalogue.csv",
        "Credentials File": "Verifies the existence of your service account JSON key"
    }

    return status, tooltips

# === TABLE SORTING ===
def sort_column(treeview, col, reverse):
    data = [(treeview.set(k, col), k) for k in treeview.get_children('')]
    data.sort(reverse=reverse)
    for index, (_, k) in enumerate(data):
        treeview.move(k, '', index)
    treeview.heading(col, command=lambda: sort_column(treeview, col, not reverse))

# === DISPLAY DATAFRAME IN TABLE ===
def create_scrollable_table(parent, dataframe, title):
    ttk.Label(parent, text=title, font=("Arial", 12, "bold"), background="#f0f4f8").pack(pady=5)
    container = tk.Frame(parent, bg="#f0f4f8")
    container.pack(fill='both', expand=True, padx=10, pady=5)

    canvas = tk.Canvas(container, bg="#f0f4f8")
    scrollbar_y = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
    scrollbar_x = ttk.Scrollbar(container, orient="horizontal", command=canvas.xview)
    scroll_frame = tk.Frame(canvas, bg="#f0f4f8")
    scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar_y.pack(side="right", fill="y")
    scrollbar_x.pack(side="bottom", fill="x")

    tree = ttk.Treeview(scroll_frame, columns=list(dataframe.columns), show="headings")
    tree.pack(fill="both", expand=True)
    for col in dataframe.columns:
        tree.heading(col, text=col, command=lambda _col=col: sort_column(tree, _col, False))
        tree.column(col, anchor='w', width=max(200, int(1400 / len(dataframe.columns))))
    for _, row in dataframe.iterrows():
        item = tree.insert("", "end", values=list(row))
        category = row.get("Category", "Other")
        bg = category_colors.get(str(category).strip(), category_colors["Other"])
        tree.tag_configure(category, background=bg)
        tree.item(item, tags=(category,))

# === RUN ANALYSIS ===
def run_analysis_gui(params):
    model = GenerativeModel("gemini-2.0-flash-001")
    subscriber_df = pd.read_csv(SUBSCRIBER_FILE)
    product_df = pd.read_csv(PRODUCT_FILE)

    mode = params['selection_mode'].get()
    if mode == 'specific':
        msisdn = params['specific_msisdn'].get()
        selected_subscribers = subscriber_df[subscriber_df['MSISDN'] == int(msisdn)]
        if selected_subscribers.empty:
            messagebox.showerror("Error", f"MSISDN {msisdn} not found in dataset.")
            return
    elif mode == 'random':
        try:
            n = int(params['random_count'].get())
            selected_subscribers = subscriber_df.sample(n)
        except:
            messagebox.showerror("Error", "Invalid number for random MSISDNs.")
            return
    else:
        selected_subscribers = subscriber_df.copy()

    subscriber_data_str = selected_subscribers.to_string(index=False)
    product_data_str = product_df.to_string(index=False)
    filters = "\n".join(f"- Include {k}" for k, v in params['variables'].items() if v.get())

    prompt = f"""
Compare the data and use it to compare with the product catalogue below. Recommend one product for each of the following subscribers:

{subscriber_data_str}

Use the product catalogue below:

{product_data_str}

Variables to consider for profiling:
{filters}

Output a clean markdown-style table with the following columns exactly:
MSISDN | RecommendedProduct | Category | Tier | ProductPrice | Reason | UpsellOption | CrossSellOption

After the table, include a short bullet-point section with additional upsell and cross-sell insights or strategy tips. Do not include general commentary—just the table and the follow-up list.
"""

    response = model.generate_content(prompt)
    response_text = response.text
    potential_table_match = re.search(r"((?:\|.+\|\n)+)", response_text)
    table_df = None
    if potential_table_match:
        table_text = potential_table_match.group(1)
        try:
            table_df = pd.read_csv(StringIO(table_text), sep="|", engine='python')
            table_df = table_df.dropna(axis=1, how='all').dropna(axis=0, how='all')
            table_df.columns = [col.strip() for col in table_df.columns]
        except:
            table_df = None
    explanation_text = response_text.replace(table_text, "") if potential_table_match else "No additional upsell/cross-sell insights were provided."

    gui = tk.Toplevel()
    gui.title("Gemini AI - Product Recommendations")
    gui.geometry("1500x900")
    gui.configure(bg="#f0f4f8")
    ttk.Label(gui, text="Gemini AI Product Recommendations for Subscribers", font=("Arial", 18, "bold"), background="#f0f4f8").pack(pady=10)

    create_scrollable_table(gui, selected_subscribers.reset_index(drop=True), "Selected Subscribers")
    if table_df is not None:
        create_scrollable_table(gui, table_df.reset_index(drop=True), "Recommended Products Table")

    ttk.Label(gui, text="Upsell & Cross-sell Details", font=("Arial", 12, "bold"), background="#f0f4f8").pack(pady=5)
    exp_frame = scrolledtext.ScrolledText(gui, width=180, height=10, wrap=tk.WORD, font=("Arial", 10))
    exp_frame.insert(tk.INSERT, explanation_text.strip())
    exp_frame.pack(padx=10, pady=5, fill='both', expand=True)

    def save_to_file():
        f = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        if f:
            with open(f, "w", encoding="utf-8") as out:
                out.write("Selected Subscribers\n")
                out.write(subscriber_data_str + "\n\n")
                out.write("Gemini AI Recommendations\n")
                out.write(response_text.strip())

    ttk.Button(gui, text="Save Output to File", command=save_to_file).pack(pady=10)

# === LAUNCHER SETUP ===
launcher = tk.Tk()
launcher.title("Amabutho Launch Page")
launcher.geometry("500x850")
launcher.configure(bg="#eef5f9")

# Embedded Logo
try:
    logo_img = Image.open(LOGO_FILE).resize((120, 120))
    logo_tk = ImageTk.PhotoImage(logo_img)
    tk.Label(launcher, image=logo_tk, bg="#eef5f9").pack(pady=10)
except:
    pass

# Title
ttk.Label(launcher, text="Amabutho AI Product Recommendation Engine", font=("Arial", 14, "bold"), background="#eef5f9").pack(pady=5)

# Health Check Frame
status, tooltips = check_integration_health()
health_frame = ttk.LabelFrame(launcher, text="Integration Health Check", padding=10)
health_frame.pack(padx=20, pady=5, fill="x")

health_labels = {}

for service, ok in status.items():
    color = "green" if ok else "red"
    label = tk.Label(health_frame, text=f"{service}: {'OK' if ok else 'FAILED'}", fg=color, font=("Arial", 10, "bold"))
    label.pack(anchor="w")
    health_labels[service] = label
    label.bind("<Enter>", lambda e, s=service: label.config(text=f"{s}: {tooltips[s]}"))
    label.bind("<Leave>", lambda e, s=service, ok=ok: label.config(text=f"{s}: {'OK' if ok else 'FAILED'}"))

# Refresh button
def refresh_health():
    status, _ = check_integration_health()
    for service, label in health_labels.items():
        ok = status[service]
        label.config(fg="green" if ok else "red", text=f"{service}: {'OK' if ok else 'FAILED'}")

ttk.Button(health_frame, text="Refresh Health Check", command=refresh_health).pack(pady=5)

# Settings Panel
settings_frame = ttk.LabelFrame(launcher, text="Settings", padding=10)
settings_frame.pack(padx=20, pady=10, fill="x")

params = {
    "variables": {},
    "selection_mode": tk.StringVar(value="random"),
    "random_count": tk.StringVar(value="4"),
    "specific_msisdn": tk.StringVar()
}

# MSISDN Input
ttk.Label(settings_frame, text="Select MSISDN Input Method:").pack(anchor="w")
ttk.Radiobutton(settings_frame, text="Specific MSISDN", variable=params["selection_mode"], value="specific").pack(anchor="w")
ttk.Entry(settings_frame, textvariable=params["specific_msisdn"]).pack(fill="x", pady=2)

ttk.Radiobutton(settings_frame, text="Random sample of MSISDNs", variable=params["selection_mode"], value="random").pack(anchor="w")
ttk.Entry(settings_frame, textvariable=params["random_count"]).pack(fill="x", pady=2)

ttk.Radiobutton(settings_frame, text="All MSISDNs", variable=params["selection_mode"], value="all").pack(anchor="w")

# Profiling Variables
ttk.Label(settings_frame, text="Variables to consider for profiling:").pack(anchor="w", pady=(10, 5))
for field in ["DemographicSegment", "DeviceType", "CurrentPlan", "VASUsed"]:
    var = tk.BooleanVar(value=True)
    params["variables"][field] = var
    ttk.Checkbutton(settings_frame, text=field, variable=var).pack(anchor="w")

# Run Button
ttk.Button(launcher, text="Run Analysis", command=lambda: run_analysis_gui(params)).pack(pady=20)
launcher.mainloop()
