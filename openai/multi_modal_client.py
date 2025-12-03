from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI()

# can handle base64 encoded images
# base64_img = encode_image(file)

res = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user",
               "content": [
                   {
                       "type": "text",
                       "text": "What is on the picture?"
                   },
                   {
                       "type": "image_url",
                       "image_url": {
                           "url": "https://i.imgur.com/2111111.jpg"
                       }
                   }

               ]}]
)
print(res.choices[0].message.content)
