import json
import random
import uuid

from fastapi import APIRouter, File, UploadFile, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from settings import file_manager, producer, model_names

kafka_router = APIRouter(prefix='/diffusion')
img_exts = ['jpg', 'png']


class DiffusionQuery(BaseModel):
    model_name: str = random.choice(model_names)
    prompt: str = 'Make it better'
    priority: int = 0   # For future


class DiffusionMessage(DiffusionQuery):
    filepath: str
    res_filepath: str
    id: str


class Response(BaseModel):
    image_id: str
    message: str
    access_link: str


@kafka_router.post('', response_model=Response)
async def start_process(meta: DiffusionQuery = Depends(), image: UploadFile = File(...)):
    # Check on type
    if not image.filename.split('.')[-1].lower() in img_exts:
        return JSONResponse({'message': 'Wrong file type, expected image'}, status_code=400)

    image_id, access_link = await produce(image.filename, image.file, meta)
    return {'image_id': image_id, 'message': 'Successfully created. You may access the result in few seconds using url',
            'access_link': access_link}


async def produce(image_name, image_file, meta: DiffusionQuery):
    """
    This function performs laying a message in queue and produce an access link for future image
    :param image_name: Name of the image
    :param image_file: File in StrinIO format
    :param meta: object of DiffusionQuery class to send necessary parameters
    :return:
    """
    image_id = str(uuid.uuid4())
    filepath = f"{image_id}.{image_name.split('.')[-1]}"
    res_filepath = f"{image_id}-result.{image_name.split('.')[-1]}"

    image = image_file.read()
    file_manager.save_file(image, filepath)
    access_link = file_manager.generate_access_link(res_filepath)

    message = DiffusionMessage(**meta.dict(), id=image_id, filepath=filepath, res_filepath=res_filepath)
    producer.produce(meta.model_name.replace('/', '.'), json.dumps(message.dict()).encode('utf-8'))
    return image_id, access_link
