import matplotlib.pyplot as plt
import pandas as pd
from collections import Counter
import seaborn as sns
import numpy as np
import os

class JobDataVisualizer:
    def __init__(self):
        plt.style.use('default')
        sns.set_palette("husl")
        
        # Set up matplotlib for better display
        plt.rcParams['figure.figsize'] = (12, 8)
        plt.rcParams['font.size'] = 10
        plt.rcParams['axes.titlesize'] = 14
        plt.rcParams['axes.labelsize'] = 12
        plt.rcParams['xtick.labelsize'] = 10
        plt.rcParams['ytick.labelsize'] = 10
        plt.rcParams['legend.fontsize'] = 10
    
    def create_visualizations(self, jobs_data, trends_data, output_dir):
        """Create comprehensive visualizations"""
        print("📊 Creating data visualizations...")
        
        if not jobs_data or not trends_data:
            print("   ⚠️ No data available for visualization")
            return
        
        try:
            # Create output directory if it doesn't exist
            os.makedirs(output_dir, exist_ok=True)
            
            # Create multiple charts
            self.plot_top_jobs(trends_data.get('top_jobs', []), output_dir)
            self.plot_top_skills(trends_data.get('top_skills', []), output_dir)
            self.plot_top_cities(trends_data.get('top_cities', []), output_dir)
            self.plot_job_sources(trends_data.get('sources', {}), output_dir)
            self.plot_job_types(trends_data.get('job_type_distribution', {}), output_dir)
            self.plot_salary_distribution(trends_data.get('salary_info', {}), output_dir)
            self.plot_posting_trends(trends_data.get('posting_trends', {}), output_dir)
            self.create_summary_dashboard(jobs_data, trends_data, output_dir)
            
            print(f"   ✅ Visualizations saved to {output_dir}")
            
        except Exception as e:
            print(f"   ❌ Error creating visualizations: {e}")
    
    def plot_top_jobs(self, top_jobs, output_dir):
        """Plot top job titles"""
        if not top_jobs:
            return
            
        jobs, counts = zip(*top_jobs[:10])
        
        plt.figure(figsize=(14, 8))
        bars = plt.barh(range(len(jobs)), counts, color='skyblue', edgecolor='navy', alpha=0.7)
        plt.yticks(range(len(jobs)), jobs)
        plt.xlabel('Number of Job Postings')
        plt.title('Top 10 Job Titles', fontsize=16, fontweight='bold')
        plt.gca().invert_yaxis()
        
        # Add value labels on bars
        for i, bar in enumerate(bars):
            width = bar.get_width()
            plt.text(width + 0.5, bar.get_y() + bar.get_height()/2, 
                    str(counts[i]), ha='left', va='center', fontweight='bold')
        
        plt.grid(axis='x', alpha=0.3)
        plt.tight_layout()
        plt.savefig(f"{output_dir}/top_jobs.png", dpi=300, bbox_inches='tight')
        plt.close()
    
    def plot_top_skills(self, top_skills, output_dir):
        """Plot top skills as pie chart"""
        if not top_skills:
            return
            
        skills, counts = zip(*top_skills[:10])
        
        plt.figure(figsize=(12, 10))
        colors = plt.cm.Set3(np.linspace(0, 1, len(skills)))
        wedges, texts, autotexts = plt.pie(counts, labels=skills, autopct='%1.1f%%', 
                                          startangle=90, colors=colors)
        
        # Enhance text appearance
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
        
        plt.title('Top 10 Required Skills Distribution', fontsize=16, fontweight='bold')
        plt.axis('equal')
        
        plt.tight_layout()
        plt.savefig(f"{output_dir}/top_skills.png", dpi=300, bbox_inches='tight')
        plt.close()
    
    def plot_top_cities(self, top_cities, output_dir):
        """Plot top cities"""
        if not top_cities:
            return
            
        cities, counts = zip(*top_cities[:10])
        
        plt.figure(figsize=(14, 8))
        bars = plt.bar(range(len(cities)), counts, color='lightcoral', 
                      edgecolor='darkred', alpha=0.7)
        plt.xticks(range(len(cities)), cities, rotation=45, ha='right')
        plt.ylabel('Number of Job Postings')
        plt.title('Top 10 Hiring Cities', fontsize=16, fontweight='bold')
        
        # Add value labels on bars
        for i, bar in enumerate(bars):
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                    str(counts[i]), ha='center', va='bottom', fontweight='bold')
        
        plt.grid(axis='y', alpha=0.3)
        plt.tight_layout()
        plt.savefig(f"{output_dir}/top_cities.png", dpi=300, bbox_inches='tight')
        plt.close()
    
    def plot_job_sources(self, sources, output_dir):
        """Plot job sources distribution"""
        if not sources:
            return
            
        plt.figure(figsize=(10, 8))
        sources_list = list(sources.keys())
        counts = list(sources.values())
        
        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7']
        plt.pie(counts, labels=sources_list, autopct='%1.1f%%', 
                colors=colors[:len(sources_list)], startangle=90)
        plt.title('Job Sources Distribution', fontsize=16, fontweight='bold')
        plt.axis('equal')
        
        plt.tight_layout()
        plt.savefig(f"{output_dir}/job_sources.png", dpi=300, bbox_inches='tight')
        plt.close()
    
    def plot_job_types(self, job_types, output_dir):
        """Plot job types distribution"""
        if not job_types:
            return
            
        plt.figure(figsize=(10, 6))
        types = list(job_types.keys())
        counts = list(job_types.values())
        
        bars = plt.bar(types, counts, color='lightgreen', edgecolor='darkgreen', alpha=0.7)
        plt.ylabel('Number of Jobs')
        plt.title('Job Type Distribution', fontsize=16, fontweight='bold')
        plt.xticks(rotation=45, ha='right')
        
        # Add value labels
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                    str(int(height)), ha='center', va='bottom', fontweight='bold')
        
        plt.grid(axis='y', alpha=0.3)
        plt.tight_layout()
        plt.savefig(f"{output_dir}/job_types.png", dpi=300, bbox_inches='tight')
        plt.close()
    
    def plot_salary_distribution(self, salary_info, output_dir):
        """Plot salary distribution"""
        salary_values = salary_info.get('salary_values', [])
        salary_ranges = salary_info.get('salary_ranges', {})
        
        if not salary_values and not salary_ranges:
            return
        
        # Create subplot for both histogram and range distribution
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
        
        # Histogram of salary values
        if salary_values:
            ax1.hist(salary_values, bins=15, alpha=0.7, color='gold', 
                    edgecolor='orange', density=False)
            ax1.set_xlabel('Salary (USD)')
            ax1.set_ylabel('Number of Jobs')
            ax1.set_title('Salary Distribution', fontweight='bold')
            ax1.grid(True, alpha=0.3)
            
            # Add average line
            avg_salary = np.mean(salary_values)
            ax1.axvline(avg_salary, color='red', linestyle='--', linewidth=2,
                       label=f'Average: ${avg_salary:,.0f}')
            ax1.legend()
        
        # Salary ranges bar chart
        if salary_ranges:
            ranges = list(salary_ranges.keys())
            range_counts = list(salary_ranges.values())
            
            # Clean up range names
            clean_ranges = [r.replace('_', ' ').replace('k', 'K').title() for r in ranges]
            
            bars = ax2.bar(clean_ranges, range_counts, color='mediumpurple', 
                          edgecolor='purple', alpha=0.7)
            ax2.set_ylabel('Number of Jobs')
            ax2.set_title('Salary Range Distribution', fontweight='bold')
            ax2.tick_params(axis='x', rotation=45)
            
            # Add value labels
            for bar in bars:
                height = bar.get_height()
                ax2.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                        str(int(height)), ha='center', va='bottom', fontweight='bold')
        
        plt.tight_layout()
        plt.savefig(f"{output_dir}/salary_distribution.png", dpi=300, bbox_inches='tight')
        plt.close()
    
    def plot_posting_trends(self, posting_trends, output_dir):
        """Plot posting trends over time"""
        if not posting_trends:
            return
            
        dates = list(posting_trends.keys())
        counts = list(posting_trends.values())
        
        # Sort by date
        date_count_pairs = list(zip(dates, counts))
        date_count_pairs.sort(key=lambda x: x[0])
        dates, counts = zip(*date_count_pairs)
        
        plt.figure(figsize=(14, 6))
        plt.plot(dates, counts, marker='o', linewidth=3, markersize=8, 
                color='steelblue', markerfacecolor='orange')
        plt.xlabel('Date')
        plt.ylabel('Number of Job Postings')
        plt.title('Job Posting Trends Over Time', fontsize=16, fontweight='bold')
        plt.xticks(rotation=45, ha='right')
        plt.grid(True, alpha=0.3)
        
        # Add trend line
        if len(dates) > 1:
            z = np.polyfit(range(len(dates)), counts, 1)
            p = np.poly1d(z)
            plt.plot(dates, p(range(len(dates))), "--", color='red', alpha=0.8,
                    label='Trend Line')
            plt.legend()
        
        plt.tight_layout()
        plt.savefig(f"{output_dir}/posting_trends.png", dpi=300, bbox_inches='tight')
        plt.close()
    
    def create_summary_dashboard(self, jobs_data, trends_data, output_dir):
        """Create a comprehensive summary dashboard"""
        fig = plt.figure(figsize=(20, 12))
        
        # Create a 3x3 grid
        gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)
        
        # 1. Top Jobs (top-left)
        ax1 = fig.add_subplot(gs[0, 0])
        top_jobs = trends_data.get('top_jobs', [])[:5]
        if top_jobs:
            jobs, counts = zip(*top_jobs)
            ax1.barh(range(len(jobs)), counts, color='skyblue')
            ax1.set_yticks(range(len(jobs)))
            ax1.set_yticklabels(jobs, fontsize=8)
            ax1.set_title('Top 5 Job Titles', fontweight='bold')
            ax1.invert_yaxis()
        
        # 2. Top Skills (top-center)
        ax2 = fig.add_subplot(gs[0, 1])
        top_skills = trends_data.get('top_skills', [])[:5]
        if top_skills:
            skills, counts = zip(*top_skills)
            ax2.pie(counts, labels=skills, autopct='%1.1f%%', startangle=90)
            ax2.set_title('Top 5 Skills', fontweight='bold')
        
        # 3. Job Sources (top-right)
        ax3 = fig.add_subplot(gs[0, 2])
        sources = trends_data.get('sources', {})
        if sources:
            source_names = list(sources.keys())
            source_counts = list(sources.values())
            ax3.pie(source_counts, labels=source_names, autopct='%1.1f%%', startangle=90)
            ax3.set_title('Data Sources', fontweight='bold')
        
        # 4. Top Cities (middle-left)
        ax4 = fig.add_subplot(gs[1, 0])
        top_cities = trends_data.get('top_cities', [])[:5]
        if top_cities:
            cities, counts = zip(*top_cities)
            ax4.bar(range(len(cities)), counts, color='lightcoral')
            ax4.set_xticks(range(len(cities)))
            ax4.set_xticklabels(cities, rotation=45, ha='right', fontsize=8)
            ax4.set_title('Top 5 Cities', fontweight='bold')
        
        # 5. Job Types (middle-center)
        ax5 = fig.add_subplot(gs[1, 1])
        job_types = trends_data.get('job_type_distribution', {})
        if job_types:
            types = list(job_types.keys())
            type_counts = list(job_types.values())
            ax5.bar(types, type_counts, color='lightgreen')
            ax5.set_title('Job Types', fontweight='bold')
            ax5.tick_params(axis='x', rotation=45)
        
        # 6. Salary Ranges (middle-right)
        ax6 = fig.add_subplot(gs[1, 2])
        salary_ranges = trends_data.get('salary_info', {}).get('salary_ranges', {})
        if salary_ranges:
            ranges = list(salary_ranges.keys())
            range_counts = list(salary_ranges.values())
            clean_ranges = [r.replace('_', ' ').title() for r in ranges]
            ax6.bar(clean_ranges, range_counts, color='gold')
            ax6.set_title('Salary Ranges', fontweight='bold')
            ax6.tick_params(axis='x', rotation=45)
        
        # 7. Summary Statistics (bottom span)
        ax7 = fig.add_subplot(gs[2, :])
        ax7.axis('off')
        
        # Create summary text
        total_jobs = trends_data.get('total_jobs', 0)
        top_job = trends_data.get('top_jobs', [('N/A', 0)])[0][0]
        top_skill = trends_data.get('top_skills', [('N/A', 0)])[0][0]
        top_city = trends_data.get('top_cities', [('N/A', 0)])[0][0]
        
        summary_text = f"""
        REAL-TIME JOB TREND ANALYSIS SUMMARY
        
        📊 Total Jobs Analyzed: {total_jobs}
        🏆 Most Common Job Title: {top_job}
        🔧 Most Required Skill: {top_skill}
        📍 Top Hiring Location: {top_city}
        
        💼 Data Sources: {', '.join(trends_data.get('sources', {}).keys())}
        📅 Analysis Date: {trends_data.get('analysis_date', 'N/A')}
        """
        
        ax7.text(0.5, 0.5, summary_text, transform=ax7.transAxes, 
                fontsize=12, ha='center', va='center',
                bbox=dict(boxstyle="round,pad=0.3", facecolor="lightblue", alpha=0.5))
        
        plt.suptitle('Job Market Analysis Dashboard', fontsize=20, fontweight='bold')
        plt.savefig(f"{output_dir}/summary_dashboard.png", dpi=300, bbox_inches='tight')
        plt.close()

# Example usage
if __name__ == "__main__":
    visualizer = JobDataVisualizer()
    
    # Sample data for testing
    sample_jobs = [
        {'title': 'Python Developer', 'salary': '$80k - $120k'},
        {'title': 'Data Scientist', 'salary': '$90k - $130k'},
    ]
    
    sample_trends = {
        'top_jobs': [('Python Developer', 25), ('Data Scientist', 20)],
        'top_skills': [('Python', 45), ('SQL', 30)],
        'top_cities': [('New York', 30), ('San Francisco', 25)],
        'sources': {'LinkedIn': 30, 'Glassdoor': 20},
        'job_type_distribution': {'Full-time': 40, 'Contract': 10},
        'salary_info': {
            'salary_values': [80000, 90000, 100000, 110000, 120000],
            'salary_ranges': {'50k_100k': 20, '100k_150k': 25}
        },
        'posting_trends': {'2024-01-01': 5, '2024-01-02': 8},
        'total_jobs': 50,
        'analysis_date': '2024-01-15 10:30:00'
    }
    
    visualizer.create_visualizations(sample_jobs, sample_trends, "test_output")
    print("Test visualizations created!")