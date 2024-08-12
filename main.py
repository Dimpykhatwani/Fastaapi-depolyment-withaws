from fastapi import FastAPI
from pydantic import BaseModel
from flask_cors import CORS
import random
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image, ImageDraw, ImageFont
import random
import textwrap
from fastapi import FastAPI
from pydantic import BaseModel
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
import random
import os
import boto3
from botocore.exceptions import NoCredentialsError

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins. Modify this as needed for production.
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods. Modify this as needed.
    allow_headers=["*"],  # Allows all headers. Modify this as needed.
)


class UserType(BaseModel):
    user_type: int

class Text(BaseModel):
    text: str

# AWS S3 configuration
AWS_ACCESS_KEY_ID = ""
AWS_SECRET_ACCESS_KEY = ""
AWS_REGION = ""
S3_BUCKET = ""

s3_client = boto3.client(
    's3',
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_REGION
)


def add_text_to_image(image_path, text, output_path, position=(10, 10), max_font_size=100, shadow_offset=(2, 2), transparency=255, font_path=None):
    # Open an image file
    with Image.open(image_path) as image:
        # Make the image editable
        image = image.convert("RGBA")
        txt = Image.new('RGBA', image.size, (255, 255, 255, 0))

        # Get an ImageDraw object
        draw = ImageDraw.Draw(txt)

        # Choose random colors for text and shadow
        font_color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255), transparency)
        shadow_color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255), transparency)

        # Determine the maximum width for the text
        image_width = image.size[0] - 2 * position[0]  # Account for padding

        # Set initial font size and load the font
        font_size = max_font_size
        font = ImageFont.truetype(font_path or "arial.ttf", font_size)

        # Function to get text width
        def get_text_width(text, font):
            bbox = draw.textbbox((0, 0), text, font=font)
            return bbox[2] - bbox[0]

        # Wrap text and adjust font size if needed
        def wrap_text(text, font, max_width):
            wrapped_lines = []
            words = text.split()
            line = ""
            for word in words:
                # Append the word to the line and check if it fits
                test_line = f"{line} {word}".strip()
                if get_text_width(test_line, font) <= max_width:
                    line = test_line
                else:
                    if line:
                        wrapped_lines.append(line)
                    line = word
            if line:
                wrapped_lines.append(line)
            return wrapped_lines

        lines = wrap_text(text, font, image_width)
        while get_text_width('\n'.join(lines), font) > image_width and font_size > 1:
            font_size -= 1
            font = ImageFont.truetype(font_path or "arial.ttf", font_size)
            lines = wrap_text(text, font, image_width)

        # Draw text with shadow
        y_text = position[1]
        for line in lines:
            shadow_pos = (position[0] + shadow_offset[0], y_text + shadow_offset[1])
            draw.text(shadow_pos, line, font=font, fill=shadow_color)
            draw.text((position[0], y_text), line, font=font, fill=font_color)
            y_text += draw.textbbox((0, 0), line, font=font)[3] - draw.textbbox((0, 0), line, font=font)[1]  # Move to the next line

        # Combine original image with text
        combined = Image.alpha_composite(image, txt)
        
        # Save the edited image
        combined.save(output_path, "PNG")

def upload_to_s3(file_path, filename):
    try:
        s3_client.upload_file(file_path, S3_BUCKET, filename)
        s3_url = f"https://{S3_BUCKET}.s3.{AWS_REGION}.amazonaws.com/{filename}"
        return s3_url
    except FileNotFoundError:
        return {"error": "The file was not found"}
    except NoCredentialsError:
        return {"error": "Credentials not available"}

def generate_post_content(user_type):
    if user_type == 1:  # Vendor
        captions = [
            "Fresh ingredients delivered daily! 🥦🍅 Get the best produce for your restaurant.",
            "Upgrade your kitchen with our top-notch appliances. Check out our latest offers! 🍳🍽️",
            "Discover a variety of spices and herbs to elevate your dishes. Shop now! 🌶️🌿",
            "Quality meats and seafood available for your culinary creations. Order today! 🥩🍤",
            "Get the freshest dairy products at unbeatable prices. Perfect for all your recipes! 🥛🧀",
            "Organic vegetables straight from the farm to your kitchen. Freshness guaranteed! 🥕🥬",
            "Boost your restaurant's flavor profile with our exotic spices and blends. 🌶️🧄",
            "High-quality grains and legumes for nutritious meals. Stock up now! 🌾🌰",
            "Cutting-edge kitchen gadgets and tools for the modern chef. Explore our range! 🔪🍲",
            "Special discounts on bulk orders. Save more on your restaurant supplies! 📦💰",
            "Fresh seafood, caught daily, delivered to your doorstep. Taste the ocean's best! 🦐🐟",
            "Gourmet oils and vinegars to enhance your culinary creations. Try them today! 🥗🫒",
            "Artisanal breads and pastries for a delightful dining experience. Freshly baked! 🥖🥐",
            "Premium coffee beans and tea leaves for the perfect brew. Energize your day! ☕🍵",
            "Essential kitchen appliances to streamline your cooking process. Shop now! 🍲⚙️",
            "Exquisite cheeses from around the world. Perfect for any dish or platter! 🧀🌎",
            "Healthy and delicious snacks for your restaurant's menu. Add variety to your offerings! 🍿🍪",
            "Wide selection of sauces and marinades to complement your dishes. Flavor explosion! 🥫🔥",
            "Eco-friendly packaging solutions for a sustainable kitchen. Go green! 🌱♻️",
            "Catering supplies for all your event needs. Quality products at great prices! 🍴🎉",
            "Exotic fruits and vegetables to add a unique twist to your menu. Taste the difference! 🍍🥑",
            "Specialty flours for all your baking needs. Perfect texture and taste! 🍞🧁",
            "Handcrafted chocolates and confections to sweeten your customers' day. 🍫🍬",
            "Variety of pasta and noodles for diverse culinary creations. From Italy to Asia! 🍝🍜",
            "Fresh herbs and microgreens to garnish your dishes. A touch of freshness! 🌿🌱",
            "Exclusive wines and spirits to complement your menu. Raise a glass! 🍷🍸",
            "Top-quality seafood and shellfish for gourmet dining experiences. Fresh and delicious! 🦀🦞",
            "Variety of nuts and seeds for healthy snacking and cooking. Nutrient-packed! 🌰🥜",
            "Artisanal condiments and spreads to enhance any meal. Discover new flavors! 🍯🥜",
            "Gourmet desserts and frozen treats for a sweet finish. Delight your guests! 🍨🍧",
            "Selection of organic and free-range meats. Ethical and delicious! 🐓🥩",
            "Beverage syrups and mixers for crafting perfect drinks. Cheers to good times! 🍹🍸",
            "Wide range of dairy alternatives for lactose-intolerant customers. Inclusive dining! 🥛🌿",
            "International spices and seasonings for global cuisine. Travel the world through flavor! 🌍🍛",
            "Innovative kitchen equipment to boost efficiency and creativity. Elevate your cooking! 🍽️⚙️",
            "Bulk supply of grains and cereals for sustainable, cost-effective cooking. Stock up! 🌾🥣",
            "Specialty seafood items, including caviar and smoked fish. Luxury dining! 🐟🥂",
            "Premium chocolate and baking supplies for dessert perfection. Satisfy your sweet tooth! 🍫🍰",
            "Local and imported cheeses for gourmet cheese boards. Pair with fine wine! 🧀🍷",
            "Gourmet oils, vinegars, and condiments for fine dining. Enhance every dish! 🥂🥗",
            "Exclusive cookware and bakeware for professional results. Cook like a pro! 🍳🧁",
            "High-quality charcuterie and deli products for savory platters. Deliciously cured! 🥓🍖",
        ] * 20  # Multiply the list to simulate more entries
        
        image_texts = [
             "Fresh Produce Sale",
            "Kitchen Appliances Discount",
            "Exclusive Spices and Herbs",
            "Quality Meats and Seafood",
            "Fresh Dairy Products",
            "Organic Vegetables",
            "Exotic Spices and Blends",
            "High-Quality Grains",
            "Kitchen Gadgets and Tools",
            "Bulk Order Discounts",
            "Fresh Seafood Delivery",
            "Gourmet Oils and Vinegars",
            "Artisanal Breads and Pastries",
            "Premium Coffee and Tea",
            "Essential Kitchen Appliances",
            "Exquisite Cheeses",
            "Healthy and Delicious Snacks",
            "Wide Selection of Sauces",
            "Eco-Friendly Packaging",
            "Catering Supplies",
            "Exotic Fruits and Vegetables",
            "Specialty Flours",
            "Handcrafted Chocolates",
            "Variety of Pasta and Noodles",
            "Fresh Herbs and Microgreens",
            "Exclusive Wines and Spirits",
            "Top-Quality Seafood",
            "Variety of Nuts and Seeds",
            "Artisanal Condiments",
            "Gourmet Desserts and Treats",
            "Organic and Free-Range Meats",
            "Beverage Syrups and Mixers",
            "Dairy Alternatives",
            "International Spices",
            "Innovative Kitchen Equipment",
            "Bulk Grains and Cereals",
            "Specialty Seafood Items",
            "Premium Chocolate Supplies",
            "Local and Imported Cheeses",
            "Fine Dining Condiments",
            "Exclusive Cookware and Bakeware",
            "High-Quality Charcuterie",
        ] * 20  # Multiply the list to simulate more entries

    elif user_type == 2:  # Chef
        captions = [
              "Excited to explore new culinary opportunities! 🍳👨‍🍳 Seeking a dynamic kitchen to showcase my skills.",
            "Passionate chef looking for the next challenge. Let's create something amazing together! 🍝🍣",
            "Experienced in international cuisine and ready to bring creativity to your restaurant. 🥘🍜",
            "Specialized in desserts and pastries, eager to bring sweetness to your menu! 🍰🍩",
            "Versatile chef with a passion for fusion cuisine. Let's make innovative dishes together! 🍣🌮",
            "Dedicated to farm-to-table cooking, focused on fresh and local ingredients. 🍅🥬",
            "Innovative chef looking to experiment with new flavors and techniques. Let's cook! 🔥🍲",
            "Skilled in preparing vegan and vegetarian dishes, promoting healthy eating. 🥦🥑",
            "Excited to bring my extensive wine and food pairing knowledge to your establishment. 🍷🍴",
            "Passionate about sustainable cooking and reducing food waste. Join the movement! 🌱♻️",
            "Ready to lead a team with my experience in high-pressure kitchen environments. 👨‍🍳🏆",
            "Proficient in molecular gastronomy and eager to push culinary boundaries. 🧪🍽️",
            "Expert in Asian cuisines, including sushi and dim sum. Let's roll! 🍣🥟",
            "Bringing a love for Mediterranean flavors and seafood to your kitchen. 🐟🍋",
            "Skilled in baking artisanal breads and pastries. Let's make something delicious! 🥖🍰",
            "Experienced in fine dining and Michelin-starred kitchens. Let's elevate the dining experience! 🌟🍽️",
            "Passionate about creating memorable dining experiences through food artistry. 🎨🍴",
            "Specializing in traditional and modern French cuisine. Bon appétit! 🇫🇷🍷",
            "Enthusiastic about teaching and mentoring young chefs. Let's grow together! 👩‍🍳👨‍🍳",
            "Looking to bring my creative plating skills to your restaurant. A feast for the eyes! 👀🍽️",
            "Expert in preparing gluten-free and allergen-free dishes. Inclusive dining for all! 🌾🚫",
            "Ready to introduce new seasonal menus and fresh ideas. Let's innovate! 🌻🍂",
            "Passionate about pastry arts, from cakes to confections. Sweet creations await! 🎂🍫",
            "Eager to showcase my BBQ and grilling expertise. Perfect for summer vibes! 🍖🔥",
            "Excited to bring my experience in food festivals and large-scale events. Let's celebrate food! 🎉🍴",
            "Focused on creating healthy, balanced meals that don't compromise on flavor. 🍏🥗",
            "Specializing in tapas and small plates, perfect for sharing. Let's make it a feast! 🍢🍤",
            "Bringing a background in hotel and resort dining to your establishment. Luxury dining experience! 🏨🍽️",
            "Excited to explore new culinary horizons and fusion cuisines. Endless possibilities! 🌏🍜",
            "Dedicated to using only the finest ingredients for exquisite taste. Quality is key! 🥇🧀",
            "Looking to create immersive dining experiences through storytelling and food. 🍽️📖",
            "Bringing a touch of artistry to every dish, from concept to plate. 🎨🍲",
            "Experienced in crafting customized menus for private dining and events. Personalized service! 🍽️🎂",
            "Ready to bring my passion for sustainable seafood to your restaurant. Let's protect our oceans! 🐠🌊",
            "Specializing in brunch menus, from eggs benedict to pancakes. The best meal of the day! 🍳🥞",
            "Expert in comfort food with a gourmet twist. Let's create heartwarming dishes! 🍔🍟",
            "Eager to bring my skills in international street food to your kitchen. Let's spice things up! 🌮🌭",
            "Passionate about dessert art, from delicate pastries to show-stopping cakes. 🍰🎂",
            "Bringing a flair for dramatic presentations and unique flavor combinations. 🍽️✨",
            "Skilled in the art of charcuterie and cheese pairings. Perfect for wine lovers! 🧀🍷",
            "Looking to introduce a health-focused menu with superfoods and nutrient-rich dishes. 🍇🥑",
            "Experienced in crafting artisan cocktails and drink pairings. Cheers to great food! 🍹🍸",
            "Focused on creating a welcoming atmosphere through food and hospitality. Let's make guests feel at home! 🏡🍴",
            "Expert in vegan desserts, from rich cakes to creamy ice creams. No dairy, no problem! 🍦🌱",
            "Passionate about food photography and styling. Every dish is a work of art! 📸🍽️",
            "Ready to innovate with new cooking technologies and techniques. The future of food is here! 🚀🍲",
            "Looking to introduce a children's menu that is both fun and nutritious. Happy kids, happy parents! 🥪🍓",
            "Bringing experience in managing kitchen operations and ensuring top quality. Consistency is key! 🔪📏",
            "Excited to collaborate with local farmers and artisans to source the best ingredients. Support local! 🌾🍎",
            "Passionate about food as a cultural experience, exploring global flavors and traditions. 🌍🍛",
            "Specializing in food and beverage pairings for an all-encompassing dining experience. 🍷🍽️",
        ] * 20  # Multiply the list to simulate more entries
        
        image_texts = [
         "Chef Looking for Opportunities",
            "Join My Culinary Journey",
            "Let's Create Culinary Magic",
            "Specializing in Desserts and Pastries",
            "Fusion Cuisine Expert",
            "Farm-to-Table Advocate",
            "Innovative Chef",
            "Vegan and Vegetarian Specialist",
            "Wine and Food Pairing Expert",
            "Sustainable Cooking Enthusiast",
            "Experienced Kitchen Leader",
            "Molecular Gastronomy Expert",
            "Asian Cuisine Specialist",
            "Mediterranean Flavors",
            "Artisanal Breads and Pastries",
            "Fine Dining Experience",
            "Food Artistry",
            "French Cuisine Specialist",
            "Mentor and Educator",
            "Creative Plating",
            "Gluten-Free and Allergen-Free",
            "Seasonal Menus",
            "Pastry Arts",
            "BBQ and Grilling Expert",
            "Festival and Event Chef",
            "Healthy Balanced Meals",
            "Tapas and Small Plates",
            "Luxury Dining Background",
            "Fusion Cuisine Explorer",
            "Quality Ingredients",
            "Immersive Dining Experiences",
            "Artistic Dish Presentation",
            "Customized Menus",
            "Sustainable Seafood",
            "Brunch Specialist",
            "Comfort Food Gourmet",
            "Street Food Specialist",
            "Dessert Artist",
            "Dramatic Presentations",
            "Charcuterie and Cheese Pairings",
            "Health-Focused Menu",
            "Artisan Cocktails",
            "Welcoming Atmosphere",
            "Vegan Dessert Specialist",
            "Food Photography and Styling",
            "Innovative Cooking Techniques",
            "Children's Menu Designer",
            "Kitchen Operations Manager",
            "Local Ingredient Advocate",
            "Cultural Culinary Experience",
            "Food and Beverage Pairings",
        ] * 20  # Multiply the list to simulate more entries

    elif user_type == 3:  # Restaurant Owner
        captions = [
            "Looking to sell my restaurant to the right buyer. Excellent location and loyal customer base. 🏢🍽️",
            "Seeking a reliable chef to join our team. Great working environment and opportunities for growth! 👨‍🍳🏆",
            "In need of quality suppliers for fresh ingredients. Let's work together to serve the best dishes. 🍅🥬",
            "Expanding our menu and looking for talented chefs to join us. Apply now! 🍲🍛",
            "Join our growing restaurant chain and be part of an exciting culinary journey! 🥂🍽️",
            "Offering a unique dining experience with a focus on local cuisine. Come dine with us! 🍽️🌿",
            "We are looking for enthusiastic servers and staff to join our team. Great work environment! 🥂🍴",
            "Introducing a new menu with seasonal dishes. Fresh flavors await! 🌷🍂",
            "Renovating our space for a fresh new look. Stay tuned for the grand reopening! 🎉🏢",
            "Special event coming up! Book your reservations now for an unforgettable experience. 📅🍽️",
            "Partnering with local farms to bring you the freshest ingredients. Taste the difference! 🌾🍅",
            "Launching a new brunch menu this weekend. Join us for delicious morning treats! 🥞☕",
            "Looking for creative bartenders to craft unique cocktails for our patrons. 🍹🍸",
            "Expanding our catering services. Let us handle your next event with delicious food! 🎂🎉",
            "Proud to announce our recent award for best restaurant in town! Thank you for your support! 🏆🍴",
            "Hosting a charity dinner to support local causes. Join us for a night of good food and giving! 🍽️❤️",
            "Seeking a passionate pastry chef to bring sweetness to our desserts menu. 🍰🧁",
            "Looking for an experienced sommelier to enhance our wine offerings. 🍷🍇",
            "Planning to open a new location soon. Stay updated for exciting news! 🏢📍",
            "Offering a limited-time discount on group bookings. Celebrate with us! 🎉🍽️",
            "Collaborating with local artists to showcase their work in our restaurant. Art meets food! 🎨🍴",
            "Launching a cooking class series for food enthusiasts. Learn from our chefs! 👨‍🍳📚",
            "Celebrating our anniversary with special dishes and offers. Join the celebration! 🎉🍾",
            "Introducing a loyalty program for our regular customers. Enjoy exclusive benefits! 🎁🍴",
            "Looking for reliable suppliers for high-quality seafood. Let's work together! 🦞🐟",
            "Expanding our menu to include vegan and gluten-free options. Inclusive dining for all! 🌱🚫",
            "Hosting a wine tasting event featuring local vineyards. Discover new favorites! 🍷🍇",
            "Seeking partnerships with local businesses for cross-promotions. Let's grow together! 🤝🏢",
            "Planning a themed dinner night. Dress up and enjoy a unique dining experience! 🎭🍽️",
            "Hiring a talented mixologist to create signature cocktails. Elevate your drink experience! 🍸🔮",
            "Offering cooking demonstrations by our head chef. Learn the secrets behind our dishes! 🍳👨‍🍳",
            "Looking to hire a dedicated restaurant manager with a passion for hospitality. 🏢👥",
            "Celebrating cultural heritage with a special menu inspired by traditional recipes. 🌍🍛",
            "Expanding our delivery service area. Enjoy our dishes from the comfort of your home! 🚚🍔",
            "Inviting food bloggers and influencers for a tasting event. Share your experience! 📸🍴",
            "Seeking talented chefs with a love for innovation and creativity. Join our team! 🍲🧑‍🍳",
            "Launching a new dessert menu featuring decadent treats. Satisfy your sweet tooth! 🍨🍫",
            "Offering live music on weekends. Enjoy great food and entertainment! 🎶🍔",
            "Looking for partners to launch a community garden project. Fresh produce, fresh ideas! 🌱👨‍🌾",
            "Planning a menu revamp to include more sustainable and organic ingredients. Go green! 🌿🍽️",
            "Excited to host a food and wine pairing dinner. A feast for the senses! 🍷🍴",
            "Announcing a new kids' menu with fun and nutritious options. Family-friendly dining! 🍔🍟",
            "Looking for an executive chef with experience in fine dining. Lead our culinary team! 🍽️👨‍🍳",
            "Partnering with local breweries for a craft beer tasting event. Cheers! 🍻🍺",
            "Offering private dining rooms for special occasions. Celebrate in style! 🎉🍽️",
            "Launching a new health-conscious menu. Delicious and nutritious! 🥗🍴",
            "Seeking a creative marketing manager to promote our brand. Join us! 📈🏢",
            "Proudly supporting local food banks and charities. Giving back to the community! ❤️🍲",
            "Expanding our outdoor seating area for a great al fresco dining experience. Enjoy the fresh air! 🌳🍽️",
        ] * 20  # Multiply the list to simulate more entries
        
        image_texts = [
            "Restaurant for Sale",
            "Hiring Experienced Chef",
            "Looking for Suppliers",
            "Join Our Culinary Team",
            "Exciting Restaurant Opportunities",
            "Local Cuisine Focus",
            "Hiring Servers and Staff",
            "New Seasonal Menu",
            "Renovation and Reopening",
            "Special Event Reservations",
            "Local Farm Partnerships",
            "Brunch Menu Launch",
            "Hiring Creative Bartenders",
            "Catering Services Expansion",
            "Award-Winning Restaurant",
            "Charity Dinner Event",
            "Hiring Pastry Chef",
            "Looking for Sommelier",
            "New Location Coming Soon",
            "Group Booking Discounts",
            "Art and Food Collaboration",
            "Cooking Class Series",
            "Anniversary Celebration",
            "Loyalty Program Launch",
            "Seeking Seafood Suppliers",
            "Vegan and Gluten-Free Options",
            "Wine Tasting Event",
            "Business Partnership Opportunities",
            "Themed Dinner Night",
            "Hiring Mixologist",
            "Cooking Demonstrations",
            "Hiring Restaurant Manager",
            "Cultural Heritage Menu",
            "Delivery Service Expansion",
            "Inviting Food Bloggers",
            "Hiring Innovative Chefs",
            "New Dessert Menu",
            "Live Music Weekends",
            "Community Garden Project",
            "Sustainable Ingredients Menu",
            "Food and Wine Pairing Dinner",
            "New Kids' Menu",
            "Hiring Executive Chef",
            "Craft Beer Tasting Event",
            "Private Dining Rooms",
            "Health-Conscious Menu",
            "Hiring Marketing Manager",
            "Supporting Local Charities",
            "Outdoor Seating Expansion",
        ] * 20  # Multiply the list to simulate more entries

    else:
        return "Invalid user type."

    # Randomly select a caption and image text
    caption = random.choice(captions)
    image_text = random.choice(image_texts)

    return caption, image_text


@app.post("/generate_content")
def generate_content(user_type: UserType):
    caption, image_text = generate_post_content(user_type.user_type)
    return {"caption": caption, "image_text": image_text}

@app.post("/generate_Post")
def generate_Post(text: Text):
    # Generate a filename with the current time
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    output_filename = f"output_{timestamp}.png"
    output_path = os.path.join('imgs', output_filename)
    
    # Ensure the 'imgs' directory exists
    os.makedirs('imgs', exist_ok=True)
    
    # Choose a random image from the 'dw' folder
    dw_folder_path = 'dw'
    if not os.path.exists(dw_folder_path) or not os.listdir(dw_folder_path):
        return {"error": "No images found in 'dw' folder"}

    random_image = random.choice(os.listdir(dw_folder_path))
    image_path = os.path.join(dw_folder_path, random_image)
    
    # Process the image and add text
    add_text_to_image(
        image_path=image_path,
        text=text.text,
        output_path=output_path,
        position=(20, 40),
        max_font_size=30,
        shadow_offset=(0, 0),
        transparency=200,
        font_path='Roboto-Bold.ttf'
    )
    
    # Upload to S3
    s3_url = upload_to_s3(output_path, output_filename)
    
    return {"image_name": output_filename, "s3_url": s3_url}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
