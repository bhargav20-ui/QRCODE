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
import qrcode
import base64
from io import BytesIO
from django.core.files.storage import FileSystemStorage
from django.shortcuts import render, redirect


# ================= ICON FOR FILES =================
def get_file_icon(name):
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
        return "📁"


# ================= SMART URL NORMALIZER =================
def normalize_url(text):
    text = text.lower().strip()

    if text.startswith(("http://", "https://")):
        return text

    # common cases
    if "." in text:
        return "https://" + text

    # pure names → assume .com
    return f"https://www.{text}.com"


def extract_domain(url):
    return url.replace("https://", "").replace("http://", "").split("/")[0]


# ================= MAIN VIEW =================
def home(request):
    qr_codes = []

    if request.method == "POST":

        # ========== WEBSITE LINKS ==========
        text = request.POST.get("text", "").strip()

        if text:
            inputs = text.replace(",", " ").split()

            for item in inputs:
                final_url = normalize_url(item)
                domain = extract_domain(final_url)

                qr = qrcode.make(final_url)
                buffer = BytesIO()
                qr.save(buffer, format="PNG")

                qr_codes.append({
                    "name": domain,
                    "url": final_url,
                    "img": base64.b64encode(buffer.getvalue()).decode(),
                    "icon": None,
                    "logo": f"https://www.google.com/s2/favicons?domain={domain}&sz=128"
                })

        # ========== FILE UPLOADS ==========
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
                "icon": get_file_icon(file.name),
                "logo": None
            })

        request.session["qr_codes"] = qr_codes
        return redirect("home")

    qr_codes = request.session.pop("qr_codes", [])
    return render(request, "qr.html", {"qr_codes": qr_codes})
