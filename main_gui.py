import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import threading
import queue
import os
from datetime import datetime
import json
import csv
from job_scraper import RealJobScraper
from data_analyzer import JobDataAnalyzer
import webbrowser

class JobTrendAnalyzerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Real-Time Job Trend Analyzer")
        self.root.geometry("1200x800")
        self.root.configure(bg='#f0f0f0')
        
        # Initialize components
        self.scraper = RealJobScraper()
        self.analyzer = JobDataAnalyzer()
        self.jobs_data = []
        self.trends_data = {}
        
        # Queue for thread communication
        self.queue = queue.Queue()
        
        # Create GUI
        self.create_widgets()
        
        # Start queue processing
        self.process_queue()
    
    def create_widgets(self):
        """Create the main GUI interface"""
        # Main title
        title_frame = tk.Frame(self.root, bg='#2c3e50', height=80)
        title_frame.pack(fill='x', padx=10, pady=5)
        title_frame.pack_propagate(False)
        
        title_label = tk.Label(title_frame, text="🔍 Real-Time Job Trend Analyzer", 
                              font=('Arial', 24, 'bold'), fg='white', bg='#2c3e50')
        title_label.pack(expand=True)
        
        # Main container
        main_frame = tk.Frame(self.root, bg='#f0f0f0')
        main_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Left panel - Search controls
        self.create_search_panel(main_frame)
        
        # Right panel - Results
        self.create_results_panel(main_frame)
        
        # Bottom panel - Status and controls
        self.create_status_panel()
    
    def create_search_panel(self, parent):
        """Create the search input panel"""
        search_frame = tk.LabelFrame(parent, text="Search Parameters", 
                                   font=('Arial', 12, 'bold'), bg='#f0f0f0')
        search_frame.pack(side='left', fill='y', padx=(0, 10), pady=5)
        
        # Skill input
        tk.Label(search_frame, text="Skill/Technology:", 
                font=('Arial', 10, 'bold'), bg='#f0f0f0').pack(anchor='w', padx=10, pady=(10, 5))
        
        self.skill_var = tk.StringVar(value="Python")
        skill_entry = tk.Entry(search_frame, textvariable=self.skill_var, 
                              font=('Arial', 11), width=25)
        skill_entry.pack(padx=10, pady=(0, 10))
        
        # Location input
        tk.Label(search_frame, text="Location (Optional):", 
                font=('Arial', 10, 'bold'), bg='#f0f0f0').pack(anchor='w', padx=10, pady=(0, 5))
        
        self.location_var = tk.StringVar(value="New York")
        location_entry = tk.Entry(search_frame, textvariable=self.location_var, 
                                 font=('Arial', 11), width=25)
        location_entry.pack(padx=10, pady=(0, 10))
        
        # Job sources
        sources_frame = tk.LabelFrame(search_frame, text="Data Sources", bg='#f0f0f0')
        sources_frame.pack(fill='x', padx=10, pady=10)
        
        self.linkedin_var = tk.BooleanVar(value=True)
        self.glassdoor_var = tk.BooleanVar(value=True)
        self.indeed_var = tk.BooleanVar(value=True)
        
        tk.Checkbutton(sources_frame, text="LinkedIn", variable=self.linkedin_var, 
                      bg='#f0f0f0', font=('Arial', 10)).pack(anchor='w', padx=5, pady=2)
        tk.Checkbutton(sources_frame, text="Glassdoor", variable=self.glassdoor_var, 
                      bg='#f0f0f0', font=('Arial', 10)).pack(anchor='w', padx=5, pady=2)
        tk.Checkbutton(sources_frame, text="Indeed", variable=self.indeed_var, 
                      bg='#f0f0f0', font=('Arial', 10)).pack(anchor='w', padx=5, pady=2)
        
        # Search options
        options_frame = tk.LabelFrame(search_frame, text="Search Options", bg='#f0f0f0')
        options_frame.pack(fill='x', padx=10, pady=10)
        
        tk.Label(options_frame, text="Max Jobs per Source:", 
                font=('Arial', 10), bg='#f0f0f0').pack(anchor='w', padx=5, pady=2)
        
        self.max_jobs_var = tk.StringVar(value="50")
        max_jobs_spinbox = tk.Spinbox(options_frame, from_=10, to=200, 
                                     textvariable=self.max_jobs_var, width=10)
        max_jobs_spinbox.pack(anchor='w', padx=5, pady=2)
        
        # Search button
        self.search_button = tk.Button(search_frame, text="🔍 Start Analysis", 
                                      command=self.start_search, font=('Arial', 12, 'bold'),
                                      bg='#3498db', fg='white', height=2, width=20)
        self.search_button.pack(pady=20)
        
        # Export buttons
        export_frame = tk.LabelFrame(search_frame, text="Export Data", bg='#f0f0f0')
        export_frame.pack(fill='x', padx=10, pady=10)
        
        tk.Button(export_frame, text="📄 Export TXT", command=self.export_txt,
                 bg='#95a5a6', fg='white', width=15).pack(pady=2)
        tk.Button(export_frame, text="📊 Export CSV", command=self.export_csv,
                 bg='#95a5a6', fg='white', width=15).pack(pady=2)
        tk.Button(export_frame, text="📈 Generate Charts", command=self.generate_charts,
                 bg='#95a5a6', fg='white', width=15).pack(pady=2)
    
    def create_results_panel(self, parent):
        """Create the results display panel"""
        results_frame = tk.LabelFrame(parent, text="Analysis Results", 
                                    font=('Arial', 12, 'bold'), bg='#f0f0f0')
        results_frame.pack(side='right', fill='both', expand=True, pady=5)
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(results_frame)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Summary tab
        self.create_summary_tab()
        
        # Jobs tab
        self.create_jobs_tab()
        
        # Trends tab
        self.create_trends_tab()
        
        # Raw data tab
        self.create_raw_data_tab()
    
    def create_summary_tab(self):
        """Create the summary tab"""
        summary_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(summary_frame, text="📊 Summary")
        
        # Summary text widget
        self.summary_text = scrolledtext.ScrolledText(summary_frame, wrap=tk.WORD, 
                                                     font=('Courier', 10), height=20)
        self.summary_text.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Initial message
        self.summary_text.insert('1.0', "Welcome to Real-Time Job Trend Analyzer!\n\n"
                                        "Enter a skill and location, then click 'Start Analysis' to begin.\n\n"
                                        "This tool will scrape real job data from:\n"
                                        "• LinkedIn Jobs\n"
                                        "• Glassdoor\n"
                                        "• Indeed\n\n"
                                        "And provide comprehensive analysis including:\n"
                                        "• Top job titles and companies\n"
                                        "• Required skills analysis\n"
                                        "• Salary information\n"
                                        "• Geographic trends\n"
                                        "• Market insights")
    
    def create_jobs_tab(self):
        """Create the jobs listing tab"""
        jobs_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(jobs_frame, text="💼 Job Listings")
        
        # Jobs treeview
        columns = ('Title', 'Company', 'Location', 'Source', 'Salary', 'Date')
        self.jobs_tree = ttk.Treeview(jobs_frame, columns=columns, show='headings', height=15)
        
        # Configure columns
        for col in columns:
            self.jobs_tree.heading(col, text=col)
            self.jobs_tree.column(col, width=120)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(jobs_frame, orient='vertical', command=self.jobs_tree.yview)
        h_scrollbar = ttk.Scrollbar(jobs_frame, orient='horizontal', command=self.jobs_tree.xview)
        self.jobs_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Pack treeview and scrollbars
        self.jobs_tree.pack(side='left', fill='both', expand=True, padx=(10, 0), pady=10)
        v_scrollbar.pack(side='right', fill='y', pady=10)
        h_scrollbar.pack(side='bottom', fill='x', padx=10)
        
        # Job details frame
        details_frame = tk.Frame(jobs_frame, bg='white', width=300)
        details_frame.pack(side='right', fill='y', padx=10, pady=10)
        details_frame.pack_propagate(False)
        
        tk.Label(details_frame, text="Job Details", font=('Arial', 12, 'bold'), 
                bg='white').pack(pady=(0, 10))
        
        self.job_details_text = scrolledtext.ScrolledText(details_frame, wrap=tk.WORD, 
                                                         font=('Arial', 9), height=20)
        self.job_details_text.pack(fill='both', expand=True)
        
        # Bind selection event
        self.jobs_tree.bind('<<TreeviewSelect>>', self.on_job_select)
    
    def create_trends_tab(self):
        """Create the trends analysis tab"""
        trends_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(trends_frame, text="📈 Trends")
        
        # Create sub-frames for different trend categories
        top_frame = tk.Frame(trends_frame, bg='white')
        top_frame.pack(fill='x', padx=10, pady=5)
        
        bottom_frame = tk.Frame(trends_frame, bg='white')
        bottom_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Top jobs frame
        jobs_trend_frame = tk.LabelFrame(top_frame, text="Top Job Titles", bg='white')
        jobs_trend_frame.pack(side='left', fill='both', expand=True, padx=(0, 5))
        
        self.top_jobs_listbox = tk.Listbox(jobs_trend_frame, font=('Arial', 9), height=8)
        self.top_jobs_listbox.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Top skills frame
        skills_trend_frame = tk.LabelFrame(top_frame, text="Top Skills", bg='white')
        skills_trend_frame.pack(side='right', fill='both', expand=True, padx=(5, 0))
        
        self.top_skills_listbox = tk.Listbox(skills_trend_frame, font=('Arial', 9), height=8)
        self.top_skills_listbox.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Detailed trends
        detailed_trends_frame = tk.LabelFrame(bottom_frame, text="Detailed Analysis", bg='white')
        detailed_trends_frame.pack(fill='both', expand=True)
        
        self.trends_text = scrolledtext.ScrolledText(detailed_trends_frame, wrap=tk.WORD, 
                                                    font=('Courier', 9))
        self.trends_text.pack(fill='both', expand=True, padx=5, pady=5)
    
    def create_raw_data_tab(self):
        """Create the raw data tab"""
        raw_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(raw_frame, text="🔧 Raw Data")
        
        self.raw_data_text = scrolledtext.ScrolledText(raw_frame, wrap=tk.WORD, 
                                                      font=('Courier', 8))
        self.raw_data_text.pack(fill='both', expand=True, padx=10, pady=10)
    
    def create_status_panel(self):
        """Create the status panel"""
        status_frame = tk.Frame(self.root, bg='#34495e', height=60)
        status_frame.pack(fill='x', side='bottom', padx=10, pady=5)
        status_frame.pack_propagate(False)
        
        # Status label
        self.status_var = tk.StringVar(value="Ready to analyze job trends")
        self.status_label = tk.Label(status_frame, textvariable=self.status_var, 
                                   font=('Arial', 10), fg='white', bg='#34495e')
        self.status_label.pack(side='left', padx=10, pady=15)
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(status_frame, variable=self.progress_var, 
                                          maximum=100, length=300)
        self.progress_bar.pack(side='right', padx=10, pady=15)
    
    def start_search(self):
        """Start the job search in a separate thread"""
        skill = self.skill_var.get().strip()
        if not skill:
            messagebox.showerror("Error", "Please enter a skill to search for!")
            return
        
        # Disable search button
        self.search_button.config(state='disabled', text="🔄 Searching...")
        
        # Clear previous results
        self.clear_results()
        
        # Start search thread
        search_thread = threading.Thread(target=self.search_jobs, daemon=True)
        search_thread.start()
    
    def search_jobs(self):
        """Search for jobs (runs in separate thread)"""
        try:
            skill = self.skill_var.get().strip()
            location = self.location_var.get().strip()
            max_jobs = int(self.max_jobs_var.get())
            
            # Update status
            self.queue.put(('status', 'Initializing job search...'))
            self.queue.put(('progress', 10))
            
            all_jobs = []
            
            # Scrape from selected sources
            if self.linkedin_var.get():
                self.queue.put(('status', 'Scraping LinkedIn jobs...'))
                self.queue.put(('progress', 20))
                linkedin_jobs = self.scraper.scrape_linkedin(skill, location, max_jobs)
                all_jobs.extend(linkedin_jobs)
                self.queue.put(('progress', 40))
            
            if self.glassdoor_var.get():
                self.queue.put(('status', 'Scraping Glassdoor jobs...'))
                glassdoor_jobs = self.scraper.scrape_glassdoor(skill, location, max_jobs)
                all_jobs.extend(glassdoor_jobs)
                self.queue.put(('progress', 60))
            
            if self.indeed_var.get():
                self.queue.put(('status', 'Scraping Indeed jobs...'))
                indeed_jobs = self.scraper.scrape_indeed(skill, location, max_jobs)
                all_jobs.extend(indeed_jobs)
                self.queue.put(('progress', 80))
            
            # Analyze data
            self.queue.put(('status', 'Analyzing job trends...'))
            trends = self.analyzer.analyze_trends(all_jobs)
            self.queue.put(('progress', 90))
            
            # Update GUI with results
            self.queue.put(('results', (all_jobs, trends)))
            self.queue.put(('progress', 100))
            self.queue.put(('status', f'Analysis complete! Found {len(all_jobs)} jobs'))
            
        except Exception as e:
            self.queue.put(('error', str(e)))
        finally:
            self.queue.put(('search_complete', None))
    
    def process_queue(self):
        """Process messages from the search thread"""
        try:
            while True:
                message_type, data = self.queue.get_nowait()
                
                if message_type == 'status':
                    self.status_var.set(data)
                elif message_type == 'progress':
                    self.progress_var.set(data)
                elif message_type == 'results':
                    self.jobs_data, self.trends_data = data
                    self.update_results()
                elif message_type == 'error':
                    messagebox.showerror("Error", f"Search failed: {data}")
                elif message_type == 'search_complete':
                    self.search_button.config(state='normal', text="🔍 Start Analysis")
                    
        except queue.Empty:
            pass
        
        # Schedule next check
        self.root.after(100, self.process_queue)
    
    def clear_results(self):
        """Clear all previous results"""
        # Clear summary
        self.summary_text.delete('1.0', tk.END)
        
        # Clear jobs tree
        for item in self.jobs_tree.get_children():
            self.jobs_tree.delete(item)
        
        # Clear job details
        self.job_details_text.delete('1.0', tk.END)
        
        # Clear trends
        self.top_jobs_listbox.delete(0, tk.END)
        self.top_skills_listbox.delete(0, tk.END)
        self.trends_text.delete('1.0', tk.END)
        
        # Clear raw data
        self.raw_data_text.delete('1.0', tk.END)
    
    def update_results(self):
        """Update the GUI with search results"""
        if not self.jobs_data or not self.trends_data:
            return
        
        # Update summary
        self.update_summary()
        
        # Update jobs listing
        self.update_jobs_listing()
        
        # Update trends
        self.update_trends()
        
        # Update raw data
        self.update_raw_data()
    
    def update_summary(self):
        """Update the summary tab"""
        summary = f"""
REAL-TIME JOB TREND ANALYSIS SUMMARY
{'='*50}

Search Query: {self.skill_var.get()} in {self.location_var.get() or 'All Locations'}
Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

OVERVIEW
--------
Total Jobs Found: {self.trends_data.get('total_jobs', 0)}
LinkedIn Jobs: {self.trends_data.get('sources', {}).get('LinkedIn', 0)}
Glassdoor Jobs: {self.trends_data.get('sources', {}).get('Glassdoor', 0)}
Indeed Jobs: {self.trends_data.get('sources', {}).get('Indeed', 0)}

TOP INSIGHTS
------------
Most Common Job Title: {self.trends_data.get('top_jobs', [('N/A', 0)])[0][0]}
Most Required Skill: {self.trends_data.get('top_skills', [('N/A', 0)])[0][0]}
Top Hiring Location: {self.trends_data.get('top_cities', [('N/A', 0)])[0][0]}
Top Hiring Company: {self.trends_data.get('top_companies', [('N/A', 0)])[0][0]}

SALARY INFORMATION
------------------
Jobs with Salary Info: {self.trends_data.get('salary_info', {}).get('total_with_salary', 0)}
Percentage with Salary: {(self.trends_data.get('salary_info', {}).get('total_with_salary', 0) / max(self.trends_data.get('total_jobs', 1), 1) * 100):.1f}%

JOB TYPE DISTRIBUTION
---------------------
"""
        
        for job_type, count in self.trends_data.get('job_type_distribution', {}).items():
            percentage = (count / max(self.trends_data.get('total_jobs', 1), 1)) * 100
            summary += f"{job_type}: {count} jobs ({percentage:.1f}%)\n"
        
        self.summary_text.insert('1.0', summary)
    
    def update_jobs_listing(self):
        """Update the jobs listing tab"""
        for job in self.jobs_data:
            self.jobs_tree.insert('', 'end', values=(
                job.get('title', 'N/A'),
                job.get('company', 'N/A'),
                job.get('location', 'N/A'),
                job.get('source', 'N/A'),
                job.get('salary', 'Not specified'),
                job.get('date_posted', 'N/A')
            ))
    
    def update_trends(self):
        """Update the trends tab"""
        # Update top jobs
        for job_title, count in self.trends_data.get('top_jobs', [])[:10]:
            self.top_jobs_listbox.insert(tk.END, f"{job_title} ({count})")
        
        # Update top skills
        for skill, count in self.trends_data.get('top_skills', [])[:10]:
            self.top_skills_listbox.insert(tk.END, f"{skill} ({count})")
        
        # Detailed trends analysis
        trends_detail = f"""
DETAILED TRENDS ANALYSIS
{'='*50}

TOP 10 JOB TITLES
-----------------
"""
        for i, (title, count) in enumerate(self.trends_data.get('top_jobs', [])[:10], 1):
            trends_detail += f"{i:2d}. {title:<40} - {count:3d} positions\n"
        
        trends_detail += f"""
TOP 15 REQUIRED SKILLS
----------------------
"""
        for i, (skill, count) in enumerate(self.trends_data.get('top_skills', [])[:15], 1):
            trends_detail += f"{i:2d}. {skill:<30} - {count:3d} mentions\n"
        
        trends_detail += f"""
TOP 10 HIRING LOCATIONS
-----------------------
"""
        for i, (city, count) in enumerate(self.trends_data.get('top_cities', [])[:10], 1):
            trends_detail += f"{i:2d}. {city:<35} - {count:3d} jobs\n"
        
        trends_detail += f"""
TOP 10 HIRING COMPANIES
-----------------------
"""
        for i, (company, count) in enumerate(self.trends_data.get('top_companies', [])[:10], 1):
            trends_detail += f"{i:2d}. {company:<30} - {count:3d} jobs\n"
        
        self.trends_text.insert('1.0', trends_detail)
    
    def update_raw_data(self):
        """Update the raw data tab"""
        raw_data = json.dumps({
            'search_parameters': {
                'skill': self.skill_var.get(),
                'location': self.location_var.get(),
                'max_jobs': self.max_jobs_var.get()
            },
            'jobs_data': self.jobs_data[:5],  # Show first 5 jobs
            'trends_data': self.trends_data
        }, indent=2)
        
        self.raw_data_text.insert('1.0', raw_data)
    
    def on_job_select(self, event):
        """Handle job selection in the treeview"""
        selection = self.jobs_tree.selection()
        if selection:
            item = self.jobs_tree.item(selection[0])
            job_index = self.jobs_tree.index(selection[0])
            
            if job_index < len(self.jobs_data):
                job = self.jobs_data[job_index]
                
                details = f"""
JOB DETAILS
{'='*30}

Title: {job.get('title', 'N/A')}
Company: {job.get('company', 'N/A')}
Location: {job.get('location', 'N/A')}
Source: {job.get('source', 'N/A')}
Job Type: {job.get('job_type', 'N/A')}
Date Posted: {job.get('date_posted', 'N/A')}
Salary: {job.get('salary', 'Not specified')}

Required Skills:
{', '.join(job.get('skills', []))}

Description:
{job.get('description', 'No description available')}

Job URL:
{job.get('url', 'Not available')}
"""
                
                self.job_details_text.delete('1.0', tk.END)
                self.job_details_text.insert('1.0', details)
    
    def export_txt(self):
        """Export results to text file"""
        if not self.jobs_data:
            messagebox.showwarning("Warning", "No data to export!")
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            title="Save analysis report"
        )
        
        if filename:
            try:
                report = self.analyzer.generate_comprehensive_report(
                    self.skill_var.get(), self.location_var.get(), 
                    self.jobs_data, self.trends_data
                )
                
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(report)
                
                messagebox.showinfo("Success", f"Report exported to {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export: {e}")
    
    def export_csv(self):
        """Export jobs data to CSV file"""
        if not self.jobs_data:
            messagebox.showwarning("Warning", "No data to export!")
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            title="Save jobs data"
        )
        
        if filename:
            try:
                with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                    fieldnames = ['title', 'company', 'location', 'skills', 'date_posted', 
                                'source', 'salary', 'job_type', 'description', 'url']
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    
                    writer.writeheader()
                    for job in self.jobs_data:
                        job_copy = job.copy()
                        job_copy['skills'] = ', '.join(job.get('skills', []))
                        writer.writerow(job_copy)
                
                messagebox.showinfo("Success", f"Data exported to {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export: {e}")
    
    def generate_charts(self):
        """Generate and display charts"""
        if not self.trends_data:
            messagebox.showwarning("Warning", "No data to visualize!")
            return
        
        try:
            from data_visualizer import JobDataVisualizer
            visualizer = JobDataVisualizer()
            
            # Create output directory
            output_dir = f"charts_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            os.makedirs(output_dir, exist_ok=True)
            
            # Generate charts
            visualizer.create_visualizations(self.jobs_data, self.trends_data, output_dir)
            
            # Open the directory
            if os.name == 'nt':  # Windows
                os.startfile(output_dir)
            elif os.name == 'posix':  # macOS and Linux
                os.system(f'open "{output_dir}"')
            
            messagebox.showinfo("Success", f"Charts generated in {output_dir}")
            
        except ImportError:
            messagebox.showerror("Error", "Visualization libraries not available!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate charts: {e}")

def main():
    """Main function to run the GUI application"""
    root = tk.Tk()
    app = JobTrendAnalyzerGUI(root)
    
    # Center the window
    root.update_idletasks()
    x = (root.winfo_screenwidth() // 2) - (root.winfo_width() // 2)
    y = (root.winfo_screenheight() // 2) - (root.winfo_height() // 2)
    root.geometry(f"+{x}+{y}")
    
    root.mainloop()

if __name__ == "__main__":
    main()