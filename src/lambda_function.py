from fastapi import FastAPI
from mangum import Mangum
import boto3
import matplotlib.pyplot as plt
from io import BytesIO
from fastapi.responses import StreamingResponse


app = FastAPI()
handler = Mangum(app)

s3_client = boto3.client('s3', region_name='us-west-2')

@app.get("/report")
def read_root():
   return {"Welcome to": "My first FastAPI depolyment using Docker image"}

@app.get("/report/{farmid}/{index}")
async def read_png(farmid: int, index: str):

    bucket_name = "gis-colourized-png-data"

    objects = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=f'{farmid}_')

    print(objects)
    num_images = len(objects['Contents'])

    cols = min(num_images,5)
    rows = (num_images + 4) // 5

    fig, axs = plt.subplots(rows,cols, figsize=(cols*5, rows * 5))

    if rows > 1:
        axs = [ax for sublist in axs for ax in sublist]

    elif rows==1:
        axs = [axs[i] for i in range(cols)]

    for i, obj in enumerate(objects['Contents']):

        print("Inside for loop")

        key = obj["Key"]
        date = key.split("/")[1].split("_")[0]

        s3_object = s3_client.get_object(Bucket=bucket_name, Key=key)
        file_byte_string = s3_object['Body'].read()

        img = plt.imread(BytesIO(file_byte_string))
        axs[i].imshow(img)
        axs[i].set_title(date)
        axs[i].axis("off")
    
    if num_images%5 != 0:

        for j in range(num_images, rows*5):
            axs[j].axis("off")

    print("Finished for loop execution")

    buf = BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)

    return StreamingResponse(buf, media_type="image/png")

if __name__ == "__main__":
   uvicorn.run(app, host="0.0.0.0", port=8080)
