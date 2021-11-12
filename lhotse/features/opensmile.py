from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Union, Optional, Sequence

import numpy as np

from lhotse.features.base import FeatureExtractor, register_extractor
from lhotse.utils import is_module_available, Seconds

@dataclass
class OpenSmileConfig:
    """ 
    OpenSmile configs are stored in separated txt files in its specific format. 
    You can specify predefined config by setting ``feature_set`` and ``feature_level`` 
    class attributes with:
    (1) ``FeatureSet`` and ``FeatureLevel`` classes predefined in
    https://github.com/audeering/opensmile-python/blob/master/opensmile/core/define.py 
    OR
    (2) strings refered to enum members,  
    You can also create your own config file and pass its path and corresponding feature level 
    as documented here https://audeering.github.io/opensmile-python/usage.html#custom-config.
    """
    feature_set:Union[str, Any] = 'ComParE_2016' # default feature set, string with set name or path to a custom config file
    feature_level:Union[str, Any] = 'lld' # default feature level or level name if a custom config file is used
    options: dict = None           # dictionary with optional script parameters
    loglevel: int = 2              # log level (0-5), the higher the number the more log messages are given
    logfile: str = None            # if not ``None`` log messages will be stored to this file
    sampling_rate: int = 16000     # If ``None`` it will call ``process_func`` with the actual sampling rate of the signal.
    channels: Union[int, Sequence[int]] = 0 # channel selection, see :func:`audresample.remix`
    mixdown: bool = False          # apply mono mix-down on selection
    resample: bool = False         # if ``True`` enforces given sampling rate by resampling
    num_workers: Optional[int] = 1 # number of parallel jobs or 1 for sequential processing. If ``None`` will be set 
                                   # to the number of processors    
    verbose: bool = False          # show debug messages        
                               

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "OpenSmileConfig":
        return OpenSmileConfig(**data)
    
    @staticmethod
    def featuresets_names():
        """
        Returns list of strings with names of pretrained FeatureSets available in opensmile.
        """
        assert is_module_available("opensmile"), 'To use opensmile extractors, please "pip install opensmile" first.'
        import opensmile
        return list(opensmile.FeatureSet.__members__)


@register_extractor
class OpenSmileWrapper(FeatureExtractor):
    """Wrapper for extraction of features implemented in OpenSmile."""

    name = "opensmile-wrapper"
    config_type = OpenSmileConfig
    smileExtractor = None
    
    def __init__(self, config: Optional[Any] = None):
        super().__init__(config=config)
        assert is_module_available(
            "opensmile"
        ), 'To use opensmile extractors, please "pip install opensmile" first.'
        import opensmile
        self.smileExtractor = opensmile.Smile(
            feature_set=self.config.feature_set,
            feature_level=self.config.feature_level,
            sampling_rate=self.config.sampling_rate,
            options=self.config.options,
            loglevel=self.config.loglevel,
            logfile=self.config.logfile,
            channels=self.config.channels,
            mixdown=self.config.mixdown,        
            resample=self.config.resample,
            num_workers=self.config.num_workers,
            verbose=self.config.verbose
        )  
        
    @property
    def frame_shift(self) -> Seconds:
    # TODO: (Parse the config)
        return 0

    def feature_dim(self, sampling_rate: int) -> int:
    # TODO (Parse the config)
        return 0
        
    def feature_names(self) -> List[str]:
        return self.smileExtractor.feature_names()

    def extract(self, samples: np.ndarray, sampling_rate: int) -> np.ndarray:    
        assert sampling_rate == self.config.sampling_rate
        return self.smileExtractor.process_signal(samples, sampling_rate=sampling_rate).to_numpy()    
    

#    @staticmethod
#    def mix(
#        features_a: np.ndarray, features_b: np.ndarray, energy_scaling_factor_b: float
#    ) -> np.ndarray:
#        # Torchaudio returns log-power spectrum, hence the need for logsumexp
#        return np.log(
#            np.maximum(
#                # protection against log(0); max with EPSILON is adequate since these are energies (always >= 0)
#                EPSILON,
#                np.exp(features_a) + energy_scaling_factor_b * np.exp(features_b),
#            )
#        )
#
#    @staticmethod
#    def compute_energy(features: np.ndarray) -> float:
#        # Torchaudio returns log-power spectrum, hence the need for exp before the sum
#        return float(np.sum(np.exp(features)))
