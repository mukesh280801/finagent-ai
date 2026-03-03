from PIL import Image, ImageDraw

width, height = 600, 800
image = Image.new("RGB", (width, height), "white")
draw = ImageDraw.Draw(image)

receipt_text = """
RELIANCE SMART
Chennai - TN

Date: 12/02/2026
Bill No: 45821

Milk           60.00
Bread          40.00
Rice          120.00

Total: ₹220.00
Payment: UPI
"""

draw.text((40, 40), receipt_text, fill="black")
image.save("sample_receipt.png")

print("Sample receipt image created successfully!")
