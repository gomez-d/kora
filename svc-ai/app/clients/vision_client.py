from huggingface_hub import hf_hub_download

from ultralytics import YOLO

from io import BytesIO

from transformers import (
    CLIPProcessor,
    CLIPModel
)

import torch
from PIL import Image


class VisionClient:

    def __init__(self):

        # ==========================================
        # 1. LOAD YOLO MODEL
        # ==========================================

        model_path = hf_hub_download(
            repo_id="arunapb/yolo11l-food-segmentation",
            filename="best.pt"
        )

        self.yolo_model = YOLO(model_path)

        # ==========================================
        # 2. LOAD CLIP MODEL
        # ==========================================

        clip_model_name = "openai/clip-vit-base-patch32"

        self.clip_processor = CLIPProcessor.from_pretrained(
            clip_model_name
        )

        self.clip_model = CLIPModel.from_pretrained(
            clip_model_name
        )

        # ==========================================
        # 3. CONFIGURE DEVICE
        # ==========================================

        self.device = (
            "cuda"
            if torch.cuda.is_available()
            else "cpu"
        )

        self.clip_model.to(self.device)

        # ==========================================
        # 4. INGREDIENTS FOR CLIP
        # ==========================================
        self.ingredients = [
            "rice",
            "beans",
            "grilled beef",
            "chicken",
            "pork",
            "turkey",
            "fish",
            "salmon",
            "tuna",
            "shrimp",
            "egg",
            "cheese",
            "milk",
            "yogurt",
            "bread",
            "tortilla",
            "pasta",
            "noodles",
            "oatmeal",
            "cereal",
            "potato",
            "sweet potato",
            "french fries",
            "mashed potatoes",
            "carrot",
            "broccoli",
            "cauliflower",
            "spinach",
            "lettuce",
            "cabbage",
            "cucumber",
            "tomato",
            "onion",
            "garlic",
            "bell pepper",
            "jalapeno",
            "corn",
            "peas",
            "green beans",
            "zucchini",
            "eggplant",
            "mushroom",
            "avocado",
            "pumpkin",
            "beetroot",
            "celery",
            "asparagus",
            "radish",
            "chickpeas",
            "lentils",
            "apple",
            "banana",
            "orange",
            "lemon",
            "lime",
            "strawberry",
            "blueberry",
            "raspberry",
            "blackberry",
            "grape",
            "watermelon",
            "melon",
            "pineapple",
            "mango",
            "papaya",
            "kiwi",
            "peach",
            "pear",
            "plum",
            "cherry",
            "coconut",
            "pomegranate",
            "walnut",
            "almond",
            "peanut",
            "cashew",
            "pistachio",
            "chia seeds",
            "flax seeds",
            "sunflower seeds",
            "peanut butter",
            "olive oil",
            "butter",
            "honey",
            "sugar",
            "salt",
            "tomato sauce",
            "mayonnaise",
            "mustard",
            "ketchup",
            "guacamole",
            "hummus",
            "salsa",
            "chocolate",
            "tofu",
            "tempeh",
            "granola"
        ]

        self.search_texts = [
            f"a photo of {ingredient}, food"
            for ingredient in self.ingredients
        ]

    def analyze(self, image):

        # ==========================================
        # 1. OPEN IMAGE
        # ==========================================

        if isinstance(image, bytes):

            original_image = Image.open(
                BytesIO(image)
            ).convert("RGB")

        else:

            original_image = Image.open(
                image
            ).convert("RGB")

        print("====================================")
        print("IMAGE SIZE:", original_image.size)
        print("DEVICE:", self.device)

        # ==========================================
        # 2. YOLO DETECTION
        # ==========================================

        results = self.yolo_model.predict(
            source=original_image,
            conf=0.25,
            imgsz=640
        )

        result = results[0]

        detection_count = (
            0
            if result.boxes is None
            else len(result.boxes)
        )

        print(
            "YOLO DETECTED:",
            detection_count,
            "objects"
        )

        # ==========================================
        # 3. YOLO RESULTS
        # ==========================================

        yolo_results = []

        if result.boxes is not None:

            boxes = result.boxes.xyxy.cpu().numpy()
            confidences = result.boxes.conf.cpu().numpy()
            classes = result.boxes.cls.cpu().numpy()

            for i in range(len(boxes)):

                class_id = int(classes[i])

                class_name = self.yolo_model.names.get(
                    class_id,
                    str(class_id)
                )

                yolo_results.append({
                    "food": str(class_name),
                    "confidence": round(
                        float(confidences[i]),
                        4
                    ),
                    "class_id": class_id,
                    "box": [
                        round(float(value), 2)
                        for value in boxes[i]
                    ]
                })

        print("YOLO RESULTS:")
        print(yolo_results)

        # ==========================================
        # IF YOLO DID NOT DETECT ANYTHING
        # ==========================================

        if len(yolo_results) == 0:

            print("YOLO DID NOT DETECT ANY OBJECTS")
            print("====================================")

            return {
                "success": True,
                "message": "YOLO did not detect any food",
                "yolo": [],
                "clip": [],
                "detections": []
            }

        # ==========================================
        # 4. GET DETECTION BOXES
        # ==========================================

        boxes = result.boxes.xyxy.cpu().numpy()

        # ==========================================
        # 5. CROP FOOD REGIONS
        # ==========================================

        image_crops = []

        for i, box in enumerate(boxes):

            x_min, y_min, x_max, y_max = box

            image_crop = original_image.crop(
                (
                    int(x_min),
                    int(y_min),
                    int(x_max),
                    int(y_max)
                )
            )

            image_crops.append(image_crop)

        print(
            "CROPS CREATED:",
            len(image_crops)
        )

        # ==========================================
        # 6. CLASSIFICATION WITH CLIP
        # ==========================================

        clip_results = []

        for i, image_crop in enumerate(image_crops):

            inputs = self.clip_processor(
                text=self.search_texts,
                images=image_crop,
                return_tensors="pt",
                padding=True
            )

            inputs = {
                key: value.to(self.device)
                for key, value in inputs.items()
            }

            with torch.no_grad():

                outputs = self.clip_model(
                    **inputs
                )

            logits_per_image = outputs.logits_per_image

            probabilities = logits_per_image.softmax(
                dim=1
            )[0].cpu().numpy()

            # Get the top 5 predictions

            indices = probabilities.argsort()[-5:][::-1]

            top_5 = []

            for index in indices:

                top_5.append({
                    "food": self.ingredients[index],
                    "confidence": round(
                        float(probabilities[index]),
                        4
                    )
                })

            clip_results.append({
                "crop": i + 1,
                "prediction": top_5[0],
                "top_5": top_5
            })

        print("====================================")
        print("CLIP RESULTS:")
        print(clip_results)

        # ==========================================
        # 7. FINAL IMAGE RESULTS
        # ==========================================

        confidence_threshold = 0.10

        valid_ingredients = set()

        # Filter predictions by confidence
        # and collect unique ingredients

        for result in clip_results:

            prediction = result["prediction"]

            if prediction["confidence"] >= confidence_threshold:

                valid_ingredients.add(
                    prediction["food"]
                )

        # Format final result

        if valid_ingredients:

            ingredient_list = list(
                valid_ingredients
            )

            if len(ingredient_list) > 1:

                detected_ingredients = (
                    ", ".join(ingredient_list[:-1])
                    + " and "
                    + ingredient_list[-1]
                )

            else:

                detected_ingredients = ingredient_list[0]

            print(
                "Detected food in the original image:",
                detected_ingredients
            )

        else:

            detected_ingredients = ""

            print(
                "No food was detected with a confidence "
                "greater than 10%."
            )

        # ==========================================
        # 8. FINAL RESPONSE
        # ==========================================

        print("====================================")
        print("COMPLETE ANALYSIS")
        print("====================================")

        detections = []

        for result in clip_results:
            prediction = result["prediction"]

            if prediction["confidence"] >= confidence_threshold:
                detections.append({
                    "food": prediction["food"],
                    "confidence": prediction["confidence"]
                })

        return {
            "success": True,
            "detections": detections
        }