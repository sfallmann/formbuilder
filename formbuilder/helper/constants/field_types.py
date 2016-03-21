CHECKBOX = "checkbox"
DATE = "date"
DATE_TIME = "datetime"
DATE_TIME_LOCAL = "datetime-local"
EMAIL = "email"
FILE = "file"
HIDDEN = "hidden"
HTML = "html"
MONTH = "month"
NUMBER = "number"
PASSWORD = "password"
RADIO = "radio"
SELECT = "select"
TEL = "tel"
COUNTRY = "country"
TEXT = "text"
TEXT_AREA = "textarea"
URL = "url"


def as_list():

    return [
        CHECKBOX,
        DATE,
        DATE_TIME,
        DATE_TIME_LOCAL,
        EMAIL,
        HIDDEN,
        HTML,
        MONTH,
        NUMBER,
        PASSWORD,
        RADIO,
        SELECT,
        TEL,
        COUNTRY,
        TEXT,
        TEXT_AREA,
        URL,
        FILE,
    ]

COMMON_ATTRS = [
    "help_text",
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

EMAIL_ATTRS = COMMON_ATTRS + [
    "send_confirmation",
]

COUNTRY_ATTRS = [
    "help_text",
    "autocomplete",
    "placeholder",
    "required",
]

NUM_ATTRS = COMMON_ATTRS + [
    "minvalue",
    "maxvalue",
]

CHOICE_ATTRS = [
    "help_text",
]

FILE_ATTRS = [
    "accept",
    "disabled",
    "help_text",
    "required",
    "maxfiles"
]

TEXT_AREA_ATTRS = [
    "autofocus",
    "help_text",
    "cols",
    "rows",
    "disabled",
    "maxlength",
    "placeholder",
    "readonly",
    #"required",
    #"value",
]

HTML_ATTRS = [
    "html"
]

CHECKBOX_ATTRS = [
    "help_text",
]

ATTRS = {
    CHECKBOX: CHECKBOX_ATTRS,
    DATE: NUM_ATTRS,
    DATE_TIME: NUM_ATTRS,
    DATE_TIME_LOCAL: NUM_ATTRS,
    EMAIL: EMAIL_ATTRS,
    HIDDEN: COMMON_ATTRS,
    HTML: HTML_ATTRS,
    MONTH: NUM_ATTRS,
    PASSWORD: COMMON_ATTRS,
    RADIO: CHOICE_ATTRS,
    SELECT: CHOICE_ATTRS,
    TEL: COMMON_ATTRS,
    COUNTRY: COUNTRY_ATTRS,
    TEXT: COMMON_ATTRS,
    TEXT_AREA: TEXT_AREA_ATTRS,
    URL: COMMON_ATTRS,
    FILE: FILE_ATTRS,
}


