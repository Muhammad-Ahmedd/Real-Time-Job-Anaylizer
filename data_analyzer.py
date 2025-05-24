from collections import Counter
from datetime import datetime, timedelta
import re
import json

class JobDataAnalyzer:
    def __init__(self):
        pass
    
    def analyze_trends(self, jobs_data):
        """Analyze job trends and generate comprehensive insights"""
        if not jobs_data:
            return {}
        
        print(f"📊 Analyzing {len(jobs_data)} job listings...")
        
        # Basic counts
        total_jobs = len(jobs_data)
        
        # Count job titles
        job_titles = [job.get('title', 'Unknown') for job in jobs_data]
        top_jobs = Counter(job_titles).most_common(20)
        
        # Count skills
        all_skills = []
        for job in jobs_data:
            skills = job.get('skills', [])
            if isinstance(skills, list):
                all_skills.extend(skills)
            elif isinstance(skills, str):
                all_skills.extend(skills.split(', '))
        top_skills = Counter(all_skills).most_common(25)
        
        # Count locations
        locations = [job.get('location', 'Unknown') for job in jobs_data]
        top_cities = Counter(locations).most_common(15)
        
        # Count companies
        companies = [job.get('company', 'Unknown') for job in jobs_data]
        top_companies = Counter(companies).most_common(15)
        
        # Analyze posting trends by date
        posting_dates = [job.get('date_posted', datetime.now().strftime('%Y-%m-%d')) for job in jobs_data]
        posting_trends = Counter(posting_dates)
        
        # Analyze job types
        job_types = [job.get('job_type', 'Full-time') for job in jobs_data]
        job_type_distribution = Counter(job_types)
        
        # Analyze salary information
        salaries = [job.get('salary') for job in jobs_data if job.get('salary')]
        salary_analysis = self._analyze_salaries(salaries)
        
        # Analyze sources
        sources = [job.get('source', 'Unknown') for job in jobs_data]
        source_distribution = Counter(sources)
        
        # Generate insights
        insights = self._generate_insights(jobs_data, top_jobs, top_skills, top_cities)
        
        trends_data = {
            'total_jobs': total_jobs,
            'top_jobs': top_jobs,
            'top_skills': top_skills,
            'top_cities': top_cities,
            'top_companies': top_companies,
            'posting_trends': dict(posting_trends),
            'job_type_distribution': dict(job_type_distribution),
            'salary_info': salary_analysis,
            'sources': dict(source_distribution),
            'insights': insights,
            'analysis_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        print(f"   ✅ Analysis complete!")
        return trends_data
    
    def _analyze_salaries(self, salaries):
        """Analyze salary information"""
        if not salaries:
            return {
                'total_with_salary': 0,
                'sample_salaries': [],
                'salary_ranges': {},
                'average_salary': None
            }
        
        # Extract numeric values from salary strings
        salary_values = []
        salary_ranges = {'under_50k': 0, '50k_100k': 0, '100k_150k': 0, 'over_150k': 0}
        
        for salary in salaries:
            if not salary:
                continue
                
            # Extract numbers from salary string
            numbers = re.findall(r'\d+', str(salary))
            if numbers:
                try:
                    if len(numbers) >= 2:
                        # Range like "$80k - $120k"
                        avg_salary = (int(numbers[0]) + int(numbers[1])) / 2
                    else:
                        # Single value like "$100k"
                        avg_salary = int(numbers[0])
                    
                    # Handle different formats (k, K, thousands)
                    if 'k' in salary.lower() or 'K' in salary:
                        avg_salary *= 1000
                    
                    salary_values.append(avg_salary)
                    
                    # Categorize salary ranges
                    if avg_salary < 50000:
                        salary_ranges['under_50k'] += 1
                    elif avg_salary < 100000:
                        salary_ranges['50k_100k'] += 1
                    elif avg_salary < 150000:
                        salary_ranges['100k_150k'] += 1
                    else:
                        salary_ranges['over_150k'] += 1
                        
                except ValueError:
                    continue
        
        average_salary = sum(salary_values) / len(salary_values) if salary_values else None
        
        return {
            'total_with_salary': len(salaries),
            'sample_salaries': salaries[:10],
            'salary_ranges': salary_ranges,
            'average_salary': average_salary,
            'salary_values': salary_values[:20]  # Sample for visualization
        }
    
    def _generate_insights(self, jobs_data, top_jobs, top_skills, top_cities):
        """Generate market insights"""
        insights = []
        
        if not jobs_data:
            return insights
        
        total_jobs = len(jobs_data)
        
        # Job market size insight
        if total_jobs > 100:
            insights.append(f"Strong job market with {total_jobs} opportunities found")
        elif total_jobs > 50:
            insights.append(f"Moderate job market with {total_jobs} opportunities")
        else:
            insights.append(f"Limited job market with {total_jobs} opportunities")
        
        # Top job title insight
        if top_jobs:
            top_job_title, top_job_count = top_jobs[0]
            percentage = (top_job_count / total_jobs) * 100
            insights.append(f"'{top_job_title}' is the most common position ({percentage:.1f}% of jobs)")
        
        # Skills demand insight
        if top_skills:
            top_skill, skill_count = top_skills[0]
            percentage = (skill_count / total_jobs) * 100
            insights.append(f"'{top_skill}' is the most in-demand skill ({percentage:.1f}% of jobs)")
        
        # Geographic concentration
        if top_cities:
            top_city, city_count = top_cities[0]
            percentage = (city_count / total_jobs) * 100
            insights.append(f"'{top_city}' has the highest concentration of jobs ({percentage:.1f}%)")
        
        # Remote work availability
        remote_jobs = len([job for job in jobs_data if 'remote' in job.get('location', '').lower() or 
                          'remote' in job.get('job_type', '').lower()])
        if remote_jobs > 0:
            remote_percentage = (remote_jobs / total_jobs) * 100
            insights.append(f"{remote_percentage:.1f}% of jobs offer remote work options")
        
        # Salary insights
        jobs_with_salary = len([job for job in jobs_data if job.get('salary')])
        if jobs_with_salary > 0:
            salary_percentage = (jobs_with_salary / total_jobs) * 100
            insights.append(f"{salary_percentage:.1f}% of jobs include salary information")
        
        return insights
    
    def generate_comprehensive_report(self, skill, location, jobs_data, trends_data):
        """Generate a comprehensive text report"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        search_query = f"{skill}" + (f" in {location}" if location else "")
        
        report = f"""
{'='*80}
                    REAL-TIME JOB TREND ANALYZER REPORT
{'='*80}

Search Query: {search_query}
Generated: {timestamp}
Total Jobs Found: {trends_data.get('total_jobs', 0)}
Data Sources: LinkedIn, Glassdoor, Indeed

{'='*80}
                           EXECUTIVE SUMMARY
{'='*80}

🏆 Top Job Title: {trends_data.get('top_jobs', [('N/A', 0)])[0][0]} ({trends_data.get('top_jobs', [('N/A', 0)])[0][1]} positions)
🔧 Most Required Skill: {trends_data.get('top_skills', [('N/A', 0)])[0][0]} ({trends_data.get('top_skills', [('N/A', 0)])[0][1]} mentions)
📍 Top Hiring Location: {trends_data.get('top_cities', [('N/A', 0)])[0][0]} ({trends_data.get('top_cities', [('N/A', 0)])[0][1]} jobs)
🏢 Top Hiring Company: {trends_data.get('top_companies', [('N/A', 0)])[0][0]} ({trends_data.get('top_companies', [('N/A', 0)])[0][1]} jobs)

{'='*80}
                          KEY MARKET INSIGHTS
{'='*80}

"""
        
        for insight in trends_data.get('insights', []):
            report += f"• {insight}\n"
        
        report += f"""
{'='*80}
                          TOP 10 JOB TITLES
{'='*80}

"""
        
        for i, (title, count) in enumerate(trends_data.get('top_jobs', [])[:10], 1):
            report += f"{i:2d}. {title:<40} - {count:3d} positions\n"
        
        report += f"""
{'='*80}
                         TOP 15 REQUIRED SKILLS
{'='*80}

"""
        
        for i, (skill_name, count) in enumerate(trends_data.get('top_skills', [])[:15], 1):
            report += f"{i:2d}. {skill_name:<30} - {count:3d} mentions\n"
        
        report += f"""
{'='*80}
                        TOP 10 HIRING LOCATIONS
{'='*80}

"""
        
        for i, (city, count) in enumerate(trends_data.get('top_cities', [])[:10], 1):
            report += f"{i:2d}. {city:<35} - {count:3d} jobs\n"
        
        report += f"""
{'='*80}
                        TOP 10 HIRING COMPANIES
{'='*80}

"""
        
        for i, (company, count) in enumerate(trends_data.get('top_companies', [])[:10], 1):
            report += f"{i:2d}. {company:<30} - {count:3d} jobs\n"
        
        report += f"""
{'='*80}
                         JOB TYPE DISTRIBUTION
{'='*80}

"""
        
        for job_type, count in trends_data.get('job_type_distribution', {}).items():
            percentage = (count / max(trends_data.get('total_jobs', 1), 1)) * 100
            report += f"{job_type:<15} - {count:3d} jobs ({percentage:5.1f}%)\n"
        
        report += f"""
{'='*80}
                           SALARY INFORMATION
{'='*80}

Jobs with Salary Info: {trends_data.get('salary_info', {}).get('total_with_salary', 0)}/{trends_data.get('total_jobs', 0)}
Average Salary: ${trends_data.get('salary_info', {}).get('average_salary', 0):,.0f} (if available)

Salary Distribution:
"""
        
        salary_ranges = trends_data.get('salary_info', {}).get('salary_ranges', {})
        for range_name, count in salary_ranges.items():
            report += f"  {range_name.replace('_', ' ').title()}: {count} jobs\n"
        
        report += f"""
Sample Salary Ranges:
"""
        
        for salary in trends_data.get('salary_info', {}).get('sample_salaries', [])[:10]:
            report += f"  • {salary}\n"
        
        report += f"""
{'='*80}
                         DETAILED JOB LISTINGS (First 20)
{'='*80}

"""
        
        for i, job in enumerate(jobs_data[:20], 1):
            report += f"""
Job #{i}
{'-'*50}
Title: {job.get('title', 'N/A')}
Company: {job.get('company', 'N/A')}
Location: {job.get('location', 'N/A')}
Source: {job.get('source', 'N/A')}
Job Type: {job.get('job_type', 'N/A')}
Date Posted: {job.get('date_posted', 'N/A')}
{f"Salary: {job.get('salary')}" if job.get('salary') else "Salary: Not specified"}
Required Skills: {', '.join(job.get('skills', []))}
URL: {job.get('url', 'Not available')}

"""
        
        if len(jobs_data) > 20:
            report += f"\n... and {len(jobs_data) - 20} more jobs (see full data export for complete listings)\n"
        
        report += f"""
{'='*80}
                            DATA SOURCES
{'='*80}

"""
        
        for source, count in trends_data.get('sources', {}).items():
            percentage = (count / max(trends_data.get('total_jobs', 1), 1)) * 100
            report += f"{source}: {count} jobs ({percentage:.1f}%)\n"
        
        report += f"""
{'='*80}
                             METHODOLOGY
{'='*80}

Data Collection Process:
1. Search performed for "{search_query}"
2. Job listings scraped from LinkedIn, Glassdoor, and Indeed
3. Data extracted: title, company, location, skills, posting date, salary
4. Results aggregated and analyzed for trends
5. Data exported to multiple formats (TXT, CSV, JSON)

Ethical Scraping Practices:
✓ Respectful request rates (2-4 second delays)
✓ robots.txt compliance awareness
✓ User-agent identification
✓ No personal data collection
✓ Rate limiting to prevent server overload

{'='*80}
                              DISCLAIMER
{'='*80}

This data is for informational purposes only. Job market trends can change
rapidly. For the most current information, please visit the respective job
platforms directly.

The salary information and job descriptions are based on publicly available
job postings and may not reflect actual compensation or complete job requirements.

Some data may be supplemented with representative examples to demonstrate
the system's capabilities when real-time scraping encounters limitations.

Report generated by Real-Time Job Trend Analyzer
© 2025 - All rights reserved
{'='*80}
"""
        
        return report

# Example usage
if __name__ == "__main__":
    analyzer = JobDataAnalyzer()
    
    # Sample job data for testing
    sample_jobs = [
        {
            'title': 'Python Developer',
            'company': 'Tech Corp',
            'location': 'New York, NY',
            'skills': ['Python', 'Django', 'SQL'],
            'date_posted': '2024-01-15',
            'source': 'LinkedIn',
            'salary': '$80k - $120k',
            'job_type': 'Full-time'
        },
        {
            'title': 'Senior Python Engineer',
            'company': 'StartupXYZ',
            'location': 'San Francisco, CA',
            'skills': ['Python', 'FastAPI', 'AWS'],
            'date_posted': '2024-01-14',
            'source': 'Glassdoor',
            'salary': '$120k - $160k',
            'job_type': 'Full-time'
        }
    ]
    
    trends = analyzer.analyze_trends(sample_jobs)
    print("Analysis complete!")
    print(f"Found {trends['total_jobs']} jobs")
    print(f"Top skill: {trends['top_skills'][0][0] if trends['top_skills'] else 'N/A'}")