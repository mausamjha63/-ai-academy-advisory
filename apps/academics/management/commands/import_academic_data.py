import os
import pandas as pd
from django.core.management.base import BaseCommand
from django.conf import settings
from academics.models import Course, CourseOffering, Prerequisite
import math

class Command(BaseCommand):
    help = 'Imports academic data from authoritative Excel sheets into the database idempotently'

    def handle(self, *args, **kwargs):
        data_dir = os.path.join(settings.BASE_DIR, 'source_data', 'Excel')
        semester_file = os.path.join(data_dir, 'Semester_Spread_Structures_Sept_2026.xlsx')
        minor_file = os.path.join(data_dir, 'Minor_Courses_for_BTech_Students.xlsx')
        
        created_courses = 0
        updated_courses = 0
        created_offerings = 0
        created_prereqs = 0
        
        def process_course(raw_code, raw_title, credits_val, prereq_val, sem_val, sheet_name, filename, row_index):
            nonlocal created_courses, updated_courses, created_offerings, created_prereqs
            if pd.isna(raw_code) or str(raw_code).strip().lower() in ['nan', 'none', 'tbd', "don't know", '']:
                return
            if pd.isna(raw_title) or str(raw_title).strip().lower() in ['nan', 'none', 'tbd', '']:
                return
                
            code = str(raw_code).strip().upper()
            title = str(raw_title).strip()
            
            # Safe Course Splitting
            codes_to_process = [code]
            titles_to_process = [title]
            
            for delimiter in ['/', '\n']:
                if delimiter in code and delimiter in title:
                    code_parts = [p.strip() for p in code.split(delimiter)]
                    title_parts = [p.strip() for p in title.split(delimiter)]
                    # Only split if they match in length and are > 1
                    if len(code_parts) == len(title_parts) and len(code_parts) > 1:
                        # Clean up any potential empty strings
                        if all(len(p) > 0 for p in code_parts) and all(len(p) > 0 for p in title_parts):
                            codes_to_process = code_parts
                            titles_to_process = title_parts
                            break
            
            c_val = None
            if not pd.isna(credits_val):
                c_str = str(credits_val).strip()
                if c_str.lower() not in ['nan', 'nil', 'tba', 'tbd', '-', '']:
                    try:
                        c_val = float(c_str)
                    except ValueError:
                        pass
                        
            p_val = None
            if not pd.isna(prereq_val):
                p_str = str(prereq_val).strip()
                if p_str.lower() not in ['nan', 'nil', 'tba', 'tbd', '-', 'none', '']:
                    p_val = p_str
                    
            metadata = {
                'source_file': filename,
                'sheet_name': sheet_name,
                'row_index': row_index
            }
            
            for i in range(len(codes_to_process)):
                indiv_code = codes_to_process[i]
                indiv_title = titles_to_process[i]
                
                # Cleanup if they STILL have invalid url characters but didn't zip correctly
                if '/' in indiv_code:
                    indiv_code = indiv_code.replace('/', '-')
                if '\n' in indiv_code:
                    indiv_code = indiv_code.replace('\n', ' ')
                    
                course, created = Course.objects.update_or_create(
                    course_code=indiv_code,
                    defaults={
                        'title': indiv_title,
                        'credits': c_val,
                        'bucket': 'Core/Minor',
                        'source_metadata': metadata
                    }
                )
                if created:
                    created_courses += 1
                else:
                    updated_courses += 1
                    
                if p_val:
                    pre, p_created = Prerequisite.objects.get_or_create(
                        course=course,
                        prerequisite_condition=p_val,
                        defaults={'uncertainty_source_metadata': metadata}
                    )
                    if p_created:
                        created_prereqs += 1
                        
                sem_name = sem_val if sem_val else "Any"
                off, o_created = CourseOffering.objects.get_or_create(
                    course=course,
                    semester=str(sem_name),
                    batch_context=sheet_name,
                    defaults={
                        'availability_status': 'AVAILABLE',
                        'source_reference': str(metadata)
                    }
                )
                if o_created:
                    created_offerings += 1

        # Process Minor Courses (simpler tabular format)
        if os.path.exists(minor_file):
            xls_minor = pd.ExcelFile(minor_file)
            for sheet in xls_minor.sheet_names:
                df = pd.read_excel(xls_minor, sheet_name=sheet)
                for index, row in df.iterrows():
                    col_map = {str(c).strip().lower(): c for c in df.columns}
                    code_col = next((c for k, c in col_map.items() if 'code' in k), None)
                    title_col = next((c for k, c in col_map.items() if 'title' in k), None)
                    cred_col = next((c for k, c in col_map.items() if 'credit' in k), None)
                    pre_col = next((c for k, c in col_map.items() if 'pre-rq' in k or 'prereq' in k), None)
                    sem_col = next((c for k, c in col_map.items() if 'sem' in k), None)
                    
                    if code_col and title_col:
                        process_course(
                            row.get(code_col), row.get(title_col),
                            row.get(cred_col) if cred_col else None,
                            row.get(pre_col) if pre_col else None,
                            row.get(sem_col) if sem_col else None,
                            sheet, 'Minor_Courses_for_BTech_Students.xlsx', index
                        )
                        
        # Process Semester Spread (complex wide grid)
        if os.path.exists(semester_file):
            xls_sem = pd.ExcelFile(semester_file)
            for sheet in xls_sem.sheet_names:
                df = pd.read_excel(xls_sem, sheet_name=sheet)
                # Find the row that defines the headers (Course Code, Course, Pre-Req, C)
                # usually row 0
                for index, row in df.iterrows():
                    # We will scan the row for "Course Code" and use offsets for the rest
                    for col_idx, val in enumerate(row):
                        if str(val).strip().lower() == "course code":
                            # Next columns should be: Course, Pre-Req, L, T, P, C
                            try:
                                c_code = row.iloc[col_idx]
                                c_title = row.iloc[col_idx + 1]
                                c_prereq = row.iloc[col_idx + 2]
                                c_cred = row.iloc[col_idx + 6] # C is usually 6 cols away
                                sem_name = df.columns[col_idx - 1] if col_idx > 0 else "Unknown" # S1, S2 etc
                                
                                # Since this row is header, we want the data from the NEXT rows
                                for data_idx in range(index + 1, len(df)):
                                    d_row = df.iloc[data_idx]
                                    d_code = d_row.iloc[col_idx]
                                    if pd.isna(d_code):
                                        continue
                                    d_title = d_row.iloc[col_idx + 1]
                                    d_prereq = d_row.iloc[col_idx + 2] if (col_idx + 2) < len(d_row) else None
                                    d_cred = d_row.iloc[col_idx + 6] if (col_idx + 6) < len(d_row) else None
                                    
                                    process_course(d_code, d_title, d_cred, d_prereq, sem_name, sheet, 'Semester_Spread_Structures_Sept_2026.xlsx', data_idx)
                            except Exception as e:
                                pass

        self.stdout.write(self.style.SUCCESS(f"Import complete. Courses: {created_courses} created, {updated_courses} updated. Offerings: {created_offerings}. Prerequisites: {created_prereqs}."))
