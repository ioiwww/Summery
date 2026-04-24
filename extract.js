const { Lens } = require('chrome-lens-ocr');
const fs = require('fs');
const path = require('path');
const { fromPath } = require('pdf2pic'); // لتحويل الـ PDF لصور

async function processPdfs() {
    const lens = new Lens('ar'); // تحديد اللغة العربية
    const inputDir = './pdfs';
    const outputDir = './Extracted_Texts';

    if (!fs.existsSync(outputDir)) fs.mkdirSync(outputDir);

    const files = fs.readdirSync(inputDir).filter(f => f.endsWith('.pdf'));

    for (const file of files) {
        console.log(`Processing: ${file}`);
        const options = {
            density: 300,
            saveFilename: "temp_page",
            savePath: "./temp",
            format: "png",
            width: 2000,
            height: 2000
        };
        
        if (!fs.existsSync("./temp")) fs.mkdirSync("./temp");
        
        const storeAsImage = fromPath(path.join(inputDir, file), options);
        // تحويل أول صفحة (أو عدل الحلقة لتشمل كل الصفحات)
        const pageRes = await storeAsImage(1); 

        try {
            const result = await lens.scanByFile(pageRes.path);
            const text = result.segments.map(s => s.text).join(' ');
            
            fs.writeFileSync(path.join(outputDir, file + '.txt'), text);
            console.log(`✅ تم استخراج النص من ${file}`);
        } catch (e) {
            console.error(`❌ خطأ في ${file}:`, e.message);
        }
    }
}

processPdfs();
