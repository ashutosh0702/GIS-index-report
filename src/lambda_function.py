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

    filtered_objects = [obj for obj in objects['Contents'] if obj["Key"].endswith(f"_{index}.png")]

    print(objects)
    num_images = len(filtered_objects)

    if filtered_objects:
        farm_name = filtered_objects[0]["Key"].split("/")[0].split("_")[1]

    cols = min(num_images,5)
    rows = (num_images + 4) // 5

    fig, axs = plt.subplots(rows,cols, figsize=(cols*5, rows * 5))

    if rows > 1:
        axs = [ax for sublist in axs for ax in sublist]

    elif rows==1:
        axs = [axs[i] for i in range(cols)]

    for i, obj in enumerate(filtered_objects):

        print("Inside for loop")

        key = obj["Key"]
        date = key.split("/")[1].split("_")[0]

        s3_object = s3_client.get_object(Bucket=bucket_name, Key=key)
        file_byte_string = s3_object['Body'].read()

        img = plt.imread(BytesIO(file_byte_string))
        axs[i].imshow(img)
        axs[i].set_title(date)
        axs[i].axis("off")
    
    print("Finished for loop execution")

    try:
        print("Before if-else block")
        if num_images%5 != 0:

            for j in range(num_images, rows*5):
                print(f"Turning off axis for subplot{j}")
                axs[j].axis("off")
        print("After if-else block")
    except Exception as e:
        print(e) 

    if filtered_objects:
        fig.suptitle(f"Temporal {index} for {farm_name}", fontsize=16)

    buf = BytesIO()
    plt.savefig(buf, format='png',dpi=200, bbox_inches='tight', pad_inches=0)
    buf.seek(0)

    return StreamingResponse(buf, media_type="image/png")

if __name__ == "__main__":
   uvicorn.run(app, host="0.0.0.0", port=8080)
