// جرب هذه الطريقة لأن المكتبة قد تُصدر الكائن مباشرة
const LensModule = require('chrome-lens-ocr');
const Lens = LensModule.Lens || LensModule; // ضمان الوصول للكلاس الصحيح
const fs = require('fs');
const path = require('path');
const { fromPath } = require('pdf2pic');

async function processPdfs() {
    // إذا استمر الخطأ هنا، سنعرف أن المشكلة في طريقة الاستدعاء
    const lens = new Lens(); 
    const inputDir = './pdfs';
    const outputDir = './Extracted_Texts';

    if (!fs.existsSync(outputDir)) fs.mkdirSync(outputDir);
    if (!fs.existsSync("./temp")) fs.mkdirSync("./temp");

    const files = fs.readdirSync(inputDir).filter(f => f.endsWith('.pdf'));

    for (const file of files) {
        console.log(`Processing: ${file}`);
        
        const options = {
            density: 300,
            saveFilename: "temp_page_" + Date.now(),
            savePath: "./temp",
            format: "png",
            width: 2000,
            height: 2000
        };
        
        try {
            const storeAsImage = fromPath(path.join(inputDir, file), options);
            const pageRes = await storeAsImage(1); 

            // استخدام المحرك لسحب النص
            const result = await lens.scanByFile(pageRes.path);
            
            // دمج النصوص المستخرجة (بما فيها العربي)
            const text = result.segments.map(s => s.text).join(' ');
            
            fs.writeFileSync(path.join(outputDir, file.replace('.pdf', '.txt')), text);
            console.log(`✅ تم استخراج النص بنجاح: ${file}`);
            
            // حذف الصورة المؤقتة
            if (fs.existsSync(pageRes.path)) fs.unlinkSync(pageRes.path);
            
        } catch (e) {
            console.error(`❌ خطأ في الملف ${file}:`, e.message);
        }
    }
}

processPdfs();
