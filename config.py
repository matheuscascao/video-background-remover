from dotenv import load_dotenv
import os
load_dotenv()


class Config:
    STABLE_DIFFUSION_BASE_URL = os.getenv('STABLE_DIFFUSION_BASE_URL')


settings = Config()
