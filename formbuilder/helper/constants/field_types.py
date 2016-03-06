CHECKBOX = "checkbox"
DATE = "date"
DATE_TIME = "datetime"
DATE_TIME_LOCAL = "datetim-local"
EMAIL = "email"
FILE = "file"
HIDDEN = "hidden"
MONTH = "month"
NUMBER = "number"
PASSWORD = "password"
RADIO = "radio"
SELECT = "select"
TEXT = "text"
TEXT_AREA = "textarea"

def as_list():

    return [
        #CHECKBOX,
        DATE,
        DATE_TIME,
        DATE_TIME_LOCAL,
        EMAIL,
        FILE,
        HIDDEN,
        MONTH,
        NUMBER,
        PASSWORD,
        RADIO,
        SELECT,
        TEXT,
        TEXT_AREA,
    ]

COMMON_ATTRS = [
    "autocomplete",
    "autofocus",
    "disabled",
    "maxlength",
    "pattern",
    "placeholder",
    "readonly",
    "required",
    #"value",
    ]

NUM_ATTRS = COMMON_ATTRS + [
    "min",
    "max",
]

CHOICE_ATTRS = [
    "choice_list"
]

FILE_ATTRS = [
    "accept",
    "disabled",
    "required",
]

TEXT_AREA_ATTRS = [
    "autofocus",
    "cols",
    "disabled",
    "maxlength",
    "placeholder"
    "readonly",
    "required",
    "rows",
    "value",
]

ATTRS = {

    DATE: NUM_ATTRS,
    DATE_TIME: NUM_ATTRS,
    DATE_TIME_LOCAL: NUM_ATTRS,
    EMAIL: COMMON_ATTRS,
    FILE: FILE_ATTRS,
    HIDDEN: COMMON_ATTRS,
    MONTH: NUM_ATTRS,
    PASSWORD: COMMON_ATTRS,
    RADIO: CHOICE_ATTRS,
    SELECT: CHOICE_ATTRS,
    TEXT: COMMON_ATTRS,
    TEXT_AREA: TEXT_AREA_ATTRS

}


