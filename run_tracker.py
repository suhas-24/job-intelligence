#!/usr/bin/env python3
"""
Job Intelligence Tracker
Uses: RemoteOK, Jobicy, Himalayas, JSearch
"""

import os
import requests
import json
import hashlib
from datetime import datetime, timezone
from collections import defaultdict

# Load .env
env_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(env_path):
    with open(env_path, 'r') as f:
        for line in f:
            line = line.strip()
            if line and '=' in line and not line.startswith('#'):
                key, val = line.split('=', 1)
                os.environ.setdefault(key, val)

# ============ FETCHERS ============

def fetch_remoteok():
    jobs = []
    try:
        resp = requests.get('https://remoteok.com/api', headers={'User-Agent': 'Mozilla/5.0'}, timeout=30)
        if resp.status_code == 200:
            data = resp.json()
            for item in data[1:]:
                key_str = '{}|{}|{}'.format(item.get('company', ''), item.get('position', ''), item.get('location', ''))
                jobs.append({
                    'event_type': 'hiring_opening',
                    'company_name': item.get('company', ''),
                    'role_or_title': item.get('position', ''),
                    'location': item.get('location', 'Remote'),
                    'source_platform': 'RemoteOK',
                    'source_name': 'RemoteOK',
                    'source_url': 'https://remoteok.com/{}'.format(item.get('id', '')),
                    'salary_or_range_if_known': item.get('salary', ''),
                    'tags': item.get('tags', []),
                    'source_date': item.get('date', ''),
                    'company_region': 'Global',
                    'event_id': hashlib.md5(key_str.encode()).hexdigest()
                })
    except Exception as e:
        print('  ⚠️ RemoteOK: {}'.format(e))
    return jobs

def fetch_jobicy():
    jobs = []
    try:
        resp = requests.get('https://jobicy.com/api/v2/remote-jobs', timeout=30)
        if resp.status_code == 200:
            data = resp.json()
            for item in data.get('jobs', []):
                key_str = '{}|{}|{}'.format(item.get('companyName', ''), item.get('jobTitle', ''), item.get('jobGeo', ''))
                jobs.append({
                    'event_type': 'hiring_opening',
                    'company_name': item.get('companyName', ''),
                    'role_or_title': item.get('jobTitle', ''),
                    'location': item.get('jobGeo', 'Remote'),
                    'source_platform': 'Jobicy',
                    'source_name': 'Jobicy',
                    'source_url': item.get('url', ''),
                    'tags': [item.get('jobType', '')],
                    'source_date': item.get('pubDate', ''),
                    'company_region': 'Global',
                    'event_id': hashlib.md5(key_str.encode()).hexdigest()
                })
    except Exception as e:
        print('  ⚠️ Jobicy: {}'.format(e))
    return jobs

def fetch_himalayas():
    jobs = []
    try:
        resp = requests.get('https://himalayas.app/jobs/api', timeout=30)
        if resp.status_code == 200:
            data = resp.json()
            for item in data:
                company_name = item.get('company', {})
                if isinstance(company_name, dict):
                    company_name = company_name.get('name', '')
                key_str = '{}|{}|{}'.format(company_name, item.get('title', ''), item.get('location', ''))
                jobs.append({
                    'event_type': 'hiring_opening',
                    'company_name': company_name,
                    'role_or_title': item.get('title', ''),
                    'location': item.get('location', 'Remote'),
                    'source_platform': 'Himalayas',
                    'source_name': 'Himalayas',
                    'source_url': item.get('url', ''),
                    'tags': [tag.get('name', '') for tag in item.get('tags', [])] if isinstance(item.get('tags'), list) else [],
                    'source_date': item.get('posted_at', ''),
                    'company_region': 'Global',
                    'event_id': hashlib.md5(key_str.encode()).hexdigest()
                })
    except Exception as e:
        print('  ⚠️ Himalayas: {}'.format(e))
    return jobs

def fetch_jsearch():
    jobs = []
    api_key = os.environ.get('JSEARCH_API_KEY', '')
    
    if not api_key:
        print('  ⏭️ JSearch skipped - no API key')
        return jobs
    
    queries = [
        ('site reliability engineer', 'india'),
        ('site reliability engineer', 'usa'),
        ('devops engineer', 'india'),
        ('devops engineer', 'usa'),
        ('cloud engineer', 'india'),
        ('ai engineer', 'india'),
        ('machine learning engineer', 'india'),
        ('data engineer', 'india'),
    ]
    
    for query, location in queries:
        try:
            url = 'https://jsearch.p.rapidapi.com/search'
            headers = {'X-RapidAPI-Key': api_key, 'X-RapidAPI-Host': 'jsearch.p.rapidapi.com'}
            params = {'query': query, 'location': location, 'num_pages': 1}
            
            resp = requests.get(url, headers=headers, params=params, timeout=30)
            
            if resp.status_code == 200:
                data = resp.json()
                for item in data.get('data', []):
                    key_str = '{}|{}|{}'.format(item.get('employer_name', ''), item.get('job_title', ''), item.get('job_location', ''))
                    jobs.append({
                        'event_type': 'hiring_opening',
                        'company_name': item.get('employer_name', ''),
                        'role_or_title': item.get('job_title', ''),
                        'location': item.get('job_location', ''),
                        'source_platform': 'JSearch',
                        'source_name': 'JSearch',
                        'source_url': item.get('job_apply_link', ''),
                        'tags': item.get('job_employment_type', '').split(',') if item.get('job_employment_type') else [],
                        'source_date': item.get('job_posted_at_datetime_utc', ''),
                        'company_region': 'India' if location == 'india' else 'US',
                        'event_id': hashlib.md5(key_str.encode()).hexdigest()
                    })
            elif resp.status_code == 403:
                print('  ⚠️ JSearch: API key not subscribed')
                break
        except Exception as e:
            print('  ⚠️ JSearch error: {}'.format(e))
            break
    
    return jobs

# ============ CLASSIFIERS ============

ROLE_KEYWORDS = {
    'ai_ml': ['ai', 'machine learning', 'ml', 'deep learning', 'nlp', 'llm', 'genai', 'data scientist', 'prompt'],
    'sre_infra': ['sre', 'site reliability', 'devops', 'cloud', 'infrastructure', 'platform', 'aws', 'gcp', 'kubernetes'],
    'software': ['engineer', 'developer', 'software', 'full stack', 'backend', 'frontend', 'mobile', 'web'],
    'product': ['product manager', 'program manager'],
    'data': ['data engineer', 'data analyst', 'bi', 'analytics']
}

def classify_role(title, tags):
    text = '{} {}'.format(title, ' '.join(tags) if isinstance(tags, list) else '').lower()
    for cat, keywords in ROLE_KEYWORDS.items():
        for kw in keywords:
            if kw in text:
                return cat
    return 'other'

def infer_region(location):
    loc = (location or '').lower()
    india = ['india', 'bengaluru', 'bangalore', 'hyderabad', 'pune', 'mumbai', 'chennai', 'delhi']
    us = ['usa', 'us', 'united states', 'san francisco', 'new york', 'seattle', 'austin']
    for x in india:
        if x in loc: return 'India'
    for x in us:
        if x in loc: return 'US'
    return 'Global'

def classify_seniority(title):
    title = title.lower()
    if any(x in title for x in ['intern', 'fresher']): return 'entry'
    if any(x in title for x in ['jr', 'junior']): return 'mid'
    if any(x in title for x in ['sr', 'senior', 'lead']): return 'senior'
    if any(x in title for x in ['staff', 'principal']): return 'staff'
    if any(x in title for x in ['director', 'head', 'vp', 'chief']): return 'director'
    return 'mid'

# ============ MAIN ============

def run():
    print('=' * 50)
    print('GLOBAL JOB INTELLIGENCE TRACKER')
    print('=' * 50)
    
    print('\n📥 Fetching from APIs...')
    jobs = []
    
    print('  → RemoteOK...')
    jobs.extend(fetch_remoteok())
    
    print('  → Jobicy...')
    jobs.extend(fetch_jobicy())
    
    print('  → Himalayas...')
    jobs.extend(fetch_himalayas())
    
    print('  → JSearch...')
    jobs.extend(fetch_jsearch())
    
    print('  Total: {} jobs'.format(len(jobs)))
    
    # Normalize
    print('\n🔧 Normalizing...')
    for job in jobs:
        job['role_category'] = classify_role(job.get('role_or_title', ''), job.get('tags', []))
        job['company_region'] = infer_region(job.get('location', ''))
        job['seniority_level'] = classify_seniority(job.get('role_or_title', ''))
        job['confidence_score'] = 0.8
        job['first_seen_at'] = datetime.now(timezone.utc).isoformat()
    
    # Dedupe
    seen = set()
    unique = []
    for job in jobs:
        key = (job.get('company_name'), job.get('role_or_title'), job.get('location'))
        if key not in seen and job.get('company_name'):
            seen.add(key)
            unique.append(job)
    
    print('  Unique: {} jobs'.format(len(unique)))
    
    # Metrics
    sources = 3 if any(j.get('source_platform') == 'JSearch' for j in unique) else 3
    metrics = {
        'global': {'total_events': len(unique), 'hiring_count': len(unique), 'layoffs_count': 0},
        'by_market': defaultdict(lambda: {'openings': 0}),
        'by_role': defaultdict(lambda: {'count': 0}),
        'sources_used': len(set(j.get('source_platform', '') for j in unique))
    }
    
    for job in unique:
        metrics['by_market'][job.get('company_region', 'Global')]['openings'] += 1
        metrics['by_role'][job.get('role_category', 'other')]['count'] += 1
    
    metrics['by_market'] = dict(metrics['by_market'])
    metrics['by_role'] = dict(metrics['by_role'])
    
    # Save
    output = {
        'run_timestamp': datetime.now(timezone.utc).isoformat(),
        'events': unique,
        'metrics': metrics
    }
    
    os.makedirs('data', exist_ok=True)
    with open('data/unified_output.json', 'w') as f:
        json.dump(output, f, indent=2)
    
    generate_report(output)
    
    print('\n✅ COMPLETE!')
    print('\n📊 Summary:')
    print('  Total: {} jobs'.format(metrics['global']['total_events']))
    print('  Sources: {}'.format(metrics['sources_used']))
    print('\nBy Market:')
    for m, d in sorted(metrics['by_market'].items(), key=lambda x: x[1]['openings'], reverse=True):
        print('    {}: {}'.format(m, d['openings']))
    print('\nBy Role:')
    for r, d in sorted(metrics['by_role'].items(), key=lambda x: x[1]['count'], reverse=True):
        print('    {}: {}'.format(r, d['count']))

def generate_report(data):
    metrics = data.get('metrics', {})
    events = data.get('events', [])
    
    md = '''# 🌍 Global Job Intelligence Report

**Generated:** {}

---

## 📊 Summary

| Metric | Count |
|--------|-------|
| Total Events | {:,} |
| Hiring | {:,} |
| Sources | {} |

---

## 🌍 By Market

| Market | Openings |
|--------|----------|
'''.format(data.get('run_timestamp', '')[:10], metrics['global']['total_events'], metrics['global']['hiring_count'], metrics['sources_used'])
    
    for m, d in sorted(metrics['by_market'].items(), key=lambda x: x[1]['openings'], reverse=True):
        md += '| {} | {} |\n'.format(m, d['openings'])
    
    md += '\n## 💼 By Role\n\n| Role | Count |\n|------|-------|\n'
    for r, d in sorted(metrics['by_role'].items(), key=lambda x: x[1]['count'], reverse=True):
        md += '| {} | {} |\n'.format(r, d['count'])
    
    # AI/SRE
    ai_sre = [e for e in events if e.get('role_category') in ['ai_ml', 'sre_infra']]
    if ai_sre:
        md += '\n## 🤖 AI/ML & SRE Roles\n\n| Company | Role | Location |\n|---------|------|----------|\n'
        for e in ai_sre[:10]:
            md += '| {} | {} | {} |\n'.format(e.get('company_name', ''), e.get('role_or_title', ''), e.get('location', 'Remote'))
    
    with open('data/daily_report.md', 'w') as f:
        f.write(md)

if __name__ == '__main__':
    run()
