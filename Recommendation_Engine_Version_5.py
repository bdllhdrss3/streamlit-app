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
import threading
import time

# === CONFIGURATIONS ===
# SUBSCRIBER_FILE ="gs://amabutho/SubscriberProfileData.csv"
SUBSCRIBER_FILE ="SubscriberProfileData.csv"
PRODUCT_FILE = "./ProductCatalogue.csv"
#PRODUCT_FILE ="gs://amabutho/SubscriberProfileData.csv"
CREDENTIALS_FILE = "./hackathon2025-454908-0a52f19ef9b1.json"
#CREDENTIALS_FILE = "./testproject-21156-533ad1f570c0.json"
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
        vertexai.init(project="hackathon2025-454908", location="us-central1")
        # vertexai.init(project="testproject-21156", location="us-central1")
        model = GenerativeModel("gemini-2.0-flash-001")
        model.generate_content("ping")
        status["Gemini API"] = True
    except Exception as e:
        status["Gemini API"] = False
        print(e)
    try:
        pd.read_csv(SUBSCRIBER_FILE,on_bad_lines='skip',nrows=1)
        status["Subscriber CSV"] = True
    except Exception as e:
        status["Subscriber CSV"] = False
        print(f"Subscriber CSV Error: {e}")

    try:
        pd.read_csv(PRODUCT_FILE,on_bad_lines='skip',nrows=1)
        status["Product Catalogue CSV"] = True
    except Exception as e:
        status["Product Catalogue CSV"] = False
        print(f"Product Catalogue CSV Error: {e}")

    try:
        with open(CREDENTIALS_FILE, 'r') as f:
            f.read()
        status["Credentials File"] = True
    except Exception as e:
        status["Credentials File"] = False
        print(f"Credentials File Error: {e}")
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
    frame = ttk.LabelFrame(parent, text=title)
    frame.pack(fill='both', expand=True, padx=10, pady=5)

    # Button frame
    button_frame = ttk.Frame(frame)
    button_frame.pack(fill='x', padx=5, pady=2)
    
    def download_csv():
        # Create loading window
        loading_window = tk.Toplevel()
        loading_window.title("Downloading...")
        loading_window.geometry("300x150")
        loading_window.transient(parent.winfo_toplevel())
        loading_window.grab_set()
        
        # Center the loading window
        loading_window.update_idletasks()
        width = loading_window.winfo_width()
        height = loading_window.winfo_height()
        x = (loading_window.winfo_screenwidth() // 2) - (width // 2)
        y = (loading_window.winfo_screenheight() // 2) - (height // 2)
        loading_window.geometry('{}x{}+{}+{}'.format(width, height, x, y))
        
        # Add progress bar and label
        ttk.Label(loading_window, text=f"Preparing {title} CSV file...", font=("Arial", 10)).pack(pady=10)
        progress = ttk.Progressbar(loading_window, orient="horizontal", length=250, mode="indeterminate")
        progress.pack(pady=10)
        progress.start(10)
        
        def download_task():
            default_name = f"{title.replace(' ', '_')}_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv"
            f = filedialog.asksaveasfilename(
                initialfile=default_name,
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
            )
            if f:
                # Simulate processing time
                time.sleep(1)
                dataframe.to_csv(f, index=False)
                loading_window.destroy()
                messagebox.showinfo("Success", f"Table saved to {f}")
            else:
                loading_window.destroy()
        
        threading.Thread(target=download_task).start()

    def download_excel():
        # Create loading window
        loading_window = tk.Toplevel()
        loading_window.title("Downloading...")
        loading_window.geometry("300x150")
        loading_window.transient(parent.winfo_toplevel())
        loading_window.grab_set()
        
        # Center the loading window
        loading_window.update_idletasks()
        width = loading_window.winfo_width()
        height = loading_window.winfo_height()
        x = (loading_window.winfo_screenwidth() // 2) - (width // 2)
        y = (loading_window.winfo_screenheight() // 2) - (height // 2)
        loading_window.geometry('{}x{}+{}+{}'.format(width, height, x, y))
        
        # Add progress bar and label
        ttk.Label(loading_window, text=f"Preparing {title} Excel file...", font=("Arial", 10)).pack(pady=10)
        progress = ttk.Progressbar(loading_window, orient="horizontal", length=250, mode="indeterminate")
        progress.pack(pady=10)
        progress.start(10)
        
        def download_task():
            default_name = f"{title.replace(' ', '_')}_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            f = filedialog.asksaveasfilename(
                initialfile=default_name,
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")]
            )
            if f:
                # Simulate processing time
                time.sleep(1)
                dataframe.to_excel(f, index=False)
                loading_window.destroy()
                messagebox.showinfo("Success", f"Table saved to {f}")
            else:
                loading_window.destroy()
        
        threading.Thread(target=download_task).start()
        
    ttk.Button(button_frame, text="Download CSV", command=download_csv).pack(side='left', padx=2)
    ttk.Button(button_frame, text="Download Excel", command=download_excel).pack(side='left', padx=2)
    # Table container with scrollbars
    container = ttk.Frame(frame)
    container.pack(fill='both', expand=True, padx=5, pady=5)

    # Create the treeview with both scrollbars
    tree = ttk.Treeview(container, columns=list(dataframe.columns), show="headings")
    vsb = ttk.Scrollbar(container, orient="vertical", command=tree.yview)
    hsb = ttk.Scrollbar(container, orient="horizontal", command=tree.xview)
    tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

    # Grid layout for scrollbars
    tree.grid(column=0, row=0, sticky='nsew')
    vsb.grid(column=1, row=0, sticky='ns')
    hsb.grid(column=0, row=1, sticky='ew')
    container.grid_columnconfigure(0, weight=1)
    container.grid_rowconfigure(0, weight=1)

    # Configure columns and populate data
    for col in dataframe.columns:
        tree.heading(col, text=col, command=lambda _col=col: sort_column(tree, _col, False))
        tree.column(col, anchor='w', width=max(100, len(str(col))*10))
        
    for _, row in dataframe.iterrows():
        item = tree.insert("", "end", values=list(row))
        category = row.get("Category", "Other")
        bg = category_colors.get(str(category).strip(), category_colors["Other"])
        tree.tag_configure(category, background=bg)
        tree.item(item, tags=(category,))

    return frame

# === RUN ANALYSIS ===
def run_analysis_gui(params):
    # Create loading window
    loading_window = tk.Toplevel()
    loading_window.title("Analyzing Data")
    loading_window.geometry("400x250")
    loading_window.configure(bg="#f0f4f8")
    
    # Center the loading window
    loading_window.update_idletasks()
    width = loading_window.winfo_width()
    height = loading_window.winfo_height()
    x = (loading_window.winfo_screenwidth() // 2) - (width // 2)
    y = (loading_window.winfo_screenheight() // 2) - (height // 2)
    loading_window.geometry('{}x{}+{}+{}'.format(width, height, x, y))
    
    # Add MTN logo if available
    try:
        logo_img = Image.open(LOGO_FILE).resize((80, 80))
        logo_tk = ImageTk.PhotoImage(logo_img)
        tk.Label(loading_window, image=logo_tk, bg="#f0f4f8").pack(pady=10)
        loading_window.logo_ref = logo_tk  # Keep a reference to prevent garbage collection
    except:
        pass
    
    # Add progress indicators
    ttk.Label(loading_window, text="Generating AI Recommendations...", 
              font=("Arial", 12, "bold"), background="#f0f4f8").pack(pady=10)
    
    progress = ttk.Progressbar(loading_window, orient="horizontal", 
                              length=350, mode="indeterminate")
    progress.pack(pady=10)
    progress.start(10)
    
    status_var = tk.StringVar(value="Loading data...")
    status_label = ttk.Label(loading_window, textvariable=status_var, 
                            background="#f0f4f8", font=("Arial", 10))
    status_label.pack(pady=5)
    
    # Run analysis in a separate thread
    def run_analysis_thread():
        try:
            status_var.set("Loading subscriber and product data...")
            model = GenerativeModel("gemini-2.0-flash-001")
            
            try:
                subscriber_df = pd.read_csv(SUBSCRIBER_FILE, on_bad_lines='skip', nrows=50)
                product_df = pd.read_csv(PRODUCT_FILE, on_bad_lines='skip', nrows=20)
                
                # Clean column names
                subscriber_df.columns = [str(col).strip() for col in subscriber_df.columns]
                product_df.columns = [str(col).strip() for col in product_df.columns]
                
            except Exception as e:
                loading_window.destroy()
                messagebox.showerror("Error", f"Failed to load data: {str(e)}")
                return

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
    MSISDN | RecommendedProduct  | Category | Tier | ProductPrice | Reason | UpsellOption | CrossSellOption
    use product names instaed of product codes
    After the table, include a short bullet-point section with additional upsell and cross-sell insights or strategy tips. Do not include general commentary—just the table and the follow-up list.
    always make the recomednations always .
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

            # In the run_analysis_gui function, update the GUI layout section:
            gui = tk.Toplevel()
            gui.title("Gemini AI - Product Recommendations")
            gui.geometry("1500x900")
            gui.configure(bg="#f0f4f8")
            
            # Main title
            ttk.Label(gui, text="Gemini AI Product Recommendations for Subscribers", 
                      font=("Arial", 18, "bold"), background="#f0f4f8").pack(pady=10)

            # Create horizontal paned window for tables
            table_paned = ttk.PanedWindow(gui, orient=tk.HORIZONTAL)
            table_paned.pack(fill='both', expand=True, padx=10, pady=5)

            # Left frame for subscribers
            left_frame = ttk.Frame(table_paned)
            table_paned.add(left_frame, weight=1)
            create_scrollable_table(left_frame, selected_subscribers.reset_index(drop=True), "Selected Subscribers")

            # Right frame for recommendations
            right_frame = ttk.Frame(table_paned)
            table_paned.add(right_frame, weight=1)
            if table_df is not None:
                create_scrollable_table(right_frame, table_df.reset_index(drop=True), "Recommended Products Table")

            # Bottom paned window for details
            bottom_paned = ttk.PanedWindow(gui, orient=tk.VERTICAL)
            bottom_paned.pack(fill='both', expand=True, padx=10, pady=5)

            # Details frame
            details_frame = ttk.LabelFrame(bottom_paned, text="Upsell & Cross-sell Details")
            bottom_paned.add(details_frame)
            
            # Create a notebook with tabs for different views of the details
            details_notebook = ttk.Notebook(details_frame)
            details_notebook.pack(fill='both', expand=True, padx=5, pady=5)
            
            # Tab for text view
            # In the run_analysis_thread function, where you create the text view:
            
            # Tab for text view
            text_tab = ttk.Frame(details_notebook)
            details_notebook.add(text_tab, text="Text View")
            
            # Format the explanation text to make it more readable
            formatted_text = explanation_text.strip()
            # Replace Markdown bullet points with proper bullet symbols
            formatted_text = re.sub(r'^\s*\*\s+', '• ', formatted_text, flags=re.MULTILINE)
            # Replace nested Markdown bullet points
            formatted_text = re.sub(r'^\s+\*\s+', '    • ', formatted_text, flags=re.MULTILINE)
            
            exp_frame = scrolledtext.ScrolledText(text_tab, width=180, height=10, 
                                            wrap=tk.WORD, font=("Arial", 10))
            exp_frame.insert(tk.INSERT, formatted_text)
            exp_frame.pack(padx=10, pady=5, fill='both', expand=True)
            
            # Tab for table view
            table_tab = ttk.Frame(details_notebook)
            details_notebook.add(table_tab, text="Table View")
            
            # Parse the explanation text to extract upsell and cross-sell details
            def extract_bullet_points(text):
                # Find bullet points in the text
                bullet_pattern = r"[-•*]\s*(.*?)(?=\n[-•*]|\n\n|$)"
                bullets = re.findall(bullet_pattern, text, re.DOTALL)
                return [b.strip() for b in bullets if b.strip()]
            
            bullets = extract_bullet_points(explanation_text)
            
            # Create dataframe for the bullet points
            if bullets:
                # Try to categorize bullets as upsell or cross-sell
                upsell_bullets = []
                crosssell_bullets = []
                other_bullets = []
                
                for bullet in bullets:
                    if re.search(r'upsell|upgrade|higher|premium', bullet, re.IGNORECASE):
                        upsell_bullets.append(("Upsell", bullet))
                    elif re.search(r'cross.?sell|additional|complement|bundle', bullet, re.IGNORECASE):
                        crosssell_bullets.append(("Cross-sell", bullet))
                    else:
                        other_bullets.append(("Other", bullet))
                
                # Combine all categorized bullets
                categorized_bullets = upsell_bullets + crosssell_bullets + other_bullets
                
                # Create a dataframe
                details_df = pd.DataFrame(categorized_bullets, columns=["Type", "Strategy"])
                
                # Create a table for the details
                details_table_frame = ttk.Frame(table_tab)
                details_table_frame.pack(fill='both', expand=True, padx=5, pady=5)
                
                # Create the treeview
                details_tree = ttk.Treeview(details_table_frame, columns=list(details_df.columns), show="headings")
                vsb = ttk.Scrollbar(details_table_frame, orient="vertical", command=details_tree.yview)
                hsb = ttk.Scrollbar(details_table_frame, orient="horizontal", command=details_tree.xview)
                details_tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
                
                # Grid layout for scrollbars
                details_tree.grid(column=0, row=0, sticky='nsew')
                vsb.grid(column=1, row=0, sticky='ns')
                hsb.grid(column=0, row=1, sticky='ew')
                details_table_frame.grid_columnconfigure(0, weight=1)
                details_table_frame.grid_rowconfigure(0, weight=1)
                
                # Configure columns
                for col in details_df.columns:
                    details_tree.heading(col, text=col, command=lambda _col=col: sort_column(details_tree, _col, False))
                    if col == "Strategy":
                        details_tree.column(col, anchor='w', width=800)
                    else:
                        details_tree.column(col, anchor='w', width=100)
                
                # Populate data
                for _, row in details_df.iterrows():
                    item = details_tree.insert("", "end", values=list(row))
                    # Color-code by type
                    if row["Type"] == "Upsell":
                        details_tree.tag_configure("upsell", background="#d1ffd6")
                        details_tree.item(item, tags=("upsell",))
                    elif row["Type"] == "Cross-sell":
                        details_tree.tag_configure("crosssell", background="#d1f0ff")
                        details_tree.item(item, tags=("crosssell",))
                
                # Add download buttons for the details table
                button_frame = ttk.Frame(table_tab)
                button_frame.pack(fill='x', padx=5, pady=5)
                
                def download_details_csv():
                    timestamp = pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')
                    default_name = f"MTN_UpsellCrosssell_Strategies_{timestamp}.csv"
                    save_dir = os.path.join(os.path.expanduser("~"), "Documents", "MTN_Reports")
                    
                    # Create directory if it doesn't exist
                    os.makedirs(save_dir, exist_ok=True)
                    
                    f = filedialog.asksaveasfilename(
                        initialfile=default_name,
                        initialdir=save_dir,
                        defaultextension=".csv",
                        filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
                    )
                    
                    if f:
                        details_df.to_csv(f, index=False)
                        messagebox.showinfo("Success", f"Strategies saved to {f}")
                
                ttk.Button(button_frame, text="Download Strategies CSV", 
                          command=download_details_csv).pack(side='left', padx=5)
            else:
                ttk.Label(table_tab, text="No structured upsell/cross-sell details found in the AI response.",
                         font=("Arial", 10)).pack(pady=20)

            # After creating all the UI elements in the results window
            def save_to_file():
                timestamp = pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')
                default_name = f"MTN_Recommendation_Report_{timestamp}.txt"
                save_dir = os.path.join(os.path.expanduser("~"), "Documents", "MTN_Reports")
                
                # Create directory if it doesn't exist
                os.makedirs(save_dir, exist_ok=True)
                
                f = filedialog.asksaveasfilename(
                    initialfile=default_name,
                    initialdir=save_dir,
                    defaultextension=".txt", 
                    filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
                )
                
                if f:
                    with open(f, "w", encoding="utf-8") as out:
                        out.write("Selected Subscribers\n")
                        out.write(subscriber_data_str + "\n\n")
                        out.write("Gemini AI Recommendations\n")
                        out.write(response_text.strip())
                    messagebox.showinfo("Success", f"Text report saved to {f}")

            def download_complete_report():
                # Create loading window
                loading_window = tk.Toplevel()
                loading_window.title("Generating Complete Report...")
                loading_window.geometry("350x180")
                loading_window.transient(gui)
                loading_window.grab_set()
                set_app_icon(loading_window)  # Set the app icon
                
                # Center the loading window
                loading_window.update_idletasks()
                width = loading_window.winfo_width()
                height = loading_window.winfo_height()
                x = (loading_window.winfo_screenwidth() // 2) - (width // 2)
                y = (loading_window.winfo_screenheight() // 2) - (height // 2)
                loading_window.geometry('{}x{}+{}+{}'.format(width, height, x, y))
                
                # Add progress bar and label
                ttk.Label(loading_window, text="Preparing comprehensive report...", font=("Arial", 10, "bold")).pack(pady=10)
                progress = ttk.Progressbar(loading_window, orient="horizontal", length=300, mode="indeterminate")
                progress.pack(pady=10)
                progress.start(10)
                
                status_var = tk.StringVar(value="Compiling data...")
                status_label = ttk.Label(loading_window, textvariable=status_var, font=("Arial", 9))
                status_label.pack(pady=5)
                
                def report_task():
                    try:
                        timestamp = pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')
                        default_name = f"MTN_Complete_Recommendation_Report_{timestamp}.xlsx"
                        save_dir = os.path.join(os.path.expanduser("~"), "Documents", "MTN_Reports")
                        
                        # Create directory if it doesn't exist
                        os.makedirs(save_dir, exist_ok=True)
                        
                        # First ask for Excel file
                        status_var.set("Preparing Excel workbook...")
                        excel_file = filedialog.asksaveasfilename(
                            initialfile=default_name,
                            initialdir=save_dir,
                            defaultextension=".xlsx",
                            filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")]
                        )
                        
                        if not excel_file:  # User canceled
                            loading_window.destroy()
                            return
                        
                        if excel_file:
                            # Create Excel writer
                            status_var.set("Creating Excel workbook...")
                            with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
                                # Write subscriber data
                                status_var.set("Adding subscriber data...")
                                selected_subscribers.to_excel(writer, sheet_name='Subscribers', index=False)
                                
                                # Write recommendations
                                status_var.set("Adding recommendations...")
                                if table_df is not None:
                                    table_df.to_excel(writer, sheet_name='Recommendations', index=False)
                                
                                # Create a sheet for insights
                                status_var.set("Adding insights and details...")
                                insights_df = pd.DataFrame({'Insights': [explanation_text.strip()]})
                                insights_df.to_excel(writer, sheet_name='Insights', index=False)
                                
                                # Add metadata sheet
                                status_var.set("Adding metadata...")
                                metadata = {
                                    'Report Generated': pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S'),
                                    'Number of Subscribers': len(selected_subscribers),
                                    'Selection Mode': mode,
                                    'Variables Used': ", ".join(k for k, v in params['variables'].items() if v.get())
                                }
                                metadata_df = pd.DataFrame(list(metadata.items()), columns=['Parameter', 'Value'])
                                metadata_df.to_excel(writer, sheet_name='Metadata', index=False)
                            
                            # Also create a PDF version if requested
                            status_var.set("Report saved successfully!")
                            time.sleep(1)
                            loading_window.destroy()
                            messagebox.showinfo("Success", f"Complete report saved to {excel_file}")
                        else:
                            loading_window.destroy()
                    except Exception as e:
                        loading_window.destroy()
                        messagebox.showerror("Error", f"Failed to generate report: {str(e)}")
                
                threading.Thread(target=report_task).start()
            
            # Add buttons at the bottom
            button_frame = ttk.Frame(gui)
            button_frame.pack(pady=10)
            ttk.Button(button_frame, text="Save Text Output", command=save_to_file).pack(side='left', padx=10)
            ttk.Button(button_frame, text="Download Complete Report", command=download_complete_report).pack(side='left', padx=10)
            ttk.Button(gui, text="Save Output to File", command=save_to_file).pack(pady=10)
            
            # Close the loading window
            loading_window.destroy()
            
        except Exception as e:
            # Handle any errors that occur during analysis
            loading_window.destroy()
            messagebox.showerror("Error", f"An error occurred during analysis: {str(e)}")
    
    # Start the analysis thread
    threading.Thread(target=run_analysis_thread).start()

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

# 4. Recommendation Comparison View
def show_comparison_view():
    comparison_window = tk.Toplevel()
    comparison_window.title("Recommendation Comparison")
    comparison_window.geometry("1200x800")
    comparison_window.configure(bg="#f0f4f8")
    
    ttk.Label(comparison_window, text="Product Recommendation Comparison", 
             font=("Arial", 16, "bold"), background="#f0f4f8").pack(pady=10)
    
    # Create a frame for the comparison chart
    chart_frame = ttk.Frame(comparison_window)
    chart_frame.pack(fill="both", expand=True, padx=20, pady=10)
    
    # Create a simple bar chart showing recommendation distribution
    if table_df is not None:
        # Count recommendations by category
        category_counts = table_df['Category'].value_counts()
        
        # Create a simple bar chart using Tkinter
        canvas = tk.Canvas(chart_frame, bg="white", width=800, height=400)
        canvas.pack(fill="both", expand=True)
        
        # Draw bars
        max_count = max(category_counts)
        bar_width = 100
        spacing = 50
        start_x = 100
        
        for i, (category, count) in enumerate(category_counts.items()):
            x = start_x + i * (bar_width + spacing)
            height = (count / max_count) * 300
            y = 350 - height
            
            # Draw the bar
            color = category_colors.get(str(category).strip(), category_colors["Other"])
            canvas.create_rectangle(x, y, x + bar_width, 350, fill=color)
            
            # Add category label
            canvas.create_text(x + bar_width/2, 370, text=category, anchor="n")
            
            # Add count label
            canvas.create_text(x + bar_width/2, y - 10, text=str(count), anchor="s")
        
        # Add axis labels
        canvas.create_text(50, 200, text="Count", angle=90, anchor="center")
        canvas.create_text(400, 400, text="Category", anchor="center")

# Add a comparison button to the results window
ttk.Button(button_frame, text="Show Comparison View", 
          command=show_comparison_view).pack(side='left', padx=10)
