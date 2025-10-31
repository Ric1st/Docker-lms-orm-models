import csv
import io
from django.db import transaction
from django.core.files.uploadedfile import UploadedFile 

from .models import CourseContent, Course 

def import_content_from_csv(csv_file: UploadedFile, course: Course) -> tuple[int, str]:
    file_data = csv_file.read().decode('utf-8')
    csv_reader = csv.reader(io.StringIO(file_data))
    
    try:
        header = next(csv_reader)
        required_headers = ['name', 'description', 'video_url']
        if not all(h in header for h in required_headers):
            return 0, "Header CSV tidak lengkap atau tidak valid. Diperlukan: name, description, video_url."
            
        header_map = {name: index for index, name in enumerate(header)}
    
    except StopIteration:
        return 0, "File CSV kosong atau hanya berisi header yang kosong."
    except Exception as e:
        return 0, f"Gagal membaca header file CSV: {e}"

    success_count = 0
    error_details = []

    try:
        with transaction.atomic():
            for row_number, row in enumerate(csv_reader, start=2): 
                if not row:
                    continue 
                
                try:
                    if len(row) < len(required_headers):
                        raise ValueError("Baris memiliki jumlah kolom yang tidak memadai.")

                    data = {
                        'name': row[header_map['name']].strip(),
                        'description': row[header_map['description']].strip(),
                        'video_url': row[header_map['video_url']].strip() if 'video_url' in header_map else '',
                    }
                    
                    if not data['name']:
                        raise ValueError("Kolom 'name' tidak boleh kosong.")
                    
                    new_content = CourseContent(
                        course_id=course,  #
                        name=data['name'],
                        description=data['description'],
                        video_url=data['video_url'],
                    )
                    new_content.save()
                    success_count += 1
                    
                except Exception as e:
                    error_details.append(f"Baris {row_number}: Data tidak valid - {str(e)}. Data: {row}")
                    
            if error_details:
                raise Exception("\n".join(error_details))
            
            return success_count, ""

    except Exception as e:
        return 0, f"Import gagal total. {e}"