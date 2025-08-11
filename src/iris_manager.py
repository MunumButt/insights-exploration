import pandas as pd
import datetime as dt
from typing import Union, Callable
import time
from elexonpy.api_client import ApiClient
from elexonpy.api import BalancingMechanismPhysicalApi
from src.logging_config import get_logger

logger = get_logger("main")

# Color scheme for different datasets
COLORS = {"PN": "purple", "MELS": "green", "MILS": "orange"}


class IRISManager:
    """
    Combined manager and client for data fetching, processing, and visualization.
    """

    def __init__(self):
        self.elexonpy_base_client = ApiClient()
        self.physapi = BalancingMechanismPhysicalApi(self.elexonpy_base_client)
        logger.info("IRIS Manager initialized")

    def _serialize_response(self, response) -> pd.DataFrame:
        """Convert API response to pandas DataFrame."""
        try:
            response_dict = response.to_dict()
            df = pd.json_normalize(response_dict["data"])
            datetime_cols = ["time_from", "time_to", "settlement_date"]
            for col in datetime_cols:
                if col in df.columns:
                    df[col] = pd.to_datetime(df[col], utc=True)
            return df
        except Exception as e:
            logger.error(f"Failed to serialize response: {e}")
            return pd.DataFrame()

    def _call_api(self, api_method: Callable, **kwargs) -> pd.DataFrame:
        """Make a synchronous API call and return a serialized DataFrame."""
        start_time = time.time()
        log_context = {
            "api_method": api_method.__name__,
            "bmu": kwargs.get("bm_unit"),
            "start_date": str(kwargs.get("_from")),
            "end_date": str(kwargs.get("to")),
        }
        try:
            kwargs.pop("async_req", None)  # Ensure synchronous call
            response = api_method(**kwargs)
            df = self._serialize_response(response)
            duration = time.time() - start_time
            logger.info(
                f"API call completed, returned {len(df)} records",
                extra={"extra_data": {**log_context, "duration_s": f"{duration:.2f}"}},
            )
            return df
        except Exception as e:
            duration = time.time() - start_time
            logger.error(
                f"API call failed: {e}",
                extra={"extra_data": {**log_context, "duration_s": f"{duration:.2f}"}},
            )
            return pd.DataFrame()

    def get_physical_data(
        self,
        bmu: str,
        start_date: Union[str, dt.datetime],
        end_date: Union[str, dt.datetime],
        datasets: list = ["PN", "MELS", "MILS"],
    ) -> pd.DataFrame:
        """Get physical data for a BMU."""
        df = self._call_api(
            api_method=self.physapi.balancing_physical_get,
            bm_unit=bmu,
            _from=start_date,
            to=end_date,
            dataset=datasets,
        )
        if not df.empty and "time_from" in df.columns:
            df = df.dropna(subset=["time_from", "time_to"]).sort_values(by="time_from")
        return df
