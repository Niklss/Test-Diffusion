import io

import torch
from PIL import Image

from common.benchmark import benchmark_decorator
from diffusers import StableDiffusionImg2ImgPipeline

from diffusion.settings import file_manager


class Processor:
    """
    This class performs prompt guided Img2Img on call
    """
    def __init__(self, model_name):
        """
        To simplify the development I shrinked the parameters.
        It is possible to add any other parameters.
        :param model_name:
        """
        self.device = 'cuda'
        self.pipe = StableDiffusionImg2ImgPipeline.from_pretrained(model_name, torch_dtype=torch.float16)
        self.pipe = self.pipe.to(self.device)
        self.generator = torch.Generator(device=self.device)
        self.strength = 0.75
        self.guidance_scale = 7.5

    @benchmark_decorator('log.txt')
    async def __call__(self, message, *args, **kwargs):
        """
        This method performs stable diffusion.
        All operations with images are performed in memory.
        File write operations perform only with S3
        Time and memory consumption writes to log.txt
        :param message: message that come from Kafka
        :param args:
        :param kwargs:
        :return:
        """
        image = file_manager.load_file(message['filepath']).read()
        image = Image.open(io.BytesIO(image))
        res_image = self.pipe(prompt=message['prompt'], image=image, strength=self.strength,
                              guidance_scale=self.guidance_scale, generator=self.generator).images[0]
        image_byte_arr = io.BytesIO()
        res_image.save(image_byte_arr, format='PNG')
        image_byte_arr = image_byte_arr.getvalue()
        file_manager.save_file(image_byte_arr, message['res_filepath'])
        return
