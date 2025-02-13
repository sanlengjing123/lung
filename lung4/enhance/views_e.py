from django.shortcuts import render
from django.http import JsonResponse
from PIL import Image, ImageOps
import os
import cv2
import numpy as np

def index(request):
    return render(request, "index.html")

def enhance_image(request):
    if request.method == 'POST':
        file = request.FILES.get('myfile')
        action = request.POST.get('action')
        if not file or not action:
            return JsonResponse({"status": 400, "message": "No file or action provided"})

        img = Image.open(file)
        save_path = './static/uploads/'
        if not os.path.exists(save_path):
            os.makedirs(save_path)
        original_path = os.path.join(save_path, file.name)
        img.save(original_path)

        if action == 'denoise':
            # Convert PIL image to OpenCV format
            img_cv = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
            # Apply denoising
            denoised_img_cv = cv2.fastNlMeansDenoisingColored(img_cv, None, 10, 10, 7, 21)
            # Convert back to PIL format
            enhanced_img = Image.fromarray(cv2.cvtColor(denoised_img_cv, cv2.COLOR_BGR2RGB))
        elif action == 'binarize':
            enhanced_img = img.convert('L').point(lambda x: 0 if x < 128 else 255, '1')
        elif action == 'grayscale':
            enhanced_img = ImageOps.grayscale(img)
        elif action == 'rotate':
            enhanced_img = img.rotate(90)
        else:
            return JsonResponse({"status": 400, "message": "Invalid action"})

        enhanced_path = os.path.join(save_path, f"enhanced_{file.name}")
        enhanced_img.save(enhanced_path)
        img_path = os.path.join('/static/uploads', f"enhanced_{file.name}")
        original_img_path = os.path.join('/static/uploads', file.name)

        return JsonResponse({"status": 200, "img_path": img_path, "img_original_path": original_img_path})

    return JsonResponse({"status": 400, "message": "Invalid request"})
