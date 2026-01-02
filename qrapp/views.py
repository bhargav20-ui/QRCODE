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


import re
import qrcode
import base64
from io import BytesIO

from django.core.files.storage import FileSystemStorage
from django.shortcuts import render, redirect


# ---------------- ICON DETECTOR ----------------
def get_icon(name):
    name = name.lower()

    if name.endswith(".pdf"):
        return "📄"
    elif name.endswith(".doc") or name.endswith(".docx"):
        return "📝"
    elif name.endswith(".ppt") or name.endswith(".pptx"):
        return "📊"
    elif name.endswith(".jpg") or name.endswith(".jpeg") or name.endswith(".png"):
        return "🖼️"
    elif name.endswith(".zip") or name.endswith(".rar"):
        return "🗜️"
    else:
        return "🔗"


# ---------------- HOME VIEW ----------------
def home(request):
    qr_codes = []
    seen = set()

    if request.method == "POST":

        # ---------- HANDLE WEBSITE LINKS ----------
        text = request.POST.get("text", "").strip()

        urls = re.findall(r'https?://[^\s]+', text)
        domains = re.findall(r'\b[a-z0-9-]+(?:\.[a-z]{2,})+\b', text)

        for item in urls + domains:
            if not item.startswith("http"):
                final_url = "https://" + item
            else:
                final_url = item

            if final_url in seen:
                continue
            seen.add(final_url)

            qr = qrcode.make(final_url)
            buffer = BytesIO()
            qr.save(buffer, format="PNG")

            qr_codes.append({
                "name": final_url.replace("https://", "").replace("www.", ""),
                "url": final_url,
                "img": base64.b64encode(buffer.getvalue()).decode(),
                "icon": "🔗"
            })

        # ---------- HANDLE FILE UPLOADS ----------
        files = request.FILES.getlist("files")
        fs = FileSystemStorage()

        for file in files:
            filename = fs.save(file.name, file)
            file_url = request.build_absolute_uri(fs.url(filename))

            qr = qrcode.make(file_url)
            buffer = BytesIO()
            qr.save(buffer, format="PNG")

            qr_codes.append({
                "name": file.name,
                "url": file_url,
                "img": base64.b64encode(buffer.getvalue()).decode(),
                "icon": get_icon(file.name)
            })

        request.session["qr_codes"] = qr_codes
        return redirect("home")

    qr_codes = request.session.pop("qr_codes", None)
    return render(request, "qr.html", {"qr_codes": qr_codes})
