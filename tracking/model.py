import mlflow.pyfunc
import pandas as pd

from service.runtime import load_checked_bundle
from src.bundle import predict_profiles


class TravelModel(mlflow.pyfunc.PythonModel):
    def load_context(self, context):
        self.bundle, _ = load_checked_bundle(context.artifacts["bundle"],
                                              context.artifacts["manifest"],
                                              context.artifacts["golden"])

    def predict(self, context, model_input, params=None):
        return pd.DataFrame(predict_profiles(self.bundle, model_input))
