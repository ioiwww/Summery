import os
import time
from pathlib import Path
from pdf2image import convert_from_path
from playwright.sync_api import sync_playwright

def extract_with_lens(image_path):
    with sync_playwright() as p:
        # إعدادات المتصفح للتمويه كجهاز حقيقي
        browser = p.chromium.launch(headless=True)
        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        context = browser.new_context(
            user_agent=user_agent,
            viewport={'width': 1920, 'height': 1080},
            locale="en-US"
        )
        page = context.new_page()
        
        # التوجه لرابط الرفع المباشر في جوجل لنس
        page.goto("https://lens.google.com/search?p=1")
        
        try:
            # انتظار ظهور عنصر الرفع
            page.wait_for_selector('input[type="file"]', timeout=30000)
            
            # رفع الصورة
            with page.expect_file_chooser() as fc_info:
                # محاكاة الضغط على زر الرفع
                page.click('div[role="button"]', force=True)
            
            file_chooser = fc_info.value
            file_chooser.set_files(image_path)
            
            # انتظار معالجة الصورة وظهور النتائج
            print("Waiting for Google to analyze the image...")
            page.wait_for_load_state("networkidle", timeout=60000)
            
            # محاولة الضغط على زر "Text"
            # جوجل أحياناً يغير الـ selectors، لذا نجرب النص والأيقونة
            text_btn = page.get_by_role("button", name="Text")
            if text_btn.is_visible():
                text_btn.click()
            else:
                # محاولة الضغط عبر الكلاس إذا فشل الاسم
                page.click('.VfPpkd-vQ0Gbe', timeout=10000)
            
            time.sleep(4) # وقت إضافي لاستقرار النص العربي
            
            # استخراج النص من الحاوية المخصصة
            # هذا الـ selector يستهدف منطقة النصوص في واجهة لنس الجديدة
            text_content = page.locator('div[jsname="V67S5c"], .UA9Z9e').inner_text()
            
            browser.close()
            return text_content
        except Exception as e:
            # في حال الفشل، نأخذ لقطة شاشة للخطأ (اختياري للتدقيق)
            # page.screenshot(path="error.png") 
            browser.close()
            return f"Error during extraction: {str(e)}"

def process_pdfs():
    input_dir = Path("./pdfs")
    output_dir = Path("./Extracted_Texts")
    output_dir.mkdir(exist_ok=True)

    # البحث عن ملفات PDF (بما فيها ملف إدارة الموارد البشرية)
    pdf_files = list(input_dir.glob("*.pdf"))
    if not pdf_files:
        print("No PDF files found in ./pdfs folder.")
        return

    for pdf_file in pdf_files:
        print(f"Working on: {pdf_file.name}")
        
        try:
            # تحويل الصفحة الأولى فقط للسرعة، يمكنك زيادة last_page إذا أردت
            images = convert_from_path(pdf_file, first_page=1, last_page=1)
            for img in images:
                temp_img = f"temp_{pdf_file.stem}.png"
                img.save(temp_img)
                
                text = extract_with_lens(temp_img)
                
                # حفظ النتيجة في ملف نصي بنفس اسم الـ PDF
                with open(output_dir / f"{pdf_file.stem}.txt", "w", encoding="utf-8") as f:
                    f.write(text)
                
                if os.path.exists(temp_img):
                    os.remove(temp_img)
                print(f"✅ Finished: {pdf_file.name}")
                
        except Exception as e:
            print(f"❌ Error processing {pdf_file.name}: {e}")

if __name__ == "__main__":
    process_pdfs()
