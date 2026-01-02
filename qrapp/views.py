# WEBSITES = {
#     "whatsapp": "https://www.whatsapp.com",
#     "google": "https://www.google.com",
#     "flipkart": "https://www.flipkart.com",
#     "amazon": "https://www.amazon.in",
#     "youtube": "https://www.youtube.com",
#     "instagram": "https://www.instagram.com",
#     "facebook": "https://www.facebook.com",
#     "twitter": "https://www.twitter.com",
#     "x": "https://www.x.com",
#     "linkedin": "https://www.linkedin.com",
#     "github": "https://www.github.com",
#     "stackoverflow": "https://www.stackoverflow.com",
#     "reddit": "https://www.reddit.com",
#     "wikipedia": "https://www.wikipedia.org",
#     "netflix": "https://www.netflix.com",
#     "spotify": "https://www.spotify.com",
#     "pinterest": "https://www.pinterest.com",
#     "tumblr": "https://www.tumblr.com",
#     "quora": "https://www.quora.com",
#     "yahoo": "https://www.yahoo.com",
#     "bing": "https://www.bing.com",
#     "ebay": "https://www.ebay.com",
#     "paypal": "https://www.paypal.com",
# }


from django.shortcuts import render, redirect
import qrcode
import io
import base64
import re
from django.core.files.storage import FileSystemStorage
from django.conf import settings




def home(request):
    qr_codes = []

    if request.method == "POST":

        # ---------- FILE UPLOAD ----------
        uploaded_file = request.FILES.get('file')

        if uploaded_file:
            fs = FileSystemStorage()
            filename = fs.save(uploaded_file.name, uploaded_file)
            file_url = request.build_absolute_uri(settings.MEDIA_URL + filename)

            qr = qrcode.make(file_url)
            buffer = io.BytesIO()
            qr.save(buffer, format="PNG")

            img_str = base64.b64encode(buffer.getvalue()).decode()

            qr_codes.append({
                "url": file_url,
                "img": img_str
            })

        # ---------- URL TEXT ----------
        text = request.POST.get("text", "").lower()
        if text:
            url = text if text.startswith("http") else "https://" + text

            qr = qrcode.make(url)
            buffer = io.BytesIO()
            qr.save(buffer, format="PNG")

            img_str = base64.b64encode(buffer.getvalue()).decode()

            qr_codes.append({
                "url": url,
                "img": img_str
            })

    return render(request, "qr.html", {"qr_codes": qr_codes})
