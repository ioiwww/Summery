require 'google-lens-ocr'
require 'fileutils'

# إعداد المجلدات
input_dir = './pdfs'
output_dir = './Extracted_Texts'
temp_dir = './temp'

FileUtils.mkdir_p(output_dir)
FileUtils.mkdir_p(temp_dir)

# البحث عن ملفات PDF
pdf_files = Dir.glob("#{input_dir}/*.pdf")

pdf_files.each do |pdf_path|
  puts "Processing: #{File.basename(pdf_path)}..."
  
  # اسم ملف الصورة المؤقتة
  temp_image = "#{temp_dir}/page.png"
  
  # تحويل الصفحة الأولى من PDF إلى صورة باستخدام pdftoppm (موجود في poppler-utils)
  system("pdftoppm -f 1 -l 1 -png -singlefile '#{pdf_path}' '#{temp_dir}/page'")
  
  begin
    # استخدام Google Lens لاستخراج النص
    # الأداة تتعرف على اللغة العربية تلقائياً
    lens = GoogleLensOCR.new
    result = lens.extract_text(temp_image)
    
    # حفظ النص المستخرج
    output_file = File.join(output_dir, File.basename(pdf_path, ".pdf") + ".txt")
    File.write(output_file, result)
    
    puts "✅ Successfully extracted: #{pdf_path}"
  rescue => e
    puts "❌ Error processing #{pdf_path}: #{e.message}"
  ensure
    # تنظيف الصورة المؤقتة
    FileUtils.rm(temp_image) if File.exist?(temp_image)
  end
end
