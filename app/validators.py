from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
import numpy as np
import pandas as pd


def validate_input_date_set_file(value):
    """
    Responsible for validating the input file for InputDataSet model to satisfy the following condition
        1. Low Bound, High Bound, Base, 10, 90 --> these headers should be present in the uploaded file
        2. Low Bound, High Bound, Base, 10, 90 --> should have all numeric and non-empty values
        3. Low Bound <= 10 <= Base <= 90 <= High Bound

    :param value: file object
    :return: raises validation error when validation fails else returns nothing
    """
    dataframe = pd.read_excel(value)
    try:
        dataframe['has_validation_error'] = np.where((dataframe['Low Bound'] <= dataframe[10]) &
                                                     (dataframe['Base'].between(dataframe[10], dataframe[90])) &
                                                     (dataframe['High Bound'] >= dataframe[90]), False, True)
    except TypeError:
        # Exception raised for non-numeric and empty inputs for fields Low Bound, Base, High Bound, 10 and 90.
        raise ValidationError(_(
            "Input file has some invalid entries(non-numeric or empty) for some columns "
            "(one of Low Bound, Base, High Bound, 10 and 90). Please correct the same and upload again."))
    except KeyError:
        # Exception raised for expected keys not present in the file uploaded.
        raise ValidationError(_(
            "Some columns are missing in the uploaded file. Please make sure to have columns namely - "
            "'Low Bound, Base, High Bound, 10, 90' and upload again."))

    if dataframe['has_validation_error'].eq(True).any():
        raise ValidationError(_("Input file has some invalid entries. Please make sure values satisfy - "
                                "'Low Bound <= 10 <= Base <= 90 <= High Bound' and upload again."))
