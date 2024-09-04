import os


class Config(object):
    pass


class ProductionConfig(Config):
    DEBUG = False
    HOST_NAME = os.getenv('HOST_NAME')
    PORT_NUMBER = os.getenv('PORT_NUMBER')
    # SECRET_AUTHEN_KEY = os.getenv('SECRET_AUTHEN_KEY')

    # Folder config
    DATA_DIR = os.getenv('DATA_DIR')
    MODEL_DIR = os.getenv('MODEL_DIR')
    LOG_DIR = os.getenv('LOG_DIR')


class DevelopmentConfig(Config):
    if os.getenv('DEBUG') and os.getenv('DEBUG') in ['True', 'False']:
        DEBUG = os.getenv('DEBUG') == 'True'
    else:
        DEBUG = True
    # if os.getenv('HOST_NAME'):
    #     HOST_NAME = os.getenv('HOST_NAME')
    # else:
    #     HOST_NAME = '0.0.0.0'
    # if os.getenv('PORT_NUMBER'):
    #     PORT_NUMBER = os.getenv('PORT_NUMBER')
    # else:
    #     PORT_NUMBER = '5000'
    # if os.getenv('SECRET_AUTHEN_KEY'):
    #     SECRET_AUTHEN_KEY = os.getenv('SECRET_AUTHEN_KEY')
    # else:
    #     SECRET_AUTHEN_KEY = ''

    # Folder config
    if os.getenv('DATA_DIR'):
        DATA_DIR = os.getenv('DATA_DIR')
    else:
        DATA_DIR = './data'
    if os.getenv('MODEL_DIR'):
        MODEL_DIR = os.getenv('MODEL_DIR')
    else:
        MODEL_DIR = './data/models/infer'
    if os.getenv('LOG_DIR'):
        LOG_DIR = os.getenv('LOG_DIR')
    else:
        LOG_DIR = './log'

    if os.getenv('MAX_SIZE_UPLOAD'):
        MAX_SIZE_UPLOAD = int(os.getenv('MAX_SIZE_UPLOAD'))
    else:
        MAX_SIZE_UPLOAD = 10485760


class ModelConfig(Config):
    ONNX_TYPE = 'onnx'
    DEFAULT_TYPE = 'default'

    if os.getenv('LOAD_MODEL') and os.getenv('LOAD_MODEL') in ['True', 'False']:
        LOAD_MODEL = os.getenv('LOAD_MODEL') == 'True'
    else:
        LOAD_MODEL = True

    if os.getenv('DEVICE') and os.getenv('DEVICE') in ['cpu', 'gpu', 'cuda']:
        DEVICE = os.getenv('DEVICE')
    else:
        DEVICE = 'cpu'

    if os.getenv('NUM_TORCH_THREADS'):
        NUM_TORCH_THREADS = os.getenv('NUM_TORCH_THREADS')
    else:
        NUM_TORCH_THREADS = '2'

    # Individual model config
    if os.getenv('YOLO_MODEL_TYPE') and os.getenv('YOLO_MODEL_TYPE') in ['onnx', 'default', 'triton']:
        YOLO_MODEL_TYPE = os.getenv('YOLO_MODEL_TYPE')
    else:
        YOLO_MODEL_TYPE = ONNX_TYPE

    if os.getenv('OCR_MODEL_TYPE') and os.getenv('OCR_MODEL_TYPE') in ['seq2seq', 'seq2seq_onnx', 'transformer',
                                                                       'transformer_onnx']:
        OCR_MODEL_TYPE = os.getenv('OCR_MODEL_TYPE')
    else:
        OCR_MODEL_TYPE = ONNX_TYPE

    if os.getenv('ANALYZER_MAX_DATAPOINTS'):
        ANALYZER_MAX_DATAPOINTS = int(os.getenv('ANALYZER_MAX_DATAPOINTS'))
    else:
        ANALYZER_MAX_DATAPOINTS = 3


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
}

VERSION = "1.0.0"
config_object = config[os.getenv('DEPLOY_ENV') or 'development']
model_config = ModelConfig
