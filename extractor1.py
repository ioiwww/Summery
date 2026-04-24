import os
import time
from pathlib import Path
from pdf2image import convert_from_path
from playwright.sync_api import sync_playwright

def extract_with_lens(image_path):
    with sync_playwright() as p:
        # إعدادات المتصفح للتمويه
        browser = p.chromium.launch(headless=True)
        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        context = browser.new_context(
            user_agent=user_agent,
            viewport={'width': 1920, 'height': 1080},
            locale="en-US"
        )
        page = context.new_page()
        
        # التوجه لرابط الرفع المباشر
        page.goto("https://lens.google.com/search?p=1", wait_until="networkidle")
        
        try:
            # بدلاً من الانتظار ليصبح مرئياً، ننتظر وجوده في الكود فقط
            print("Locating hidden upload input...")
            upload_input = page.locator('input[type="file"]')
            upload_input.wait_for(state="attached", timeout=30000)
            
            # الرفع مباشرة بدون الضغط على أي زر
            print("Uploading image directly...")
            upload_input.set_input_files(image_path)
            
            # انتظار التحليل والانتقال لصفحة النتائج
            print("Waiting for analysis results...")
            page.wait_for_load_state("networkidle", timeout=60000)
            
            # محاولة الضغط على زر "Text"
            # استخدمنا "hidden=True" لأن جوجل أحياناً يخفي الأزرار خلف طبقات
            text_btn = page.get_by_role("button", name="Text")
            page.wait_for_selector('button:has-text("Text")', timeout=15000)
            text_btn.click()
            
            time.sleep(5) # وقت استقرار النص العربي
            
            # استخراج النص من الحاويات المعروفة في جوجل لنس
            # جربنا أكثر من Selector لضمان الإمساك بالنص
            text_selectors = ['div[jsname="V67S5c"]', '.UA9Z9e', '[role="main"]']
            extracted_text = ""
            
            for selector in text_selectors:
                element = page.locator(selector).first
                if element.is_visible():
                    extracted_text = element.inner_text()
                    if len(extracted_text.strip()) > 0:
                        break
            
            browser.close()
            return extracted_text if extracted_text else "No text could be extracted."
            
        except Exception as e:
            browser.close()
            return f"Error during extraction: {str(e)}"

def process_pdfs():
    input_dir = Path("./pdfs")
    output_dir = Path("./Extracted_Texts")
    output_dir.mkdir(exist_ok=True)

    pdf_files = list(input_dir.glob("*.pdf"))
    if not pdf_files:
        print("No PDF files found.")
        return

    for pdf_file in pdf_files:
        print(f"Processing: {pdf_file.name}")
        try:
            images = convert_from_path(pdf_file, first_page=1, last_page=1)
            for img in images:
                temp_img = f"temp_{pdf_file.stem}.png"
                img.save(temp_img)
                
                text = extract_with_lens(temp_img)
                
                with open(output_dir / f"{pdf_file.stem}.txt", "w", encoding="utf-8") as f:
                    f.write(text)
                
                if os.path.exists(temp_img):
                    os.remove(temp_img)
                print(f"✅ Finished: {pdf_file.name}")
                
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    process_pdfs()
