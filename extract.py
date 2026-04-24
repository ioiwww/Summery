import os
import easyocr
from pathlib import Path
from pdf2image import convert_from_path

def process_pdfs():
    input_dir = Path("./pdfs")
    output_dir = Path("./Extracted_Texts")
    output_dir.mkdir(exist_ok=True)

    # تحميل نموذج اللغة العربية والإنجليزية (بيتحمل مرة وحدة بس)
    print("Loading OCR Models (Arabic/English)...")
    reader = easyocr.Reader(['ar', 'en']) 

    for pdf_file in input_dir.glob("*.pdf"):
        print(f"Working on: {pdf_file.name}")
        
        try:
            # تحويل صفحات الـ PDF لصور
            images = convert_from_path(pdf_file)
            full_text = []

            for i, img in enumerate(images):
                img_path = f"page_{i}.png"
                img.save(img_path)
                
                # استخراج النص العربي
                # paragraph=True بيساعد على تجميع الجمل بشكل منطقي
                result = reader.readtext(img_path, detail=0, paragraph=True)
                full_text.append(f"--- Page {i+1} ---\n" + "\n".join(result))
                
                if os.path.exists(img_path):
                    os.remove(img_path)

            # حفظ النتيجة
            output_file = output_dir / f"{pdf_file.stem}.txt"
            with open(output_file, "w", encoding="utf-8") as f:
                f.write("\n\n".join(full_text))
            
            print(f"✅ Extracted: {pdf_file.name}")

        except Exception as e:
            print(f"❌ Failed {pdf_file.name}: {e}")

if __name__ == "__main__":
    process_pdfs()
