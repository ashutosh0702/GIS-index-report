from fastapi import FastAPI
from mangum import Mangum
import boto3
import matplotlib.pyplot as plt
from io import BytesIO

app = FastAPI()

s3_client = boto3.client('s3', region_name='us-west-2')

@app.get("/{farmid}/{index}")
async def read_png(farmid: int, index: str):

    bucket_name = "gis-colourized-png-data"

    objects = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=f'{farmid}_')

    fig, axs = plt.subplots(len(objects['Contents']), 1, figsize=(10, len(objects['Contents']) * 5))

    for i, obj in enumerate(objects['Contents']):

        key = obj["Key"]
        date = key.split("/")[1].split("_")[0]

        s3_object = s3_client.get_object(Bucket=bucket_name, Key=key)
        file_byte_string = s3_objects['Body'].read()

        img = plt.imread(BytesIO(file_byte_string))
        axs[i].imshow(img)
        axs[i].set_title(date)
        axs[i].axis("off")

    buf = BytesIO()
    plt.savefig(buf, format='.png')
    buf.seek(0)

    return StreamingResponse(buf, media_type="image/png")

handler = Mangum(app)
