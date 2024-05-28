from abc import abstractmethod
from typing import List, Union

# import torch

from object_models.exceptions import HealthCheckException
from pipeline.data_obj.datapoint import DataPoint


class SingletonMeta(type):
    """
        The Singleton class can be implemented in different ways in Python. Some
        possible methods include: base class, decorator, metaclass. We will use the
        metaclass because it is best suited for this purpose.
    """
    _instances = {}

    def __call__(cls, *args, **kwargs):
        """
        Possible changes to the value of the `__init__` argument do not affect
        the returned instance.
        """
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]


class BaseDetector(metaclass=SingletonMeta):
    """
    Abstract class for AI models.
    """

    def predict(self, *args, **kwargs) -> any:
        """
        Abstract method that contains all processing steps of the component.
        """
        raise NotImplementedError


class PipelineComponent(metaclass=SingletonMeta):
    @abstractmethod
    def serve(self, dp: DataPoint) -> None:
        """
        Processing an image through the whole pipeline component. Abstract method that contains all processing steps of
        the component.
        """
        raise NotImplementedError

    def health_check(self) -> bool:
        """
                Health check for the component.
                """
        raise NotImplementedError


class ForkComponent(metaclass=SingletonMeta):
    @abstractmethod
    def serve(self, dp: Union[DataPoint, List[DataPoint]]) -> Union[DataPoint, List[DataPoint]]:
        """
        Processing an image through the whole pipeline component. Abstract method that contains all processing steps of
        """
        raise NotImplementedError

    @abstractmethod
    def health_check(self) -> bool:
        """
        Health check for the component.
        """
        raise NotImplementedError


class PreProcessComponent(metaclass=SingletonMeta):
    @abstractmethod
    def serve(self, path, analyze_config=None) -> Union[DataPoint, List[DataPoint]]:
        """
        Load images from the data source and create a list of DataPoint objects.
        """
        raise NotImplementedError

    @abstractmethod
    def health_check(self) -> bool:
        """
        Health check for the component.
        """
        raise NotImplementedError


class PostProcessComponent(metaclass=SingletonMeta):
    @abstractmethod
    def serve(self, dps: Union[DataPoint, List[DataPoint]]) -> any:
        """
        Receive a list of DataPoint objects and return the desired output.
        """
        raise NotImplementedError

    @abstractmethod
    def health_check(self) -> bool:
        """
        Health check for the component.
        """
        raise NotImplementedError


class BasePipeline(metaclass=SingletonMeta):
    """
    Abstract class for Pipeline.
    """
    pipeline_component_list: List[PipelineComponent]

    # @classmethod
    # def init_torch(cls, model_config):
    #     """
    #     Initialize torch.
    #     """
    #
    #     if not hasattr(model_config, "DEVICE"):
    #         model_config.DEVICE = 0 if torch.cuda.is_available() else 'cpu'
    #
    #     # if model_config.NUM_TORCH_THREADS is not None and str(model_config.NUM_TORCH_THREADS).isdigit():
    #     #     model_config.NUM_TORCH_THREADS = int(model_config.NUM_TORCH_THREADS)
    #     #     log.dlog_i("Init torch with {} threads".format(model_config.NUM_TORCH_THREADS))
    #     #     torch.set_num_threads(model_config.NUM_TORCH_THREADS)
    #     # else:
    #     #     log.dlog_i("Init torch with default threads")
    #     #     model_config.NUM_TORCH_THREADS = None
    #     return model_config

    @classmethod
    @abstractmethod
    def build(cls, *args, **kwargs):
        """
        Abstract method to build the pipeline.
        """
        raise NotImplementedError

    @abstractmethod
    def analyze(self, *args, **kwargs) -> any:
        """
               Abstract method for analyzing the pipeline.
               """
        raise NotImplementedError

    def health_check(self):
        """
        Health check for the pipeline.
        """

        data = []
        for component in self.pipeline_component_list:
            if not component.health_check():
                data.append({"name": component.__class__.__name__, "status": "OK"})
            else:
                raise HealthCheckException(component.__class__.__name__)
        return data
