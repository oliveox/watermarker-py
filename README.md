# watermarker-goes-boom

### install steps
1. install python 3.10
2. pip install -r requirements.txt

### commands examples
python src/main.py --v 1 --i "tests/resources" --w "tests/resources/images/png/watermark.png" \
--p "done_" --o "tests/watermarked"

### Test files conventions
Naming: {width}x{height}-{media_file_source}-{instance}.{format}

Different devices may encode metadata differently. 
Marking the media file source helps for supporting / debugging different devices and formats.

- camera = digital camera (mirrorless / DSLR)
- iphone = iphone phone camera
- android = android phone camera
- action = action camera
- web = downloaded from the internet (unknown specific device source)
- not specified = probably web