const LensModule = require('chrome-lens-ocr');
const fs = require('fs');
const path = require('path');
const { fromPath } = require('pdf2pic');

async function processPdfs() {
    // الحل هنا: الوصول لخاصية .Lens أو .default.Lens حسب طريقة التصدير
    const LensClass = LensModule.Lens || (LensModule.default && LensModule.default.Lens);
    
    if (!LensClass) {
        throw new Error("لم نتمكن من العثور على الكلاس Lens داخل المكتبة. تأكد من تثبيت النسخة الصحيحة.");
    }

    const lens = new LensClass(); 
    const inputDir = './pdfs';
    const outputDir = './Extracted_Texts';

    if (!fs.existsSync(outputDir)) fs.mkdirSync(outputDir, { recursive: true });
    if (!fs.existsSync("./temp")) fs.mkdirSync("./temp", { recursive: true });

    const files = fs.readdirSync(inputDir).filter(f => f.toLowerCase().endsWith('.pdf'));

    for (const file of files) {
        console.log(`جارٍ معالجة: ${file}`);
        
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
            const pageRes = await storeAsImage(1); // استخراج الصفحة الأولى

            // سحب النص باستخدام محرك Google Lens
            const result = await lens.scanByFile(pageRes.path);
            
            // تجميع النص (يدعم العربي تلقائياً)
            const text = result.segments.map(s => s.text).join(' ');
            
            const outputFileName = file.replace('.pdf', '.txt');
            fs.writeFileSync(path.join(outputDir, outputFileName), text);
            console.log(`✅ تم استخراج النص بنجاح من: ${file}`);
            
            // تنظيف الملفات المؤقتة
            if (fs.existsSync(pageRes.path)) fs.unlinkSync(pageRes.path);
            
        } catch (e) {
            console.error(`❌ فشل في معالجة ${file}:`, e.message);
        }
    }
}

processPdfs().catch(err => {
    console.error("خطأ فادح:", err);
    process.exit(1);
});
