import os
import time
from pathlib import Path
from pdf2image import convert_from_path
from playwright.sync_api import sync_playwright

def extract_with_lens(image_path):
    with sync_playwright() as p:
        # تشغيل المتصفح مع إعدادات اللغة الإنجليزية لتوحيد الأزرار
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(locale="en-US")
        page = context.new_page()
        
        # التوجه لمحرك بحث الصور
        page.goto("https://www.google.com/searchbyimage?sbisrc=cr_1&image_url=")
        
        # رفع الصورة
        try:
            with page.expect_file_chooser(timeout=60000) as fc_info:
                # الضغط على أيقونة الكاميرا/الرفع
                page.click('div[aria-label="Search by image"]', timeout=30000)
                # الضغط على زر اختيار الملف
                page.click('span:has-text("upload"), span:has-text("Select"), .fbtU7b', timeout=30000)
            
            file_chooser = fc_info.value
            file_chooser.set_files(image_path)
            
            # الانتظار حتى يتم تحميل الصفحة الجديدة بعد الرفع
            page.wait_for_load_state("networkidle", timeout=60000)
            
            # محاولة الضغط على زر "Text" بطرق مختلفة (بالنص أو بالأيقونة)
            # استعملنا كذا selector عشان لو واحد فشل التاني ينجح
            selectors = [
                'button:has-text("Text")', 
                'div[role="tab"] >> text="Text"',
                '.VfPpkd-vQ0Gbe >> text="Text"'
            ]
            
            success = False
            for selector in selectors:
                try:
                    page.wait_for_selector(selector, timeout=10000)
                    page.click(selector)
                    success = True
                    break
                except:
                    continue
            
            # انتظار ظهور النص المستخرج
            time.sleep(5) 
            
            # سحب كل النصوص اللي تظهر في الحاوية الأساسية للنتائج
            # Google Lens بيحط النصوص المستخرجة جوا عناصر معينة
            extracted_elements = page.query_selector_all('.UA9Z9e, .H99u6b, [role="main"]')
            all_text = [el.inner_text() for el in extracted_elements]
            
            browser.close()
            return "\n".join(all_text)
            
        except Exception as e:
            browser.close()
            raise e

def process_pdfs():
    input_dir = Path("./pdfs")
    output_dir = Path("./Extracted_Texts")
    output_dir.mkdir(exist_ok=True)

    for pdf_file in input_dir.glob("*.pdf"):
        print(f"Working on: {pdf_file.name}")
        # تحويل أول صفحة
        try:
            images = convert_from_path(pdf_file, first_page=1, last_page=1)
            for img in images:
                img_path = "temp_page.png"
                img.save(img_path, "PNG")
                
                try:
                    text = extract_with_lens(img_path)
                    if text and len(text.strip()) > 5:
                        with open(output_dir / f"{pdf_file.stem}.txt", "w", encoding="utf-8") as f:
                            f.write(text)
                        print(f"✅ Extracted: {pdf_file.name}")
                    else:
                        print(f"⚠️ No text found in: {pdf_file.name}")
                except Exception as e:
                    print(f"❌ Failed to extract {pdf_file.name}: {str(e)[:100]}")
                finally:
                    if os.path.exists(img_path):
                        os.remove(img_path)
        except Exception as e:
            print(f"❌ Could not convert PDF {pdf_file.name}: {e}")

if __name__ == "__main__":
    process_pdfs()
