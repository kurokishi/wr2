# core/config.py
import os
from dataclasses import dataclass
from typing import Optional
import json

@dataclass
class Config:
    """Konfigurasi aplikasi Warren AI"""
    
    # Data provider settings
    data_provider: str = "yahoo"  # "yahoo", "alpha_vantage", "fmp"
    
    # API Keys (akan diisi dari environment variables)
    yahoo_api_key: Optional[str] = None
    alpha_vantage_api_key: Optional[str] = None
    fmp_api_key: Optional[str] = None
    
    # Analysis settings
    default_period: str = "2y"
    rsi_period: int = 14
    moving_averages: list = None  # Default: [20, 50, 200]
    
    # Display settings
    currency: str = "IDR"
    locale: str = "id_ID"
    
    # Cache settings
    cache_enabled: bool = True
    cache_duration: int = 3600  # seconds
    
    def __post_init__(self):
        # Load from environment variables
        self.yahoo_api_key = os.getenv("YAHOO_API_KEY", self.yahoo_api_key)
        self.alpha_vantage_api_key = os.getenv("ALPHA_VANTAGE_API_KEY", self.alpha_vantage_api_key)
        self.fmp_api_key = os.getenv("FMP_API_KEY", self.fmp_api_key)
        
        # Set default values
        if self.moving_averages is None:
            self.moving_averages = [20, 50, 200]
    
    @classmethod
    def from_json(cls, json_file: str):
        """Load configuration from JSON file"""
        with open(json_file, 'r') as f:
            config_dict = json.load(f)
        return cls(**config_dict)
    
    def to_dict(self):
        """Convert config to dictionary"""
        return {
            'data_provider': self.data_provider,
            'default_period': self.default_period,
            'currency': self.currency,
            'cache_enabled': self.cache_enabled
        }
