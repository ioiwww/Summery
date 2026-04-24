import os
from py_google_lens import GoogleLens
from pdf2image import convert_from_path
from pathlib import Path

def process_pdfs():
    input_dir = Path("./pdfs")
    output_dir = Path("./Extracted_Texts")
    temp_dir = Path("./temp")

    # إنشاء المجلدات
    output_dir.mkdir(exist_ok=True)
    temp_dir.mkdir(exist_ok=True)

    lens = GoogleLens()

    for pdf_file in input_dir.glob("*.pdf"):
        print(f"Processing: {pdf_file.name}")
        
        # تحويل الصفحة الأولى فقط من الـ PDF لصورة
        images = convert_from_path(pdf_file, first_page=1, last_page=1)
        
        for i, image in enumerate(images):
            temp_image_path = temp_dir / f"{pdf_file.stem}_page.png"
            image.save(temp_image_path, "PNG")

            try:
                # استخراج النص باستخدام Google Lens
                result = lens.fetch_image_data(str(temp_image_path))
                
                # استرجاع النص فقط من النتيجة
                extracted_text = result.text
                
                output_file = output_dir / f"{pdf_file.stem}.txt"
                with open(output_file, "w", encoding="utf-8") as f:
                    f.write(extracted_text)
                
                print(f"✅ Success: {pdf_file.name}")
            except Exception as e:
                print(f"❌ Error in {pdf_file.name}: {e}")
            finally:
                if temp_image_path.exists():
                    temp_image_path.unlink()

if __name__ == "__main__":
    process_pdfs()
