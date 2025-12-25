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


def home(request):
    if request.method == "POST":
        text = request.POST.get("text", "").lower()

        qr_codes = []
        seen = set()

        # 1️⃣ Extract full URLs
        urls = re.findall(r'https?://[^\s]+', text)
        text = re.sub(r'https?://[^\s]+', ' ', text)

        # 2️⃣ Extract domains with extensions (.com, .edu, .in, etc.)
        domains = re.findall(
            r'\b[a-z0-9-]+(?:\.[a-z0-9-]+)+\b',
            text
        )

        for d in domains:
            text = text.replace(d, " ")

        # 3️⃣ Extract plain words (amazon, flipkart, gitam)
        words = re.findall(r'\b[a-z]{3,}\b', text)

        all_items = urls + domains + words

        for item in all_items:
            if item.startswith("http"):
                url = item
            elif "." in item:
                url = "https://" + item
            else:
                url = "https://" + item + ".com"

            if url in seen:
                continue
            seen.add(url)

            qr = qrcode.make(url)
            buffer = io.BytesIO()
            qr.save(buffer, format="PNG")

            img_str = base64.b64encode(buffer.getvalue()).decode()

            qr_codes.append({
                "url": url,
                "img": img_str
            })

        request.session["qr_codes"] = qr_codes
        return redirect("home")

    qr_codes = request.session.pop("qr_codes", None)
    return render(request, "qr.html", {"qr_codes": qr_codes})
