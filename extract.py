import os
import time
from pathlib import Path
from pdf2image import convert_from_path
from playwright.sync_api import sync_playwright

def extract_with_lens(image_path):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        # التوجه لموقع Google Lens (عبر بحث الصور)
        page.goto("https://www.google.com/searchbyimage?sbisrc=cr_1&image_url=")
        
        # رفع الصورة
        with page.expect_file_chooser() as fc_info:
            page.click('div[aria-label="Search by image"]')
            page.click('span:has-text("upload a file")')
            
        file_chooser = fc_info.value
        file_chooser.set_files(image_path)
        
        # الانتظار لمعالجة الصورة والضغط على زر "Text"
        page.wait_for_selector('button:has-text("Text")')
        page.click('button:has-text("Text")')
        
        # الضغط على "Select all text"
        page.wait_for_selector('button:has-text("Select all text")')
        page.click('button:has-text("Select all text")')
        
        # سحب النص من العناصر التي تظهر
        time.sleep(2) # انتظار بسيط لضمان ظهور النص
        text = page.inner_text('div[role="main"]') # هذا يسحب النص الظاهر
        
        browser.close()
        return text

def process_pdfs():
    input_dir = Path("./pdfs")
    output_dir = Path("./Extracted_Texts")
    output_dir.mkdir(exist_ok=True)

    for pdf_file in input_dir.glob("*.pdf"):
        print(f"Working on: {pdf_file.name}")
        images = convert_from_path(pdf_file, first_page=1, last_page=1)
        
        for img in images:
            img_path = "temp_page.png"
            img.save(img_path, "PNG")
            
            try:
                text = extract_with_lens(img_path)
                with open(output_dir / f"{pdf_file.stem}.txt", "w", encoding="utf-8") as f:
                    f.write(text)
                print(f"✅ Extracted: {pdf_file.name}")
            except Exception as e:
                print(f"❌ Failed: {e}")
            finally:
                if os.path.exists(img_path):
                    os.remove(img_path)

if __name__ == "__main__":
    process_pdfs()
