// التعديل هنا: استدعاء الجزء الصحيح من المكتبة
const { Lens } = require('chrome-lens-ocr'); 
const fs = require('fs');
const path = require('path');
const { fromPath } = require('pdf2pic');

async function processPdfs() {
    // ملاحظة: إذا استمر الخطأ، جرب إزالة ('ar') وتركها فارغة Lens() 
    // لأن المحرك يتعرف على اللغة تلقائياً في النسخ الجديدة
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

            // استدعاء الفحص
            const result = await lens.scanByFile(pageRes.path);
            
            // استخراج النص العربي
            const text = result.segments.map(s => s.text).join(' ');
            
            fs.writeFileSync(path.join(outputDir, file + '.txt'), text);
            console.log(`✅ Done: ${file}`);
            
            // تنظيف الملف المؤقت
            if (fs.existsSync(pageRes.path)) fs.unlinkSync(pageRes.path);
            
        } catch (e) {
            console.error(`❌ Error in ${file}:`, e.message);
        }
    }
}

processPdfs();
